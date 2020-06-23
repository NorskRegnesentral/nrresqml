import os
import pathlib
import shutil
from zipfile import ZipFile

from lxml import etree

from nrresqml.serialization import elementify
from nrresqml.derivatives.hdf5resqmladaptor import Hdf5ResQmlAdaptor
from nrresqml.resqml import ResQml
from nrresqml.structures import contenttypes, xsd
from nrresqml.structures.energetics import EpcExternalPartReference, AbstractObject
from nrresqml.structures.relationships import Relationships, Relationship


_RELS_DIR = '_rels'


def _create_cache_folder(cache_dir: pathlib.Path):
    os.makedirs(str(cache_dir), exist_ok=False)
    os.makedirs(str(cache_dir / _RELS_DIR))
    os.makedirs(str(cache_dir / 'docProps'))


class _Cacher:
    def __init__(self, save_path: pathlib.Path, zip_mode: bool) -> None:
        self._zip_mode = zip_mode
        self._epc_file_path = save_path.with_suffix('.epc')
        # Initialize folders
        if not zip_mode:
            # Will throw if folder already exists
            _create_cache_folder(self._epc_file_path)
        else:
            # Ok if folder exists, but file cannot
            os.makedirs(str(self._epc_file_path.parent), exist_ok=True)
            if self._epc_file_path.is_file():
                os.remove(str(self._epc_file_path))

    def _handle(self, base_name: str):
        if self._zip_mode:
            return ZipFile(self._epc_file_path, 'a').open(base_name, 'w')
        else:
            return str(self._epc_file_path / base_name)

    def dump_epc_object(self, obj: AbstractObject, el: etree.Element):
        tree_obj = etree.ElementTree(el)
        base_name = obj.base_name()
        fh = self._handle(base_name)
        tree_obj.write(fh, pretty_print=True, encoding='utf-8', xml_declaration=True)

    def dump_relationships(self, obj: AbstractObject, rels: Relationships):
        el = elementify.elementify(rels, [], None)
        tree_obj = etree.ElementTree(el)
        fn = pathlib.Path(_RELS_DIR) / (obj.base_name() + '.rels')
        fh = self._handle(str(fn))
        tree_obj.write(fh, pretty_print=True, standalone=False, encoding='utf-8')

    def dump_content_types(self, ct: contenttypes.Types):
        el = elementify.elementify(ct, [], None)
        tree = etree.ElementTree(el)
        fh = self._handle('[ContentTypes].xml')
        tree.write(fh, pretty_print=True, standalone=False, encoding='utf-8')

    def dump_dot_rels(self):
        type_ = 'http://schemas.openxmlformats.org/package/2006/relationships/metadata/core-properties'
        r = [Relationship('rId1', 'docProps/core.xml', None, type_)]
        rs = Relationships(r)
        el = elementify.elementify(rs, [], None)
        tree = etree.ElementTree(el)
        fh = self._handle('_rels/.rels')
        tree.write(fh, pretty_print=True, standalone=False, encoding='utf-8')

    def dump_core(self):
        from nrresqml.structures import core
        core = core.coreProperties(core.W3CDTF.now(), xsd.string('NR ResQml from NetCDF'))
        el = elementify.elementify(core, [], None)
        tree = etree.ElementTree(el)
        fh = self._handle('docProps/core.xml')
        tree.write(fh, pretty_print=True, standalone=False, encoding='utf-8')


def build_from_adaptor(adaptor: Hdf5ResQmlAdaptor, save_path: pathlib.Path, use_zip=False) -> ResQml:
    """
    Creates a ResQml object from the given adaptor and writes it to file. Returns the created ResQml instance for
    convenience
    """
    # Create the objects
    obs = adaptor.create_objects()
    h5_fn = save_path.with_suffix('.h5').name
    rq = ResQml(obs, save_path)
    for ec in rq.objects(EpcExternalPartReference):
        rq.set_hdf5_reference(ec, h5_fn)

    # Set up the cacher
    c = _Cacher(save_path.with_suffix('.epc'), use_zip)

    # Dump objects
    for obj in obs:
        el = elementify.elementify(obj, obs, None)
        c.dump_epc_object(obj, el)

    # Dump relationships
    for obj in obs:
        rs = rq.relationships(obj)
        c.dump_relationships(obj, rs)

    # Dump content types
    c.dump_content_types(rq.content_types())

    # Dump datafile
    df = save_path.parent / h5_fn
    adaptor.dump_h5_file(df)

    # Dump boiler-plate files
    c.dump_dot_rels()
    c.dump_core()

    return rq
