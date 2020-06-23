from dataclasses import dataclass
from typing import Optional, List

from nrresqml.structures import xsd
from nrresqml.structures.resqml.geometry import AbstractValueArray
from nrresqml.structures.resqml.common import AbstractResqmlDataObject
from nrresqml.structures.resqml._rqtools import ResqmlComplexType, ResqmlBasicEnum
from nrresqml.structures.resqml.representations import IndexableElements, AbstractRepresentation


class ResqmlUom(ResqmlBasicEnum):
    m = 'm'


class ResqmlPropertyKind(ResqmlBasicEnum):
    discrete = 0
    porosity = 1
    permeability_rock = 2
    permeability_length = 3
    permeability_thickness = 4
    volume_per_volume = 5
    categorical = 6


""" PatchOfValues """


@dataclass
class PatchOfValues(ResqmlComplexType):
    RepresentationPatchIndex: xsd.integer
    Values: AbstractValueArray


""" AbstractPropertyKind """


@dataclass
class AbstractPropertyKind(ResqmlComplexType):
    pass


@dataclass
class PropertyKind(AbstractResqmlDataObject):
    NamingSystem: xsd.string
    IsAbstract: xsd.boolean
    Representative_uom: ResqmlUom
    ParentPropertyKind: AbstractPropertyKind


@dataclass
class LocalPropertyKind(AbstractPropertyKind):
    LocalPropertyKind: PropertyKind


@dataclass
class StandardPropertyKind(AbstractPropertyKind):
    Kind: ResqmlPropertyKind


""" AbstractPropertyLookup and StringLookup """


@dataclass
class StringLookup(ResqmlComplexType):
    Key: xsd.integer
    Value: xsd.string


@dataclass
class AbstractPropertyLookup(AbstractResqmlDataObject):
    pass


@dataclass
class StringTableLookup(AbstractPropertyLookup):
    Value: List[StringLookup]


""" AbstractProperty """


@dataclass
class AbstractProperty(AbstractResqmlDataObject):
    IndexableElement: IndexableElements
    Count: xsd.positiveInteger
    RealizationIndex: Optional[xsd.positiveInteger]
    TimeStep: Optional[xsd.positiveInteger]
    SupportingRepresentation: AbstractRepresentation
    PropertyKind: AbstractPropertyKind


@dataclass
class AbstractValuesProperty(AbstractProperty):
    PatchOfValues: PatchOfValues


@dataclass
class CategoricalProperty(AbstractValuesProperty):
    Lookup: AbstractPropertyLookup


@dataclass
class ContinuousProperty(AbstractValuesProperty):
    MinimumValue: xsd.double
    Uom: ResqmlUom  # underscores added since the true property name is UOM, deviating from CamelCase
    MaximumValue: xsd.double
