import skopt

import gudpy_cli as cli
from core import data
from core import gudpy
from core.gudrun_file import GudrunFile
from core.sample import Sample


class ParameterOptimisation:
    def __init__(self):
        pass


class BayesianOptimisation:
    def __init__(
            self,
            gudrunFile: GudrunFile,
            targetSample: Sample,
            simulation: str,
            actual: str,
            limit: float = 0.5
    ) -> None:
        self.LIMIT = limit
        self.gudrunFile = gudrunFile
        self.sample = targetSample
        self.simulation = data.NpDataSet(simulation, self.LIMIT)
        self.actual = data.NpDataSet(actual, self.LIMIT)

        self.gudrunIterator = None
        self.gudrun = gudpy.Gudrun()

    def tweakExponent(self, exponents):
        cli.echoIndent("Running parameters: " + str(exponents))

        Amplitude1, Decay1 = exponents[:2]
        Amplitude2, Decay2 = exponents[:2]

        self.sample.exponentialValues = []
        self.sample.exponentialValues.append(
            [Amplitude1, Decay1, 0.0]
        )
        self.sample.exponentialValues.append(
            [Amplitude2, Decay2, 0.0]
        )

        self.gudrun.gudrun(
            gudrunFile=self.gudrunFile,
            purge=None,
            suppress=True
        )

        mintFile = self.gudrun.gudrunOutput.output(
            name=self.sample.name,
            dataFile=self.sample.dataFiles[0],
            type=".mint01"
        )

        self.actual = data.NpDataSet(mintFile, self.LIMIT)

        error = data.meanSquaredError(self.actual, self.simulation)

        cli.echoIndent(f"MSE: {error}\n")
        return error

    def optimise(self, ncalls=15):
        paramSpace = [
            skopt.space.Real(0, 2, name='amplitdute1'),
            skopt.space.Real(1, 3, name='decay1'),
            skopt.space.Real(0, 0.5, name='amplitude2'),
            skopt.space.Real(0, 1, name='decay2'),
        ]

        result = skopt.gp_minimize(
            self.tweakExponent, paramSpace, n_calls=ncalls
        )

        return result
