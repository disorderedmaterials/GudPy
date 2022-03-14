from PySide6.QtCore import QObject, Signal
import os
from src.gudrun_classes.gud_file import GudFile
from src.gudrun_classes.sample import Sample
from src.gudrun_classes.composition_iterator import gss
from copy import deepcopy


class CompositionWorker(QObject):
    finished = Signal(Sample, Sample)
    started = Signal(Sample)
    nextIteration = Signal(int)
    errorOccured = Signal(str)

    def __init__(self, args, kwargs, sample):
        self.args = args
        self.kwargs = kwargs
        self.sample = sample
        self.updatedSample = None
        self.errored = False
        self.currentIteration = 0
        super(CompositionWorker, self).__init__()

    def work(self):
        self.started.emit(self.sample)
        gss(
            self.costup,
            *self.args,
            **self.kwargs,
            startIterFunc=self.nextIteration.emit
        )
        if not self.errored:
            self.finished.emit(self.sample, self.updatedSample)

    def costup(
        self, x, gudrunFile, sampleBackground,
        components, totalMolecules=None
    ):

        gf = deepcopy(gudrunFile)
        gf.sampleBackgrounds = [sampleBackground]

        x = abs(x)

        if len(components) == 1:

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
            for weightedComponent in (
                sampleBackground.samples[0].composition.weightedComponents
            ):
                if weightedComponent.component.eq(components[0]):
                    wcA = weightedComponent
                elif weightedComponent.component.eq(components[1]):
                    wcB = weightedComponent

            if wcA and wcB:
                wcA.ratio = x
                wcB.ratio = abs(totalMolecules - x)

        sampleBackground.samples[0].composition.translate()
        self.updatedSample = sampleBackground.samples[0]
        outpath = os.path.join(
            gf.instrument.GudrunInputFileDir,
            "gudpy.txt"
        )
        self.proc, func, args = gf.dcs(path=outpath, headless=False)
        func(*args)
        self.proc.setWorkingDirectory(gf.instrument.GudrunInputFileDir)
        self.proc.start()
        self.proc.waitForFinished(-1)
        result = bytes(self.proc.readAllStandardOutput()).decode("utf8")
        print(result)

        ERROR_KWDS = [
            "does not exist",
            "error",
            "Error"
        ]
        if [KWD for KWD in ERROR_KWDS if KWD in result]:
            self.errorOccured.emit(result)
            self.errored = True
            return None

        gudPath = sampleBackground.samples[0].dataFiles.dataFiles[0].replace(
            gudrunFile.instrument.dataFileType,
            "gud"
        )

        gudFile = GudFile(
            os.path.join(
                gudrunFile.instrument.GudrunInputFileDir, gudPath
            )
        )

        if gudFile.averageLevelMergedDCS == gudFile.expectedDCS:
            return 0
        else:
            return (gudFile.expectedDCS-gudFile.averageLevelMergedDCS)**2
