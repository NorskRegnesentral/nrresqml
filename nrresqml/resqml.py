import glob
import pathlib
from dataclasses import is_dataclass
from typing import List, Dict, Iterator, Optional, Type
from zipfile import ZipFile

from lxml import etree

from nrresqml.serialization.postprocessing import resolve_references
from nrresqml.serialization import objectify
from nrresqml.derivatives import utils
from nrresqml.factories.resqml import relationships
from nrresqml.structures import contenttypes
from nrresqml.structures.energetics import AbstractObject, EpcExternalPartReference, UuidString
from nrresqml.structures.relationships import Relationships


def _create_content_type_override(obj: AbstractObject) -> contenttypes.Override:
    return contenttypes.Override(obj.content_type_string(), '/' + obj.base_name())


class ResQml:
    def __init__(self, objects: List[AbstractObject], root_path: pathlib.Path) -> None:
        assert root_path.suffix == '.epc'
        # Path to the root directory of the ResQml file. Primarily used to access the HDF5 data file properly
        self._root_path = root_path
        # List of all the ResQml objects (internal representations)
        self._objects = objects
        # Dict that maps uuid's to their corresponding HDF5 file. For the ResQml object to be consistent, it is
        # necessary that each object of type EpcExternalPartReference has a corresponding entry in this dict.
        self._hdf5_refs: Dict[UuidString, str] = {}

    def set_hdf5_reference(self, obj: EpcExternalPartReference, hdf5_file: str):
        assert obj in self._objects
        self._hdf5_refs[obj.uuid] = hdf5_file

    def get_full_hdf5_reference(self, obj: EpcExternalPartReference) -> str:
        return str(self._root_path.parent / self._hdf5_refs[obj.uuid])

    def objects(self, types: Optional[Type] = None) -> Iterator[AbstractObject]:
        for obj in self._objects:
            if types is None or isinstance(obj, types):
                yield obj

    def find(self, uuid: UuidString) -> Optional[AbstractObject]:
        for o in self._objects:
            if o.uuid == uuid:
                return o
        return None

    def relationships(self, obj: AbstractObject) -> Relationships:
        # Check if obj is an EpcExternalPartReference, in which case it is handled in a special way
        if isinstance(obj, EpcExternalPartReference):
            fp = self._hdf5_refs[obj.uuid]
            rels = relationships.create_epc_external_part_reference_relationship(obj, pathlib.Path(fp))
            return Relationships([rels])

        r = []
        for _, att_obj in utils.iterate_attributes(obj):
            if att_obj in self._objects:
                # Attribute is referenced, create and append relationship
                r.append(relationships.create_general_relationship(att_obj))
            elif is_dataclass(att_obj):
                # Attribute is not referenced, but may reference other objects deeper in the hierarchy
                r += self.relationships(att_obj).Relationship
        return Relationships(r)

    def content_types(self) -> contenttypes.Types:
        defs = [
            contenttypes.Default('application/vnd.openxmlformats-package.relationships+xml', 'rels'),
            contenttypes.Default('application/xml', 'xml'),
        ]
        overrides = [_create_content_type_override(obj) for obj in self._objects]
        return contenttypes.Types(defs, overrides)

    @staticmethod
    def read(cache_dir: pathlib.Path) -> 'ResQml':
        # Load objects
        fn = glob.glob(str(cache_dir) + '/*.xml')
        ets = [etree.parse(f) for f in fn]
        objs = [objectify.objectify(e.getroot()) for e in ets]
        [resolve_references(obj, objs) for obj in objs]
        rq = ResQml(objs, cache_dir)

        # Set hdf5 references
        h5_file = cache_dir.with_suffix('.h5').name  # Assumed convention to ensure relative paths are correct
        for epr in rq.objects(EpcExternalPartReference):
            rq.set_hdf5_reference(epr, h5_file)
        return rq

    @staticmethod
    def read_zipped(epc_file: pathlib.Path) -> 'ResQml':
        with ZipFile(epc_file, 'r') as z:
            ets = [
                etree.parse(z.open(n))
                for n in z.namelist()
                if n.endswith('.xml') and n.startswith('obj_')
            ]
            objs = [objectify.objectify(e.getroot()) for e in ets]
            [resolve_references(obj, objs) for obj in objs]
            rq = ResQml(objs, epc_file)

            # Set hdf5 references
            h5_file = epc_file.with_suffix('.h5').name  # Assumed convention to ensure relative paths are correct
            for epr in rq.objects(EpcExternalPartReference):
                rq.set_hdf5_reference(epr, h5_file)
        return rq
