from src.gudrun_classes.composition import Components
from src.gudrun_classes.enums import Geometry
from src.gudrun_classes.isotopes import Sears91
from src.gudrun_classes.mass_data import massData as md

geometry = Geometry.FLATPLATE
NUM_GUDPY_CORE_OBJECTS = 4
USE_USER_DEFINED_COMPONENTS = False
NORMALISE_COMPOSITIONS = False
components = Components()

massData = md
sears91 = Sears91()