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
    def __init__(self, dataFiles, name):
        """
        Constructs all the necessary attributes for the DataFiles object.

        Parameters
        ----------
        dataFiles : list
            List of filenames belonging to the object.
        name : str
            Name of the parent of the data files, e.g. Sample Background
        """
        self.dataFiles = dataFiles
        self.name = name
        self.str = [
            df + "        " + name + " data files"
            for df in dataFiles
            ]

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
        return """\n""".join(self.str)

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
        return len(self.dataFiles)
