from dataclasses import dataclass

import h5py
import numpy as np

from nrresqml.factories.resqml.common import create_meta_data
from nrresqml.factories.resqml.representations import create_local_depth_3d_crs
from nrresqml.structures import xsd
from nrresqml.structures.energetics import EpcExternalPartReference, Hdf5Dataset
from nrresqml.structures.resqml.geometry import DoubleHdf5Array, Point3dHdf5Array, ParametricLineArray,\
    Point3dParametricArray
from nrresqml.structures.resqml.representations import IjkGridRepresentation, IjkGridGeometry, KDirection


class IjkGridCreationError(Exception):
    pass


@dataclass
class _GridParameters:
    nx: int
    ny: int
    nz: int
    dx: float
    dy: float
    zz: np.ndarray
    x0: float
    y0: float


def _extract_grid_parameters(_d3_file: h5py.File) -> _GridParameters:
    # Check that the file contains the expected parameters
    _keys = set(_d3_file.keys())
    if not {'XCOR', 'xcor'}.intersection(_keys):
        raise IjkGridCreationError('Missing at least parameter "XCOR" or "xcor"')
    if not {'YCOR', 'ycor'}.intersection(_keys):
        raise IjkGridCreationError('Missing at least parameter "YCOR" or "ycor"')
    if not {'DPS', 'zcor'}.intersection(_keys):
        raise IjkGridCreationError('Missing at least parameter "DPS" or "zcor"')
    # Extract parameters
    xcor = _d3_file['xcor'] if 'xcor' in _keys else _d3_file['XCOR']
    ycor = _d3_file['ycor'] if 'ycor' in _keys else _d3_file['YCOR']
    zcor = _d3_file['zcor'] if 'zcor' in _keys else _d3_file['DPS']
    nk, ni, nj = zcor.shape
    dx = (np.max(xcor) - np.min(xcor)) / (ni - 1)
    dy = (np.max(ycor) - np.min(ycor)) / (nj - 1)
    zz = np.array(zcor)
    if 'zcor' not in _d3_file:
        # DPS was used, which is a temporal layer and may not be spatially feasible
        zz = IjkGridCreator.mono_elevation(zz)
    return _GridParameters(ni, nj, nk, dx, dy, zz, xcor[0, 0], ycor[0, 0])


def _hdf5_array(h5_epc_ref: EpcExternalPartReference, h5_path: str):
    vals = Hdf5Dataset(xsd.string(h5_path), h5_epc_ref)
    arr = DoubleHdf5Array(vals)
    return arr


class IjkGridCreator:
    def __init__(self, d3_file: h5py.File) -> None:
        """
        Class used to create an IJK grid from a given data file. The file is expected to come from Delft 3D. This means
        that it is assumed to contain at least the variables DPS, XCOR and YCOR, which will be used to build the grid.
        Alternatively, zcor, xcor, ycor. Most importantly, it interprets the grid to have flat cell tops.

        :param d3_file: A HDF5 file, imported by h5py
        """
        # Grid geometry data
        gp = _extract_grid_parameters(d3_file)
        self._control_points = IjkGridCreator.pillarized_control_points(gp)
        # Control point parameters. Describes each pillar as monotonized z values
        self._control_point_parameters = IjkGridCreator.pillarize(gp.zz)

    @property
    def _control_points_path(self):
        return f'control_points_{id(self._control_points)}'

    @property
    def _control_point_parameters_path(self):
        return f'control_point_parameters_{id(self._control_point_parameters)}'

    @property
    def pillars(self) -> np.ndarray:
        """
        Returns the regularly spaced pillars that represents the grid as a Nx x Ny x Nz grid. The pillars are
        monotonically increasing in the z-direction
        :return:
        """
        # With the current implementation, the pillars exactly match the control point parameters.
        return self._control_point_parameters

    def ijk_representation(self, h5_epc_ref: EpcExternalPartReference) -> IjkGridRepresentation:
        """
        Creates and returns the IjkGridRepresentation for the input data file

        :param h5_epc_ref: The EpcExternalPartReference that is used to reference the data file (HDF5 file) that
                           corresponds to the ResQml file.

        :return:           The IjkGridRepresentation of the grid constructed from the d3_file
        """
        # Create geometry
        crs = create_local_depth_3d_crs()
        plane = Point3dHdf5Array(Hdf5Dataset(xsd.string(self._control_points_path), h5_epc_ref))
        lines = ParametricLineArray(
            _hdf5_array(h5_epc_ref, self._control_point_parameters_path),
            plane
        )
        points = Point3dParametricArray(_hdf5_array(h5_epc_ref, self._control_points_path), lines)
        geom = IjkGridGeometry(crs, points, KDirection.up, xsd.boolean(True))
        # Create representation
        meta = create_meta_data('Delft 3D-based grid')
        rep = IjkGridRepresentation(
            **meta,
            Geometry=geom,
            Nk=xsd.positiveInteger(self._control_point_parameters.shape[3]),
            Ni=xsd.positiveInteger(self._control_point_parameters.shape[1]),
            Nj=xsd.positiveInteger(self._control_point_parameters.shape[2])
        )
        return rep

    def dump_grid_data(self, h5_file: h5py.File):
        h5_file.create_dataset(
            self._control_points_path, data=self._control_points, compression='gzip'
        )
        h5_file.create_dataset(
            self._control_point_parameters_path, data=self._control_point_parameters, compression='gzip'
        )

    @staticmethod
    def mono_elevation(depth: np.ndarray) -> np.ndarray:
        """
        Convert depth values to elevation values, and truncate them at
        every time step to ensure elevation is monotonically nondecreasing
        in time at every grid location.
        :param depth: DPS from Delft3D output file. 3D numpy array
        :return: truncated elevation values. 3D numpy array
        """
        base_depth = depth[0, :, :]
        relative_elevation = depth - base_depth
        truncated_elevation = np.maximum.accumulate(relative_elevation[::-1, :, :], axis=0)[::-1]
        return -truncated_elevation

    @staticmethod
    def pillarized_control_points(gp: _GridParameters):
        cp = np.ndarray((4, gp.nx, gp.ny, 3), dtype=np.float)
        xx, yy = np.meshgrid(np.arange(gp.nx + 1) * gp.dx, np.arange(gp.ny + 1) * gp.dy, indexing='ij')
        # Control points. Describes the lateral distribution of pillars
        cp[0, :, :, 0] = xx[:-1, :-1]
        cp[1, :, :, 0] = xx[1:, :-1]
        cp[2, :, :, 0] = xx[1:, 1:]
        cp[3, :, :, 0] = xx[-1:, 1:]
        cp[0, :, :, 1] = yy[:-1, :-1]
        cp[1, :, :, 1] = yy[1:, :-1]
        cp[2, :, :, 1] = yy[1:, 1:]
        cp[3, :, :, 1] = yy[-1:, 1:]

        # Add reference and set z-value to nan
        cp[:, :, :, 0] += gp.x0
        cp[:, :, :, 1] += gp.y0
        cp[:, :, :, 2] = np.nan
        return cp

    @staticmethod
    def pillarize(pillars: np.ndarray) -> np.ndarray:
        """
        Convert shared pillars (nz x nx x ny) to split pillars (4 x nx x ny x nz)
        """
        assert pillars.ndim == 3
        nk, ni, nj = pillars.shape
        column_pillars = np.zeros((4, ni, nj, nk), dtype=pillars.dtype)
        pt = pillars.transpose((1, 2, 0))
        # Duplicate pillars.
        column_pillars[0, :, :, :] = pt
        column_pillars[1, :, :, :] = pt
        column_pillars[2, :, :, :] = pt
        column_pillars[3, :, :, :] = pt
        return column_pillars
