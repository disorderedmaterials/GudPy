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
    yamlignore : str{}
        Class attributes to ignore during yaml serialisation.

    Methods
    -------
    eq(obj)
        Checks for equality between elements.
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
        self.massNo = int(massNo) if massNo % 1 == 0 else massNo
        self.abundance = abundance

        self.yamlignore = {
            "yamlignore"
        }

    def __str__(self):
        """
        Returns the string representation of the Element object.

        Returns
        -------
        string : str
            String representation of Element.
        """
        return (
            self.atomicSymbol
            + "  "
            + str(self.massNo)
            + "  "
            + str(self.abundance)
        )

    def __repr__(self):
        """
        Returns the string representation of the Element object.

        Returns
        -------
        string : str
            String representation of Element.
        """
        return str(self)

    def eq(self, obj):
        """
        Checks for equality between `obj` and the current object.

        Parameters
        ----------
        obj : Element
            Object to compare against.

        Returns
        -------
        bool : self == obj
        """
        if (
            hasattr(obj, 'atomicSymbol')
            and hasattr(obj, 'massNo')
            and hasattr(obj, 'abundance')
        ):
            return (
                self.atomicSymbol == obj.atomicSymbol
                and self.massNo == obj.massNo
                and self.abundance == obj.abundance
            )
