from src.gudrun_classes.element import Element


class Component():

    def __init__(self, name):
        self.elements = []
        self.name = name

    def addElement(self, element):
        self.elements.append(element)


class Components():

    def __init__(self):
        self.components = []

    def addComponent(self, component):
        self.components.append(component)


class WeightedComponent():

    def __init__(self, component, ratio):
        self.component = component
        self.ratio = ratio

    def translate(self):
        elements = []
        for element in self.component.elements:
            abundance = self.ratio * element.abundance
            elements.append(
                Element(
                    element.atomicSymbol, element.massNo, abundance
                )
            )
        return elements


class Composition():

    def __init__(self, type_):
        self.type_ = type_
        self.elements = []
        self.weightedComponents = []

    def addComponent(self, component, ratio):
        self.weightedComponents.append(
            WeightedComponent(component, ratio)
        )

    def addElement(self, element):
        self.elements.append(element)

    def addElements(self, elements):
        self.elements.extend(elements)

    def translate(self):
        elements = []
        self.elements = []
        for component in self.weightedComponents:
            elements.extend(component.translate())
        self.sumAndMutate(elements)

    def sumAndMutate(self, elements):
        for element in elements:
            exists = False
            for element_ in self.elements:
                if element.atomicSymbol == element_.atomicSymbol:
                    element_.abundance += element.abundance
                    exists = True
            if not exists:
                self.elements.append(element)

    def __str__(self):
        string = [
            str(c) + "        " + self.type_ + " atomic composition"
            for c in self.elements
        ]

        return "\n".join(string) if len(string) else ""
