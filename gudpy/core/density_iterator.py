from core.single_param_iterator import SingleParamIterator


class DensityIterator(SingleParamIterator):
    """
    Class to represent a Density Iterator. Inherits SingleParamIterator.
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
    organiseOutput
        Organises the output of the iteration.
    """
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

    def organiseOutput(self, n):
        self.gudrunFile.iterativeOrganise(f"IterateByDensity_{n}")