import os
import time

from core.io.gud_file import GudFile
from core.iterators import SingleParamIterator


class TweakFactorIterator(SingleParamIterator):
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

    def __init__(self, gudrunFile):
        """
        Constructs all the necessary attributes for the
        TweakFactorIterator object.
        """

    name = "IterateByTweakFactor"

    def performIteration(self, _n):
        """
        Performs a single iteration of the current workflow.

        Parameters
        ----------
        _n : int
            Iteration number.
        """
        # Iterate through all samples,
        # updating their tweak factor from the output of gudrun_dcs.
        for sampleBackground in self.gudrunFile.sampleBackgrounds:
            for sample in [
                s for s in sampleBackground.samples
                if s.runThisSample and len(s.dataFiles)
            ]:
                gudPath = sample.dataFiles[0].replace(
                    self.gudrunFile.instrument.dataFileType,
                    "gud"
                )
                gudFile = GudFile(
                    os.path.join(
                        self.gudrunFile.instrument.GudrunInputFileDir,
                        gudPath
                    )
                )
                tweakFactor = float(gudFile.suggestedTweakFactor)
                sample.sampleTweakFactor = tweakFactor

    def iterate(self, n):
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
        # Perform n iterations of tweaking by tweak factor.
        for i in range(n):

            # Write out what we currently have,
            # and run gudrun_dcs on that file.
            self.gudrunFile.process(iterative=True)
            time.sleep(1)
            self.performIteration(i)
            self.organiseOutput(n, i)
