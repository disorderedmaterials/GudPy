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
    3: ["Structure Factor (mint01), Radial Distribution Functions", "SF_MINT01_RDF"],
    4: ["Structure Factor (mdcs01), Radial Distribution Functions", "SF_MDCS01_RDF"],
    5: ["Structure Factor (mint01), (Cans)", "SF_MINT01_CANS"],
    6: ["Structure Factor (mdcs01), (Cans)", "SF_MDCS01_CANS"],
    7: ["Radial Distribution Functions (Cans)", "RDF_CANS"],
    8: ["Structure Factor (mint01), Radial Distribution Functions (Cans)", "SF_MINT01_RDF_CANS"],
    9: ["Structure Factor (mdcs01), Radial Distribution Functions (Cans)", "SF_MDCS01_RDF_CANS"]
}


PlotModes = enumFromDict(
    "PlotModes", PLOT_MODES
)

SPLIT_PLOTS = {
    PlotModes.SF_MINT01_RDF: (PlotModes.SF_MINT01, PlotModes.RDF),
    PlotModes.SF_MDCS01_RDF: (PlotModes.SF_MDCS01, PlotModes.RDF),
    PlotModes.SF_MINT01_RDF_CANS: (PlotModes.SF_MINT01_CANS, PlotModes.RDF_CANS),
    PlotModes.SF_MDCS01_RDF_CANS: (PlotModes.SF_MDCS01_CANS, PlotModes.RDF_CANS)
}


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
