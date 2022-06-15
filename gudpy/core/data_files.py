from core import config


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
    yamlignore : str{}
        Class attributes to ignore during yaml serialisation.   
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

        self.yamlignore = {
            "str",
            "yamlignore"
        }

    def __str__(self):
        """
        Returns the string representation of the DataFiles object.

        Returns
        -------
            str : String representation of DataFiles.
        """
        self.str = [
            df + config.spc5 + self.name + " data files"
            for df in self.dataFiles
            ]
        return """\n""".join(self.str)

    def __len__(self):
        """
        Returns the length of the dataFiles list member.

        Returns
        -------
            int : Number of data files,
        """
        return len(self.dataFiles)

    def __getitem__(self, n):
        """
        Gets the dataFile at index `n`.

        Parameters
        ----------
        n : int
            Index to retrieve from.
        Returns
        -------
            str : selected data file.
        """
        return self.dataFiles[n]

    def __setitem__(self, n, item):
        """
        Sets the dataFile at index `n` to `item`.

        Parameters
        ----------
        n : int
            Index to set at.
        item : str
            Item to set value at index to.
        """
        if n >= len(self):
            self.dataFiles.extend(n+1)
        self.dataFiles[n] = item

    def __iter__(self):
        """
        Wrapper for iterating the internal list of data files.

        Returns
        -------
            Iterator : iterator on `dataFiles`.
        """
        return iter(self.dataFiles)
