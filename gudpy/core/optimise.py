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
from core.io import gudpy_io


class InelasticityOptimisation:
    def __init__(
        self,
        gudrunFile: GudrunFile,
        purge=None,
    ):
        self.originalGudrunFile = copy.deepcopy(gudrunFile)
        self.purge = purge
        self.gudrunIterators = gudpy.GudrunIterator(
            gudrunFile, iterators.InelasticitySubtraction(3))
        self.samples = {}
        self.results = {}

        for sample in gudrunFile.runSamples():
            if not sample.mse:
                continue

            self.mse[sample.name]["initial"] = copy.deepcopy(sample)

    def optimise(self):
        for i, gudrun in enumerate(self.gudrunIterators.gudrunObjects):
            exitcode = self.gudrunIterators.singleIteration(
                self.gudrunIterators.gudrunFile, gudrun, self.purge)
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
            samples: list[Sample],
            gudrun: "gudpy.Gudrun",
            limit: float = 0.5,
            nIters: int = 15,
            verbose=False
    ) -> None:
        self.limit = limit
        self.nIters = nIters
        self.gudrunFile = gudrunFile
        self.samples = samples
        self.sample = samples[0]
        self.nCurrent = 0
        self.mse = None

        self.simulation = data.NpDataSet(
            self.sample.referenceDataFile, self.limit)
        self.actual = data.NpDataSet(
            self.sample.dataFiles[0].mintFile, self.limit)
        self.verbose = verbose

        self.gudrun = gudrun

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
        )

        mintFile = self.sample.dataFiles[0].mintFile

        self.actual = data.NpDataSet(mintFile, self.limit)

        error = data.meanSquaredError(self.actual, self.simulation)

        self.nCurrent += 1
        self.mse = error

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

        projectFolder = gudpy_io.GudPyIO.projectDir
        with tempfile.TemporaryDirectory() as tmp:
            dir = os.path.join(tmp, "Optimisation")
            utils.makeDir(os.path.join(dir))
            gudpy_io.GudPyIO.projectDir = dir
            result = skopt.gp_minimize(
                self.tweakExponent, paramSpace, n_calls=self.nIters
            )
            mse = round(result.fun, 5)
            optExponents = [result.x[0:2] + [0.0],
                            result.x[2:] + [0.0]]

        gudpy_io.GudPyIO.projectDir = projectFolder
        return mse, optExponents

    def optimise(self):
        for sample in self.samples:
            self.sample = sample
            self.simulation = data.NpDataSet(
                sample.referenceDataFile, self.limit)
            self.actual = data.NpDataSet(
                sample.dataFiles[0].mintFile, self.limit)

            self.optimiseSample()

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
