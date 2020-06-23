import getpass
import uuid

from nrresqml.structures import xsd
from nrresqml.structures.energetics import Citation, UuidString, DescriptionString, NameString

_SCHEMA_VERSION = 'v2.0.1'


def create_meta_data(title):
    return dict(
        uuid=UuidString(str(uuid.uuid1())),
        schemaVersion=_SCHEMA_VERSION,
        Citation=Citation(
            Title=DescriptionString(title),
            Originator=NameString(getpass.getuser()),
            Format=DescriptionString('[NorwegianComputingCenter:netcdf2resqml]'),
            Creation=xsd.dateTime.now(),
        )
    )
