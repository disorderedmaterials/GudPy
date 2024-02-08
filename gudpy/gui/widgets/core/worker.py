import os
import math
from PySide6.QtCore import QObject, Signal, QThread
import copy

from core import gudpy
import core.exception as exc
from core.gudrun_file import GudrunFile
from core.purge_file import PurgeFile
from core.iterators import Iterator
from core import iterators, enums, config, utils

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
        self.progressChanged.emit(self._progress(), self.name)


class PurgeWorker(Worker, gudpy.Purge):
    def __init__(self, purgeFile: PurgeFile, gudrunFile: GudrunFile):
        super().__init__()
        self.name = "Purge"
        self.purgeFile = purgeFile
        self.detectors = None
        self.dataFileType = gudrunFile.instrument.dataFileType
        self.dataFiles = [gudrunFile.instrument.groupFileName]

        self.appendDfs(gudrunFile.normalisation.dataFiles[0])
        self.appendDfs(gudrunFile.normalisation.dataFilesBg[0])
        self.appendDfs([df for sb in gudrunFile.sampleBackgrounds
                        for df in sb.dataFiles])
        if not gudrunFile.purgeFile.excludeSampleAndCan:
            self.appendDfs([df for sb in gudrunFile.sampleBackgrounds
                            for s in sb.samples for df in s.dataFiles
                            if s.runThisSample])
            self.appendDfs([df for sb in gudrunFile.sampleBackgrounds
                            for s in sb.samples for c in s.containers
                            for df in c.dataFiles if s.runThisSample])

    def _progress(self):
        stepSize = math.ceil(100 / len(self.dataFiles))
        progress = 0
        for df in self.dataFiles:
            if df in self.output:
                progress += stepSize
        return progress

    def appendDfs(self, dfs):
        if isinstance(dfs, str):
            dfs = [dfs]
        for df in dfs:
            self.dataFiles.append(
                df.replace(self.dataFileType, "grp")
            )

    def run(self):
        exitcode = super(PurgeWorker, self).purge(self.purgeFile)
        self.finished.emit(exitcode)
        if exitcode != 0:
            return


class GudrunWorker(Worker, gudpy.Gudrun):
    def __init__(self, gudrunFile: GudrunFile, iterator: Iterator = None):
        super().__init__()
        self.name = "Gudrun"
        self.gudrunFile = gudrunFile
        self.iterator = iterator
        self.progress = 0

        # Number of GudPy objects
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

    def _progress(self):
        stepSize = math.ceil(100 / self.markers)
        self.progress += stepSize * sum([
            self.output.count("Got to: INSTRUMENT"),
            self.output.count("Got to: BEAM"),
            self.output.count("Got to: NORMALISATION"),
            self.output.count("Got to: SAMPLE BACKGROUND"),
            self.output.count("Finished merging data for sample"),
            self.output.count("Got to: CONTAINER"),
        ])
        if isinstance(self.iterator, iterators.InelasticitySubtraction):
            self.progress /= 2
        return self.progress

    def run(self):
        exitcode = super(GudrunWorker, self).gudrun(
            self.gudrunFile, self.iterator)
        self.finished.emit(exitcode)


class IteratorBaseWorker():
    nextIteration = Signal(int)
    outputChanged = Signal(str)
    progress = Signal(int, str)
    finished = Signal(int)

    def __init__(self, iterator):
        self.name = iterator.name
        self.gudrunObjects = []
        self.output = ""
        self.error = ""

    def _outputChanged(self, output):
        self.output += output
        self.outputChanged.emit(output)

    def _progress(self, progress):
        self.progress.emit(progress, self.name)

    def _nextIteration(self, nCurrent):
        self.output = ""
        self.nextIteration.emit(nCurrent)

    def run(self):
        exitcode, error = super().iterate()
        self.error = error
        self.finished.emit(exitcode)


class GudrunIteratorWorker(QThread, IteratorBaseWorker, gudpy.GudrunIterator):
    def __init__(
        self,
        iterator: iterators.Iterator,
        gudrunFile: GudrunFile
    ):
        super().__init__(iterator=iterator, gudrunFile=gudrunFile)

        for _ in range(iterator.nTotal):
            worker = GudrunWorker(self.gudrunFile, self.iterator)
            self.worker.outputChanged.connect(self._outputChanged)
            self.worker.progress.connect(self._progress)
            self.gudrunObjects.append(worker)


class CompositionWorker(QThread, IteratorBaseWorker, gudpy.CompositionIterator):
    def __init__(
        self,
        iterator: iterators.Composition,
        gudrunFile: GudrunFile
    ):
        super().__init__(iterator=iterator, gudrunFile=gudrunFile)

        for _ in range(iterator.nTotal):
            worker = GudrunWorker(self.gudrunFile, self.iterator)
            self.worker.outputChanged.connect(self._outputChanged)
            self.worker.progress.connect(self._progress)
            self.gudrunObjects.append(worker)


class BatchWorker(QThread, IteratorBaseWorker, gudpy.BatchProcessing):
    def __init__(
        self,
        gudrunFile: GudrunFile,
        iterator: iterators.Iterator = None,
        batchSize=1,
        stepSize=1,
        offset: int = 0,
        rtol=0.0,
        separateFirstBatch=False
    ):
        super().__init__(
            gudrunFile=gudrunFile,
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
                worker = GudrunWorker(
                    self.firstBatch,
                    gudrunIterator.iterator
                )
                self.worker.outputChanged.connect(self._outputChanged)
                self.worker.progress.connect(self._progress)
                gudrunIterator.append(worker)

    def run(self):
        try:
            self.process()
            self.finished.emit(0)
        except exc.GudrunException as e:
            self.error = str(e)
            self.finished.emit(1)
