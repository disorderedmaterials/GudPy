from src.gudrun_classes.single_param_iterator import SingleParamIterator

class ThicknessIterator(SingleParamIterator):

    def applyCoefficientToAttribute(self, object, coefficient):
        totalThickness = object.upstreamThickness + object.downstreamThickness
        totalThickness*=coefficient
        object.downstreamThickness = totalThickness / 2
        object.upstreamThickness = totalThickness / 2
