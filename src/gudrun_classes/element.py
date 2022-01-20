from src.gudrun_classes import config
class Element:
    """
    Class to represent an Element.

    ...

    Attributes
    ----------
    atomicSymbol : str
        The atomic symbol belonging to the element, e.g. H.
    massNo : int
        The atomic number belonging to the element (total number of nucleons).
    abundance : float
        Abundance of the element.
    Methods
    -------
    """
    def __init__(self, atomicSymbol, massNo, abundance):
        """
        Constructs all the necessary attributes for the DataFiles object.

        Parameters
        ----------
        atomicSymbol : str
            The atomic symbol belonging to the element, e.g. H.
        massNo : int
            The atomic number belonging to the element
            (total number of nucleons).
        abundance : float
            Abundance of the element.
        """
        self.atomicSymbol = atomicSymbol
        self.massNo = massNo
        self.abundance = abundance

    def __str__(self):
        """
        Returns the string representation of the Element object.

        Parameters
        ----------
        None

        Returns
        -------
        string : str
            String representation of Element.
        """
        return (
            self.atomicSymbol
            + config.spc2
            + str(self.massNo)
            + config.spc2
            + str(self.abundance)
        )

    def __repr__(self):
        """
        Returns the string representation of the Element object.

        Parameters
        ----------
        None

        Returns
        -------
        string : str
            String representation of Element.
        """
        return str(self)
