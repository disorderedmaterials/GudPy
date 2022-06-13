import re
import math

from core.element import Element
from core.isotopes import Sears91
from core.exception import ChemicalFormulaParserException
from core.mass_data import massData


class ChemicalFormulaParser():
    """
    Chemical formula parser. Uses regular expressions, and Sears91 data
    to parse chemical formulae.

    ...

    Attributes
    ----------
    stream : char[]
        Stream of chars to parse.
    regex : re.Pattern
        Regular expression pattern for chemical formulae.
    sears91 : Sears91
        Sears91 isotope data.

    Methods
    ----------
    consumeTokens(n)
        Consumes n tokens from the stream.
    parse(stream)
        Parses a chemical formula from the stream.
    parseElement()
        Parses an Element.
    parseSymbol()
        Parses an atomic symbol.
    parseMassNo()
        Parses a mass number.
    parseAbundance()
        Parses abundance.
    """

    def __init__(self):
        """
        Constructs all the necessary attributes for the ChemicalFormulaParser object.
        """
        self.stream = []
        self.regex = re.compile(r"[A-Z][a-z]?(\[\d+\])?\d*")
        self.sears91 = Sears91()

    def consumeTokens(self, n):
        """
        Consumes n tokens from the input stream.

        Parameters
        ----------
        n : int
            Number of tokens to consume.
        """
        for _ in range(n):
            if self.stream:
                self.stream.pop(0)

    def parse(self, stream):
        """
        Core method of the ChemicalFormulaParser.
        Parses a chemical formula from a given stream of text.

        Parameters
        ----------
        stream : str
            Input stream.
        
        Returns
        -------
        Element[]  | False : List of parsed Element objects, or False if failure.
        """
        # Check string is a chemical formula.
        if not self.regex.match(stream):
            return None

        # Split string into list of chars.
        self.stream = list(stream)
        elements = []

        while self.stream:
            # Parse an element.
            element = self.parseElement()
            # If element is valid, append it.
            # Otherwise, parsing has failed, so return Fale.
            if element:
                elements.append(element)
            else:
                return False
        return elements

    def parseElement(self):
        """
        Parses the next element from the stream.

        Returns
        -------
        Element | None : Parsed Element, if any.
        """

        # Parse symbol.
        symbol = self.parseSymbol()
        
        # Parse mass number.
        massNo = self.parseMassNo()

        # Parse abundance.
        abundance = self.parseAbundance()

        # Infer D as H[2].
        if symbol == "D":
            symbol = "H"
            massNo = 2.0
        
        # Check isotope is valid.
        if symbol in massData.keys():
            if (
                not self.sears91.isotopes(symbol)
                or self.sears91.isIsotope(symbol, massNo)
            ):
                # Construct and return Element object.
                return Element(symbol, massNo, abundance)
            else:
                # Isotope is invalid, raise exception.
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
        """
        Parses an atomic symbol.

        Returns
        -------
        str | None : atomic symbol parsed, if any.
        """
        if self.stream:
            # Use regular expression to extract atomic symbol.
            match = re.match(r"[A-Z][a-z]|[A-Z]", "".join(self.stream))
            if match:
                # Consume len(atomicSymbol) tokens from the stream.
                self.consumeTokens(len(match.group(0)))

                # Return atomicSymbol.
                return match.group(0)

    def parseMassNo(self):
        """
        Parses a mass number.

        Returns
        -------
        int : parsed mass number.
        """
        if self.stream:
            # Use regular expression to extract mass number.
            match = re.match(r"\[\d+\]", "".join(self.stream))
            if match:
                # Consume len(str(massNo)) tokens from the stream.
                self.consumeTokens(len(match.group(0)))
                # Cast to int and return mass number.
                return int("".join(match.group(0)[1:-1]))

        # If no mass number is supplied, then it is the natural istope.
        # So return 0.
        return 0

    def parseAbundance(self):
        """
        Parses an abundance.

        Returns
        -------
        float : parsed abundance.
        """
        if self.stream:
            # Use regular expression to extract abundance.
            match = re.match(r"\d+\.\d+|\d+", "".join(self.stream))
            if match:
                # Consume len(str(abundance)) tokens from the stream.
                self.consumeTokens(len(match.group(0)))
                # Cast to float and return abundance.
                return float(match.group(0))

        # If no abundance is supplied, then return 1.0.
        return 1.0


class Component():
    """
    Class to represent a component. This essentially maintains a composition, and can be named.

    ...

    Attributes
    ----------
    name : str
        Component name.
    elements : Element[]
        Composition.
    parser : ChemicalFormulaParser
        Parser to use for parsing chemical formulae.
    yamlignore : str{}
        Class attributes to ignore during yaml serialisation.        

    Methods
    -------
    addElement(element)
        Adds an element to the internal composition.
    parse(persistent=True)
        Parses chemical formula from `name`.
    eq(obj)
        Checks for equality between components.
    """

    def __init__(self, name="", elements=[]):
        """
        Constructs all the necessary attributes for the Component object.

        Parameters
        ----------
        name : str, optional
            Name to assign to component.
        elements : Element[]
            List of Element objects to assign to internal composition.
        """
        self.name = name
        self.elements = elements
        self.parser = ChemicalFormulaParser()

        self.yamlignore = {
            "parser",
            "yamlignore"
        }

    def addElement(self, element):
        """
        Adds an element to the internal composition.

        Parameters
        ----------
        element : Element
            Target Element object to append.
        """
        self.elements.append(element)

    def parse(self, persistent=True):
        """
        Parses chemical fromula from `name`.
        Optionally assign the parsed chemical formula to the internal composition.

        Parameters
        ----------
        persistent : bool, optional
            Should the parsed chemical formula persist in the object.
        
        Returns
        -------
        None | Element[] : If not persistent, list of parsed Elements.
        """
        # Parse elements from name.
        elements = self.parser.parse(self.name)
        
        # If persistent, assign elements.
        if elements and persistent:
            self.elements = elements
        # Otherwise return them.
        elif elements and not persistent:
            return elements

    def __str__(self):
        """
        Returns the string representation of the Component object.

        Returns
        -------
        str : String representation of Component.
        """
        if not self.elements:
            return f"{self.name}\n{{\n}}"
        elements = "\n".join([str(x) for x in self.elements])
        return f"{self.name}\n(\n{elements}\n)"

    def eq(self, obj):
        """
        Checks for equality between `obj` and the current object.

        Returns
        -------
        bool : self == obj
        """
        return all(
            [
                e.eq(el) for e, el in zip(self.elements, obj.elements)
            ]
         ) and self.name == obj.name


class Components():
    """
    Class to represent a set of components.

    ...

    Attributes
    ----------
    components : Component[]
        List of Components.
    yamlignore : str{}
        Class attributes to ignore during yaml serialisation.        

    Methods
    -------
    addComponent(element)
        Adds an Component to the components.
    count()
        Returns number of components.   
    """

    def __init__(self, components=[]):
        """
        Constructs all the necessary attributes for the Components object.

        Parameters
        ----------
        components : Component[], optional
            List of Component objects to assign to internal components.
        """
        self.components = components

        self.yamlignore = {
            "yamlignore"
        }

    def addComponent(self, component):
        """
        Adds a component to the internal components.

        Parameters
        ----------
        component : Component
            Target Component object to append.
        """
        self.components.append(component)

    def count(self):
        """
        Counts number of components.

        Returns
        -------
        int : number of components.
        """
        return len(self.components)

    def __str__(self):
        """
        Returns the string representation of the Components object.

        Returns
        -------
        str : String representation of Components.
        """
        return "\n".join(
            [str(x) for x in self.components]
        )


class WeightedComponent():
    """
    Class to represent a weighted component.
    This essentially maintains a composition, and can be named.
    However, this also has a weighting.

    ...

    Attributes
    ----------
    component : Component
        Component to be weighted.
    ratio : float
        Weighting of component.
    yamlignore : str{}
        Class attributes to ignore during yaml serialisation.        

    Methods
    -------
    translate()
        Applies ratio to component.
    eq(obj)
        Checks for equality between weighted components.
    """
    def __init__(self, component, ratio):
        """
        Constructs all the necessary attributes for the WeightedComponent object.

        Parameters
        ----------
        component : Component
            Component to be weighted.
        ratio : float
            Weighting of component.
        """
        self.component = component
        self.ratio = ratio
        self.yamlignore = {
            "yamlignore"
        }

    def translate(self):
        """
        Applies the ratio to the component.

        Returns
        -------
        Element[] : list of elements, with ratio applied.
        """
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
        """
        Checks for equality between `obj` and the current object.

        Returns
        -------
        bool : self == obj
        """
        if hasattr(obj, "component") and hasattr(obj, "ratio"):
            return self.component == obj.component and self.ratio == obj.ratio


class Composition():
    """
    Class to represent a Composition.
    This can be a collection of elements, or weighted components.

    ...

    Attributes
    ----------
    type_ : str
        Composition type.
    elements : Element[]
        List of elements that constitute composition.
    weightedComponents : WeightedComponent[]
        List of weighted components that constitute composition.
    yamlignore : str{}
        Class attributes to ignore during yaml serialisation.        

    Methods
    -------
    addComponent(element)
        Adds an Component to the components.
    addElement(element)
        Adds an element to the internal composition.
    addElements(elements)
        Adds elements to the internal composition.
    shallowTranslate()
        Performs a shallow translate of weighted components to elements.
    translate()
        Performs a deep translate of weighted components to elements.
    sumAndMutate(elements, target)
        Sums elements into target.
    calculateExpectedDCSLevel(elements)
        Calculates expected DCS level given a composition.
    """
    def __init__(self, type_, elements=None):
        """
        Constructs all the necessary attributes for the Composition object.

        Parameters
        ----------
        type_ : str
            Composition type.
        elements : Element[]
            List of Element objects to assign to internal composition.
        """
        self.type_ = type_
        if not elements:
            self.elements = []
        else:
            self.elements = elements
        self.weightedComponents = []

        self.yamlignore = {
            "yamlignore"
        }

    def addComponent(self, component, ratio):
        """
        Adds a weighted component to the internal components.

        Parameters
        ----------
        component : Component
            Target Component object to append.
        ratio : float
            Ratio to use for component.
        """
        self.weightedComponents.append(
            WeightedComponent(component, ratio)
        )

    def addElement(self, element):
        """
        Adds an element to the internal composition.

        Parameters
        ----------
        element : Element
            Target Element object to append.
        """
        self.elements.append(element)

    def addElements(self, elements):
        """
        Adds an element to the internal composition.

        Parameters
        ----------
        elements : Element[]
            Target Element objects to append.
        """
        self.elements.extend(elements)

    def shallowTranslate(self):
        """
        Performs a shallow translate of weighted components to elements.

        Returns
        -------
        Element[] : list of translated elements.
        """
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

        Parameters
        ----------
        elements : Element[]
            List of Elements.
        target : Element[]
            Target list of Elements to sum into.
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

    @staticmethod
    def calculateExpectedDCSLevel(elements):
        """
        Calculates expected DCS level given a composition.

        Parameters
        ----------
        elements : Element[]
            List of Elements that contsitute composition.
        

        Returns
        -------
        float : expected DCS level.
        """

        # Calculate total abundance.
        totalAbundance = sum([el.abundance for el in elements])
        s91 = Sears91()

        # If there are elements.
        if len(elements) and totalAbundance > 0.0:
            # Return average bound scattering cross section / 4.0 / pi
            return round(sum(
                [
                    s91.totalXS(
                        s91.isotopeData(
                            el.atomicSymbol, el.massNo
                        )
                    ) * (el.abundance/totalAbundance) for el in elements
                ]
            ) / 4.0 / math.pi, 5)

        # Otherwise return 0.0.
        return 0.0

    def __str__(self):
        """
        Returns the string representation of the Composition object.

        Returns
        -------
        str : String representation of Composition.
        """
        string = ""
        for el in self.elements:
            string += (
                str(el) + "        "
                "Composition\n"
            )

        return string.rstrip()