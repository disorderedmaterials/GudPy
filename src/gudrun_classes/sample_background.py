from src.gudrun_classes import pathmagic  # noqa: F401
from src.scripts.utils import spacify
from src.gudrun_classes.data_files import DataFiles


class SampleBackground:
    """
    Class to represent a SampleBackground.

    ...

    Attributes
    ----------
    numberOfFilesPeriodNumber : tuple(int, int)
        Number of data files and their period number.
    dataFiles : DataFiles
        DataFiles object storing data files belonging to the container.
    samples : Sample[]
        List of Sample objects against the SampleBackground.
    Methods
    -------
    """
    def __init__(self):
        """
        Constructs all the necessary attributes for the
        SampleBackground object.

        Parameters
        ----------
        None
        """
        self.numberOfFilesPeriodNumber = (0, 0)
        self.dataFiles = DataFiles([], "SAMPLE BACKGROUND")
        self.samples = []

    def __str__(self):
        """
        Returns the string representation of the SampleBackground object.

        Parameters
        ----------
        None

        Returns
        -------
        string : str
            String representation of SampleBackground.
        """
        TAB = "          "
        SAMPLES = "\n".join([str(x) for x in self.samples if x.runThisSample])

        dataFilesLine = (
            f'{str(self.dataFiles)}\n'
            if len(self.dataFiles.dataFiles) > 0
            else
            ''
        )

        return (
            f'SAMPLE BACKGROUND{TAB}{{\n\n'
            f'{spacify(self.numberOfFilesPeriodNumber)}{TAB}'
            f'Number of files and period number\n'
            f'{dataFilesLine}\n'
            f'}}\n'
            f'{SAMPLES}'

        )
