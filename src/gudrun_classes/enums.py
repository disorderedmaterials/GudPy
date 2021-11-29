from enum import Enum
from itertools import chain, product

def enumFromDict(clsname, _dict):
    return Enum(
        value=clsname,
        names=chain.from_iterable(
            product(v, [k]) for k, v in _dict.items() # Cartesian product of all keys and values.
        )
    )

class Instruments(Enum):
    SANDALS = 0
    GEM = 1
    NIMROD = 2
    D4C = 3
    POLARIS = 4
    HIPD = 5
    NPDF = 6


class Scales(Enum):
    Q = 1
    D_SPACING = 2
    WAVELENGTH = 3
    ENERGY = 4
    TOF = 5


UNITS_OF_DENSITY = {
    0: ["atoms/\u212b^3", "ATOMIC"],
    1: ["gm/cm^3", "CHEMICAL"]   
}


UnitsOfDensity = enumFromDict("UnitsOfDensity", UNITS_OF_DENSITY)

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
    INV_CM_SR = 1


class Geometry(Enum):
    FLATPLATE = 0
    CYLINDRICAL = 1
    SameAsBeam = 2


class CrossSectionSource(Enum):
    TABLES = 0
    TRANSMISSION = 1
    FILE = 2

TOP_HAT_WIDTHS = {
    0: ["No Fourier Transform", "NO_FT"],
    1: ["Subtract Average (Qmin)", "SUB_AVERAGE"],
    2: ["Absolute Width (DeltaQ)", "ABSOLUTE"]
}

TopHatWidths = enumFromDict("TopHatWidths", TOP_HAT_WIDTHS)