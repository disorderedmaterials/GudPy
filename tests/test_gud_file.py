
import sys, os
import unittest
from unittest.result import failfast
from unittest.suite import TestSuite
from unittest import TestCase, TextTestRunner

try:
    sys.path.insert(1, os.path.join(sys.path[0], '../gudrun_classes'))
    from gud_file import GudFile
except ModuleNotFoundError:
    sys.path.insert(1, os.path.join(sys.path[0], 'gudrun_classes'))
    from gudrun_classes.gud_file import GudFile



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

    @unittest.skip
    def testGudFileInitDataTypes(self):

        g = GudFile()
        self.assertIsInstance(g.path, str)
        self.assertIsInstance(g.name, str)
        self.assertIsInstance(g.title, str)
        self.assertIsInstance(g.author, str)
        self.assertIsInstance(g.stamp, str)
        self.assertIsInstance(g.densityAcm3, float)
        self.assertIsInstance(g.densityGcm3, float)
        self.assertIsInstance(g.averageLevelMergedDCS, float)
        self.assertIsInstance(g.averageScatteringLengthSquared, float)
        self.assertIsInstance(g.averageSquareOfScatteringLength, float)
        self.assertIsInstance(g.expectedDCS, float)
        self.assertIsInstance(g.coherentRatio, float)
        self.assertIsInstance(g.groups, list)
        self.assertIsInstance(g.groupsTable, str)
        self.assertIsInstance(g.noGroups, int)
        self.assertIsInstanceI(g.averageLevelMergedDCS, float)
        self.assertIsInstance(g.gradient, float)
        self.assertIsInstance(g.err, str)
        self.assertIsInstance(g.suggestedTweakFactor, float)
        self.assertIsInstance(g.contents, str)