import time
import os
from copy import deepcopy
import math

from core.gud_file import GudFile
from core.enums import Scales


class Iterator():
    """
    Class to represent an Iterator.
    This class is used for iteratively tweaking a parameter by a coefficient.
    This means running gudrun_dcs iteratively, and adjusting parameter
    of each sample across iterations. The new coefficient
    applied is the coefficient calculated from the results of
    gudrun_dcs in the previous iteration.

    ...

    Attributes
    ----------
    gudrunFile : GudrunFile
        Input GudrunFile that we will be using for iterating.
    Methods
    ----------
    performIteration()
        Performs a single iteration.
    applyCoefficientToAttribute(object, coefficient)
        To be overriden by sub-classes.
    iterate()
        Perform n iterations of iterating by tweak factor.
    organiseOutput
        To be overriden by sub-classes.
    """

    name = ""

    def __init__(self, gudrunFile, nTotal):
        """
        Constructs all the necessary attributes for the
        Iterator object.

        Parameters
        ----------
        gudrunFile : GudrunFile
            Input GudrunFile that we will be using for iterating.
        nTotal : int
            Total number of iterations to be run
        """
        self.gudrunFile = gudrunFile
        self.nTotal = nTotal
        self.nCurrent = -1
        self.iterationType = self.name

    def performIteration(self):
        """
        Performs a single iteration of the current workflow.

        """
        if self.nCurrent == -1:
            self.nCurrent += 1
            return
        # Iterate through all samples that are being run,
        # applying the coefficient to the target parameter.
        for sampleBackground in self.gudrunFile.sampleBackgrounds:
            for sample in [
                s for s in sampleBackground.samples
                if s.runThisSample and len(s.dataFiles)
            ]:
                gudFile = GudFile(
                    self.gudrunFile.gudrunOutput.gudFile(name=sample.name)
                )
                # Calculate coefficient: actualDCSLevel / expectedDCSLevel
                coefficient = (
                    gudFile.averageLevelMergedDCS / gudFile.expectedDCS
                )
                # Apply the coefficient.
                self.applyCoefficientToAttribute(sample, coefficient)
        self.nCurrent += 1

    def applyCoefficientToAttribute(self, object, coefficient):
        """
        Stub method to be overriden by sub-classes.
        The idea is that this method applies the 'coefficient'
        to a class-specific attribute of 'object'.

        Parameters
        ----------
        object : Sample
            Target object.
        coefficient : float
            Coefficient to use.
        """
        pass

    def organiseOutput(self):
        """
        This organises the output of the iteration.
        """
        gudrunOutput = self.gudrunFile.organiseOutput()
        return gudrunOutput

    def iterate(self):
        """
        This method is the core of the Iterator.
        It performs n iterations of tweaking by a class-specific parameter.
        Namely, it performs gudrun_dcs n times, adjusting said parameter
        for each sample before each iteration, after the first one,
        using the results of the previous iteration to do so.

        Parameters
        ----------
        n : int
            Number of iterations to perform.
        """
        self.gudrunFile.dcs(iterator=self)
        for _ in range(self.nTotal):
            time.sleep(1)
            self.performIteration()
            self.gudrunFile.dcs(iterator=self)


class Radius(Iterator):
    """
    Class to represent a Radius Iterator. Inherits Iterator.
    This class is used for iteratively tweaking the thickness of a
    flatplate sample.
    This means running gudrun_dcs iteratively, and adjusting the inner/outer
    radius of each sample across iterations.
    The new radii are determined by applying a coefficient calculated
    from the results of gudrun_dcs in the previous iteration.
    ...

    Methods
    ----------
    applyCoefficientToAttribute
        Multiplies a sample's inner/outer radii by a given coefficient.
    setTargetRadius
        Sets the target radius attribute.
    """
    name = "IterateByRadius"

    def applyCoefficientToAttribute(self, object, coefficient):
        if self.targetRadius == "inner":
            object.innerRadius *= coefficient
        elif self.targetRadius == "outer":
            object.outerRadius *= coefficient

    def setTargetRadius(self, targetRadius):
        self.targetRadius = targetRadius


class Thickness(Iterator):
    """
    Class to represent a Thickness Iterator. Inherits Iterator.
    This class is used for iteratively tweaking the thickness of a
    flatplate sample.
    This means running gudrun_dcs iteratively, and adjusting the thickness
    of each sample across iterations. The new thickness is determined by
    applying a coefficient calculated from the results of gudrun_dcs in the
    previous iteration.
    ...

    Methods
    ----------
    applyCoefficientToAttribute
        Multiplies a sample's thicknesses by a given coefficient.
    organiseOutput
        Organises the output of the iteration.
    """

    name = "IterateByThickness"

    def applyCoefficientToAttribute(self, object, coefficient):
        # Determine a new total thickness.
        totalThickness = object.upstreamThickness + object.downstreamThickness
        totalThickness *= coefficient
        # Assign the new thicknesses.
        object.downstreamThickness = totalThickness / 2
        object.upstreamThickness = totalThickness / 2


class TweakFactor(Iterator):
    """
    Class to represent a Tweak Factor Iterator.
    This class is used for iteratively tweaking by the tweak factor.
    This means running gudrun_dcs iteratively, and adjusting the tweak
    factor of each sample across iterations. The new tweak factor
    applied is the tweak factor suggested by
    gudrun_dcs in the previous iteration.

    ...

    Attributes
    ----------
    gudrunFile : GudrunFile
        Input GudrunFile that we will be using for iterating.
    Methods
    ----------
    performIteration(_n)
        Performs a single iteration.
    iterate(n)
        Perform n iterations of iterating by tweak factor.
    """

    name = "IterateByTweakFactor"

    def performIteration(self):
        """
        Performs a single iteration of the current workflow.

        Parameters
        ----------
        _n : int
            Iteration number.
        """
        if self.nCurrent == -1:
            self.nCurrent += 1
            return

        # Iterate through all samples,
        # updating their tweak factor from the output of gudrun_dcs.
        for sampleBackground in self.gudrunFile.sampleBackgrounds:
            for sample in [
                s for s in sampleBackground.samples
                if s.runThisSample and len(s.dataFiles)
            ]:
                gudFile = GudFile(
                    self.gudrunFile.gudrunOutput.gudFile(name=sample.name)
                )
                tweakFactor = float(gudFile.suggestedTweakFactor)
                sample.sampleTweakFactor = tweakFactor
        self.nCurrent += 1

    def iterate(self):
        """
        This method is the core of the TweakFactorIterator.
        It performs n iterations of tweaking by the tweak factor.
        Namely, it performs gudrun_dcs n times, adjusting the tweak factor
        for each sample before each iteration, after the first one, to
        the suggested tweak factor outputted from the previous iteration
        of gudrun_dcs. gudrun_dcs outputs a .gud file, which we
        parse to extract the suggested tweak factor from.

        Parameters
        ----------
        n : int
            Number of iterations to perform.
        """
        self.gudrunFile.dcs(iterator=self)
        # Perform n iterations of tweaking by tweak factor.
        for _ in range(self.nTotal):

            # Write out what we currently have,
            # and run gudrun_dcs on that file.
            time.sleep(1)
            self.performIteration()
            self.gudrunFile.dcs(iterator=self)


class Density(Iterator):
    """
    Class to represent a Density Iterator. Inherits Iterator.
    This class is used for iteratively tweaking the density.
    This means running gudrun_dcs iteratively, and adjusting the density
    of each sample across iterations. The new density is determined by
    applying a coefficient calculated from the results of gudrun_dcs in the
    previous iteration.
    ...

    Methods
    ----------
    applyCoefficientToAttribute
        Multiplies a sample's density by a given coefficient.
    """
    name = "IterateByDensity"

    def applyCoefficientToAttribute(self, object, coefficient):
        """
        Multiplies a sample's density by a given coefficient.
        Overrides the implementation from the base class.

        Parameters
        ----------
        object : Sample
            Target object.
        coefficient : float
            Coefficient to use.
        """
        # Apply the coefficient to the density.
        object.density *= coefficient


class InelasticitySubtraction(Iterator):
    """
    Class to represent a InelasticitySubtraction iterator.
    This class is used for iteratively subtracting wavelength.
    Each iteration comprises of a wavelength run and a
    Q binning run.
    A typical use case for this class might be for
    in-elasticity subtractions.

    ...

    Attributes
    ----------
    gudrunFile : GudrunFile
        Input GudrunFile that we will be using for iterating.
    topHatWidths : float[]
        List storing the width of top hat functions for FT for each sample
        that is being run.
    QMax : float
        Stores the maximum Q for final merged data.
        Stored, as we switch between scales this data needs to be held.
    QMin : float
        Stores the minimum Q for final merged data.
        Stored, as we switch between scales this data needs to be held.
    QStep : float
        Step size for corrections on Q scale.
        Stored, as we switch between scales this data needs to be held.
    Methods
    ----------
    enableLogarithmicBinning
        Enables logarithmic binning
    disableLogarithmicBinning
        Disables logarithmic binning
    collectQRange
        Collects QMax, QMin and QStep, and stores them as attributes.
    applyQRange
        Applies the Q range and step collected to the X-scale.
    applyWavelengthRanges
        Apply the wavelength ranges of the instrument to the X-scale.
    zeroTopHatWidths
        Set width of top hat functions for FT to zero, for each sample.
    setSelfScatteringFiles(scale)
        Alters file extensions of self scattering files, to the
        relevant extension for the scale inputted.
    wavelengthIteration(i)
        Performs one iteration on the wavelength scale.
    QIteration(i)
        Performs one iteration on the Q scale.
    iterate(n)
        Perform n iterations on the wavelength scale and Q scale.
    """

    name = "IterateByInelasticitySubtraction"

    def __init__(self, gudrunFile, nTotal):
        """
        Constructs all the necessary attributes for the
        InelasticitySubtraction object.

        Parameters
        ----------
        gudrunFile : GudrunFile
            Input GudrunFile that we will be using for iterating.
        """
        super().__init__(gudrunFile, nTotal)
        # Does a default iteration first (no changes)
        self.iterationType = "QIteration"
        # Individual iterations
        self.iterationCount = 0
        # Iteration pair
        self.nCurrent = 0
        self.topHatWidths = []
        self.QMax = 0.
        self.QMin = 0.
        self.QStep = 0.
        self.gudrunOutputs = []

    def enableLogarithmicBinning(self):
        """
        Enables logarithmic binning.
        """
        self.gudrunFile.instrument.useLogarithmicBinning = True

    def disableLogarithmicBinning(self):
        """
        Disables logarithmic binning.
        """
        self.gudrunFile.instrument.useLogarithmicBinning = False

    def collectQRange(self):
        """
        Collects the max, min and step on the Q scale.
        Stores them in attributes.
        """
        self.QMax = self.gudrunFile.instrument.XMax
        self.QMin = self.gudrunFile.instrument.XMin
        self.QStep = self.gudrunFile.instrument.XStep

    def applyQRange(self):
        """
        Apply max, min and step from Q scale to X scale.
        """
        self.gudrunFile.instrument.XMax = self.QMax
        self.gudrunFile.instrument.XMin = self.QMin
        self.gudrunFile.instrument.XStep = self.QStep

    def applyWavelengthRanges(self):
        """
        Apply max, min and step from wavelength scale to X scale.
        """
        self.gudrunFile.instrument.XMax = (
            self.gudrunFile.instrument.wavelengthMax
        )
        self.gudrunFile.instrument.XMin = (
            self.gudrunFile.instrument.wavelengthMin
        )

    def zeroTopHatWidths(self):
        """
        Iterate through all samples, setting the
        width of top hat functions for FT to zero, for each sample
        that is being run.
        """

        # Iterate through all of the samples, and set top hat widths to zero.
        for sampleBackground in self.gudrunFile.sampleBackgrounds:
            for sample in sampleBackground.samples:
                if sample.runThisSample:
                    target = sample
                    target.topHatW = 0

    def resetTopHatWidths(self):
        """
        Iterate through all samples, setting the
        width of top hat functions for their previous values, for each sample
        that is being run.
        """

        # Iterate through all of the samples, and set top hat widths to
        # their previous values
        for sampleBackground in self.gudrunFile.sampleBackgrounds:
            for sample, topHatW in zip(
                    sampleBackground.samples, self.topHatWidths):
                target = sample
                target.topHatW = topHatW

    def collectTopHatWidths(self):
        """
        Iterate through all samples, collecting the
        width of top hat functions, for each sample that is being run.
        """
        self.topHatWidths = []

        # Iterate over samples, saving their top hat widths
        for sampleBackground in self.gudrunFile.sampleBackgrounds:
            for sample in sampleBackground.samples:
                if sample.runThisSample:
                    self.topHatWidths.append(sample.topHatW)

    def setSelfScatteringFiles(self, scale):
        """
        Alters file extensions of self scattering files for samples being run.
        If the scale selected is the Q-scale, then set self scattering file
        extensions to msubw01. If the scale selected is the wavelength-scale,
        then set self scattering file extensions to mint01.
        """
        # Dict to pick suffix based on scale
        suffix = {Scales.Q: ".msubw01", Scales.WAVELENGTH: ".mint01"}[scale]

        # Iterate through all of the samples, and set the suffixes of
        # all of their data files to the suffix
        # relevant to the specified scale
        for sampleBackground in self.gudrunFile.sampleBackgrounds:
            for sample in sampleBackground.samples:
                if sample.runThisSample and len(sample.dataFiles):
                    target = sample
                    filename = target.dataFiles[0]
                    prevOutput = (
                        self.gudrunFile.gudrunOutput.output(
                            sample.name, filename, suffix)
                        if self.gudrunFile.gudrunOutput else ""
                    )
                    target.fileSelfScattering = (
                        os.path.join(
                            prevOutput,
                        )
                    )

    def wavelengthIteration(self):
        """
        Performs one iteration on the wavelength scale.
        If the iteration is the first iteration,
        then disable subtracting of wavelength-binned data,
        collect the top hat widths for all samples being run,
        as well as the Q range.
        If it's a normal iteration, then enable subtracting
        of wavelength-binned data.
        During all iterations, apply wavelength ranges to
        the x-scale, enable logarithmic binning, set the scale
        to the wavelength scale, zero the top hat widths, change
        the extensions of the self scattering files to .mint01.
        Then, write out the gudrunFile and call gudrun_dcs.
        """
        self.iterationType = "WavelengthIteration"
        # First iteration
        if self.iterationCount == 0:
            # Disable subtracting of wavelength binned data.
            # Collect the top hat widths and Q range and step size.
            self.gudrunFile.instrument.subWavelengthBinnedData = False
            self.collectTopHatWidths()
            self.collectQRange()
        else:
            # Enable subtracting of wavelength binned data
            self.gudrunFile.instrument.subWavelengthBinnedData = True

        # Set the min, max and step size on the X scale
        # To the min, max and step size on the wavelength scale
        # Set the correct scale, zero top hat widths and
        # alter data file suffixes.
        self.applyWavelengthRanges()
        self.enableLogarithmicBinning()
        self.gudrunFile.instrument.scaleSelection = (
            Scales.WAVELENGTH
        )
        self.zeroTopHatWidths()
        self.setSelfScatteringFiles(Scales.WAVELENGTH)

    def QIteration(self):
        """
        Performs one iteration on the Q scale.
        Enables subtracting of wavelength-binned data.
        During all iterations, apply Q ranges to
        the x-scale, disable logarithmic binning, set the scale
        to the Q scale, reset the top hat widths, change
        the extensions of the self scattering files to .msubw01.
        Then, write out the gudrunFile and call gudrun_dcs.
        """
        self.iterationType = "QIteration"
        # Enable subtracting of wavelength binned data
        self.gudrunFile.instrument.subWavelengthBinnedData = True
        # Set the min, max and step size on the X scale
        # To the min, max and step size on the Q scale
        # Set the correct scale, reset top hat widths
        # alter data file suffixes.
        self.applyQRange()
        self.disableLogarithmicBinning()
        self.gudrunFile.instrument.scaleSelection = Scales.Q
        self.resetTopHatWidths()
        self.setSelfScatteringFiles(Scales.Q)

    def performIteration(self):
        if self.iterationType == "QIteration":
            self.wavelengthIteration()
            self.iterationCount += 1
        else:
            self.QIteration()
            self.nCurrent += 1

    def organiseOutput(self):
        """
        This organises the output of the iteration.
        """
        overwrite = (self.iterationCount == 1 and
                     self.iterationType == "WavelengthIteration")
        return self.gudrunFile.organiseOutput(
            head=f"{self.iterationType}_{self.iterationCount}",
            overwrite=overwrite)

    def iterate(self):
        """
        Perform n iterations on both
        the wavelength scale and Q scale.
        """
        for _ in range(self.nTotal * 2):
            self.performIteration()
            self.gudrunFile.dcs(iterator=self)
            self.gudrunOutputs.append(self.gudrunFile.gudrunOutput)
            time.sleep(1)


def gss(
    f, bounds, n, maxN, rtol, args=(),
    startIterFunc=None, endIterFunc=None
):
    if startIterFunc:
        startIterFunc(n)
    if n >= maxN:
        return bounds[1]

    if (
        (abs(bounds[2] - bounds[0]) / min([abs(bounds[0]), abs(bounds[2])]))
        < (rtol / 100)**2
    ):
        if endIterFunc:
            endIterFunc(n)
        return (bounds[2] + bounds[1]) / 2

    # Calculate a potential centre = c + 2 - GR * (upper-c)
    d = bounds[1] + (2 - (1 + math.sqrt(5)) / 2) * (bounds[2] - bounds[1])

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
            f, bounds, n + 1, maxN, rtol,
            args=args, startIterFunc=startIterFunc, endIterFunc=endIterFunc
        )
    # Otherwise, swap and reverse.
    else:
        bounds = [d, bounds[1], bounds[0]]
        if endIterFunc:
            endIterFunc()
        return gss(
            f, bounds, n + 1, maxN, rtol,
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


class Composition():
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

    name = "IterateByComposition"

    def __init__(self, gudrunFile):
        self.gudrunFile = gudrunFile
        self.components = []
        self.ratio = 0
        self.nTotal = 0
        self.nCurrent = 0
        self.iterationType = self.name
        self.nWeightedComponents = 0

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
        self.gudrunFile.dcs(iterator=self)

        time.sleep(1)

        gudFile = GudFile(
            os.path.join(
                self.gudrunFile.gudrunOutput.gudFile(
                    name=sampleBackground.samples[0].name)
            )
        )

        self.nCurrent += 1

        if gudFile.averageLevelMergedDCS == gudFile.expectedDCS:
            return 0
        else:
            return (gudFile.expectedDCS - gudFile.averageLevelMergedDCS)**2

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
        self.gudrunFile.dcs(iterator=self)

        time.sleep(1)

        gudFile = GudFile(
            os.path.join(
                self.gudrunFile.gudrunOutput.gudFile(
                    name=sampleBackground.samples[0].name)
            )
        )

        self.nCurrent += 1

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

    def organiseOutput(self):
        """
        This organises the output of the iteration.
        """
        gudrunOutput = self.gudrunFile.organiseOutput()
        return gudrunOutput