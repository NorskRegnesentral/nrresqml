from dataclasses import dataclass
from typing import List, Tuple, Optional

from nrresqml.structures import xsd


class W3CDTF(xsd.dateTime):
    @classmethod
    def namespaces(cls) -> List[Tuple[Optional[str], str]]:
        return [('dcterms', 'http://purl.org/dc/terms/')] + super().namespaces()


@dataclass
class coreProperties(xsd.XsdComplexType):
    # TODO: the namespace of these types is not correct
    created: W3CDTF
    creator: xsd.string

    @classmethod
    def namespaces(cls) -> List[Tuple[Optional[str], str]]:
        return [
                   ('cp', 'http://schemas.openxmlformats.org/package/2006/metadata/core-properties'),
                   ('dc', 'http://purl.org/dc/elements/1.1/'),
                   ('dcterms', 'http://purl.org/dc/terms/'),
               ] + super().namespaces()
