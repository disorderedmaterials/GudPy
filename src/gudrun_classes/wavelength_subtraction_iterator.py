from pathlib import Path
from enums import Scales


class WavelengthSubtractionIterator():
    """
    Class to represent a WavelengthSubtractionIterator.
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

    def __init__(self, gudrunFile):
        """
        Constructs all the necessary attributes for the PurgeFile object.

        Parameters
        ----------
        gudrunFile : GudrunFile
            Input GudrunFile that we will be using for iterating.
        """
        self.gudrunFile = gudrunFile
        self.topHatWidths = []
        self.QMax = 0.
        self.QMin = 0.
        self.QStep = 0.

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
        # Enumerator for sample backgrounds
        iterator = enumerate(self.gudrunFile.sampleBackgrounds)

        # Iterate through all of the samples, and set top hat widths to zero.
        for i, sampleBackground in iterator:
            for j, sample in enumerate(sampleBackground.samples):
                if sample.runThisSample:
                    target = self.gudrunFile.sampleBackgrounds[i].samples[j]
                    target.topHatW = 0

    def resetTopHatWidths(self):
        """
        Iterate through all samples, setting the
        width of top hat functions for their previous values, for each sample
        that is being run.
        """
        # Enumerator for sample backgrounds
        iterator = enumerate(self.gudrunFile.sampleBackgrounds)

        # Iterate through all of the samples, and set top hat widths to
        # their previous values
        for i, sampleBackground in iterator:
            for j, sample in enumerate(sampleBackground.samples):
                if sample.runThisSample:
                    target = self.gudrunFile.sampleBackgrounds[i].samples[j]
                    target.topHatW = self.topHatWidths[j]

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
        suffix = {Scales.Q: "msubw01", Scales.WAVELENGTH: "mint01"}[scale]

        # Enumerator for sample backgrounds
        iterator = enumerate(self.gudrunFile.sampleBackgrounds)

        # Iterate through all of the samples, and set the suffixes of
        # all of their data files to the suffix
        # relevant to the specified scale
        for i, sampleBackground in iterator:
            for j, sample in enumerate(sampleBackground.samples):
                if sample.runThisSample:
                    target = self.gudrunFile.sampleBackgrounds[i].samples[j]
                    filename = target.dataFiles.dataFiles[0]
                    target.fileSelfScattering = (
                        str(Path(filename).stem) + '.' + suffix
                    )

    def wavelengthIteration(self, i):
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
        Then, write out the GudrunFile and call gudrun_dcs.
        """
        # First iteration
        if i == 0:
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

        # Write out updated file and call gudrun_dcs.
        self.gudrunFile.process()

    def QIteration(self, i):
        """
        Performs one iteration on the Q scale.
        Enables subtracting of wavelength-binned data.
        During all iterations, apply Q ranges to
        the x-scale, disable logarithmic binning, set the scale
        to the Q scale, reset the top hat widths, change
        the extensions of the self scattering files to .msubw01.
        Then, write out the GudrunFile and call gudrun_dcs.
        """
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

        # Write out updated file and call gudrun_dcs.
        self.gudrunFile.process()

    def iterate(self, n):
        """
        Perform n iterations on both
        the wavelength scale and Q scale.
        """

        for i in range(n):

            self.wavelengthIteration(i)
            self.QIteration(i)
