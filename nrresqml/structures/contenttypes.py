from dataclasses import dataclass
from typing import List, Tuple, Optional

from nrresqml.structures import xsd


@dataclass
class _ContentTypesComplexType(xsd.XsdComplexType):
    @classmethod
    def namespaces(cls) -> List[Tuple[Optional[str], str]]:
        return [(None, 'http://schemas.openxmlformats.org/package/2006/content-types')]


@dataclass
class Default(_ContentTypesComplexType):
    ContentType: str
    Extension: str

    @classmethod
    def xml_attributes(cls) -> List[str]:
        return ['ContentType', 'Extension'] + super().xml_attributes()


@dataclass
class Override(_ContentTypesComplexType):
    ContentType: str
    PartName: str

    @classmethod
    def xml_attributes(cls) -> List[str]:
        return ['ContentType', 'PartName'] + super().xml_attributes()


@dataclass
class Types(_ContentTypesComplexType):
    Default: List[Default]
    Override: List[Override]
