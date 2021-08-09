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


class NormalisationType(Enum):
    NOTHING = 0
    AVERAGE_SQUARED = 1
    AVERAGE_OF_SQUARES = 2


class OutputUnits(Enum):
    BARNS_ATOM_SR = 0
    CM_INV_SR = 1
