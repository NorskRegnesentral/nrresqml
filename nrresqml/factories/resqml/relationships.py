import pathlib

from nrresqml.structures.energetics import EpcExternalPartReference, AbstractObject
from nrresqml.structures.relationships import Relationship, TargetMode


def create_epc_external_part_reference_relationship(obj: EpcExternalPartReference, file_path: pathlib.Path
                                                    ) -> Relationship:
    return Relationship(str(obj.uuid), str(file_path), TargetMode.External,
                        'http://schemas.energistics.org/package/2012/relationships/externalResource')


def create_general_relationship(obj: AbstractObject) -> Relationship:
    return Relationship(str(obj.uuid), obj.base_name(), None,
                        'http://schemas.energistics.org/package/2012/relationships/externalPartProxyToMl')
