from copy import deepcopy
import math
import os
import time
from core.gud_file import GudFile


def gss(
    f, bounds, n, maxN, rtol, args=(),
    startIterFunc=None, endIterFunc=None
):
    """
    Golden-section search. Used to find extremum of a given cost function
    `f` (with arguments `args`), with interval `bounds`. Converges when `n >=  maxN` or
    current result within `rtol`.

    Parameters
    ----------
    f : function
        Function to evaluate against.
    bounds : float[]
        Lower bound, start point, upper bound.
    n : int
        Current iteration.
    maxN : int
        Maximum number of iterations.
    rtol : float
        Relative tolerance for convergence.
    args : tuple(any), optional
        Arguments to pass to evaluation function.
    startIterFunc : function, optional
        Function to call at the start of an iteration.
    endIterFunc : function, optional
        Function to call at the end of an iteration.
    
    Returns
    -------
        None | float : Final result
    """
    # If available, call startIterFunc.
    if startIterFunc:
        startIterFunc(n)
    
    # If we have reached maximum number of iterations, return the current centre.
    if n >= maxN:
        return bounds[1]

    # Check to see if we are within the convergence tolerance.
    if (
        (abs(bounds[2] - bounds[0]) / min([abs(bounds[0]), abs(bounds[2])]))
        < (rtol/100)**2
    ):
        # If available, call endIterFunc.
        if endIterFunc:
            endIterFunc(n)
        # Return average of centre and upper bound.
        return (bounds[2] + bounds[1]) / 2

    # Calculate a potential centre = c + 2 - GR * (upper-c)
    d = bounds[1] + (2 - (1 + math.sqrt(5))/2)*(bounds[2]-bounds[1])

    # Call evaluation function, using arguments and potential centre.
    fd1 = f(d, *args)

    # If no result, return None.
    if fd1 is None:
        # If available, call endIterFunc.
        if endIterFunc:
            endIterFunc(n)
        return None

    # Call evaluation function, using arguments and current centre.
    fd2 = f(bounds[1], *args)
    if fd2 is None:
        # If available, call endIterFunc.
        if endIterFunc:
            endIterFunc(n)
        return None

    # If the new centre evaluates to less than the current
    if fd1 < fd2:
        # Swap them, making the previous centre the new lower bound.
        bounds = [bounds[1], d, bounds[2]]

        # If available, call endIterFunc.
        if endIterFunc:
            endIterFunc(n)
        
        # Recurse using new bounds.
        return gss(
            f, bounds, n+1, maxN, rtol,
            args=args, startIterFunc=startIterFunc, endIterFunc=endIterFunc
        )
    # Otherwise, swap and reverse.
    else:
        bounds = [d, bounds[1], bounds[0]]

        # If available, call endIterFunc.
        if endIterFunc:
            endIterFunc()

        # Recurse using new bounds.
        return gss(
            f, bounds, n+1, maxN, rtol,
            args=args, startIterFunc=startIterFunc, endIterFunc=endIterFunc
        )


def calculateTotalMolecules(components, sample):
    """
    Calculates the total number of molecules in `sample` that belong
    to `components`.

    Parameters
    ----------
    components : Components
        Components object to check sample component membership against.
    sample : Sample
        Target sample object.

    Returns
    -------
        float : Total sum of molecules
    """
    # Sum molecules in sample composition, belongiong to components.
    total = 0
    for wc in sample.composition.weightedComponents:
        for c in components:
            # If c == wc.component, add to the sum.
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
        """
        Constructs all the necessary attributes for the CompositionIterator object.

        Parameters
        ----------
        gudrunFile : GudrunFile
            Parent GudrunFile object.
        """
        self.gudrunFile = gudrunFile
        self.components = []
        self.ratio = 0


    def setComponent(self, component, ratio=1):
        """
        Sets component and ratio.

        Parameters
        ----------
        component : Component
            Component to set.
        ratio : int, optional
            Ratio of component.
        """
        self.components = [component]
        self.ratio = ratio


    def setComponents(self, components, ratio=1):
        """
        Sets components and ratio.

        Parameters
        ----------
        components : Component[]
            Components to set.
        ratio : int, optional
            Ratio of component.
        """
        self.components = [c for c in components if c]
        self.ratio = ratio

    def processSingleComponent(self, x, sampleBackground):
        """
        Cost function for processing a single component.

        Parameters
        ----------
        x : float
            Chosen ratio.
        sampleBackground : SampleBackground
            Target Sample Background.
        
        Returns
        -------
        float : Determined cost
        """
        self.gudrunFile.sampleBackgrounds = [sampleBackground]

        # Ensure x is not negative.
        x = abs(x)
        
        # Filter components to find targets.
        weightedComponents = [
            wc for wc in (
                sampleBackground.samples[0].composition.weightedComponents
            )
            for c in self.components
            if c.eq(wc.component)
        ]
        
        # Apply ratio to components.
        for component in weightedComponents:
            component.ratio = x

        # Translate into atomic composition.
        sampleBackground.samples[0].composition.translate()

        # Process.
        self.gudrunFile.process()

        # Sleep to prevent race conditions.
        time.sleep(1)

        # Read the .gud file into a GudFile object.
        gudPath = sampleBackground.samples[0].dataFiles[0].replace(
                    self.gudrunFile.instrument.dataFileType,
                    "gud"
                )
        gudFile = GudFile(
            os.path.join(
                self.gudrunFile.instrument.GudrunInputFileDir, gudPath
            )
        )

        # Determine cost.
        if gudFile.averageLevelMergedDCS == gudFile.expectedDCS:
            return 0
        else:
            return (gudFile.expectedDCS-gudFile.averageLevelMergedDCS)**2


    def processTwoComponents(self, x, sampleBackground, totalMolecules):
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
        
        Returns
        -------
        float : Determined cost
        """
        self.gudrunFile.sampleBackgrounds = [sampleBackground]

        # Ensure x is not negative.
        x = abs(x)

        # Filter components to find targets.
        wcA = wcB = None
        for weightedComponent in (
            sampleBackground.samples[0].composition.weightedComponents
        ):
            if weightedComponent.component.eq(self.components[0]):
                wcA = weightedComponent
            elif weightedComponent.component.eq(self.components[1]):
                wcB = weightedComponent

        # Apply ratio to components, maintaining totalMolecules.
        if wcA and wcB:
            wcA.ratio = x
            wcB.ratio = abs(totalMolecules - x)

        # Translate into atomic composition.
        sampleBackground.samples[0].composition.translate()

        # Process.
        self.gudrunFile.process()

        # Sleep to prevent race conditions.
        time.sleep(1)

        # Read the .gud file into a GudFile object. 
        gudPath = sampleBackground.samples[0].dataFiles[0].replace(
                    self.gudrunFile.instrument.dataFileType,
                    "gud"
                )
        gudFile = GudFile(
            os.path.join(
                self.gudrunFile.instrument.GudrunInputFileDir, gudPath
            )
        )

        # Determine cost.
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

    def iterate(self, n=10, rtol=10.):
        """
        This method is the core of the CompositionIterator.
        It performs n iterations of tweaking by the ratio of component(s).

        Parameters
        ----------
        n : int
            Number of iterations to perform.
        rtol : float
            Relative tolerance
        """
        # Check components and ratio has been set.
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
                        # Interval is [1e-2, ratio, 10]
                        self.gss(
                            self.processSingleComponent,
                            [1e-2, self.ratio, 10], 0,
                            args=(sb,)
                        )
                    elif len(self.components) == 2:
                        # Calculate total molecules.
                        totalMolecules = self.calculateTotalMolecules(sample)

                        # Perform golden-section search.
                        # Interval is [1e-2, ratio, 10]
                        self.gss(
                            self.processTwoComponents,
                            [1e-2, self.ratio, 10], 0,
                            args=(sb, totalMolecules,)
                        )

    def gss(self, f, bounds, n, args=()):
        """
        Wrapper for calling gss using class attributes.

        Parameters
        ----------
        f : function
            Function to evaluate against.
        bounds : float[]
            Lower bound, start point, upper bound.
        n : int
            Current iteration.
        args : tuple(any), optional
            Arguments to pass to evaluation function.

        Returns
        -------
        None | float : Final result
        """
        return gss(f, bounds, n, self.maxIterations, self.rtol, args=args)
