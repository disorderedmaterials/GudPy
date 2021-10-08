from src.gudrun_classes.gud_file import GudFile


class TweakFactorIterator():
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
    iterate(n)
        Perform n iterations of iterating by tweak factor.
    """
    def __init__(self, gudrunFile):
        """
        Constructs all the necessary attributes for the
        TweakFactorIterator object.

        Parameters
        ----------
        gudrunFile : GudrunFile
            Input GudrunFile that we will be using for iterating.
        """
        self.gudrunFile = gudrunFile

    def iterate(self, n):
        """
        This method is the core of the TweakFactorIterator.
        It performs n iterations of tweaking by the tweak factor.
        Namely, it performs gudurn_dcs n times, adjusting the tweak factor
        for each sample before each iteration, after the first one, to
        the suggested tweak factor outputted from the previous iteration
        of gudrun_dcs. gudrun_dcs outputs a .gud file, which we
        parse to extract the suggested tweak factor from.

        Parameters
        ----------
        n : int
            Number of iterations to perform.
        """
        # Perform n iterations of tweaking by tweak factor.
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
                                    self.gudrunFile.instrument.dataFileType,
                                    "gud"
                                )
                        gudFile = GudFile(gud)
                        tweakFactor = float(
                            gudFile.suggestedTweakFactor.strip()
                            )
                        sampleBackground_ = (
                            self.gudrunFile.sampleBackgrounds[j]
                        )
                        sampleBackground_.samples[k].sampleTweakFactor = (
                                                    tweakFactor
                        )
