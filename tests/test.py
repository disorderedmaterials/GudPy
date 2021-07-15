
from logging import FATAL
import sys, os
from unittest.result import failfast
from unittest.suite import TestSuite
from unittest import TestCase, TextTestRunner

sys.path.insert(1, os.path.join(sys.path[0], '../gudrun_classes'))
sys.path.insert(2, os.path.join(sys.path[0], '../scripts'))

from utils import *

from gudrun_file import GudrunFile
from gud_file import GudFile
from beam import Beam
from composition import Composition
from container import Container
from data_files import DataFiles
from element import Element
from instrument import Instrument
from normalisation import Normalisation
from sample_background import SampleBackground
from sample import Sample


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



class TestParseGudrunFile(TestCase):

    def testEmptyPath(self):

        emptyPath = ''
        self.assertRaises(ValueError, GudrunFile, path=emptyPath)


    def testInvalidPath(self):

        invalidPath = 'invalid_path'
        self.assertRaises(ValueError, GudrunFile, path=invalidPath)

class TestParseGudFile(TestCase):

    def testEmptyPath(self):

        emptyPath = ''
        self.assertRaises(ValueError, GudFile, emptyPath)
    
    def testInvalidFileType(self):

        invalid_file_type = 'NIMROD0001_H20_in_N9.txt'
        self.assertRaises(ValueError, GudFile, invalid_file_type)

    def testInvalidPath(self):

        invalid_path = 'invalid_path.gud'
        self.assertRaises(ValueError, GudFile, invalid_path)



def suite():

    suite = TestSuite()

    suite.addTest(TestUtils('testNumifyBoolFalse'))
    suite.addTest(TestUtils('testNumifyBoolTrue'))
    suite.addTest(TestUtils('testNumifyBoolBad'))
    
    suite.addTest(TestUtils('testBoolifyNum0'))
    suite.addTest(TestUtils('testBoolifyNum1'))
    suite.addTest(TestUtils('testBoolifyNumBad'))
    
    suite.addTest(TestUtils('testSpacifyNonStr'))
    suite.addTest(TestUtils('testSpacifyStrs'))
    suite.addTest(TestUtils('testSpacifyTuple'))

    suite.addTest(TestUtils('testFirstwordLong'))
    suite.addTest(TestUtils('testFirstwordShort'))
    suite.addTest(TestUtils('testFirstWordEmpty'))



    suite.addTest(TestParseGudrunFile('testEmptyPath'))
    suite.addTest(TestParseGudrunFile('testInvalidPath'))

    suite.addTest(TestParseGudFile('testEmptyPath'))
    suite.addTest(TestParseGudFile('testInvalidFileType'))
    suite.addTest(TestParseGudFile('testInvalidPath'))

    return suite


if __name__ == '__main__':

    testRunner = TextTestRunner(failfast=True, verbosity=2)
    testRunner.run(suite())
