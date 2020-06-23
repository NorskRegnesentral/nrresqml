import sys
import os
import pathlib

from nrresqml.derivatives.hdf5resqmladaptor import Delft3DResQmlAdaptor, AdaptorError
from nrresqml.derivatives import rqbuilder as rio


def _derive_archel_name(delft3d_name: str):
    # TODO: handle the variety of naming conventions for files containing architectural elements/subenvironments.
    #  The following observations are made:
    #    * Subenvironment files usually exists for older results, but are less refined
    #    * Architectural elements files does not yet exist on the threadds server
    #    * Architectural elements files seem to contain both subenvironment and architectural elements data sets
    if delft3d_name.startswith('http'):
        # Files on the OpenDAP server does not yet contain architectural elements, only sub-environment
        return os.path.dirname(delft3d_name).replace('simulation', 'postprocess') + '/subenvironment.nc'
    else:
        an = os.path.dirname(delft3d_name) + '/architectural_elements.nc'
        if os.path.isfile(an):
            return an
        else:
            # This should perhaps be the first attempt, if the file has the required keys (archel/subenv)
            return delft3d_name


def convert_delft3d_to_resqml(delft3d_file_name: str, resqml_output_directory: str) -> None:
    """
    Converts an existing Delft3D NetCdf file to a ResQml file(s)

    :param delft3d_file_name:       File path to the NetCdf file (usually a .nc file)
    :param resqml_output_directory: Path to an existing directory where the ResQml database should be written. The
                                    directory must already exist and be writable. The following two files will be
                                    written:
                                        - resqml_output_directory/<resqml_file_name>.epc
                                        - resqml_output_directory/<resqml_file_name>.h5
                                     The base name 'resqml_file_name' is derived from delft3d_file_name
    """
    try:
        # Derive name of file containing architectural elements from the base name
        archel_file = _derive_archel_name(delft3d_file_name)
        daf = Delft3DResQmlAdaptor(
            delft3d_file_name,
            archel_file,
        )
    except AdaptorError as e:
        print('Failed to create ResQml database:')
        print(e)
        sys.exit(1)
    save_path = pathlib.Path(resqml_output_directory) / pathlib.Path(delft3d_file_name).with_suffix('.epc').name
    rio.build_from_adaptor(daf, save_path, True)
