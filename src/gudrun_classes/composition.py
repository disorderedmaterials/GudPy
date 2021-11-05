from src.gudrun_classes.element import Element
from src.scripts.utils import isnumeric
import re
class ChemicalFormulaParser():

    def __init__(self):
        self.stream = None
        self.regex = re.compile("[A-Z][a-z]?\d*")

    def getNextToken(self):
        return self.stream.pop(0) if self.stream else None

    def peekNextToken(self):
        return self.stream[0] if self.stream else None

    def parse(self, stream):
        if not self.regex.match(stream):
            return None
        self.stream = list(stream)
        elements = []
        while self.stream:
            element = self.parseElement()
            if element:
                elements.append(element)
            else:
                return False
        return elements

    def parseElement(self):

        symbol = self.parseSymbol()
        abundance = self.parseAbundance()
        if symbol and abundance:
            return Element(symbol, 0, abundance)

    def parseSymbol(self):
        symbol = ""
        token = self.peekNextToken()
        if token:
            if token.isupper():
                symbol = self.getNextToken()
                if self.peekNextToken() and self.peekNextToken().islower():
                    symbol += self.getNextToken()
        return symbol

    def parseAbundance(self):
        abundance = 1
        token = self.peekNextToken()
        if token:
            if isnumeric(token):
                abundanceStr = self.getNextToken()
                while self.peekNextToken() and isnumeric(self.peekNextToken()):
                    token = self.getNextToken()
                    abundanceStr+=token
                abundance = int(abundanceStr)
        return abundance

class Component():

    def __init__(self, name):
        self.elements = []
        self.name = name
        self.parser = ChemicalFormulaParser()
        # self.nameChanged()

    def addElement(self, element):
        self.elements.append(element)

    def parse(self, persistent=True):
        elements = self.parser.parse(self.name)
        if elements and persistent:
            self.elements = elements
        elif elements and not persistent:
            return elements

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

    def __init__(self, type_, elements=[]):
        self.type_ = type_
        self.elements = elements
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
        """
        Translates the weighted components present in the composition,
        into a relative composition of elements.
        """
        elements = []
        self.elements = []
        for component in self.weightedComponents:
            elements.extend(component.translate())
        self.sumAndMutate(elements)

    def sumAndMutate(self, elements):
        """
        Sums the abundances of elements within the composition.
        This ensures that the same element isn't written out
        multiple times.
        """
        for element in elements:
            exists = False
            for element_ in self.elements:
                if element.atomicSymbol == element_.atomicSymbol:
                    element_.abundance += element.abundance
                    exists = True
            if not exists:
                self.elements.append(element)

    def __str__(self):
        string = ""
        for el in self.elements:
            string += (
                str(el) + "        " +
                self.type_ + " atomic composition\n"
            )

        return string.rstrip()
