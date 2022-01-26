from itertools import chain, product
from enum import Enum


def enumFromDict(clsname, _dict):
    return Enum(
        value=clsname,
        # Cartesian product of all keys and values.
        names=chain.from_iterable(
            product(v, [k]) for k, v in _dict.items()
        )
    )


PLOT_MODES = {
    0: ["Structure Factor (mint01)", "SF_MINT01"],
    1: ["Structure Factor (mdcs01)", "SF_MDCS01"],
    2: ["Radial Distribution Functions", "RDF"],
    3: ["Radial Distribution Functions (Cans)", "RDF_CANS"],
    4: ["Structure Factor (mint01), (Cans)", "SF_MINT01_CANS"],
    5: ["Structure Factor (mdcs01), (Cans)", "SF_MDCS01_CANS"],
}


PlotModes = enumFromDict(
    "PlotModes", PLOT_MODES
)


class SeriesTypes(Enum):
    MINT01 = 0
    MDCS01 = 1
    MGOR01 = 2
    MDOR01 = 3
    DCSLEVEL = 4


class Axes(Enum):
    X = 0
    Y = 1
    A = 3
