from core.single_param_iterator import SingleParamIterator


class ThicknessIterator(SingleParamIterator):
    """
    Class to represent a Thickness Iterator. Inherits SingleParamIterator.
    This class is used for iteratively tweaking the thickness of a
    flatplate sample.
    This means running gudrun_dcs iteratively, and adjusting the thickness
    of each sample across iterations. The new thickness is determined by
    applying a coefficient calculated from the results of gudrun_dcs in the
    previous iteration.
    ...

    Methods
    ----------
    applyCoefficientToAttribute
        Multiplies a sample's thicknesses by a given coefficient.
    organiseOutput
        Organises the output of the iteration.
    """
    def applyCoefficientToAttribute(self, object, coefficient):
        # Determine a new total thickness.
        totalThickness = object.upstreamThickness + object.downstreamThickness
        totalThickness *= coefficient
        # Assign the new thicknesses.
        object.downstreamThickness = totalThickness / 2
        object.upstreamThickness = totalThickness / 2

    def organiseOutput(self, n):
        self.gudrunFile.iterativeOrganise(f"IterateByThickness_{n}")