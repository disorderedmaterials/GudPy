from src.gudrun_classes.single_param_iterator import SingleParamIterator


class RadiusIterator(SingleParamIterator):
    """
    Class to represent a Radius Iterator. Inherits SingleParamIterator.
    This class is used for iteratively tweaking the thickness of a
    flatplate sample.
    This means running gudrun_dcs iteratively, and adjusting the inner/outer
    radius of each sample across iterations.
    The new radii are determined by applying a coefficient calculated
    from the results of gudrun_dcs in the previous iteration.
    ...

    Methods
    ----------
    applyCoefficientToAttribute
        Multiplies a sample's inner/outer radii by a given coefficient.
    setTargetRadius
        Sets the target radius attribute.
    """
    def applyCoefficientToAttribute(self, object, coefficient):
        if self.targetRadius == "inner":
            object.innerRadius *= coefficient
        elif self.targetRadius == "outer":
            object.innerRadius *= coefficient

    def setTargetRadius(self, targetRadius):
        self.targetRadius = targetRadius