import os
import math
from copy import deepcopy
import typing as typ
from PySide6.QtCore import QObject, Signal, QThread

from core import gudpy
from core.gud_file import GudFile
from core.gudrun_file import GudrunFile
from core.purge_file import PurgeFile
from core.iterators import Iterator
from core.sample import Sample
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

        self.purge = PurgeWorker()
        self.gudrun = GudrunWorker()

    def processProgress(self, stdout):
        progress = self.progressIncrementDCS(self.gudrunFile, stdout)
        if isinstance(self.iterator, iterators.InelasticitySubtraction):
            progress /= 2
        progress += self.mainWidget.progressBar.value()
        self.mainWidget.progressBar.setValue(
            progress if progress <= 100 else 100
        )


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
        progress = stepSize * sum([
            self.stdout.count("Got to: INSTRUMENT"),
            self.stdout.count("Got to: BEAM"),
            self.stdout.count("Got to: NORMALISATION"),
            self.stdout.count("Got to: SAMPLE BACKGROUND"),
            self.stdout.count("Finished merging data for sample"),
            self.stdout.count("Got to: CONTAINER"),
        ])
        if isinstance(self.iterator, iterators.InelasticitySubtraction):
            progress /= 2
        return progress

    def run(self):
        exitcode = super(GudrunWorker, self).gudrun(self.gudrunFile)
        self.finished.emit(exitcode)


class CompositionWorker(QObject):
    finished = Signal(Sample, Sample)
    started = Signal(Sample)
    nextIteration = Signal(int)
    errorOccured = Signal(str)

    def __init__(self, args, kwargs, sample, gudrunFile):
        self.args = args
        self.kwargs = kwargs
        self.sample = sample
        self.updatedSample = None
        self.errored = False
        self.gudrunFile = gudrunFile
        super(CompositionWorker, self).__init__()

    def work(self):
        self.started.emit(self.sample)
        # perform golden-section search.
        iterators.gss(
            self.costup,
            *self.args,
            **self.kwargs,
            startIterFunc=self.nextIteration.emit
        )
        if not self.errored:
            # If an error occurs emit appropiate signal.
            self.finished.emit(self.sample, self.updatedSample)

    def costup(
        self, x, gudrunFile, sampleBackground,
        components, totalMolecules=None
    ):

        if QThread.currentThread().isInterruptionRequested():
            return None
        gf = deepcopy(gudrunFile)
        gf.sampleBackgrounds = [sampleBackground]

        # Prevent negative x.
        x = abs(x)

        if len(components) == 1:
            # Determine instances where target components are used.
            weightedComponents = [
                wc for wc in sampleBackground.samples[0]
                .composition.weightedComponents
                for c in components
                if c.eq(wc.component)
            ]
            for component in weightedComponents:
                component.ratio = x

        elif len(components) == 2:
            wcA = wcB = None
            # Determine instances where target components are used.
            for weightedComponent in (
                sampleBackground.samples[0].composition.weightedComponents
            ):
                if weightedComponent.component.eq(components[0]):
                    wcA = weightedComponent
                elif weightedComponent.component.eq(components[1]):
                    wcB = weightedComponent

            if wcA and wcB:
                # Ensure combined ratio == totalMolecules.
                wcA.ratio = x
                wcB.ratio = abs(totalMolecules - x)

        # Update composition
        sampleBackground.samples[0].composition.translate()
        self.updatedSample = sampleBackground.samples[0]

        # Set up process and execute.
        outpath = os.path.join(
            gf.instrument.GudrunInputFileDir,
            "gudpy.txt"
        )
        self.proc, func, args = gf.dcs(path=outpath, headless=False)
        func(*args)
        self.proc.setWorkingDirectory(gf.instrument.GudrunInputFileDir)
        self.proc.start()
        # Block until process is finished.
        self.proc.waitForFinished(-1)
        # Read from stdout.
        if not self.proc:
            return None
        data = self.proc.readAllStandardOutput()
        result = bytes(data).decode("utf8")

        # Check for errors.
        ERROR_KWDS = [
            "does not exist",
            "error",
            "Error"
        ]
        if [KWD for KWD in ERROR_KWDS if KWD in result]:
            self.errorOccured.emit(result)
            self.errored = True
            return None

        gudPath = sampleBackground.samples[0].dataFiles[0].replace(
            gudrunFile.instrument.dataFileType,
            "gud"
        )

        gudFile = GudFile(
            os.path.join(
                gudrunFile.instrument.GudrunInputFileDir, gudPath
            )
        )

        # Determine cost.
        if gudFile.averageLevelMergedDCS == gudFile.expectedDCS:
            return 0
        else:
            return (gudFile.expectedDCS-gudFile.averageLevelMergedDCS)**2
