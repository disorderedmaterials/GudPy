import os
import time

from core.gud_file import GudFile


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
        self.nCurrent = 0

    def performIteration(self):
        """
        Performs a single iteration of the current workflow.

        """
        # Iterate through all samples that are being run,
        # applying the coefficient to the target parameter.
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
        This should organises the output of the iteration.

        Parameters
        ----------
        nTotal : int
            Total number of requested iterations
        nCurrent : int
            Current iteration
        """
        self.gudrunFile.organiseOutputs(
            self.nCurrent, self.name)

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
        for _ in range(self.nTotal):
            self.gudrunFile.process()
            time.sleep(1)
            self.performIteration()
            self.organiseOutput()
