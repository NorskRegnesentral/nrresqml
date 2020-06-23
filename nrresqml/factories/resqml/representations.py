from nrresqml.factories.resqml.common import create_meta_data
from nrresqml.structures import xsd
from nrresqml.structures.energetics import VerticalUnknownCrs, ProjectedCrsEpsgCode, AxisOrder2d, LengthUom
from nrresqml.structures.resqml.common import LocalDepth3dCrs
from nrresqml.structures.resqml.geometry import Point3dOffset, Point3d, Point3dLatticeArray
from nrresqml.structures.resqml.representations import IjkGridGeometry, KDirection, IjkGridRepresentation


def create_local_depth_3d_crs():
    v_crs = VerticalUnknownCrs(xsd.string('Unknown'))
    p_crs = ProjectedCrsEpsgCode(xsd.positiveInteger(4146))
    crs_meta = create_meta_data('Delft 3D CRS')
    crs = LocalDepth3dCrs(
        **crs_meta,
        ArealRotation=xsd.double(0.0),
        ProjectedAxisOrder=AxisOrder2d.easting_northing,
        ProjectedUom=LengthUom.m,
        VerticalUom=LengthUom.m,
        XOffset=xsd.double(0.0),
        YOffset=xsd.double(0.0),
        ZIncreasingDownward=xsd.boolean(True),
        ZOffset=xsd.double(0.0),
        VerticalCrs=v_crs,
        ProjectedCrs=p_crs
    )
    return crs


def create_grid_representation_for_regular_grid(ni, nj, nk, dx, dy, dz) -> IjkGridRepresentation:
    crs = create_local_depth_3d_crs()
    ds = Point3dOffset(Point3d(dx, dy, dz))
    arr = Point3dLatticeArray(xsd.boolean(True), Point3d(xsd.double(0.0), xsd.double(0.0), xsd.double(0.0)), ds)
    geom = IjkGridGeometry(crs, arr, KDirection.down, xsd.boolean(True))
    grid_meta = create_meta_data('Converted Delft 3D grid')
    grid = IjkGridRepresentation(**grid_meta, Geometry=geom, Ni=ni, Nj=nj, Nk=nk)
    return grid
