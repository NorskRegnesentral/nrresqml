from dataclasses import dataclass
from enum import Enum
from typing import List, Optional, Tuple

from nrresqml.structures import xsd


class TargetMode(Enum):
    External = 0
    Undefined = 1


@dataclass
class Relationship(xsd.XsdComplexType):
    Id: str
    Target: str
    TargetMode: Optional[TargetMode]
    Type: str

    @classmethod
    def namespaces(cls) -> List[Tuple[Optional[str], str]]:
        return []

    @classmethod
    def xml_attributes(cls) -> List[str]:
        return super().xml_attributes() + ['Id', 'Target', 'TargetMode', 'Type']


@dataclass
class Relationships(xsd.XsdComplexType):
    Relationship: List[Relationship]

    @classmethod
    def namespaces(cls) -> List[Tuple[Optional[str], str]]:
        return [(None, 'http://schemas.openxmlformats.org/package/2006/relationships')]
