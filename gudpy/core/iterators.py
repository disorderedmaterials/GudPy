from copy import deepcopy
import math
from enum import Enum

from core.gud_file import GudFile
from core.enums import Scales, IterationModes
from core.gudrun_file import GudrunFile
import core.output_file_handler as handlers


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
    applyCoefficientToAttribute(sample, coefficient)
        To be overriden by sub-classes.
    iterate()
        Perform n iterations of iterating by tweak factor.
    organiseOutput
        To be overriden by sub-classes.
    """

    def __init__(self, nTotal):
        """
        Constructs all the necessary attributes for the
        Iterator sample.

        Parameters
        ----------
        gudrunFile : GudrunFile
            Input GudrunFile that we will be using for iterating.
        nTotal : int
            Total number of iterations to be run
        iterationType : str
            Type of iteration being conducted
        requireDefault : bool

        """
        self.name = ""
        self.nTotal = nTotal
        self.nCurrent = -1
        self.iterationType = self.name
        self.requireDefault = True
        self.result = {}

    def performIteration(
        self,
        gudrunFile: GudrunFile,
        prevOutput: handlers.GudrunOutput
    ) -> GudrunFile:
        """
        Performs a single iteration of the current workflow.

        """
        if self.nCurrent == -1:
            self.nCurrent += 1
            return
        # Iterate through all samples that are being run,
        # applying the coefficient to the target parameter.
        for sampleBackground in gudrunFile.sampleBackgrounds:
            for sample in [
                s for s in sampleBackground.samples
                if s.runThisSample and len(s.dataFiles)
            ]:
                gudFile = GudFile(
                    prevOutput.gudFile(name=sample.name)
                )
                # Calculate coefficient: actualDCSLevel / expectedDCSLevel
                coefficient = (
                    gudFile.averageLevelMergedDCS / gudFile.expectedDCS
                )
                # Apply the coefficient.
                self.applyCoefficientToAttribute(
                    sample, coefficient, prevOutput)
        self.nCurrent += 1
        return gudrunFile

    def applyCoefficientToAttribute(self, sample, coefficient, prevOutput):
        """
        Stub method to be overriden by sub-classes.
        The idea is that this method applies the 'coefficient'
        to a class-specific attribute of 'sample'.

        Parameters
        ----------
        sample : Sample
            Target sample.
        coefficient : float
            Coefficient to use.
        """
        pass

    def organiseOutput(self, gudrunFile, exclude=[]):
        """
        This organises the output of the iteration.
        """
        outputHandler = handlers.GudrunOutputHandler(
            gudrunFile=gudrunFile,
        )
        return outputHandler.organiseOutput(exclude=exclude)


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

    def __init__(self, nTotal, target="inner"):
        super().__init__(nTotal, name="Radius")
        self.iterationMode = None
        self.setTargetRadius(target)

    def applyCoefficientToAttribute(self, sample, coefficient, prevOutput):
        if not self.result.get(sample.name, ""):
            self.result[sample.name] = {}
            self.result[sample.name]["Old"] = {
                f"{self.targetRadius.capitalize()} Radius": sample.innerRadius
                if self.targetRadius == "inner" else sample.outerRadius
            }
        if self.targetRadius == "inner":
            sample.innerRadius *= coefficient
            self.result[sample.name]["New"] = {
                "Inner Radius": sample.innerRadius
            }
        elif self.targetRadius == "outer":
            sample.outerRadius *= coefficient
            self.result[sample.name]["New"] = {
                "Outer Radius": sample.outerRadius
            }

    def setTargetRadius(self, targetRadius):
        self.targetRadius = targetRadius
        if self.targetRadius == "inner":
            self.iterationMode = IterationModes.INNER_RADIUS
        if self.targetRadius == "outer":
            self.iterationMode = IterationModes.OUTER_RADIUS


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

    def __init__(self, nTotal):
        super().__init__(nTotal)
        self.name = "thickness"
        self.iterationMode = IterationModes.THICKNESS

    def applyCoefficientToAttribute(self, sample, coefficient, prevOutput):
        if not self.result.get(sample.name, ""):
            self.result[sample.name] = {}
            self.result[sample.name]["Old"] = {
                "Downstream Thickness": sample.downstreamThickness,
                "Upstream Thickness": sample.upstreamThickness
            }
        # Determine a new total thickness.
        totalThickness = sample.upstreamThickness + sample.downstreamThickness
        totalThickness *= coefficient
        # Assign the new thicknesses.
        sample.downstreamThickness = totalThickness / 2
        sample.upstreamThickness = totalThickness / 2

        self.result[sample.name]["New"] = {
            "Downstream Thickness": sample.downstreamThickness,
            "Upstream Thickness": sample.upstreamThickness
        }


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

    def __init__(self, nTotal):
        super().__init__(nTotal)
        self.name = "tweakfactor"
        self.iterationMode = IterationModes.TWEAK_FACTOR

    def performIteration(self, gudrunFile, prevOutput) -> GudrunFile:
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
        for sampleBackground in gudrunFile.sampleBackgrounds:
            for sample in [
                s for s in sampleBackground.samples
                if s.runThisSample and len(s.dataFiles)
            ]:
                if not self.result.get(sample.name, ""):
                    self.result[sample.name] = {}
                    self.result[sample.name]["Old"] = {
                        "Tweak Factor": sample.sampleTweakFactor
                    }
                gudFile = GudFile(
                    prevOutput.gudFile(name=sample.name)
                )
                tweakFactor = float(gudFile.suggestedTweakFactor)
                sample.sampleTweakFactor = tweakFactor

                self.result[sample.name]["New"] = {
                    "Tweak Factor": tweakFactor
                }
        self.nCurrent += 1
        return gudrunFile


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

    def __init__(self, nTotal):
        super().__init__(nTotal)
        self.name = "density"
        self.iterationMode = IterationModes.DENSITY

    def applyCoefficientToAttribute(self, sample, coefficient, prevOutput):
        """
        Multiplies a sample's density by a given coefficient.
        Overrides the implementation from the base class.

        Parameters
        ----------
        sample : Sample
            Target sample.
        coefficient : float
            Coefficient to use.
        """
        # Apply the coefficient to the density.
        if not self.result.get(sample.name, ""):
            self.result[sample.name] = {}
            self.result[sample.name]["Old"] = {
                "Density": sample.density
            }
        sample.density *= coefficient
        self.result[sample.name]["New"] = {"Density": sample.density}


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

    def __init__(self, nTotal):
        """
        Constructs all the necessary attributes for the
        InelasticitySubtraction sample.

        Parameters
        ----------
        gudrunFile : GudrunFile
            Input GudrunFile that we will be using for iterating.
        """
        nTotal *= 2
        super().__init__(nTotal)
        self.name = "inelasticity subtraction"
        self.iterationMode = IterationModes.INELASTICITY
        # Does a default iteration first (no changes)
        self.iterationType = "QIteration"
        # Individual iterations
        self.iterationCount = 0
        # If a default iteration is required
        self.requireDefault = False
        # Iteration pair
        self.nCurrent = 0
        self.topHatWidths = []
        self.QMax = 0.
        self.QMin = 0.
        self.QStep = 0.
        self.gudrunOutputs = []

    def enableLogarithmicBinning(self, gudrunFile):
        """
        Enables logarithmic binning.
        """
        gudrunFile.instrument.useLogarithmicBinning = True

    def disableLogarithmicBinning(self, gudrunFile):
        """
        Disables logarithmic binning.
        """
        gudrunFile.instrument.useLogarithmicBinning = False

    def collectQRange(self, gudrunFile):
        """
        Collects the max, min and step on the Q scale.
        Stores them in attributes.
        """
        self.QMax = gudrunFile.instrument.XMax
        self.QMin = gudrunFile.instrument.XMin
        self.QStep = gudrunFile.instrument.XStep

    def applyQRange(self, gudrunFile):
        """
        Apply max, min and step from Q scale to X scale.
        """
        gudrunFile.instrument.XMax = self.QMax
        gudrunFile.instrument.XMin = self.QMin
        gudrunFile.instrument.XStep = self.QStep

    def applyWavelengthRanges(self, gudrunFile):
        """
        Apply max, min and step from wavelength scale to X scale.
        """
        gudrunFile.instrument.XMax = (
            gudrunFile.instrument.wavelengthMax
        )
        gudrunFile.instrument.XMin = (
            gudrunFile.instrument.wavelengthMin
        )

    def zeroTopHatWidths(self, gudrunFile):
        """
        Iterate through all samples, setting the
        width of top hat functions for FT to zero, for each sample
        that is being run.
        """

        # Iterate through all of the samples, and set top hat widths to zero.
        for sampleBackground in gudrunFile.sampleBackgrounds:
            for sample in sampleBackground.samples:
                if sample.runThisSample:
                    target = sample
                    target.topHatW = 0

    def resetTopHatWidths(self, gudrunFile):
        """
        Iterate through all samples, setting the
        width of top hat functions for their previous values, for each sample
        that is being run.
        """

        # Iterate through all of the samples, and set top hat widths to
        # their previous values
        for sampleBackground in gudrunFile.sampleBackgrounds:
            for sample, topHatW in zip(
                    sampleBackground.samples, self.topHatWidths):
                target = sample
                target.topHatW = topHatW

    def collectTopHatWidths(self, gudrunFile):
        """
        Iterate through all samples, collecting the
        width of top hat functions, for each sample that is being run.
        """
        self.topHatWidths = []

        # Iterate over samples, saving their top hat widths
        for sampleBackground in gudrunFile.sampleBackgrounds:
            for sample in sampleBackground.samples:
                if sample.runThisSample:
                    self.topHatWidths.append(sample.topHatW)

    def setSelfScatteringFiles(self, scale, gudrunFile, prevOutput=None):
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
        for sampleBackground in gudrunFile.sampleBackgrounds:
            for sample in sampleBackground.samples:
                if sample.runThisSample and len(sample.dataFiles):
                    target = sample
                    filename = target.dataFiles[0]
                    targetFile = (
                        prevOutput.output(
                            sample.name, filename, suffix)
                        if prevOutput else ""
                    )
                    target.fileSelfScattering = (
                        targetFile
                    )

    def wavelengthIteration(self, gudrunFile, prevOutput):
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
            gudrunFile.instrument.subWavelengthBinnedData = False
            self.collectTopHatWidths(gudrunFile)
            self.collectQRange(gudrunFile)
        else:
            # Enable subtracting of wavelength binned data
            gudrunFile.instrument.subWavelengthBinnedData = True

        # Set the min, max and step size on the X scale
        # To the min, max and step size on the wavelength scale
        # Set the correct scale, zero top hat widths and
        # alter data file suffixes.
        self.applyWavelengthRanges(gudrunFile)
        self.enableLogarithmicBinning(gudrunFile)
        gudrunFile.instrument.scaleSelection = (
            Scales.WAVELENGTH
        )
        self.zeroTopHatWidths(gudrunFile)
        self.setSelfScatteringFiles(Scales.WAVELENGTH, gudrunFile, prevOutput)

    def QIteration(self, gudrunFile, prevOutput):
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
        gudrunFile.instrument.subWavelengthBinnedData = True
        # Set the min, max and step size on the X scale
        # To the min, max and step size on the Q scale
        # Set the correct scale, reset top hat widths
        # alter data file suffixes.
        self.applyQRange(gudrunFile)
        self.disableLogarithmicBinning(gudrunFile)
        gudrunFile.instrument.scaleSelection = Scales.Q
        self.resetTopHatWidths(gudrunFile)
        self.setSelfScatteringFiles(Scales.Q, gudrunFile, prevOutput)

    def performIteration(self, gudrunFile, prevOutput):
        if self.iterationType == "QIteration":
            self.wavelengthIteration(gudrunFile, prevOutput)
            self.iterationCount += 1
        else:
            self.QIteration(gudrunFile, prevOutput)
            self.nCurrent += 1
        return gudrunFile

    def organiseOutput(self, gudrunFile, exclude=[]):
        """
        This organises the output of the iteration.
        """
        overwrite = (self.iterationCount == 1 and
                     self.iterationType == "WavelengthIteration")
        outputHandler = handlers.GudrunOutputHandler(
            gudrunFile=gudrunFile,
            head=f"{self.iterationType}_{self.iterationCount}",
            overwrite=overwrite
        )
        output = outputHandler.organiseOutput(exclude=exclude)
        self.gudrunOutputs.append(output)
        return output


def calculateTotalMolecules(components, sample):
    # Sum molecules in sample composition, belongiong to components.
    total = 0
    for wc in sample.composition.weightedComponents:
        for c in components:
            if wc.component.eq(c):
                total += wc.ratio
                break
    return total


class Composition(Iterator):
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

    class Mode(Enum):
        SINGLE = 1
        DOUBLE = 2

    def __init__(
        self,
        gudrunFile,
        mode: Mode = Mode.SINGLE,
        startBound=1e-2,
        endBound=10,
        nTotal=10,
        rtol=10,
        ratio=1,
        components=[],
    ):
        self.name = "composition"
        self.originalGudrunFile = gudrunFile
        self.mode = mode
        self.nCurrent = 0
        self.newCenter = None
        self.newCenterOutput = None

        self.ratio = ratio
        self.components = [c for c in components if c]

        if len(self.components) == 1:
            self.mode = Composition.Mode.SINGLE
        else:
            self.mode = Composition.Mode.DOUBLE

        self.nTotal = nTotal
        self.rtol = rtol

        self.sampleArgs = []

        self.updatedSample = None
        self.currentCenter = 0
        self.compositionMap = {}

        for sampleBackground in gudrunFile.sampleBackgrounds:
            for sample in sampleBackground.samples:
                if sample.runThisSample:
                    if [
                        wc for wc in sample.composition.weightedComponents
                        if self.components[0].eq(wc.component)
                    ]:
                        sb = deepcopy(sampleBackground)
                        sb.samples = [deepcopy(sample)]
                        if self.mode == Composition.Mode.SINGLE:
                            self.sampleArgs.append({
                                "sample": sample,
                                "background": sb,
                                "molecules": None,
                                "bounds": [startBound, self.ratio, endBound]
                            })
                        elif self.mode == Composition.Mode.DOUBLE:
                            self.sampleArgs.append({
                                "sample": sample,
                                "background": sb,
                                "molecules": self.calculateTotalMolecules(
                                    self.components,
                                    sample
                                ),
                                "bounds": [startBound, self.ratio, endBound]
                            })
        print(self.sampleArgs)

    def costUp(
        self,
        x,
        sampleArg,
        gudrunFile
    ):
        # Prevent negative x
        x = abs(x)

        if self.mode == Composition.Mode.SINGLE:
            # Determine instances where target components are used.
            weightedComponents = [
                wc for wc in sampleArg["background"].samples[0]
                .composition.weightedComponents
                for c in self.components
                if c.eq(wc.component)
            ]
            for component in weightedComponents:
                component.ratio = x

        elif self.mode == Composition.Mode.DOUBLE:
            wcA = wcB = None
            # Determine instances where target components are used.
            for weightedComponent in (
                sampleArg[
                    "background"
                ].samples[0].composition.weightedComponents
            ):
                if weightedComponent.component.eq(self.components[0]):
                    wcA = weightedComponent
                elif weightedComponent.component.eq(self.components[1]):
                    wcB = weightedComponent

            if wcA and wcB:
                # Ensure combined ratio == totalMolecules.
                wcA.ratio = x
                wcB.ratio = abs(sampleArg["molecules"] - x)

        sampleArg["background"].samples[0].composition.translate()
        self.updatedSample = sampleArg["background"].samples[0]
        self.compositionMap[sampleArg["sample"]] = self.updatedSample

        gudrunFile.sampleBackgrounds = [sampleArg["background"]]
        return gudrunFile

    def determineCost(self, gudFile: GudFile):
        if gudFile.averageLevelMergedDCS == gudFile.expectedDCS:
            return 0
        else:
            return (gudFile.expectedDCS-gudFile.averageLevelMergedDCS)**2

    def iterateCurrentCenter(
            self, gudrunFile: GudrunFile, sampleArg) -> GudrunFile:
        gudrunFileCopy = deepcopy(gudrunFile)
        return self.costUp(sampleArg["bounds"][1], sampleArg, gudrunFileCopy)

    def iterateNewPotentialCenter(self, gudrunFile: GudrunFile, sampleArg):
        gudrunFileCopy = deepcopy(gudrunFile)
        bounds = sampleArg["bounds"]

        # Calculate a potential centre = c + 2 - GR * (upper-c)
        self.newCenter = bounds[1] + (2 - (1 + math.sqrt(5)) / 2) * \
            (bounds[2] - bounds[1])

        # If the new centre evaluates to less than the current
        return self.costUp(self.newCenter, sampleArg, gudrunFileCopy)

    def performIteration(
        self,
        gudrunFile: GudrunFile,
        sampleArg: dict,
        prevOutput: handlers.GudrunOutput
    ) -> GudrunFile:
        bounds = sampleArg["bounds"]
        if (
            (abs(bounds[2] - bounds[0]) /
             min([abs(bounds[0]), abs(bounds[2])]))
            < (self.rtol / 100)**2
        ):
            sampleArg["result"] = (
                (bounds[2] + bounds[1]) / 2)
            return

        if self.newCenterOutput and prevOutput:
            print(prevOutput)
            gudFileCurrentCenter = GudFile(prevOutput.gudFile(
                name=sampleArg["background"].samples[0].name))
            gudFileNewCenter = GudFile(self.newCenterOutput.gudFile(
                name=sampleArg["background"].samples[0].name))
            currentCost = self.determineCost(gudFileCurrentCenter)
            newCost = self.determineCost(gudFileNewCenter)

            if newCost < currentCost:
                # Swap them, making the previous centre the new lower bound.
                sampleArg["bounds"] = [bounds[1], self.newCenter, bounds[2]]
            else:
                # Otherwise, swap and reverse.
                sampleArg["bounds"] = [self.newCenter, bounds[1], bounds[0]]
            self.nCurrent += 1
            self.newCenterOutput = None
            return self.iterateCurrentCenter(gudrunFile, sampleArg)
        else:
            self.newCenterOutput = prevOutput
            return self.iterateNewPotentialCenter(gudrunFile, sampleArg)
