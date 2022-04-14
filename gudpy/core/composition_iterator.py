from copy import deepcopy
import math
import os
import time

from core.gud_file import GudFile


def gss(f, bounds, n, maxN, rtol, args=(), startIterFunc=None, endIterFunc=None):
    if startIterFunc:
        startIterFunc(n)
    if n >= maxN:
        return bounds[1]

    if (
        (abs(bounds[2] - bounds[0]) / min([abs(bounds[0]), abs(bounds[2])]))
        < (rtol/100)**2
    ):
        if endIterFunc:
            endIterFunc(n)
        return (bounds[2] + bounds[1]) / 2

    # Calculate a potential centre = c + 2 - GR * (upper-c)
    d = bounds[1] + (2 - (1 + math.sqrt(5))/2)*(bounds[2]-bounds[1])

    # If the new centre evaluates to less than the current
    fd1 = f(d, *args)
    if fd1 is None:
        if endIterFunc:
            endIterFunc(n)
        return None
    fd2 = f(bounds[1], *args)
    if fd2 is None:
        if endIterFunc:
            endIterFunc(n)
        return None
    if fd1 < fd2:
        # Swap them, making the previous centre the new lower bound.
        bounds = [bounds[1], d, bounds[2]]
        if endIterFunc:
            endIterFunc(n)
        return gss(
            f, bounds, n+1, maxN, rtol,
            args=args, startIterFunc=startIterFunc, endIterFunc=endIterFunc
        )
    # Otherwise, swap and reverse.
    else:
        bounds = [d, bounds[1], bounds[0]]
        if endIterFunc:
            endIterFunc()
        return gss(
            f, bounds, n+1, maxN, rtol,
            args=args, startIterFunc=startIterFunc, endIterFunc=endIterFunc
        )


def calculateTotalMolecules(components, sample):
    # Sum molecules in sample composition, belongiong to components.
    total = 0
    for wc in sample.composition.weightedComponents:
        for c in components:
            if wc.component.eq(c):
                total += wc.ratio
                break
    return total


class CompositionIterator():
    """
    Class to represent a Composition Iterator.
    This class is used for iteratively tweaking composition
    by defined components.
    This is achieved by running gudrun_dcs iteratively,
    using golden-section search to find the optimal value of
    ratio's of components in composition, or ratio between two components,
    and altering the values as such between iterations.

    ...

    Attributes
    ----------
    gudrunFile : GudrunFile
        Input GudrunFile that we will be using for iterating.
    components : Component[]
        Components to perform iteration on.
    ratio : float
        Starting ratio.
    Methods
    ----------
    setComponent(component, ratio=1)
        Sets component and ratio.
    setComponents(components, ratio)
        Sets components and ratio.
    processSingleComponent(x, sampleBackground)
        Cost function for processing a single component.
    processTwoComponents(x, sampleBackground, totalMolecules)
        Cost function for processing two components.
    iterate(n=10, rtol=10)
        Performs n iterations with a relative tolerance of 10.
    gss(f, bounds, n, args=())
        Performs n iterations using cost function f, args and bounds.
    """
    def __init__(self, gudrunFile):
        self.gudrunFile = gudrunFile
        self.components = []
        self.ratio = 0

    """
    Sets component and ratio.

    Parameters
    ----------
    component : Component
        Component to set.
    ratio : int, optional
        Ratio of component.
    """
    def setComponent(self, component, ratio=1):
        self.components = [component]
        self.ratio = ratio

    """
    Sets components and ratio.

    Parameters
    ----------
    components : Component[]
        Components to set.
    ratio : int, optional
        Ratio of component.
    """
    def setComponents(self, components, ratio=1):
        self.components = [c for c in components if c]
        self.ratio = ratio

    """
    Cost function for processing a single component.

    Parameters
    ----------
    x : float
        Chosen ratio.
    sampleBackground : SampleBackground
        Target Sample Background.
    """
    def processSingleComponent(self, x, sampleBackground):
        self.gudrunFile.sampleBackgrounds = [sampleBackground]

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
        self.gudrunFile.process()

        time.sleep(1)
        gudPath = sampleBackground.samples[0].dataFiles.dataFiles[0].replace(
                    self.gudrunFile.instrument.dataFileType,
                    "gud"
                )
        gudFile = GudFile(
            os.path.join(
                self.gudrunFile.instrument.GudrunInputFileDir, gudPath
            )
        )

        if gudFile.averageLevelMergedDCS == gudFile.expectedDCS:
            return 0
        else:
            return (gudFile.expectedDCS-gudFile.averageLevelMergedDCS)**2

    """
    Cost function for processing two components.

    Parameters
    ----------
    x : float
        Chosen ratio.
    sampleBackground : SampleBackground
        Target Sample Background.
    totalMolecules : float
        Sum of molecules of both components.
    """
    def processTwoComponents(self, x, sampleBackground, totalMolecules):
        self.gudrunFile.sampleBackgrounds = [sampleBackground]
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
        self.gudrunFile.process()

        time.sleep(1)
        gudPath = sampleBackground.samples[0].dataFiles.dataFiles[0].replace(
                    self.gudrunFile.instrument.dataFileType,
                    "gud"
                )
        gudFile = GudFile(
            os.path.join(
                self.gudrunFile.instrument.GudrunInputFileDir, gudPath
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

    """
    This method is the core of the CompositionIterato.
    It performs n iterations of tweaking by the ratio of component(s).

    Parameters
    ----------
    n : int
        Number of iterations to perform.
    rtol : float
        Relative tolerance
    """
    def iterate(self, n=10, rtol=10.):
        if not self.components or not self.ratio:
            return None
        # Only include samples that are marked for analysis.
        for sampleBackground in self.gudrunFile.sampleBackgrounds:
            for sample in sampleBackground.samples:
                if sample.runThisSample:
                    sb = deepcopy(sampleBackground)
                    sb.samples = [sample]
                    if len(self.components) == 1:
                        self.maxIterations = n
                        self.rtol = rtol
                        # Perform golden-section search.
                        self.gss(
                            self.processSingleComponent,
                            [1e-2, self.ratio, 10], 0,
                            args=(sb,)
                        )
                    elif len(self.components) == 2:
                        totalMolecules = self.calculateTotalMolecules(sample)
                        # Perform golden-section search.
                        self.gss(
                            self.processTwoComponents,
                            [1e-2, self.ratio, 10], 0,
                            args=(sb, totalMolecules,)
                        )

    def gss(self, f, bounds, n, args=()):
        return gss(f, bounds, n, self.maxIterations, self.rtol, args=args)
