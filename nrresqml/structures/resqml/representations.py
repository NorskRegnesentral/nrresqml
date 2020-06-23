from dataclasses import dataclass

from nrresqml.structures import xsd
from nrresqml.structures.resqml.common import AbstractResqmlDataObject
from nrresqml.structures.resqml._rqtools import ResqmlBasicEnum
from nrresqml.structures.resqml.geometry import AbstractGeometry, PointGeometry


class KDirection(ResqmlBasicEnum):
    up = 0
    down = 1


class IndexableElements(ResqmlBasicEnum):
    cells = 0


@dataclass
class AbstractGridGeometry(PointGeometry):
    pass


@dataclass
class AbstractColumnLayerGridGeometry(AbstractGridGeometry):
    # Only implements k_direction. Other parameters may be required as well
    KDirection: KDirection


@dataclass
class IjkGridGeometry(AbstractColumnLayerGridGeometry):
    GridIsRightHanded: xsd.boolean


@dataclass
class AbstractRepresentation(AbstractResqmlDataObject):
    Geometry: AbstractGeometry


@dataclass
class AbstractGridRepresentation(AbstractRepresentation):
    pass


@dataclass
class AbstractColumnLayerGridRepresentation(AbstractGridRepresentation):
    Nk: xsd.positiveInteger


@dataclass
class IjkGridRepresentation(AbstractColumnLayerGridRepresentation):
    Ni: xsd.positiveInteger
    Nj: xsd.positiveInteger
