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
    0: ["Structure Factor (mint01, mdcs01)", "SF"],
    1: ["Structure Factor (mint01)", "SF_MINT01"],
    2: ["Structure Factor (mdcs01)", "SF_MDCS01"],
    3: ["Radial Distribution Functions", "RDF"],
    4: [
        "Structure Factor (mint01, mdcs01), Radial Distribution Functions",
        "SF_RDF"
    ],
    5: [
        "Structure Factor (mint01), Radial Distribution Functions",
        "SF_MINT01_RDF"
    ],
    6: [
        "Structure Factor (mdcs01), Radial Distribution Functions",
        "SF_MDCS01_RDF"
    ],
    7: ["Structure Factor (mint01, mdcs01) (Cans)", "SF_CANS"],
    8: ["Structure Factor (mint01), (Cans)", "SF_MINT01_CANS"],
    9: ["Structure Factor (mdcs01), (Cans)", "SF_MDCS01_CANS"],
    10: ["Radial Distribution Functions (Cans)", "RDF_CANS"],
    11: [
        "Structure Factor (mint01, mdcs01),"
        "Radial Distribution Functions (Cans)",
        "SF_RDF_CANS"
    ],
    12: [
        "Structure Factor (mint01), Radial Distribution Functions (Cans)",
        "SF_MINT01_RDF_CANS"
    ],
    13: [
        "Structure Factor (mdcs01), Radial Distribution Functions (Cans)"
        "SF_MDCS01_RDF_CANS"
    ]
}


PlotModes = enumFromDict(
    "PlotModes", PLOT_MODES
)

SPLIT_PLOTS = {
    PlotModes.SF_MINT01_RDF: (PlotModes.SF_MINT01, PlotModes.RDF),
    PlotModes.SF_MDCS01_RDF: (PlotModes.SF_MDCS01, PlotModes.RDF),
    PlotModes.SF_MINT01_RDF_CANS: (
        PlotModes.SF_MINT01_CANS, PlotModes.RDF_CANS
    ),
    PlotModes.SF_MDCS01_RDF_CANS: (
        PlotModes.SF_MDCS01_CANS, PlotModes.RDF_CANS
    ),
    PlotModes.SF_RDF: (PlotModes.SF, PlotModes.RDF),
    PlotModes.SF_RDF_CANS: (PlotModes.SF_CANS, PlotModes.RDF_CANS)
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
