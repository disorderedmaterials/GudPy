import os
import sys

from core.enums import Geometry
from core.gui_config import GUIConfig

# Spacing definitions, for writing input file to gudrun_dcs.
spc2 = "  "
spc5 = "          "

# Global geometry.
geometry = Geometry.FLATPLATE

# Constant - number of 'GudPy' core objects.
# Currently, this consists of: Instrument, Components, Beam, Normalisation.
NUM_GUDPY_CORE_OBJECTS = 4

# Should components be used in sample compositions?
USE_USER_DEFINED_COMPONENTS = False

# Should compositions be normalised to 1?
NORMALISE_COMPOSITIONS = False

# Root directory that script is running from.
__rootdir__ = os.path.dirname(os.path.abspath(sys.argv[0]))

# Root for container configurations.
__root__ = (
    os.path.join(sys._MEIPASS, "bin", "configs", "containers")
    if hasattr(sys, "_MEIPASS")
    else os.path.join(__rootdir__, "bin", "configs", "containers")
)

# Container configurations.
containerConfigurations = {
    os.path.basename(path)
    .replace(".config", "")
    .replace("_", " "):
    path for path in [
        os.path.join(path, name)
        for path, _, files in os.walk(__root__)
        for name in files
    ]
}

GUI = GUIConfig()
