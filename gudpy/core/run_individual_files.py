from copy import deepcopy

from core.data_files import DataFiles


class RunIndividualFiles():
    """
    Class for running data files individually for samples.

    ...

    Attributes
    ----------
    gudrunFile : GudrunFile
        GudrunFile to create new instance from, for running
        data files individually.
    Methods
    -------
    partition():
        Partitions the samples of the GudrunFile, for running
        data files individually.
    """

    def __init__(self, gudrunFile):
        self.gudrunFile = deepcopy(gudrunFile)
        self.partition()

    def partition(self):

        # Deepcopy the sample backgrounds.
        sampleBackgrounds = deepcopy(self.gudrunFile.sampleBackgrounds)
        # Clear the original list.
        self.gudrunFile.sampleBackgrounds = []

        # Enumerate through all sample backgrounds
        # and their samples.
        # For each sample, create a copy for each
        # data file, and add it to the corresponding
        # sample background.
        for i, sampleBackground in enumerate(sampleBackgrounds):

            # deepcopy the samples
            samples = deepcopy(sampleBackground.samples)
            sampleBackgrounds[i].samples = []

            # Enumerate samples.
            for sample in samples:
                if sample.runThisSample:
                    # Enumerate the datafiles belonging to the sample.
                    for dataFile in sample.dataFiles.dataFiles:

                        # deepcopy the current sample
                        childSample = deepcopy(sample)

                        # Only run one data file.
                        childSample.dataFiles = (
                            DataFiles([dataFile], childSample.name)
                        )
                        childSample.name = f"{childSample.name} [{dataFile}]"

                        # Append sample
                        sampleBackgrounds[i].samples.append(childSample)

        # Update gudrunFile to use the newly constructed sample background.
        self.gudrunFile.sampleBackgrounds = sampleBackgrounds
