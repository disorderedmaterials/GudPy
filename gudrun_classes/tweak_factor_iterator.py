try:
    from gud_file import GudFile
except ModuleNotFoundError:
    from gudrun_classes.gud_file import GudFile


class TweakFactorIterator():

    def __init__(self, gudrunFile):

        self.gudrunFile = gudrunFile

    def iterate(self, n):

        for i in range(n):

            # Write out what we currently have,
            # and run gudrun_dcs on that file.
            self.gudrunFile.process()

            # Iterate through all samples,
            # updating their tweak factor from the output of gudrun_dcs.
            iterator = enumerate(self.gudrunFile.sampleBackgrounds)
            for j, sampleBackground in iterator:
                for k, sample in enumerate(sampleBackground.samples):
                    if sample.runThisSample:
                        gud = sample.dataFiles.dataFiles[0].replace(
                                    self.instrument.dataFileType,
                                    "gud"
                                )
                        gudFile = GudFile(gud)
                        tweakFactor = float(
                            gudFile.suggestedTweakFactor.strip()
                            )
                        targSampleBackground = self.sampleBackgrounds[j]
                        targSampleBackground.samples[k].sampleTweakFactor = (
                                                    tweakFactor
                        )
