import os
from nrresqml.api import convert_delft3d_to_resqml


__version__ = open(os.path.join(os.path.dirname(__file__), 'VERSION.txt')).read()
