from src.gudrun_classes.single_param_iterator import SingleParamIterator

class DensityIterator(SingleParamIterator):

    def applyCoefficientToAttribute(self, object, coefficient):
        object.density*=coefficient
