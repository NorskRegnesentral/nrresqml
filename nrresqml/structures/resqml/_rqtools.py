from typing import List, Tuple, Optional

from nrresqml.structures.xsd import XsdComplexType, BasicEnum


_main_ns = ('resqml2', 'http://www.energistics.org/energyml/data/resqmlv2')


class ResqmlComplexType(XsdComplexType):
    @classmethod
    def namespaces(cls) -> List[Tuple[Optional[str], str]]:
        return [_main_ns] + super().namespaces()


class ResqmlBasicEnum(BasicEnum):
    @classmethod
    def namespaces(cls) -> List[Tuple[Optional[str], str]]:
        return [_main_ns]
