import os
import math
from PySide6.QtCore import QObject, Signal, QThread

from core import gudpy
from core.gudrun_file import GudrunFile
from core.purge_file import PurgeFile
from core.iterators import Iterator
from core import iterators, enums, config, utils

SUFFIX = ".exe" if os.name == "nt" else ""


class GudPyGUI(QObject, gudpy.GudPy):
    def __init__(
        self,
        projectDir: str = "",
        loadFile: str = "",
        format: enums.Format = enums.Format.YAML,
        config: bool = False,
    ):

        super().__init__(
            projectDir=projectDir, loadFile=loadFile,
            format=format, config=config,
        )

        self.output = ""
        self.outputIterations = {}


class Worker(QThread):
    outputChanged = Signal(str)
    progress = Signal(int)
    finished = Signal(int)

    def __init___(self):
        super().__init__()

    def _outputChanged(self, output):
        self.output += output
        self.outputChanged.emit(output)
        self.progress.emit(self._progress())


class PurgeWorker(Worker, gudpy.Purge):
    def __init__(self, purgeFile: PurgeFile, gudrunFile: GudrunFile):
        super().__init__()
        self.purgeFile = purgeFile
        self.detectors = None
        self.dataFiles = [self.gudrunFile.instrument.groupFileName]

        self.appendDfs(self.gudrunFile.normalisation.dataFiles[0])
        self.appendDfs(self.gudrunFile.normalisation.dataFilesBg[0])
        self.appendDfs([df for sb in self.gudrunFile.sampleBackgrounds
                        for df in sb.dataFiles])
        if not self.gudrunFile.purgeFile.excludeSampleAndCan:
            self.appendDfs([df for sb in self.gudrunFile.sampleBackgrounds
                            for s in sb.samples for df in s.dataFiles
                            if s.runThisSample])
            self.appendDfs([df for sb in self.gudrunFile.sampleBackgrounds
                            for s in sb.samples for c in s.containers
                            for df in c.dataFiles if s.runThisSample])

    def _progress(self):
        stepSize = math.ceil(100 / len(self.dataFiles))
        progress = 0
        for df in self.dataFiles:
            if df in self.stdout:
                progress += stepSize
        return progress

    def appendDfs(self, dfs):
        if isinstance(dfs, str):
            dfs = [dfs]
        for df in dfs:
            self.dataFiles.append(
                df.replace(self.gudrunFile.instrument.dataFileType, "grp")
            )

    def run(self):
        exitcode = super(PurgeWorker, self).purge(self.purgeFile)
        self.finished.emit(exitcode)
        if exitcode != 0:
            return

        # Find the number of detectors
        for line in self.stdout.split("\n"):
            if "spectra in" in line and self.dataFiles[-1] in line:
                self.detectors = utils.nthint(line, 0)


class GudrunWorker(Worker, gudpy.Gudrun):
    def __init__(self, gudrunFile: GudrunFile, iterator: Iterator):
        super().__init__(iterator=iterator)
        self.gudrunFile = gudrunFile
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
            self.stdout.count("Got to: INSTRUMENT"),
            self.stdout.count("Got to: BEAM"),
            self.stdout.count("Got to: NORMALISATION"),
            self.stdout.count("Got to: SAMPLE BACKGROUND"),
            self.stdout.count("Finished merging data for sample"),
            self.stdout.count("Got to: CONTAINER"),
        ])
        if isinstance(self.iterator, iterators.InelasticitySubtraction):
            self.progress /= 2
        return self.progress

    def run(self):
        exitcode = super(GudrunWorker, self).gudrun(self.gudrunFile)
        self.finished.emit(exitcode)


class GudrunIteratorWorker(QThread, gudpy.GudrunIterator):
    nextIteration = Signal(int)
    outputChanged = Signal(str)
    progress = Signal(int)
    finished = Signal(int)

    def __init__(
        self,
        iterator: iterators.Iterator,
        gudrunFile: GudrunFile
    ):
        super().__init__(iterator=iterator, gudrunFile=gudrunFile)
        self.gudrunObjects = []
        self.output = ""

        for _ in range(iterator.nTotal):
            worker = GudrunWorker(self.gudrunFile, self.iterator)
            self.worker.outputChanged.connect(self._outputChanged)
            self.worker.progress.connect(self._progress)
            self.gudrunObjects.append(worker)

    def _outputChanged(self, output):
        self.output += output
        self.outputChanged.emit(output)

    def _progress(self, progress):
        self.progress.emit(progress)

    def _nextIteration(self):
        self.output = ""
        self.nextIteration.emit(self.iterator.nCurrent)

    def run(self):
        exitcode = super(GudrunIteratorWorker, self).iterate()
        self.finished.emit(exitcode)


class CompositionWorker(QThread, gudpy.CompositionIterator):
    def __init__(
        self,
        iterator: iterators.Composition,
        gudrunFile: GudrunFile
    ):
        super().__init__(iterator=iterator, gudrunFile=gudrunFile)
        self.gudrunObjects = []
        self.output = ""

        for _ in range(iterator.nTotal):
            worker = GudrunWorker(self.gudrunFile, self.iterator)
            self.worker.outputChanged.connect(self._outputChanged)
            self.worker.progress.connect(self._progress)
            self.gudrunObjects.append(worker)

    def _outputChanged(self, output):
        self.output += output
        self.outputChanged.emit(output)

    def _progress(self, progress):
        self.progress.emit(progress)

    def _nextIteration(self):
        self.output = ""
        self.nextIteration.emit(self.iterator.nCurrent)

    def run(self):
        exitcode = super(CompositionWorker, self).iterate()
        self.finished.emit(exitcode)
