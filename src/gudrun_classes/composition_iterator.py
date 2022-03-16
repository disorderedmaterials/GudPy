from copy import deepcopy
import math
from src.gudrun_classes.gud_file import GudFile
import os
import time


def gss(f, bounds, n, maxN, rtol, args=(), startIterFunc=None):
    if startIterFunc:
        startIterFunc(n)
    if n >= maxN:
        return bounds[1]

    if (
        (abs(bounds[2] - bounds[0]) / min([abs(bounds[0]), abs(bounds[2])]))
        < (rtol/100)**2
    ):
        return (bounds[2] + bounds[1]) / 2

    # Calculate a potential centre = c + 2 - GR * (upper-c)
    d = bounds[1] + (2 - (1 + math.sqrt(5))/2)*(bounds[2]-bounds[1])

    # If the new centre evaluates to less than the current
    fd1 = f(d, *args)
    if fd1 is None:
        return None
    fd2 = f(bounds[1], *args)
    if fd2 is None:
        return None
    if fd1 < fd2:
        # Swap them, making the previous centre the new lower bound.
        bounds = [bounds[1], d, bounds[2]]
        return gss(
            f, bounds, n+1, maxN, rtol,
            args=args, startIterFunc=startIterFunc
        )
    # Otherwise, swap and reverse.
    else:
        bounds = [d, bounds[1], bounds[0]]
        return gss(
            f, bounds, n+1, maxN, rtol,
            args=args, startIterFunc=startIterFunc
        )


def calculateTotalMolecules(components, sample):
    total = 0
    for wc in sample.composition.weightedComponents:
        for c in components:
            if wc.component.eq(c):
                total += wc.ratio
                break
    return total


class CompositionIterator():
    def __init__(self, gudrunFile):
        self.gudrunFile = deepcopy(gudrunFile)
        self.components = []
        self.ratio = 0

    def setComponent(self, component, ratio=1):
        self.components = [component]
        self.ratio = ratio

    def setComponents(self, components, ratio=1):
        self.components = [c for c in components if c]
        self.ratio = ratio

    def processSingleComponent(self, x, sampleBackground):
        gudrunFile = deepcopy(self.gudrunFile)
        gudrunFile.sampleBackgrounds = [sampleBackground]

        x = abs(x)
        weightedComponents = [
            wc for wc in (
                sampleBackground.samples[0].composition.weightedComponents
            )
            for c in self.components
            if c.eq(wc.component)
        ]
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

        if gudFile.averageLevelMergedDCS == gudFile.expectedDCS:
            return 0
        else:
            return (gudFile.expectedDCS-gudFile.averageLevelMergedDCS)**2

    def processTwoComponents(self, x, sampleBackground, totalMolecules):
        gudrunFile = deepcopy(self.gudrunFile)
        gudrunFile.sampleBackgrounds = [sampleBackground]
        x = abs(x)
        wcA = wcB = None
        for weightedComponent in (
            sampleBackground.samples[0].composition.weightedComponents
        ):
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

        if gudFile.averageLevelMergedDCS == gudFile.expectedDCS:
            return 0
        else:
            return abs(
                gudFile.expectedDCS - gudFile.averageLevelMergedDCS
            ) / min(
                [
                    abs(gudFile.averageLevelMergedDCS),
                    abs(gudFile.expectedDCS)
                ]
            )

    def iterate(self, n=10, rtol=10):
        if not self.components or not self.ratio:
            return None
        for sampleBackground in self.gudrunFile.sampleBackgrounds:
            for sample in sampleBackground.samples:
                if sample.runThisSample:
                    sb = deepcopy(sampleBackground)
                    sb.samples = [sample]
                    if len(self.components) == 1:
                        self.maxIterations = n
                        self.rtol = rtol
                        self.gss(
                            self.processSingleComponent,
                            [1e-2, self.ratio, 10], 0,
                            args=(sb,)
                        )
                    elif len(self.components) == 2:
                        totalMolecules = self.calculateTotalMolecules(sample)
                        self.gss(
                            self.processTwoComponents,
                            [1e-2, self.ratio, 10], 0,
                            args=(sb, totalMolecules,)
                        )

    def gss(self, f, bounds, n, args=()):
        return gss(f, bounds, n, self.maxIterations, self.rtol, args=args)
