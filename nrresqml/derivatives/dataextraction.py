import numpy as np
import h5py
from typing import Optional

from nrresqml.resqml import ResQml
from nrresqml.structures.energetics import Hdf5Dataset
from nrresqml.structures.resqml.geometry import IntegerHdf5Array, DoubleHdf5Array, Point3dParametricArray, \
    ParametricLineArray, Point3dHdf5Array
from nrresqml.structures.resqml.properties import CategoricalProperty, ContinuousProperty
from nrresqml.structures.resqml.representations import AbstractRepresentation, IjkGridRepresentation, IjkGridGeometry


def crop_array(arr_zxy,
               array_x0,
               array_y0,
               array_dx,
               array_dy,
               crop_x0,
               crop_y0,
               crop_x1,
               crop_y1):
    assert crop_x1 > crop_x0 and crop_y1 > crop_y0
    nx, ny = arr_zxy.shape[1:]
    # Determine crop indexes
    i0 = np.ceil((crop_x0 - array_x0) / array_dx)
    j0 = np.ceil((crop_y0 - array_y0) / array_dy)
    i1 = np.floor((crop_x1 - array_x0) / array_dx)
    j1 = np.floor((crop_y1 - array_y0) / array_dy)
    i0 = int(max(0, i0))
    j0 = int(max(0, j0))
    i1 = int(min(nx, i1))
    j1 = int(min(ny, j1))
    assert j1 > j0 and i1 > i0  # Verify that the crop box is properly specified
    return arr_zxy[:, i0:i1, j0:j1]


def extract_geometry(rq: ResQml, flatten_pillars: bool, indexing: str):
    assert indexing in ('ijk', 'kij')
    # Extract pillars and other grid parameters
    z = list(rq.objects(IjkGridRepresentation))
    assert len(z) == 1  # Should be one and only one grid in the object. Multiple grids are not supported (yet)
    # Assert on types to be explicit about the assumed types and to aid code completion
    ijk = z[0]
    assert isinstance(ijk, IjkGridRepresentation)
    assert isinstance(ijk.Geometry, IjkGridGeometry)
    assert isinstance(ijk.Geometry.Points, Point3dParametricArray)
    assert isinstance(ijk.Geometry.Points.ParametricLines, ParametricLineArray)
    assert isinstance(ijk.Geometry.Points.ParametricLines.ControlPointParameters, DoubleHdf5Array)
    pillars = _extract_dataset(rq, ijk.Geometry.Points.ParametricLines.ControlPointParameters.Values)
    assert isinstance(ijk.Geometry.Points.ParametricLines.ControlPoints, Point3dHdf5Array)
    xxyyzz = _extract_dataset(rq, ijk.Geometry.Points.ParametricLines.ControlPoints.Coordinates)
    if xxyyzz.ndim == 3:
        # This is technically an outdated format, but is supported nonetheless
        xx, yy = xxyyzz[:, :, 0], xxyyzz[:, :, 1]
        # Pillars are technically already flattened when this format is used, as the outdated format did not support
        # a non-flattened format. The primary purpose of the new format was to support this types of pillars.
        flatten_pillars = False
    else:
        assert xxyyzz.ndim == 4
        xx, yy = xxyyzz[:, :, :, 0], xxyyzz[:, :, :, 1]
    if flatten_pillars:
        xx = xx[0, :, :]
        yy = yy[0, :, :]
        pillars = np.mean(pillars, axis=0)
    pillars = pillars.transpose({'ijk': (0, 1, 2), 'kij': (2, 0, 1)}[indexing])
    return ijk, xx, yy, pillars


def extract_property(resqml: ResQml, supp_rep: Optional[AbstractRepresentation], h5_path: str, categorical: bool):
    if categorical:
        p_type = CategoricalProperty
        a_type = IntegerHdf5Array
    else:
        p_type = ContinuousProperty
        a_type = DoubleHdf5Array
    props = [
        a for a in resqml.objects(p_type)
        if isinstance(a, p_type)
        and isinstance(a.PatchOfValues.Values, a_type)
        and a.PatchOfValues.Values.Values.PathInHdfFile == h5_path
        and (supp_rep is None or a.SupportingRepresentation.uuid == supp_rep.uuid)
    ]
    assert len(props) == 1
    prop = props[0].PatchOfValues.Values
    assert isinstance(prop, a_type)
    return _extract_dataset(resqml, prop.Values)


def _extract_dataset(resqml: ResQml, hdf5_dataset: Hdf5Dataset):
    hdf5_path = resqml.get_full_hdf5_reference(hdf5_dataset.HdfProxy)
    h5ds = h5py.File(hdf5_path, mode='r')
    hdf5_path = hdf5_dataset.PathInHdfFile
    # Convert to ndarray. This yields easier-to-read error message if something goes wrong with indexing (or similar)
    return np.array(h5ds[hdf5_path])
