
from logging import StringTemplateStyle
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

class TestParseGudrunFile(TestCase):

    def testEmptyPath(self):

        emptyPath = ''
        self.assertRaises(ValueError, GudrunFile, path=emptyPath)


    def testInvalidPath(self):

        invalidPath = 'invalid_path'
        self.assertRaises(ValueError, GudrunFile, path=invalidPath)

    def testInstrumentInitDataTypes(self):

        instrument = Instrument()

        self.assertIsInstance(instrument, Instrument)
        self.assertIsInstance(instrument.name, str)
        self.assertIsInstance(instrument.GudrunInputFileDir, str)
        self.assertIsInstance(instrument.dataFileDir, str)
        self.assertIsInstance(instrument.dataFileType, str)
        self.assertIsInstance(instrument.detectorCalibrationFileName, str)
        self.assertIsInstance(instrument.columnNoPhiVals, int)
        self.assertIsInstance(instrument.groupFileName, str)
        self.assertIsInstance(instrument.deadtimeConstantsFileName, str)
        self.assertIsInstance(instrument.spectrumNumbersForIncidentBeamMonitor, list)
        self.assertIsInstance(instrument.wavelengthRangeForMonitorNormalisation, tuple)
        self.assertIsInstance(instrument.spectrumNumbersForTransmissionMonitor, list)
        self.assertIsInstance(instrument.incidentMonitorQuietCountConst, float)
        self.assertIsInstance(instrument.transmissionMonitorQuietCountConst, float)
        self.assertIsInstance(instrument.channelNosSpikeAnalysis, tuple)
        self.assertIsInstance(instrument.spikeAnalysisAcceptanceFactor, int)
        self.assertIsInstance(instrument.wavelengthRangeForMonitorNormalisation, tuple)
        self.assertIsInstance(instrument.NoSmoothsOnMonitor, int)
        self.assertIsInstance(instrument.XScaleRangeStep, tuple)
        self.assertIsInstance(instrument.groupingParameterPanel, tuple)
        self.assertIsInstance(instrument.groupsAcceptanceFactor, float)
        self.assertIsInstance(instrument.mergePower, int)
        self.assertIsInstance(instrument.subSingleAtomScattering, bool)
        self.assertIsInstance(instrument.byChannel, int)
        self.assertIsInstance(instrument.incidentFlightPath, float)
        self.assertIsInstance(instrument.spectrumNumberForOutputDiagnosticFiles, int)
        self.assertIsInstance(instrument.neutronScatteringParametersFile, str)
        self.assertIsInstance(instrument.scaleSelection, int)
        self.assertIsInstance(instrument.subWavelengthBinnedData, bool)
        self.assertIsInstance(instrument.GudrunStartFolder, str)
        self.assertIsInstance(instrument.startupFileFolder, str)
        self.assertIsInstance(instrument.logarithmicStepSize, float)
        self.assertIsInstance(instrument.hardGroupEdges, bool)
        self.assertIsInstance(instrument.numberIterations, int)
        self.assertIsInstance(instrument.tweakTweakFactors, bool) 
   
    def testBeamInitDataTypes(self):

        beam = Beam()
        
        self.assertIsInstance(beam, Beam)
        self.assertIsInstance(beam.sampleGeometry, str)
        self.assertIsInstance(beam.noBeamProfileValues, int)
        self.assertIsInstance(beam.beamProfileValues, list)
        self.assertIsInstance(beam.stepSizeAbsorptionMSNoSlices, tuple)
        self.assertIsInstance(beam.incidentBeamEdgesRelCentroid, tuple)
        self.assertIsInstance(beam.scatteredBeamEdgesRelCentroid, tuple)
        self.assertIsInstance(beam.filenameIncidentBeamSpectrumParams, str)
        self.assertIsInstance(beam.overallBackgroundFactor, float)
        self.assertIsInstance(beam.sampleDependantBackgroundFactor, float)
        self.assertIsInstance(beam.shieldingAttenuationCoefficient, float)

    def testNormalisationInitDataTypes(self):

        normalisation = Normalisation()

        self.assertIsInstance(normalisation, Normalisation)
        self.assertIsInstance(normalisation.numberOfFilesPeriodNumber, tuple)
        self.assertIsInstance(normalisation.dataFiles, DataFiles)
        self.assertIsInstance(normalisation.numberOfFilesPeriodNumberBg, tuple)
        self.assertIsInstance(normalisation.dataFilesBg, DataFiles)
        self.assertIsInstance(normalisation.forceCalculationOfCorrections, bool)
        self.assertIsInstance(normalisation.composition, Composition)
        self.assertIsInstance(normalisation.geometry, str)
        self.assertIsInstance(normalisation.thickness, tuple)
        self.assertIsInstance(normalisation.angleOfRotationSampleWidth, tuple)
        self.assertIsInstance(normalisation.densityOfAtoms, float)
        self.assertIsInstance(normalisation.tempForNormalisationPC, int)
        self.assertIsInstance(normalisation.totalCrossSectionSource, str)
        self.assertIsInstance(normalisation.normalisationDifferentialCrossSectionFilename, str)
        self.assertIsInstance(normalisation.lowerLimitSmoothedNormalisation, float)
        self.assertIsInstance(normalisation.normalisationDegreeSmoothing, float)
        self.assertIsInstance(normalisation.minNormalisationSignalBR, float)

    def testSampleBackgroundDataTypes(self):

        sampleBackground = SampleBackground()

        self.assertIsInstance(sampleBackground, SampleBackground)
        self.assertIsInstance(sampleBackground.numberOfFilesPeriodNumber, tuple)
        self.assertIsInstance(sampleBackground.dataFiles, DataFiles)
        self.assertIsInstance(sampleBackground.samples, list)   

    def testSampleDataTypes(self):

        sample = Sample()

        self.assertIsInstance(sample, Sample)
        self.assertIsInstance(sample.name, str)
        self.assertIsInstance(sample.numberOfFilesPeriodNumber, tuple)
        self.assertIsInstance(sample.dataFiles, DataFiles)
        self.assertIsInstance(sample.forceCalculationOfCorrections, bool)
        self.assertIsInstance(sample.composition, Composition)
        self.assertIsInstance(sample.geometry, str)
        self.assertIsInstance(sample.thickness, tuple)
        self.assertIsInstance(sample.angleOfRotationSampleWidth, tuple)
        self.assertIsInstance(sample.densityOfAtoms, float)
        self.assertIsInstance(sample.tempForNormalisationPC, int)
        self.assertIsInstance(sample.totalCrossSectionSource, str)
        self.assertIsInstance(sample.sampleTweakFactor, float)
        self.assertIsInstance(sample.topHatW, float)
        self.assertIsInstance(sample.minRadFT, float)
        

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

    suite.addTest(TestUtils('testExtractIntsFromString'))
    suite.addTest(TestUtils('testExtractIntsFromString1'))
    suite.addTest(TestUtils('testExtractIntsFromBadString'))

    suite.addTest(TestUtils('testExtractFloatsFromString'))
    suite.addTest(TestUtils('testExtractFloatsFromString1'))
    suite.addTest(TestUtils('testExtractFloatsFromBadString'))

    suite.addTest(TestUtils('testCountOccurencesList'))
    suite.addTest(TestUtils('testCountOccurencesTuple'))

    suite.addTest(TestUtils('testIterIsTypeStr'))
    suite.addTest(TestUtils('testIterIsTypeInt'))
    suite.addTest(TestUtils('testIterIsTypeMixed'))

    suite.addTest(TestParseGudrunFile('testEmptyPath'))
    suite.addTest(TestParseGudrunFile('testInvalidPath'))

    suite.addTest(TestParseGudrunFile('testInstrumentInitDataTypes'))
    suite.addTest(TestParseGudrunFile('testBeamInitDataTypes'))
    suite.addTest(TestParseGudrunFile('testNormalisationInitDataTypes'))
    suite.addTest(TestParseGudrunFile('testSampleBackgroundDataTypes'))



    suite.addTest(TestParseGudFile('testEmptyPath'))
    suite.addTest(TestParseGudFile('testInvalidFileType'))
    suite.addTest(TestParseGudFile('testInvalidPath'))


    return suite


if __name__ == '__main__':

    testRunner = TextTestRunner(failfast=True, verbosity=3)
    testRunner.run(suite())
