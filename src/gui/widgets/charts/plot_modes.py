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
    4: ["Structure Factor (mint01, mdcs01), (Cans)", "SF_CANS"],
    5: ["Radial Distribution Functions (Cans)", "RDF_CANS"],
    6: ["Structure Factor (mint01), (Cans)", "SF_MINT01_CANS"],
    7: ["Structure Factor (mdcs01), (Cans)", "SF_MDCS01_CANS"],
}

PlotModes = enumFromDict(
    "PlotModes", PLOT_MODES
)