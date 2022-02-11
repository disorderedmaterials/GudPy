from copy import deepcopy
from src.gudrun_classes.gud_file import GudFile
import os
import time
from scipy.optimize import minimize, minimize_scalar
import sys
import numpy as np



class CompositionIterator():
    def __init__(self, gudrunFile):
        self.gudrunFile = deepcopy(gudrunFile)
        self.components = []
        self.ratio = 0

    def setComponent(self, component, ratio=1):
        self.components = [component]
        self.ratio = ratio
    
    def setComponents(self, components, ratioX=1, ratioY=1):
        self.components = components
        self.ratioX = ratioX
        self.ratioY = ratioY

    def process(self, x, sampleBackground):
        gudrunFile = deepcopy(self.gudrunFile)
        gudrunFile.sampleBackgrounds = [sampleBackground]

        x = abs(x)
        weightedComponents = [wc for wc in sampleBackground.samples[0].composition.weightedComponents for c in self.components if c.eq(wc.component)]
        for component in weightedComponents:
            component.ratio = x
            print(component.ratio)

        sampleBackground.samples[0].composition.translate()
        gudrunFile.process()

        time.sleep(1)
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

    def iterate(self, n=5, rtol=10):
        if not self.components or not self.ratio: return None

        for sampleBackground in self.gudrunFile.sampleBackgrounds:
            for sample in sampleBackground.samples:
                if sample.runThisSample:
                    sb = deepcopy(sampleBackground)
                    sb.samples = [sample]
                    result = minimize_scalar(self.process, args=(sb,), method='Golden', options={"maxiter":n, "xtol": rtol})
                    print(f"final ratio for component {self.components[0].name} in {sample.name}: {result['x']}")
