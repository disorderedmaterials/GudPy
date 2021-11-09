from src.gudrun_classes.composition import Component
from unittest import TestCase


class TestChemicalParser(TestCase):

    def testValidParse(self):

        formula = "H2O"
        component = Component(formula)
        component.parse()

        self.assertEqual(len(component.elements), 2)

        self.assertEqual(component.elements[0].atomicSymbol, "H")
        self.assertEqual(component.elements[0].massNo, 0)
        self.assertEqual(component.elements[0].abundance, 2.0)

        self.assertEqual(component.elements[1].atomicSymbol, "O")
        self.assertEqual(component.elements[1].massNo, 0)
        self.assertEqual(component.elements[1].abundance, 1.0)

    def testInvalidParse(self):

        formula = "h2o"
        component = Component(formula)
        component.parse()

        self.assertEqual(len(component.elements), 0)

    def testD2OParse(self):

        formula = "D2O"
        component = Component(formula)
        component.parse()

        self.assertEqual(len(component.elements), 2)

        self.assertEqual(component.elements[0].atomicSymbol, "H")
        self.assertEqual(component.elements[0].massNo, 2)
        self.assertEqual(component.elements[0].abundance, 2.0)

        self.assertEqual(component.elements[1].atomicSymbol, "O")
        self.assertEqual(component.elements[1].massNo, 0)
        self.assertEqual(component.elements[1].abundance, 1.0)

    def testHardParse(self):

        formula = "H2ONaCl9D2OK"
        component = Component(formula)
        component.parse()

        self.assertEqual(len(component.elements), 7)

        self.assertEqual(component.elements[0].atomicSymbol, "H")
        self.assertEqual(component.elements[0].massNo, 0)
        self.assertEqual(component.elements[0].abundance, 2.0)

        self.assertEqual(component.elements[1].atomicSymbol, "O")
        self.assertEqual(component.elements[1].massNo, 0)
        self.assertEqual(component.elements[1].abundance, 1.0)

        self.assertEqual(component.elements[2].atomicSymbol, "Na")
        self.assertEqual(component.elements[2].massNo, 0)
        self.assertEqual(component.elements[2].abundance, 1.0)

        self.assertEqual(component.elements[3].atomicSymbol, "Cl")
        self.assertEqual(component.elements[3].massNo, 0)
        self.assertEqual(component.elements[3].abundance, 9.0)

        self.assertEqual(component.elements[4].atomicSymbol, "H")
        self.assertEqual(component.elements[4].massNo, 0)
        self.assertEqual(component.elements[4].abundance, 2.0)

        self.assertEqual(component.elements[5].atomicSymbol, "O")
        self.assertEqual(component.elements[5].massNo, 0)
        self.assertEqual(component.elements[5].abundance, 1.0)

        self.assertEqual(component.elements[6].atomicSymbol, "K")
        self.assertEqual(component.elements[6].massNo, 0)
        self.assertEqual(component.elements[6].abundance, 1.0)

    def testParseDecimalAbundance(self):

        formula = "H1.0K1.0Ar33.0Au26.5"
        component = Component(formula)
        component.parse()

        self.assertEqual(len(component.elements), 4)

        self.assertEqual(component.elements[0].atomicSymbol, "H")
        self.assertEqual(component.elements[0].massNo, 0)
        self.assertEqual(component.elements[0].abundance, 1.0)

        self.assertEqual(component.elements[1].atomicSymbol, "K")
        self.assertEqual(component.elements[1].massNo, 0)
        self.assertEqual(component.elements[1].abundance, 1.0)

        self.assertEqual(component.elements[2].atomicSymbol, "Ar")
        self.assertEqual(component.elements[2].massNo, 0)
        self.assertEqual(component.elements[2].abundance, 33.0)

        self.assertEqual(component.elements[3].atomicSymbol, "Au")
        self.assertEqual(component.elements[3].massNo, 0)
        self.assertEqual(component.elements[3].abundance, 26.5)

    def testInvalidParse2(self):

        formula = "H2O1./"

        component = Component(formula)
        component.parse()

        self.assertEqual(len(component.elements), 0)
