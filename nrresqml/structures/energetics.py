import re
from dataclasses import dataclass
from typing import Optional, List, Tuple, Any
from nrresqml.structures import xsd


_main_ns = ('eml', 'http://www.energistics.org/energyml/data/commonv2')
_uuid_regex = re.compile(r"[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}")


class _EnergeticsEnum(xsd.BasicEnum):
    @classmethod
    def namespaces(cls) -> List[Tuple[Optional[str], str]]:
        return [_main_ns]


@dataclass
class _EnergeticsComplexType(xsd.XsdComplexType):
    @classmethod
    def namespaces(cls) -> List[Tuple[Optional[str], str]]:
        return [_main_ns] + super().namespaces()


""" Basic types """


class DescriptionString(xsd.string):
    @classmethod
    def namespaces(cls) -> List[Tuple[Optional[str], str]]:
        return [_main_ns] + super().namespaces()


class NameString(xsd.string):
    @classmethod
    def namespaces(cls) -> List[Tuple[Optional[str], str]]:
        return [_main_ns] + super().namespaces()


class UuidString(xsd.string):
    def __new__(cls, value) -> Any:
        assert re.match(_uuid_regex, value) is not None
        return super().__new__(cls, value)

    @classmethod
    def namespaces(cls) -> List[Tuple[Optional[str], str]]:
        return [_main_ns] + super().namespaces()


""" Complex types """


@dataclass
class DataObjectReference(xsd.XsdComplexType):
    ContentType: xsd.string
    Title: DescriptionString
    UUID: UuidString
    UuidAuthority: Optional[xsd.string]
    VersionString: Optional[NameString]


@dataclass
class Citation(_EnergeticsComplexType):
    Title: DescriptionString
    Originator: NameString
    Format: DescriptionString
    Creation: xsd.dateTime


@dataclass
class AbstractObject(_EnergeticsComplexType):
    schemaVersion: xsd.string
    uuid: UuidString
    Citation: Optional[Citation]

    @classmethod
    def xml_attributes(cls) -> List[str]:
        return super().xml_attributes() + ['uuid', 'schemaVersion']

    def base_name(self) -> str:
        return f'obj_{self.type_name()}_{self.uuid}.xml'


@dataclass
class AbstractCitedDataObject(AbstractObject):
    Citation: Citation


@dataclass
class EpcExternalPartReference(AbstractCitedDataObject):
    MimeType: xsd.string


@dataclass
class Hdf5Dataset(_EnergeticsComplexType):
    PathInHdfFile: xsd.string
    HdfProxy: EpcExternalPartReference


class AxisOrder2d(_EnergeticsEnum):
    easting_northing = 0
    northing_easting = 1
    westing_southing = 2
    southing_westing = 3
    northing_westing = 4
    westing_northing = 5


@dataclass
class AbstractVerticalCrs(_EnergeticsComplexType):
    pass


@dataclass
class AbstractProjectedCrs(_EnergeticsComplexType):
    pass


@dataclass
class VerticalUnknownCrs(AbstractVerticalCrs):
    Unknown: xsd.string


@dataclass
class ProjectedCrsEpsgCode(AbstractProjectedCrs):
    EpsgCode: xsd.positiveInteger


class LengthUom(_EnergeticsEnum):
    m = 0


class TimeUom(_EnergeticsEnum):
    ms = 0
