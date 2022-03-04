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

    def __init__(self, args, kwargs, sample):
        self.args = args
        self.kwargs = kwargs
        self.sample = sample
        self.updatedSample = None
        super(CompositionWorker, self).__init__()

    def work(self):
        self.started.emit(self.sample)
        print(self.sample.composition)
        gss(self.costup, *self.args, **self.kwargs)
        self.finished.emit(self.sample, self.updatedSample)
        print(self.updatedSample.composition)

    def costup(self, x, gudrunFile, sampleBackground, components, totalMolecules=None):

        gf = deepcopy(gudrunFile)
        gf.sampleBackgrounds = [sampleBackground]

        x = abs(x)
        print(x)

        if len(components) == 1:

            weightedComponents = [wc for wc in sampleBackground.samples[0].composition.weightedComponents for c in components if c.eq(wc.component)]
            for component in weightedComponents:
                component.ratio = x
        
        elif len(components) == 2:
            wcA = wcB = None
            for weightedComponent in sampleBackground.samples[0].composition.weightedComponents:
                if weightedComponent.component.eq(components[0]):
                    wcA = weightedComponent
                elif weightedComponent.component.eq(components[1]):
                    wcB = weightedComponent

            if wcA and wcB:
                wcA.ratio = x
                wcB.ratio = abs(totalMolecules - x)

        sampleBackground.samples[0].composition.translate()
        self.updatedSample = sampleBackground.samples[0]
        gf.process()

        gudPath = sampleBackground.samples[0].dataFiles.dataFiles[0].replace(
            gudrunFile.instrument.dataFileType,
            "gud"
        )

        gudFile = GudFile(
            os.path.join(
                gudrunFile.instrument.GudrunInputFileDir, gudPath
            )
        )

        print(gudFile.averageLevelMergedDCS, gudFile.expectedDCS, (gudFile.expectedDCS-gudFile.averageLevelMergedDCS)**2)
        if gudFile.averageLevelMergedDCS == gudFile.expectedDCS:
            return 0
        else:
            return (gudFile.expectedDCS-gudFile.averageLevelMergedDCS)**2


