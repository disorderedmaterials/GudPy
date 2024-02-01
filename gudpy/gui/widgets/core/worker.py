import os
from copy import deepcopy
from PySide6.QtCore import QObject, Signal, QThread

from core import gudpy
from core.gud_file import GudFile
from core.sample import Sample
from core import iterators

SUFFIX = ".exe" if os.name == "nt" else ""


class Worker(QObject):
    started = Signal(int)
    errorOccured = Signal(str)
    outputChanged = Signal(str)
    finished = Signal(int)

    def __init___(self):
        super().__init__()

    def _outputChanged(self, output):
        self.outputChanged.emit(output)

    def _errorOccured(self, stderr):
        self.errorOccured.emit(stderr)


class PurgeWorker(Worker, gudpy.Purge):
    def __init__(self, gudrunFile):
        super().__init__(gudrunFile=gudrunFile)

    def purge(self):
        self.started.emit(1)
        super(PurgeWorker, self).purge()
        self.finished.emit(1)


class GudrunWorker(Worker, gudpy.Gudrun):
    def __init__(self, gudrunFile, iterator):
        super().__init__(gudrunFile=gudrunFile, iterator=iterator)

    def gudrun(self):
        self.started.emit(1)
        super(GudrunWorker, self).gudrun()
        self.finished.emit(1)


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
