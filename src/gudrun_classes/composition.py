from enum import Enum
from src.gudrun_classes.components import Components


class CompositionType(Enum):
    EXACT = 0
    RATIOD = 1


class Composition:
    """
    Class to represent an Atomic Composition.

    ...

    Attributes
    ----------
    composition : list
        List of Element/Component objects present in the composition.
    type_ : str
        Type of composition e.g. Sample.
    Methods
    -------
    """
    def __init__(self, composition, type_):
        """
        Constructs all the necessary attributes for the Composition object.

        Parameters
        ----------
        None
        """
        self.composition = composition
        self.type_ = type_

        # Create an auxilliary list for storing strings
        if isinstance(self.composition, Components):
            self.str = [
                str(c) + "        " + type_ + " atomic composition"
                for c in self.composition.components
            ]
        else:
            self.str = [
                str(c) + "        " + type_ + " atomic composition"
                for c in self.composition
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
        return "\n".join(self.str) if len(self.str) > 0 else ""
