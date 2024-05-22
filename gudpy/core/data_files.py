import os

from core import config
from core import utils
from core.gud_file import GudFile


class DataFile:
    def __init__(self, filename, isSampleDataFile: bool = False):
        self.filename = filename
        self.name = utils.replace_unwanted_chars(
            os.path.splitext(filename)[0]
        )
        self.ext = os.path.splitext(filename)[1]
        self.outputFolder = ""
        self._outputs = {}
        self.isSampleDataFile = isSampleDataFile

        self.yamlignore = {
            "str",
            "yamlignore"
        }

    def addOutput(self, path):
        ext = os.path.splitext(path)[1]
        self._outputs[ext] = path

    def outputs(self, ext):
        return self._outputs[ext]

    def __str__(self):
        return self.filename

    @property
    def gudFile(self):
        if not self.isSampleDataFile:
            return None
        gudPath = self._outputs.get(".gud", None)
        if not gudPath:
            return None
        return GudFile(gudPath)

    @property
    def mintFile(self):
        if not self.isSampleDataFile:
            return None
        return self._outputs.get(".mint01", None)

    @property
    def msubwFile(self):
        if not self.isSampleDataFile:
            return None
        return self._outputs.get(".msubw01", None)


class DataFiles:
    """
    Class to represent a set of data files belonging to an object.

    ...

    Attributes
    ----------
    dataFiles : list
        List of filenames belonging to the object.
    name : str
        Name of the parent of the data files, e.g. Sample Background
    Methods
    -------
    """

    def __init__(self, dataFiles, name, isSampleDataFile=False):
        """
        Constructs all the necessary attributes for the DataFiles object.

        Parameters
        ----------
        dataFiles : list
            List of filenames belonging to the object.
        name : str
            Name of the parent of the data files, e.g. Sample Background
        """

        self._dataFiles: DataFile = []
        self.isSampleDataFile = isSampleDataFile
        self.setFiles(dataFiles)

        self.name = name

        self.yamlignore = {
            "str",
            "yamlignore"
        }

        self.outputFolders = {}
        self._outputs = {}

    def setFiles(self, dataFilenames):
        self._dataFiles.clear()
        for dataFile in dataFilenames:
            if not dataFile:
                continue
            self._dataFiles.append(DataFile(dataFile, self.isSampleDataFile))

    def __str__(self):
        """
        Returns the string representation of the DataFiles object.

        Parameters
        ----------
        None

        Returns
        -------
        string : str
            String representation of DataFiles.
        """
        self.str = [
            df.filename + config.spc10 + self.name + " data files"
            for df in self._dataFiles
        ]
        return """\n""".join(self.str)

    @property
    def dataFilenames(self):
        dfNames = [df.filename for df in self._dataFiles]
        return dfNames

    @property
    def dataFiles(self):
        return self._dataFiles

    def __len__(self):
        """
        Returns the length of the dataFiles list member.

        Parameters
        ----------
        None

        Returns
        -------
        int
            Number of data files,
        """
        return len(self._dataFiles)

    def __getitem__(self, n):
        return self._dataFiles[n]

    def __setitem__(self, n, item):
        if n >= len(self):
            self._dataFiles.extend(n+1)
        self._dataFiles[n] = DataFile(item)

    def __iter__(self):
        return iter(self._dataFiles)
