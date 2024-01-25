from core.iterators.iterator import Iterator


class DensityIterator(Iterator):
    """
    Class to represent a Density Iterator. Inherits Iterator.
    This class is used for iteratively tweaking the density.
    This means running gudrun_dcs iteratively, and adjusting the density
    of each sample across iterations. The new density is determined by
    applying a coefficient calculated from the results of gudrun_dcs in the
    previous iteration.
    ...

    Methods
    ----------
    applyCoefficientToAttribute
        Multiplies a sample's density by a given coefficient.
    """
    name = "IterateByDensity"

    def applyCoefficientToAttribute(self, object, coefficient):
        """
        Multiplies a sample's density by a given coefficient.
        Overrides the implementation from the base class.

        Parameters
        ----------
        object : Sample
            Target object.
        coefficient : float
            Coefficient to use.
        """
        # Apply the coefficient to the density.
        object.density *= coefficient
