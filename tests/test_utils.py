
import sys, os
import unittest
from unittest.result import failfast
from unittest.suite import TestSuite
from unittest import TestCase, TextTestRunner
sys.path.insert(1, os.path.join(sys.path[0], '../gudrun_classes'))
sys.path.insert(2, os.path.join(sys.path[0], '../scripts'))

try:
    from utils import *
except ModuleNotFoundError:
    sys.path.insert(2, os.path.join(sys.path[0], 'scripts'))  
    from scripts.utils import *


class TestUtils(TestCase):

    def testNumifyBoolFalse(self):

        self.assertEqual(numifyBool(False), 0)
    
    def testNumifyBoolTrue(self):

        self.assertEqual(numifyBool(True), 1)

    def testNumifyBoolBad(self):

        self.assertEqual(numifyBool(None), 0)

    def testBoolifyNum0(self):

        self.assertEqual(boolifyNum(0), False)

    def testBoolifyNum1(self):

        self.assertEqual(boolifyNum(1), True)

    def testBoolifyNumBad(self):

        self.assertRaises(ValueError, boolifyNum, 2)

    def testSpacifyNonStr(self):

        self.assertEqual(spacify([1,2,3]), "1 2 3")

    def testSpacifyStrs(self):

        self.assertEqual(spacify(["1", "2", "3"]), "1 2 3")

    def testSpacifyTuple(self):

        self.assertEqual(spacify((1,2,3)), "1 2 3")

    def testFirstwordLong(self):

        self.assertEqual(firstword("Today is a good day!\n Today is a really good day!"), "Today")

    def testFirstwordShort(self):

        self.assertEqual(firstword("Hello"), "Hello")

    def testFirstWordEmpty(self):

        self.assertEqual(firstword(""), "")

    def testExtractIntsFromString(self):

        self.assertEqual(extract_ints_from_string("1 2 3 4 Hello\n"), [1,2,3,4])

    def testExtractIntsFromString1(self):

        self.assertEqual(extract_ints_from_string("1 2 3 4 Hello 5 6 7 8"), [1,2,3,4])

    def testExtractIntsFromBadString(self):

        self.assertEqual(extract_ints_from_string("No integers here!\n"), [])

    def testExtractFloatsFromString(self):

        self.assertEqual(extract_floats_from_string("1.0 2.0 3.0 4.0 Hello\n"), [1.0,2.0,3.0,4.0])

    def testExtractFloatsFromString1(self):

        self.assertEqual(extract_floats_from_string("1.0 2.0 3.0 4.0 Hello 5.0 6.0 7.0 8.0"), [1.0,2.0,3.0,4.0])

    def testExtractFloatsFromBadString(self):

        self.assertEqual(extract_floats_from_string("No floats here!\n"), [])

    def testCountOccurencesList(self):
    
        self.assertEqual(count_occurrences("Hello", ["Hello world", "Hello there", "Hi world", "Hello", "Hi there"]), 3)

    def testCountOccurencesTuple(self):

        self.assertEqual(count_occurrences("Hello", ("Hello world", "Hello there", "Hi world", "Hello", "Hi there")), 3)

    def testIterIsTypeStr(self):

        self.assertTrue(iteristype(["1", "2", "3"], str))
        self.assertFalse(iteristype(["1", "2", "3"], int))

    def testIterIsTypeInt(self):

        self.assertTrue(iteristype([1,2,3], int))
        self.assertFalse(iteristype(["1", "2", "3"], int))

    def testIterIsTypeMixed(self):

        self.assertFalse(iteristype([None, 1, TestCase()], TestCase))
        self.assertFalse(iteristype([None, 1, TestCase()], int))