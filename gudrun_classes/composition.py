
class Composition:
    """
    Class to represent an Atomic Composition.

    ...

    Attributes
    ----------
    elements : list
        List of Element objects present in the composition.
    type_ : str
        Type of composition e.g. Sample.
    Methods
    -------
    """
    def __init__(self, elements, type_):
        """
        Constructs all the necessary attributes for the Composition object.

        Parameters
        ----------
        None
        """
        self.elements = elements
        self.type_ = type_

        # Create an auxilliary list for storing strings
        self.str = [
            str(el) + "        " + type_ + " atomic composition"
            for el in self.elements
        ]

    def __str__(self):
        """
        Returns the string representation of the Composition object.

        Parameters
        ----------
        None

        Returns
        -------
        string : str
            String representation of Composition.
        """
        return "\n".join(self.str)
