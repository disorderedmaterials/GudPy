import skopt
import os
import tempfile
import copy
from scipy.optimize import minimize
import shutil

import gudpy_cli as cli
from core import data
from core import iterators
from core import gudpy
from core import utils
from core.gudrun_file import GudrunFile
from core.sample import Sample


class InelasticityOptimisation:
    def __init__(
        self,
        gudrunFile: GudrunFile,
    ):
        self.originalGudrunFile = copy.deepcopy(gudrunFile)
        self.gudrunIterators = gudpy.GudrunIterator(
            gudrunFile, iterators.InelasticitySubtraction(3))
        self.samples = {}
        self.results = {}

        for sample in gudrunFile.runSamples():
            if not sample.mse:
                continue

            self.mse[sample.name]["initial"] = copy.deepcopy(sample)

    def optimise(self, purge: gudpy.Purge):
        for i, gudrun in enumerate(self.gudrunIterators.gudrunObjects):
            exitcode = self.gudrunIterators.singleIteration(
                self.gudrunIterators.gudrunFile, gudrun, purge)
            if exitcode:  # An exit code != 0 indicates failure
                self.exitcode = (exitcode, gudrun.error)
                return self.exitcode
            if self.gudrunIterators.iterator.iterationType == "QIteration":
                for sample in self.gudrunIterators.gudrunFile.runSamples():
                    self.mse[sample.name][i] = copy.deepcopy(sample)

        for sample in self.originalGudrunFile.runSamples():
            self.results[sample.name]["bestSample"] = (
                self.mse[sample.name]["initial"]
            )
            self.results[sample.name]["bestIt"] = "initial"
            for iteration, sample in self.mse[sample.name]:
                if sample.mse < self.results[sample.name]["bestSample"]:
                    self.results[sample.name]["bestSample"] = sample
                    self.results[sample.name]["bestIt"] = iteration

        return self.results

    def exportResults(self, path):
        utils.makeDir(path)
        for sample in self.originalGudrunFile.runSamples():
            bestMint = (
                self.results[sample.name]["bestSample"].dataFiles[0].mintFile
            )
            shutil.copyfile(bestMint, os.path.join(
                path, f"{sample.name}.mint01"
            ))


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
