from dataclasses import dataclass
from typing import List, Tuple, Optional

from nrresqml.structures.resqml._rqtools import ResqmlComplexType
from nrresqml.structures import xsd
from nrresqml.structures.energetics import AxisOrder2d, AbstractVerticalCrs, AbstractProjectedCrs, LengthUom, TimeUom,\
    AbstractCitedDataObject


@dataclass
class AbstractResqmlDataObject(AbstractCitedDataObject, ResqmlComplexType):
    @classmethod
    def namespaces(cls) -> List[Tuple[Optional[str], str]]:
        r_ns = ResqmlComplexType.namespaces()
        a_ns = AbstractCitedDataObject.namespaces()
        order = r_ns + a_ns
        return list(dict.fromkeys(order).keys())  # Cast to dict to make sure keys are unique


@dataclass
class AbstractLocal3dCrs(AbstractResqmlDataObject):
    ArealRotation: xsd.double
    ProjectedAxisOrder: AxisOrder2d
    ProjectedUom: LengthUom
    VerticalUom: LengthUom
    XOffset: xsd.double
    YOffset: xsd.double
    ZIncreasingDownward: xsd.boolean
    ZOffset: xsd.double
    VerticalCrs: AbstractVerticalCrs
    ProjectedCrs: AbstractProjectedCrs


@dataclass
class LocalDepth3dCrs(AbstractLocal3dCrs):
    pass


@dataclass
class LocalTime3dCrs(AbstractLocal3dCrs):
    TimeUom: TimeUom
