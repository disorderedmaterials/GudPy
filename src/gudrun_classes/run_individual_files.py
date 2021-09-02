from copy import deepcopy
from src.gudrun_classes.gudrun_file import GudrunFile
from src.gudrun_classes.purge_file import PurgeFile
from src.gudrun_classes.data_files import DataFiles


class RunIndividualFiles():
    """
    Class for running data files individually for samples.
    Writes out a new instance of a GudrunFile, with samples
    duplicated for each of their data files.

    ...

    Attributes
    ----------
    gudrunFile : GudrunFile
        GudrunFile to create new instance from, for running
        data files individually.
    Methods
    -------
    dcs(path=''):
        Call gudrun_dcs on the path supplied. If the path is its
        default value, then use the path attribute as the path.
        "Inherited" from GudrunFile.
    partition():
        Partitions the samples of the GudrunFile, for running
        data files individually.
    write_out_individually():
        Writes partitioned GudrunFile out to 'gudrun_dcs.dat'.
    purge():
        Create a PurgeFile from the GudrunFile, and run purge_det on it.
    process():
        Write out the GudrunFile with individual data files,
        and call gudrun_dcs on the outputted file.
    write_out(overwrite=False)
        Writes out the string representation of the GudrunFile to a file.
        Mildly-inherited from GudrunFile.
    """

    # Inherit dcs() from GudrunFile.
    dcs = GudrunFile.dcs

    def __init__(self, gudrunFile):
        """
        Constructs all the necessary attributes
        for the RunIndividualFiles object.

        Parameters
        ----------
        gudrunFile : GudrunFile
            Input GudrunFile that we will partition, and use.
        """
        self.gudrunFile = gudrunFile
        self.partition()

    def partition(self):
        """
        Partition the data files of each sample across multiple
        duplicates of that sample. For instance, if a sample
        has three corresponding data files, three versions of the sample
        will be created, one for each data file.

        Parameters
        ----------
        None
        Returns
        -------
        None
        """
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
            for j, sample in enumerate(samples):

                # Enumerate the datafiles belonging to the sample.
                for k, dataFile in enumerate(sample.dataFiles.dataFiles):

                    # deepcopy the current sample
                    childSample = deepcopy(sample)

                    # Only run one data file.
                    childSample.dataFiles = (
                        DataFiles([dataFile], childSample.name)
                    )

                    # Append sample
                    sampleBackgrounds[i].samples.append(childSample)
        # Update gudrunFile to use the newly constructed sample background.

        self.gudrunFile.sampleBackgrounds = sampleBackgrounds

    def write_out_individually(self):
        """
        Writes out the string representation of the partitioned GudrunFile
        to "gudrun_dcs.dat".

        Parameters
        ----------
        None
        Returns
        -------
        None
        """
        self.outpath = self.path = "gudrun_dcs.dat"
        self.write_out()

    def purge(self):
        """
        Create a PurgeFile from the GudrunFile,
        and then call Purge.purge() to purge the detectors.

        Parameters
        ----------
        None
        Returns
        -------
        subprocess.CompletedProcess
            The result of calling purge_det using subprocess.run.
            Can access stdout/stderr from this.
        """
        return PurgeFile(self.gudrunFile).purge()

    def process(self):
        """
        Write out the the partitioned GudrunFile, then
        purge detectors and then call gudrun_dcs on the file that
        was written out.

        Parameters
        ----------
        None
        Returns
        -------
        subprocess.CompletedProcess
            The result of calling gudrun_dcs using subprocess.run.
            Can access stdout/stderr from this.
        """
        self.write_out_individually()
        return self.dcs()

    def write_out(self):
        """
        Writes out the string representation of the GudrunFile.

        Parameters
        ----------
        None
        Returns
        -------
        None
        """
        f = open(self.path, "w", encoding="utf-8")
        f.write(str(self.gudrunFile))
        f.close()
