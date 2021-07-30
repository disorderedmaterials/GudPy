from enum import Enum


class WavelengthSubtractionIterator():

    def __init__(self, gudrunFile):

        self.gudrunFile = gudrunFile
        self.topHatWidths = []
        self.QMax = 0.
        self.QMin = 0.
        self.QStep = 0.

        class Scales(Enum):
            Q = 1
            D_SPACE = 2
            WAVELENGTH = 3
            ENERGY = 4
            TOF = 5

        self.scales = Scales()

    def enableLogarithmicBinning(self):

        self.gudrunFile.instrument.useLogarithmicBinning = False

    def disableLogarithmicBinning(self):

        self.gudrunFile.instrument.useLogarithmicBinning = True

    def collectQRange(self):
        # Collect max, min and step on Q scale.
        self.QMax = self.gudrunFile.instrument.XMax
        self.QMin = self.gudrunFile.instrument.XMin
        self.QStep = self.gudrunFile.instrument.XStep

    def applyQRange(self):
        # Apply max, min and step from Q scale to X scale.
        self.gudrunFile.instrument.XMax = self.QMax
        self.gudrunFile.instrument.XMin = self.QMin
        self.gudrunFile.instrument.XStep = self.QStep

    def applyWavelengthRanges(self):
        # Apply max, min and step from wavelength scale to X scale.
        self.gudrunFile.instrument.XMax = (
            self.gudrunFile.instrument.wavelengthMax
        )
        self.gudrunFile.instrument.XMin = (
            self.gudrunFile.instrument.wavelengthMin
        )
        self.gudrunFile.instrument.XStep = (
            self.gudrunFile.instrument.wavelengthStep
        )

    def zeroTopHatWidths(self):
        # Enumerator for sample backgrounds
        iterator = enumerate(self.gudrunFile.sampleBackgrounds)

        # Iterate through all of the samples, and set top hat widths to zero.
        for i, sampleBackground in iterator:
            for j, sample in enumerate(sampleBackground.samples):
                if sample.runThisSample:
                    target = self.gudrunFile.sampleBackgrounds[i].samples[j]
                    target.topHatW = 0

    def resetTopHatWidths(self):
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

        self.topHatWidths = []

        # Iterate over samples, saving their top hat widths
        for sampleBackground in self.gudrunFile.sampleBackgrounds:
            for sample in sampleBackground.samples:
                self.topHatWidths.append(sample.topHatW)

    def setSelfScatteringFiles(self, scale):

        dataFileType = self.gudrunFile.instrument.dataFileType
        # Dict to pick suffix based on scale
        suffix = {1: "msubw01", 3: "mint01"}[scale]

        # Enumerator for sample backgrounds
        iterator = enumerate(self.gudrunFile.sampleBackgrounds)

        # Iterate through all of the samples, and set the suffixes of
        # all of their data files to the suffix
        # relevant to the specified scale
        for i, sampleBackground in iterator:
            for j, sample in enumerate(sampleBackground.samples):
                if sample.runThisSample:
                    target = self.gudrunFile.sampleBackgrounds[i].samples[j]
                    target.fileSelfScattering = (
                        target.dataFiles.dataFiles[0].replace(
                            dataFileType, suffix
                            )
                    )

    def wavelengthIteration(self, i):

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
        self.gudrunFile.instrument.scaleSelection = 3
        self.zeroTopHatWidths()
        self.setSelfScatteringFiles(self.scales.WAVELENGTH)

        # Write out updated file and call gudrun_dcs.
        self.gudrunFile.process()

    def QIteration(self, i):

        # Enable subtracting of wavelength binned data
        self.gudrunFile.instrument.subWavelengthBinnedData = True
        # Set the min, max and step size on the X scale
        # To the min, max and step size on the wavelength scale
        # Set the correct scale, reset top hat widths
        # alter data file suffixes.
        self.applyQRange()
        self.gudrunFile.instrument.scaleSelection = 1
        self.resetTopHatWidths()
        self.setSelfScatteringFiles(self.scales.Q)

        # Write out updated file and call gudrun_dcs.
        self.gudrunFile.process()

    def iterate(self, n):

        # Perform n iterations on both
        # the wavelength scale and Q scale.
        for i in range(n):

            self.wavelengthIteration(i)
            self.QIteration(i)
