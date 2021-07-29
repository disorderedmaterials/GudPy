
class WavelengthSubtractionIterator():

    def __init__(self, gudrunFile):

        self.gudrunFile = gudrunFile
        self.topHatWidths = []
        self.QRange = ()

    def enableLogarithmicBinning(self):

        # -ve to signal logarithmic binning
        self.gudrunFile.instrument.XScaleRangeStep += (-0.01,)

    def disableLogarithmicBinning(self):

        self.gudrunFile.instrument.XScaleRangeStep = (
            self.gudrunFile.instrument.XScaleRangeStep[: -1]
        )
    
    def collectQRange(self):
        self.QRange = self.gudrunFile.instrument.XScaleRangeStep

    def applyQRange(self):
        self.gudrunFile.instrument.XScaleRangeStep = self.QRange

    def applyWavelengthRanges(self):
        self.gudrunFile.instrument.XScaleRangeStep = self.gudrunFile.instrument.wavelengthRangeStepSize[:2]

    def zeroTopHatWidths(self):

        iterator = enumerate(self.gudrunFile.sampleBackgrounds)

        for i, sampleBackground in iterator:
            for j, sample in enumerate(sampleBackground.samples):
                if sample.runThisSample:
                    target = self.gudrunFile.sampleBackgrounds[i].samples[j]
                    target.topHatW = 0

    def resetTopHatWidths(self):

        iterator = enumerate(self.gudrunFile.sampleBackgrounds)

        for i, sampleBackground in iterator:
            for j, sample in enumerate(sampleBackground.samples):
                if sample.runThisSample:
                    target = self.gudrunFile.sampleBackgrounds[i].samples[j]
                    target.topHatW = self.topHatWidths[j]

    def collectTopHatWidths(self):

        self.topHatWidths = []

        for sampleBackground in self.gudrunFile.sampleBackgrounds:
            for sample in sampleBackground.samples:
                self.topHatWidths.append(sample.topHatW)

    def setSelfScatteringFiles(self, scale):

        dataFileType = self.gudrunFile.instrument.dataFileType
        suffix = {1: "msubw01",3: "mint01"}[scale]

        iterator = enumerate(self.gudrunFile.sampleBackgrounds)

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
            self.gudrunFile.instrument.subWavelengthBinnedData = False
            self.collectTopHatWidths()
            self.collectQRange()
        else:
            self.gudrunFile.instrument.subWavelengthBinnedData = True
        self.applyWavelengthRanges()
        self.enableLogarithmicBinning()
        self.gudrunFile.instrument.scaleSelection = 3
        self.zeroTopHatWidths()
        self.setSelfScatteringFiles(3)
        self.gudrunFile.process()

    def QIteration(self, i):

        self.gudrunFile.instrument.subWavelengthBinnedData = True
        self.applyQRange()
        self.gudrunFile.instrument.scaleSelection = 1
        self.resetTopHatWidths()
        self.setSelfScatteringFiles(1)
        self.gudrunFile.process()

    def iterate(self, n):

        for i in range(n):

            self.wavelengthIteration(i)
            self.QIteration(i)
