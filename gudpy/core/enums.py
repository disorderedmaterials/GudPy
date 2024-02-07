from enum import Enum
from itertools import chain, product


def enumFromDict(clsname, _dict):
    return Enum(
        value=clsname,
        names=chain.from_iterable(
            product(v, [k]) for k, v in _dict.items()  # Cartesian product
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


MERGE_WEIGHTS = {
    0: ["None", "NONE"],
    1: ["By Detector", "DETECTOR"],
    2: ["By Channel", "CHANNEL"]
}

MergeWeights = enumFromDict("MergeWeights", MERGE_WEIGHTS)

NORMALISATION_TYPES = {
    0: ["Nothing", "NOTHING"],
    1: ["<b>^2", "AVERAGE_SQUARED"],
    2: ["<b^2>", "AVERAGE_OF_SQUARES"]
}

NormalisationType = enumFromDict("NormalisationType", NORMALISATION_TYPES)

OUTPUT_UNITS = {
    0: ["barns/atom/sr", "BARNS_ATOM_SR"],
    1: ["cm^-1/sr", "INV_CM_SR"]
}

OutputUnits = enumFromDict("OutputUnits", OUTPUT_UNITS)


class Geometry(Enum):
    FLATPLATE = 0
    CYLINDRICAL = 1
    SameAsBeam = 2


class CrossSectionSource(Enum):
    TABLES = 0
    TRANSMISSION = 1
    FILE = 2


FT_MODES = {
    0: ["No Fourier Transform", "NO_FT"],
    1: ["Subtract Average (Qmin)", "SUB_AVERAGE"],
    2: ["Absolute Width (DeltaQ)", "ABSOLUTE"]
}

FTModes = enumFromDict("FTModes", FT_MODES)


class Format(Enum):
    TXT = 0
    YAML = 1


EXTRAPOLATION_MODES = {
    0: ["BACKWARDS"],
    1: ["FORWARDS"],
    2: ["BI_DIRECTIONAL"],
    3: ["FORWARDS_SUMMED"],
    4: ["NONE"]
}

ExtrapolationModes = enumFromDict("ExtrapolationModes", EXTRAPOLATION_MODES)

ITERATION_MODES = {
    0: ["None", "NONE"],
    1: ["Tweak Factor", "TWEAK_FACTOR"],
    2: ["Thickness", "THICKNESS"],
    3: ["Inner Radius", "INNER_RADIUS"],
    4: ["Outer Radius", "OUTER_RADIUS"],
    5: ["Density", "DENSITY"],
    6: ["Inelasticity Subtraction", "INELASTICITY"]
}

IterationModes = enumFromDict("IterationModes", ITERATION_MODES)
