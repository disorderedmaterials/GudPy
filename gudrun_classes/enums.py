from enum import Enum


class Scales(Enum):
    Q = 1
    D_SPACE = 2
    WAVELENGTH = 3
    ENERGY = 4
    TOF = 5


class unitsOfDensity(Enum):
    ATOMIC = 0
    CHEMICAL = 1
