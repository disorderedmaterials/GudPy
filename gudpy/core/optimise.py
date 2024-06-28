import skopt
import os
import tempfile
import copy
from scipy.optimize import minimize
import shutil

import gudpy_cli as cli
from core import data
from core import gudpy
from core import utils
from core.gudrun_file import GudrunFile
from core.sample import Sample
from core.io import gudpy_io
import core.exception as exc


class InelasticityOptimisation:
    def __init__(
        self,
        gudrunIterator: "gudpy.GudrunIterator",
        samples: list[Sample],
        purge=None,
    ):
        self.samples = []
        self.purge = purge
        self.gudrunIterator = gudrunIterator
        self.mse = {}
        self.results = {}
        self.exitcode = 0
        self.error = ""

        self.mseRec = {}

        for sample in self.gudrunFile.samples():
            sample.runThisSample = False
            if sample.name in [s.name for s in samples]:
                sample.runThisSample = True
                self.samples.append(sample)

            self.mse[sample.name] = {}
            self.mse[sample.name]["initial"] = copy.deepcopy(sample)
            self.results[sample.name] = {}

    @property
    def gudrunFile(self):
        return self.gudrunIterator.gudrunFile

    def optimise(self):
        projectDir = gudpy_io.GudPyIO.projectDir
        gudpy_io.GudPyIO.projectDir = os.path.join(projectDir, "Optimise")

        for gudrun in self.gudrunIterator.gudrunObjects:
            exitcode, error = self.gudrunIterator.singleIteration(
                self.gudrunFile, gudrun, self.purge)
            self.exitcode = exitcode
            if exitcode:  # An exit code != 0 indicates failure
                self.error = error
                return (exitcode, error)
            if self.gudrunIterator.iterator.iterationType == "QIteration":
                for sample in self.samples:
                    i = self.gudrunIterator.iterator.iterationCount
                    self.mse[sample.name][i] = copy.deepcopy(sample)

        for sample in self.samples:
            self.results[sample.name]["bestSample"] = (
                self.mse[sample.name]["initial"]
            )
            self.results[sample.name]["bestIt"] = "None"
            for iteration, sample in self.mse[sample.name].items():
                if (sample.mse()
                        < self.results[sample.name]["bestSample"].mse()):
                    self.results[sample.name]["bestSample"] = sample
                    self.results[sample.name]["bestIt"] = iteration

        gudpy_io.GudPyIO.projectDir = projectDir

        return (0, self.mseRec)

    def exportResults(self, path):
        utils.makeDir(path)
        for sample in self.samples:
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
            purge: "gudpy.Purge" = None,
            limit: float = 0.5,
            nIters: int = 15,
            verbose=False
    ) -> None:
        self.limit = limit
        self.nCalls = nIters
        self.nIters = nIters * len(samples)
        self.purge = purge
        self.gudrunFile = copy.deepcopy(gudrunFile)
        self.samples = []
        self.sample = None
        self.nCurrent = 1
        self.mse = None
        self.result = None

        self.exitcode = 0
        self.error = ""

        for sample in samples:
            for copySample in self.gudrunFile.runSamples():
                if sample.name == copySample.name:
                    self.samples.append(copySample)
        self.sample = self.samples[0]

        self.gudrun = gudpy.Gudrun()
        self.gudrunObjects = []
        self.gudrunQueue = []
        for _ in range(nIters * len(self.samples)):
            self.gudrunQueue.append(gudpy.Gudrun())

        self.simulation = data.NpDataSet(
            self.sample.referenceDataFile, self.limit)
        self.actual = data.NpDataSet(
            self.sample.dataFiles[0].mintFile, self.limit)
        self.verbose = verbose

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

        gudrun = self.gudrunQueue.pop()

        self.gudrunObjects.append(gudrun)
        exitcode = gudrun.gudrun(
            gudrunFile=self.gudrunFile,
            purge=self.purge
        )

        if exitcode:
            raise exc.GudrunException(gudrun.error)

        mintFile = self.sample.dataFiles[0].mintFile

        self.actual = data.NpDataSet(mintFile, self.limit)

        error = data.meanSquaredError(self.actual, self.simulation)

        self.nCurrent += 1
        self.mse = round(error, 5)

        if self.verbose:
            cli.echoIndent(f"MSE: {error}\n")
        return error

    def optimiseSample(self):
        self.mse = None
        for sample in self.gudrunFile.runSamples():
            if sample.name != self.sample.name:
                sample.runThisSample = False
            else:
                sample.runThisSample = True

        initError = self.sample.mse(limit=self.limit)
        initExp = self.sample.exponentialValues
        paramSpace = [
            skopt.space.Real(0, 3, name='amplitdute1'),
            skopt.space.Real(0, 5, name='decay1'),
            skopt.space.Real(0, 3, name='amplitdute2'),
            skopt.space.Real(0, 5, name='decay2'),
        ]

        projectFolder = gudpy_io.GudPyIO.projectDir
        outputPath = os.path.join(projectFolder, "Optimise", "Exponents")
        utils.makeDir(outputPath)
        gudpy_io.GudPyIO.projectDir = outputPath
        result = skopt.gp_minimize(
            self.tweakExponent, paramSpace, n_calls=self.nCalls
        )
        self.result = result
        mse = round(result.fun, 5)
        self.mse = mse
        optExponents = [result.x[0:2] + [0.0],
                        result.x[2:] + [0.0]]

        gudpy_io.GudPyIO.projectDir = projectFolder

        if initError < mse:
            optExponents = initExp
            self.mse = initError

        return optExponents

    def optimise(self):
        projectFolder = gudpy_io.GudPyIO.projectDir
        try:
            for sample in self.samples:
                self.sample = sample
                self.simulation = data.NpDataSet(
                    sample.referenceDataFile, self.limit)
                self.actual = data.NpDataSet(
                    sample.dataFiles[0].mintFile, self.limit)
                optExponents = self.optimiseSample()
                self.sample.exponentialValues = optExponents
                self.nCurrent = 1
            self.nCurrent = "Final Run"
            for sample in self.gudrunFile.samples():
                sample.runThisSample = True
            outputPath = os.path.join(projectFolder, "Optimise", "Exponents")
            gudpy_io.GudPyIO.projectDir = outputPath
            self.gudrun.gudrun(gudrunFile=self.gudrunFile, purge=self.purge)
            gudpy_io.GudPyIO.projectDir = projectFolder
        except exc.GudrunException as e:
            gudpy_io.GudPyIO.projectDir = projectFolder
            self.error = e.args
            return (1, e)
        return (0, "")

    def gradientDescent(self, maxiter=15):
        cli.echoIndent("Gradient Descent")
        initial = [el for sl in self.sample.exponentialValues
                   for el in sl[:-1]]
        initial.extend([0.0] * (4 - len(initial)))
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
