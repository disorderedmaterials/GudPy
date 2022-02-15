from copy import deepcopy
from random import sample
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
    
    def setComponents(self, components, ratios = [1,1]):
        self.components = components
        self.ratio = ratios

    def processSingleComponent(self, x, sampleBackground):
        gudrunFile = deepcopy(self.gudrunFile)
        gudrunFile.sampleBackgrounds = [sampleBackground]

        x = abs(x)
        weightedComponents = [wc for wc in sampleBackground.samples[0].composition.weightedComponents for c in self.components if c.eq(wc.component)]
        for component in weightedComponents:
            component.ratio = x

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

    def processTwoComponents(self, x, sampleBackground, totalMolecules):
        gudrunFile = deepcopy(self.gudrunFile)
        gudrunFile.sampleBackgrounds = [sampleBackground]
        x = abs(x)
        wcA = wcB = None
        for weightedComponent in sampleBackground.samples[0].composition.weightedComponents:
            if weightedComponent.component.eq(self.components[0]):
                wcA = weightedComponent
            elif weightedComponent.component.eq(self.components[1]):
                wcB = weightedComponent

        if wcA and wcB:
            wcA.ratio = x
            wcB.ratio = abs(totalMolecules - x)


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

    def calculateTotalMolecules(self, sample):
        total = 0
        for wc in sample.composition.weightedComponents:
            for c in self.components:
                if wc.component.eq(c):
                    total+=wc.ratio
                    break
        return total

    def iterate(self, n=5, rtol=10):
        if not self.components or not self.ratio: return None
        print(self.components)
        for sampleBackground in self.gudrunFile.sampleBackgrounds:
            for sample in sampleBackground.samples:
                if sample.runThisSample:
                    sb = deepcopy(sampleBackground)
                    sb.samples = [sample]
                    if len(self.components) == 1:
                        result = minimize_scalar(self.processSingleComponent, args=(sb,), method='Golden', options={"maxiter":n, "xtol": rtol})
                        print(f"final ratio for component {self.components[0].name} in {sample.name}: {result['x']}")
                    elif len(self.components) == 2:
                        totalMolecules = self.calculateTotalMolecules(sample)
                        print(f"tot: {totalMolecules}")
                        result = minimize_scalar(self.processTwoComponents, args=(sb, totalMolecules), method='Golden', options={"maxiter":n, "xtol": rtol})
                        print(f"final ratio: {result['x']}")
                        print(f"Success: {result['success']}")