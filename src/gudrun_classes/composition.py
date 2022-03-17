from src.gudrun_classes.element import Element
from src.gudrun_classes.isotopes import Sears91
from src.gudrun_classes.exception import ChemicalFormulaParserException
from src.gudrun_classes.mass_data import massData
import re
import math


class ChemicalFormulaParser():

    def __init__(self):
        self.stream = None
        self.regex = re.compile(r"[A-Z][a-z]?(\[\d+\])?\d*")
        self.sears91 = Sears91()

    def consumeTokens(self, n):
        for _ in range(n):
            if self.stream:
                self.stream.pop(0)

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
        massNo = self.parseMassNo()
        abundance = self.parseAbundance()
        if symbol == "D":
            symbol = "H"
            massNo = 2.0
        if symbol in massData.keys():
            if (
                not self.sears91.isotopes(symbol)
                or self.sears91.isIsotope(symbol, massNo)
            ):
                return Element(symbol, massNo, abundance)
            else:
                validIsotopes = "\n  -    ".join(
                    [
                        f"{self.sears91.isotope(isotope)}"
                        f", {symbol}[{self.sears91.mass(isotope)}]"
                        for isotope in self.sears91.isotopes(symbol)
                    ]
                )
                raise ChemicalFormulaParserException(
                    f"{symbol}_{massNo} is not a valid isotope of {symbol}\n."
                    f" The following are valid:\n  -    {validIsotopes}"
                )

    def parseSymbol(self):
        if self.stream:
            match = re.match(r"[A-Z][a-z]|[A-Z]", "".join(self.stream))
            if match:
                self.consumeTokens(len(match.group(0)))
                return match.group(0)

    def parseMassNo(self):
        if self.stream:
            match = re.match(r"\[\d+\]", "".join(self.stream))
            if match:
                self.consumeTokens(len(match.group(0)))
                return int("".join(match.group(0)[1:-1]))
        return 0

    def parseAbundance(self):
        if self.stream:
            match = re.match(r"\d+\.\d+|\d+", "".join(self.stream))
            if match:
                self.consumeTokens(len(match.group(0)))
                return float(match.group(0))
        return 1.0


class Component():

    def __init__(self, name):
        self.elements = []
        self.name = name
        self.parser = ChemicalFormulaParser()

    def addElement(self, element):
        self.elements.append(element)

    def parse(self, persistent=True):
        elements = self.parser.parse(self.name)
        if elements and persistent:
            self.elements = elements
        elif elements and not persistent:
            return elements

    def __str__(self):
        if not self.elements:
            return f"{self.name}\n{{\n}}"
        elements = "\n".join([str(x) for x in self.elements])
        return f"{self.name}\n(\n{elements}\n)"

    def eq(self, obj):
        return all(
            [
                e.eq(el) for e, el in zip(self.elements, obj.elements)
            ]
         ) and self.name == obj.name


class Components():

    def __init__(self):
        self.components = []

    def addComponent(self, component):
        self.components.append(component)

    def __str__(self):
        return "\n".join(
            [str(x) for x in self.components]
        )


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

    def eq(self, obj):
        if hasattr(obj, "component") and hasattr(obj, "ratio"):
            return self.component == obj.component and self.ratio == obj.ratio


class Composition():

    def __init__(self, type_, elements=None):
        self.type_ = type_
        if not elements:
            self.elements = []
        else:
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

    def shallowTranslate(self):
        elements = []
        for component in self.weightedComponents:
            elements.extend(component.translate())
        self.sumAndMutate(elements, elements)
        return elements

    def translate(self):
        """
        Translates the weighted components present in the composition,
        into a relative composition of elements.
        """
        elements = []
        self.elements = []
        for component in self.weightedComponents:
            elements.extend(component.translate())
        self.sumAndMutate(elements, self.elements)

    @staticmethod
    def sumAndMutate(elements, target):
        """
        Sums the abundances of elements within the composition.
        This ensures that the same element isn't written out
        multiple times.
        """
        for element in elements:
            exists = False
            for element_ in target:
                if (
                    element.atomicSymbol == element_.atomicSymbol
                    and element.massNo == element_.massNo
                ):
                    element_.abundance += element.abundance
                    exists = True
            if not exists:
                target.append(element)

    def __str__(self):
        string = ""
        for el in self.elements:
            string += (
                str(el) + "        "
                "Composition\n"
            )

        return string.rstrip()

    @staticmethod
    def calculateExpectedDCSLevel(elements):
        totalAbundance = sum([el.abundance for el in elements])
        s91 = Sears91()
        if len(elements):
            return round(sum(
                [
                    s91.totalXS(
                        s91.isotopeData(
                            el.atomicSymbol, el.massNo
                        )
                    ) * (el.abundance/totalAbundance) for el in elements
                ]
            ) / 4.0 / math.pi, 5)
        return 0.0
