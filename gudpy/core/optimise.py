import skopt

import gudpy_cli as cli
from core import data
from core import iterators
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
            expected: str,
            actual: str
    ) -> None:
        self.gudrunFile = gudrunFile
        self.sample = targetSample
        self.expected = data.DataSet(expected, True)
        self.actual = data.DataSet(actual, True)
        self.gudrunIterator = None

    def tweakParameters(self, nIterations):
        cli.echoIndent(f"Iteration count: {nIterations}")

        iterator = iterators.InelasticitySubtraction(nIterations[0])
        self.gudrunIterator = gudpy.GudrunIterator(
            self.gudrunFile,
            iterator,
        )
        self.gudrunIterator.iterate(purge=None, save=False)

        error = data.meanSquaredError(self.actual, self.expected)
        print(f"init error {error}")

        mintFile = self.gudrunIterator.gudrunOutput.output(
            name=self.sample.name,
            dataFile=self.sample.dataFiles[0],
            type=".mint01"
        )

        cli.echoIndent(mintFile)

        self.actual = data.DataSet(mintFile, True)
        error = data.meanSquaredError(self.actual, self.expected)

        cli.echoIndent(f"MSE: {error}")
        return error

    def optimise(self):
        cli.echoProcess("Bayesian Optimisation")

        paramRanges = [skopt.space.Integer(1, 3, name='nIterations')]
        result = skopt.gp_minimize(
            self.tweakParameters, paramRanges
        )

        print(result)
