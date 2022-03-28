from src.gudrun_classes.composition import Components
from src.gudrun_classes.enums import Geometry
from src.gudrun_classes.gui_config import GUIConfig
import os
import sys

spc2 = "  "
spc5 = "          "

geometry = Geometry.FLATPLATE
NUM_GUDPY_CORE_OBJECTS = 4
USE_USER_DEFINED_COMPONENTS = False
NORMALISE_COMPOSITIONS = False
components = Components()

__rootdir__ = os.path.dirname(os.path.abspath(sys.argv[0]))

__root__ = (
    os.path.join(sys._MEIPASS, "bin", "configs", "containers")
    if hasattr(sys, "_MEIPASS")
    else os.path.join(__rootdir__, "bin", "configs", "containers")
)

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