from enum import Enum


class Scales(Enum):
    Q = 1
    D_SPACING = 2
    WAVELENGTH = 3
    ENERGY = 4
    TOF = 5


class UnitsOfDensity(Enum):
    ATOMIC = 0
    CHEMICAL = 1


class MergeWeights(Enum):
    NONE = 0
    DETECTOR = 1
    CHANNEL = 2
