from src.gudrun_classes.gud_file import GudFile
import os


class ThicknessIterator():
    """
    Class to represent a Thickness Iterator.
    This class is used for iteratively altering the thickness of the sample.
    This class is relevant to flatplate samples only.
    This means running gudrun_dcs iteratively,
    adjusting the thickness of each sample across iterations. The new
    thickness is calculated from the output of
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
        ThicknessIterator object.

        Parameters
        ----------
        gudrunFile : GudrunFile
            Input GudrunFile that we will be using for iterating.
        """
        self.gudrunFile = gudrunFile

    def performIteration(self, _n):
        # Iterate through all samples,
        # altering their thickness' from the output of gudrun_dcs.
        iterator = enumerate(self.gudrunFile.sampleBackgrounds)
        for j, sampleBackground in iterator:
            for k, sample in enumerate(sampleBackground.samples):
                if sample.runThisSample:
                    # print(f"Sample: {k} Iteration: {_n}, density before: {sample.density}")
                    gud = sample.dataFiles.dataFiles[0].replace(
                                self.gudrunFile.instrument.dataFileType,
                                "gud"
                            )
                    gudFile = GudFile(
                        os.path.join(
                            self.gudrunFile.instrument.GudrunInputFileDir, gud
                        )
                    )
                    expectedDCSLevel = float(
                        gudFile.expectedDCS
                    )
                    mergeLevel = float(
                        gudFile.averageLevelMergedDCS
                    )

                    # Calculate a coefficient, dcsLevel/mergeLevel
                    coefficient = expectedDCSLevel/mergeLevel
                    sampleBackground_ = (
                        self.gudrunFile.sampleBackgrounds[j]
                    )

                    # Apply the coefficient to the sample thickness.
                    sampleBackground_.samples[k].upstreamThickness*=coefficient
                    sampleBackground_.samples[k].downstreamThickness*=coefficient

    def iterate(self, n):
        """
        This method is the core of the ThicknessIterator.
        It performs n iterations of altering sample thickness'.
        Namely, it performs gudurn_dcs n times, adjusting the thickness
        for each sample before each iteration, after the first one, by
        applying a coefficient calculated by the previous output
        of gudrun_dcs. gudrun_dcs outputs a .gud file, which we
        parse to extract the merge level and expected DCS level from.

        Parameters
        ----------
        n : int
            Number of iterations to perform.
        """
        # Perform n iterations of adjusting the thickness.
        for i in range(n):

            # Write out what we currently have,
            # and run gudrun_dcs on that file.
            self.gudrunFile.process()
            self.performIteration(i)

