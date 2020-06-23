from nrresqml.factories.resqml.common import create_meta_data
from nrresqml.structures import xsd
from nrresqml.structures.energetics import EpcExternalPartReference, DataObjectReference, AbstractObject,\
    DescriptionString


def create_hdf5_reference():
    meta = create_meta_data('Hdf Proxy')
    return EpcExternalPartReference(**meta, MimeType=xsd.string('application/x-hdf5'))


def reference(obj: AbstractObject) -> DataObjectReference:
    if isinstance(obj, EpcExternalPartReference):
        title = DescriptionString('Hdf Proxy')
    else:
        title = obj.Citation.Title
    ct = xsd.string(obj.content_type_string())
    return DataObjectReference(ct, title, obj.uuid, None, None)
