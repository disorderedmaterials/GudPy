from src.gudrun_classes.composition import Components
from src.gudrun_classes.enums import Geometry
import os
import sys

geometry = Geometry.FLATPLATE
NUM_GUDPY_CORE_OBJECTS = 4
USE_USER_DEFINED_COMPONENTS = False
NORMALISE_COMPOSITIONS = False
components = Components()

containerConfigurations = {
    path
    .replace(".config", "")
    .replace("_", " ") : 
    path for path in os.listdir(
        os.path.join(sys._MEIPASS, "bin", "configs", "containers")
        if hasattr(sys, "_MEIPASS")
        else os.path.join("bin", "configs", "containers")
    )
}
