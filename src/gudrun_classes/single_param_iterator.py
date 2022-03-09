from src.gudrun_classes.gud_file import GudFile
import os
import time


class SingleParamIterator():
    """
    Class to represent a Single Param Iterator.
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
    performIteration(_n)
        Performs a single iteration.
    applyCoefficientToAttribute(object, coefficient)
        To be overriden by sub-classes.
    iterate(n)
        Perform n iterations of iterating by tweak factor.
    """
    def __init__(self, gudrunFile):
        """
        Constructs all the necessary attributes for the
        SingleParamIterator object.

        Parameters
        ----------
        gudrunFile : GudrunFile
            Input GudrunFile that we will be using for iterating.
        """
        self.gudrunFile = gudrunFile

    def performIteration(self, _n):
        """
        Performs a single iteration of the current workflow.

        Parameters
        ----------
        _n : int
            Iteration number.
        """
        # Iterate through all samples that are being run,
        # applying the coefficient to the target parameter.
        for sampleBackground in self.gudrunFile.sampleBackgrounds:
            for sample in [
                s for s in sampleBackground.samples
                if s.runThisSample
            ]:
                gudPath = sample.dataFiles.dataFiles[0].replace(
                            self.gudrunFile.instrument.dataFileType,
                            "gud"
                        )
                gudFile = GudFile(
                    os.path.join(
                        self.gudrunFile.instrument.GudrunInputFileDir,
                        gudPath
                    )
                )
                # Calculate coefficient: actualDCSLevel / expectedDCSLevel
                coefficient = (
                    gudFile.averageLevelMergedDCS / gudFile.expectedDCS
                )
                # Apply the coefficient.
                self.applyCoefficientToAttribute(sample, coefficient)

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

    def iterate(self, n):
        """
        This method is the core of the SingleParamIterator.
        It performs n iterations of tweaking by a class-specific parameter.
        Namely, it performs gudrun_dcs n times, adjusting said parameter
        for each sample before each iteration, after the first one,
        using the results of the previous iteration to do so.

        Parameters
        ----------
        n : int
            Number of iterations to perform.
        """
        for i in range(n):
            self.gudrunFile.process()
            time.sleep(1)
            self.performIteration(i)
