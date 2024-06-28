import os
import math
from PySide6.QtCore import Signal, QThread

from core import gudpy
import core.exception as exc
from core.gudrun_file import GudrunFile
from core.purge_file import PurgeFile
from core.iterators import Iterator, InelasticitySubtraction
from core import iterators, config
from core import optimise
from core.sample import Sample

SUFFIX = ".exe" if os.name == "nt" else ""


class Worker(QThread):
    outputChanged = Signal(str)
    progressChanged = Signal(int, str)
    finished = Signal(int)

    def __init__(self):
        super().__init__()
        self.name = ""
        self.output = ""

    def _outputChanged(self, output):
        self.output += output
        self.outputChanged.emit(output)
        self.progressChanged.emit(self._progressChanged(), self.name)


class PurgeWorker(Worker, gudpy.Purge):
    def __init__(self, purgeFile: PurgeFile, gudrunFile: GudrunFile):
        super().__init__()
        self.name = "Purge"
        self.purgeFile = purgeFile
        self.detectors = None
        self.dataFileType = gudrunFile.instrument.dataFileType
        self.dataFiles = [gudrunFile.instrument.groupFileName]

        self.appendDataFiles(
            [df.filename for df in gudrunFile.normalisation.dataFiles])
        self.appendDataFiles(
            [df.filename for df in gudrunFile.normalisation.dataFilesBg])
        self.appendDataFiles([df.filename for sb
                              in gudrunFile.sampleBackgrounds
                              for df in sb.dataFiles])
        if not purgeFile.excludeSampleAndCan:
            self.appendDataFiles([df.filename for sb
                                  in gudrunFile.sampleBackgrounds
                                  for s in sb.samples for df in s.dataFiles
                                  if s.runThisSample])
            self.appendDataFiles([df.filename for sb
                                  in gudrunFile.sampleBackgrounds
                                  for s in sb.samples for c in s.containers
                                  for df in c.dataFiles if s.runThisSample])

    def _progressChanged(self):
        stepSize = math.ceil(100 / len(self.dataFiles))
        progress = 0
        for df in self.dataFiles:
            if df in self.output:
                progress += stepSize
        return progress

    def appendDataFiles(self, dfs):
        if isinstance(dfs, str):
            dfs = [dfs]
        for df in dfs:
            self.dataFiles.append(
                df.replace(self.dataFileType, "grp")
            )

    def run(self):
        exitcode = self.purge(self.purgeFile)
        self.finished.emit(exitcode)
        if exitcode != 0:
            return


class GudrunWorker(Worker, gudpy.Gudrun):
    def __init__(
            self,
            gudrunFile: GudrunFile,
            purge: PurgeWorker = None,
            iterator: Iterator = None
    ):
        super().__init__()
        self.name = "Gudrun"
        self.gudrunFile = gudrunFile
        self.iterator = iterator
        self.purge = purge
        self.purge = None
        self.progress = 0

        # Number of GudPy objects
        self.markers = None

    def _progressChanged(self):
        if not self.markers:
            self.markers = (
                config.NUM_GUDPY_CORE_OBJECTS - 1
                + len(self.gudrunFile.sampleBackgrounds) + sum([sum([
                    len([
                        sample
                        for sample in sampleBackground.samples
                        if sample.runThisSample
                    ]),
                    *[
                        len(sample.containers)
                        for sample in sampleBackground.samples
                        if sample.runThisSample
                    ]])
                    for sampleBackground in self.gudrunFile.sampleBackgrounds
                ]))

        stepSize = math.ceil(100 / self.markers)
        self.progress = stepSize * sum([
            self.output.count("Got to: INSTRUMENT"),
            self.output.count("Got to: BEAM"),
            self.output.count("Got to: NORMALISATION"),
            self.output.count("Got to: SAMPLE BACKGROUND"),
            self.output.count("Finished merging data for sample"),
            self.output.count("Got to: CONTAINER"),
        ])
        return self.progress

    def run(self):
        exitcode = self.gudrun(
            gudrunFile=self.gudrunFile,
            purge=self.purge, iterator=self.iterator)
        self.finished.emit(exitcode)


class IteratorBaseWorker(QThread):
    outputChanged = Signal(str)
    progressChanged = Signal(int, str)
    finished = Signal(int)

    def __init__(
        self,
        iterator: iterators.Iterator,
        gudrunFile: GudrunFile,
        purge: PurgeWorker = None,
    ):
        super().__init__(iterator=iterator, gudrunFile=gudrunFile)
        self.gudrunObjects = []
        self.purge = purge
        self.output = {}
        self.error = ""

        for _ in range(iterator.nTotal
                       + (1 if iterator.requireDefault else 0)):
            worker = GudrunWorker(self.gudrunFile, iterator)
            worker.outputChanged.connect(self._outputChanged)
            worker.progressChanged.connect(self._progressChanged)
            self.gudrunObjects.append(worker)

    def _outputChanged(self, output):
        idx = (f"{self.iterator.name} {self.iterator.nCurrent}"
               if self.iterator.nCurrent != 0
               or not self.iterator.requireDefault else "Default run")

        if isinstance(self.iterator, InelasticitySubtraction):
            idx = (
                f"{self.iterator.iterationType} {self.iterator.iterationCount}"
            )

        currentOutput = self.output.get(idx, "")
        self.output[idx] = currentOutput + output
        self.outputChanged.emit(output)

    def _progressChanged(self, progress):
        self.progressChanged.emit(
            progress,
            f"Iterate by {self.iterator.name} - "
            f"{self.iterator.nCurrent}/{self.iterator.nTotal}"
            if self.iterator.nCurrent != 0
            or not self.iterator.requireDefault else "Gudrun - Default run"
        )

    def run(self):
        exitcode, error = self.iterate(purge=self.purge)
        self.error = error
        self.finished.emit(exitcode)


class GudrunIteratorWorker(IteratorBaseWorker, gudpy.GudrunIterator):
    def __init__(
        self,
        iterator: iterators.Iterator,
        gudrunFile: GudrunFile,
        purge: PurgeWorker = None,
    ):
        super().__init__(iterator=iterator, gudrunFile=gudrunFile, purge=purge)


class CompositionWorker(IteratorBaseWorker, gudpy.CompositionIterator):
    def __init__(
        self,
        iterator: iterators.Composition,
        gudrunFile: GudrunFile,
        purge: PurgeWorker = None,
    ):
        super().__init__(iterator=iterator, gudrunFile=gudrunFile, purge=purge)

    def run(self):
        exitcode, error = self.iterate(purge=self.purge)
        self.error = error
        self.finished.emit(exitcode)


class BatchWorker(IteratorBaseWorker, gudpy.BatchProcessing):
    def __init__(
        self,
        gudrunFile: GudrunFile,
        purge: PurgeWorker = None,
        iterator: iterators.Iterator = None,
        batchSize=1,
        stepSize=1,
        offset: int = 0,
        rtol=0.0,
        separateFirstBatch=False
    ):
        super().__init__(
            gudrunFile=gudrunFile,
            purge=purge,
            iterator=iterator,
            batchSize=batchSize,
            stepSize=stepSize,
            offset=offset,
            rtol=rtol,
            separateFirstBatch=separateFirstBatch
        )
        self.name = "Batch Processing " + iterator.name if iterator else ""

        # Iterate through gudrun iterators and connect the signals
        for gudrunIterator in self.gudrunIterators.items():
            if not gudrunIterator:
                continue
            # Create GudrunWorker objects to replace Gudrun objects
            gudrunIterator.gudrunObjects = []
            for _ in range(self.iterator.nTotal):
                worker = GudrunWorker(self.firstBatch, gudrunIterator.iterator)
                worker.outputChanged.connect(self._outputChanged)
                worker.progressChanged.connect(self._progressChanged)
                gudrunIterator.append(worker)

    def run(self):
        try:
            self.process(purge=self.purge)
            self.finished.emit(0)
        except exc.GudrunException as e:
            self.error = str(e)
            self.finished.emit(1)


class OptimiseExponentsWorker(QThread, optimise.BayesianOptimisation):
    outputChanged = Signal(str)
    progressChanged = Signal(int, str)
    finished = Signal(int)

    def __init__(
        self,
        gudrunFile: GudrunFile,
        samples: list[Sample],
        purge: PurgeWorker = None,
        limit: float = 0.5,
        nIters: int = 15,
        verbose=False
    ) -> None:
        super().__init__(
            gudrunFile=gudrunFile,
            samples=samples,
            limit=limit,
            nIters=nIters,
            verbose=verbose
        )
        self.output = {}

        self.gudrunObjects = []
        self.gudrunQueue = []
        for _ in range(nIters * len(samples)):
            gudrunWorker = GudrunWorker(
                gudrunFile=self.gudrunFile, purge=purge)
            self.gudrunObjects.append(gudrunWorker)
            self.gudrunQueue.append(gudrunWorker)
            gudrunWorker.outputChanged.connect(self._outputChanged)
            gudrunWorker.progressChanged.connect(self._progressChanged)

        self.gudrun = GudrunWorker(gudrunFile=self.gudrunFile, purge=purge)
        self.gudrun.outputChanged.connect(self._outputChanged)
        self.gudrun.progressChanged.connect(self._progressChanged)

    def _outputChanged(self, output):
        idx = f"{self.sample.name} {self.nCurrent}"

        currentOutput = self.output.get(idx, "")
        self.output[idx] = currentOutput + output
        self.outputChanged.emit(output)

    def _progressChanged(self, progress):
        rounded = ""

        for set in self.sample.exponentialValues:
            roundedSet = [round(v, 3) for v in set]
            if rounded:
                rounded += ", "
            rounded += str(roundedSet)

        if self.nCurrent == "Final Run":
            text = (
                "Final Run with params " +
                f"- {rounded}"
            )
        else:
            text = (
                f"Optimise {self.sample.name} " +
                f"- {rounded}" +
                (f" MSE: {self.mse} " if self.mse else "") +
                f"- {self.nCurrent}/{int(self.nIters/len(self.samples))}"
            )

        self.progressChanged.emit(
            progress,
            text
        )

    def _progressChangedFinalRun(self, progress):
        rounded = ""

        for set in self.sample.exponentialValues:
            roundedSet = [round(v, 3) for v in set]
            if rounded:
                rounded += ", "
            rounded += str(roundedSet)

        text = (
            "Final run with params " +
            f"- {rounded}" +
            f" MSE: {self.mse}"
        )

        self.progressChanged.emit(
            progress,
            text
        )

    def run(self):
        exitcode, error = self.optimise()
        self.error = error
        self.finished.emit(exitcode)


class OptimiseInelasticityWorker(QThread, optimise.InelasticityOptimisation):
    outputChanged = Signal(str)
    progressChanged = Signal(int, str)
    finished = Signal(int)

    def __init__(
        self,
        gudrunFile: GudrunFile,
        samples: list,
        purge: PurgeWorker = None,
    ) -> None:
        self.gudrunIterator = GudrunIteratorWorker(
            gudrunFile=gudrunFile,
            iterator=iterators.InelasticitySubtraction(3)
        )

        super().__init__(
            gudrunIterator=self.gudrunIterator,
            samples=samples,
            purge=purge
        )

        for gudrunWorker in self.gudrunIterator.gudrunObjects:
            gudrunWorker.outputChanged.connect(self._outputChanged)
            gudrunWorker.progressChanged.connect(self._progressChanged)

    @property
    def output(self):
        return self.gudrunIterator.output

    def _outputChanged(self, output):
        idx = (f"{self.gudrunIterator.iterator.nCurrent}")

        currentOutput = self.output.get(idx, "")
        self.output[idx] = currentOutput + output
        self.outputChanged.emit(output)

    def _progressChanged(self, progress):
        text = ("Optimise Inelasticity - " +
                f"{self.gudrunIterator.iterator.iterationType} " +
                f"{self.gudrunIterator.iterator.iterationCount} / 3")

        self.progressChanged.emit(
            progress,
            text
        )

    def run(self):
        exitcode, res = self.optimise()
        self.error = res
        self.finished.emit(exitcode)
