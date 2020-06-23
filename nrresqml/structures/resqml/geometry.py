from dataclasses import dataclass
from typing import Optional

from nrresqml.structures.energetics import Hdf5Dataset
from nrresqml.structures import xsd
from nrresqml.structures.resqml.common import AbstractLocal3dCrs
from nrresqml.structures.resqml._rqtools import ResqmlComplexType


@dataclass
class Point3d(ResqmlComplexType):
    Coordinate1: xsd.double
    Coordinate2: xsd.double
    Coordinate3: xsd.double


@dataclass
class Point3dOffset(ResqmlComplexType):
    Offset: Point3d


""" Abstract Value Array """


@dataclass
class AbstractValueArray(ResqmlComplexType):
    pass


@dataclass
class AbstractIntegerArray(AbstractValueArray):
    pass


@dataclass
class IntegerHdf5Array(AbstractIntegerArray):
    Values: Hdf5Dataset
    NullValue: xsd.integer


@dataclass
class AbstractDoubleArray(AbstractValueArray):
    pass


@dataclass
class DoubleHdf5Array(AbstractDoubleArray):
    Values: Hdf5Dataset


""" AbstractPoint3dArray """


@dataclass
class AbstractPoint3dArray(ResqmlComplexType):
    pass


@dataclass
class Point3dLatticeArray(AbstractPoint3dArray):
    AllDimensionsAreOrthogonal: Optional[xsd.boolean]
    Origin: Point3d
    Offset: Point3dOffset


@dataclass
class Point3dHdf5Array(AbstractPoint3dArray):
    Coordinates: Hdf5Dataset


@dataclass
class AbstractGeometry(ResqmlComplexType):
    LocalCrs: AbstractLocal3dCrs


@dataclass
class PointGeometry(AbstractGeometry):
    Points: AbstractPoint3dArray


@dataclass
class AbstractPoint3dArray(ResqmlComplexType):
    pass


@dataclass
class AbstractParametricLineArray(ResqmlComplexType):
    pass


@dataclass
class ParametricLineArray(AbstractParametricLineArray):
    ControlPointParameters: AbstractDoubleArray
    ControlPoints: AbstractPoint3dArray


@dataclass
class Point3dParametricArray(AbstractPoint3dArray):
    Parameters: AbstractValueArray
    ParametricLines: AbstractParametricLineArray
