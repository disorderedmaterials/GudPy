import skopt
import os
import tempfile
from scipy.optimize import minimize

import gudpy_cli as cli
from core import data
from core import iterators
from core import gudpy
from core import utils
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
            limit: float = 0.5,
            verbose=False
    ) -> None:
        self.LIMIT = limit
        self.gudrunFile = gudrunFile
        self.sample = targetSample
        self.simulation = data.NpDataSet(simulation, self.LIMIT)
        self.actual = data.NpDataSet(actual, self.LIMIT)
        self.verbose = verbose

        self.gudrunIterator = None
        self.gudrun = gudpy.Gudrun()

    def tweakExponent(self, exponents):
        if self.verbose:
            cli.echoIndent("Running parameters: " + str(exponents))

        Amplitude1, Decay1 = exponents[:2]
        Amplitude2, Decay2 = exponents[2:4]

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

        if self.verbose:
            cli.echoIndent(f"MSE: {error}\n")
        return error

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

        error = data.meanSquaredError(self.actual, self.simulation)
        print(f"init error {error}")

        mintFile = self.gudrun.gudrunOutput.output(
            name=self.sample.name,
            dataFile=self.sample.dataFiles[0],
            type=".mint01"
        )

        self.actual = data.NpDataSet(mintFile, self.LIMIT)

        self.actual = data.DataSet(mintFile, True, self.LIMIT)
        error = data.meanSquaredError(self.actual, self.simulation)

    def optimise(self, ncalls=15):
        paramSpace = [
            skopt.space.Real(0, 3, name='amplitdute1'),
            skopt.space.Real(0, 5, name='decay1'),
            skopt.space.Real(0, 3, name='amplitdute2'),
            skopt.space.Real(0, 5, name='decay2'),
        ]

        with tempfile.TemporaryDirectory() as tmp:
            dir = os.path.join(tmp, "Optimisation")
            utils.makeDir(os.path.join(dir))
            self.gudrunFile.projectDir = dir
            result = skopt.gp_minimize(
                self.tweakExponent, paramSpace, n_calls=ncalls
            )
            mse = round(result.fun, 5)
            optExponents = [result.x[0:2] + [0.0],
                            result.x[2:] + [0.0]]

        return mse, optExponents

    def gradientDescent(self, maxiter=15):
        cli.echoIndent("Gradient Descent")
        initial = [el for sl in self.sample.exponentialValues
                   for el in sl[:-1]]
        initial.extend([0.0] * (4 - len(initial)))
        print(initial)
        bounds = [(0, 3), (0, 3), (0, 3), (0, 3)]
        with tempfile.TemporaryDirectory() as tmp:
            dir = os.path.join(tmp, "Optimisation")
            utils.makeDir(os.path.join(dir))
            self.gudrunFile.projectDir = dir
            result = minimize(
                fun=self.tweakExponent,
                x0=initial,
                bounds=bounds,
                method='Nelder-Mead',
                options={"maxiter": maxiter}
            )
        mse = round(result.fun, 5)
        result.x = result.x.tolist()
        optExponents = [result.x[0:2] + [0.0], result.x[2:] + [0.0]]
        return mse, optExponents
