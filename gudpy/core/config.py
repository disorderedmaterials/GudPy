import os
import sys

from core.enums import Geometry
from core.gui_config import GUIConfig

spc2 = "  "
spc10 = "          "

geometry = Geometry.FLATPLATE
NUM_GUDPY_CORE_OBJECTS = 4
USE_USER_DEFINED_COMPONENTS = False
NORMALISE_COMPOSITIONS = False

__rootdir__ = os.path.dirname(os.path.abspath(sys.argv[0]))

__root__ = (
    os.path.join(sys._MEIPASS, "bin", "configs", "containers")
    if hasattr(sys, "_MEIPASS")
    else os.path.join(__rootdir__, "bin", "configs", "containers")
)

configDir = (
    os.path.join(sys._MEIPASS, "bin", "configs", "instruments")
    if hasattr(sys, "_MEIPASS")
    else os.path.join(
        __rootdir__, "bin", "configs", "instruments"
    )
)

NIMROD2012 = os.path.join(configDir, "NIMROD_84modules_2012.config")
SANDALS2011 = os.path.join(configDir, "SANDALS_2011.config")

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
