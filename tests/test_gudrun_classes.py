from unittest import TestCase

from gudrun_file import GudrunFile
from beam import Beam
from composition import Composition
from container import Container
from data_files import DataFiles
from element import Element
from instrument import Instrument
from normalisation import Normalisation
from sample_background import SampleBackground
from sample import Sample
from enums import Scales, UnitsOfDensity, MergeWeights


class TestGudrunClasses(TestCase):

    def testEmptyPath(self):

        emptyPath = ""
        self.assertRaises(ValueError, GudrunFile, path=emptyPath)

    def testInvalidPath(self):

        invalidPath = "invalid_path"
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
        self.assertIsInstance(
            instrument.spectrumNumbersForIncidentBeamMonitor, list
        )
        self.assertIsInstance(
            instrument.wavelengthRangeForMonitorNormalisation, tuple
        )
        self.assertIsInstance(
            instrument.spectrumNumbersForTransmissionMonitor, list
        )
        self.assertIsInstance(instrument.incidentMonitorQuietCountConst, float)
        self.assertIsInstance(
            instrument.transmissionMonitorQuietCountConst, float
        )
        self.assertIsInstance(instrument.channelNosSpikeAnalysis, tuple)
        self.assertIsInstance(instrument.spikeAnalysisAcceptanceFactor, int)
        self.assertIsInstance(instrument.wavelengthMin, float)
        self.assertIsInstance(instrument.wavelengthMax, float)
        self.assertIsInstance(instrument.wavelengthStep, float)
        self.assertIsInstance(instrument.NoSmoothsOnMonitor, int)
        self.assertIsInstance(instrument.XMin, float)
        self.assertIsInstance(instrument.XMax, float)
        self.assertIsInstance(instrument.XStep, float)
        self.assertIsInstance(instrument.useLogarithmicBinning, bool)
        self.assertIsInstance(instrument.groupingParameterPanel, tuple)
        self.assertIsInstance(instrument.groupsAcceptanceFactor, float)
        self.assertIsInstance(instrument.mergePower, int)
        self.assertIsInstance(instrument.subSingleAtomScattering, bool)
        self.assertIsInstance(instrument.mergeWeights, MergeWeights)
        self.assertIsInstance(instrument.incidentFlightPath, float)
        self.assertIsInstance(
            instrument.spectrumNumberForOutputDiagnosticFiles, int
        )
        self.assertIsInstance(instrument.neutronScatteringParametersFile, str)
        self.assertIsInstance(instrument.scaleSelection, Scales)
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
        self.assertIsInstance(beam.stepSizeAbsorption, float)
        self.assertIsInstance(beam.stepSizeMS, float)
        self.assertIsInstance(beam.noSlices, int)
        self.assertIsInstance(beam.incidentBeamLeftEdge, float)
        self.assertIsInstance(beam.incidentBeamRightEdge, float)
        self.assertIsInstance(beam.incidentBeamTopEdge, float)
        self.assertIsInstance(beam.incidentBeamBottomEdge, float)
        self.assertIsInstance(beam.scatteredBeamLeftEdge, float)
        self.assertIsInstance(beam.scatteredBeamRightEdge, float)
        self.assertIsInstance(beam.scatteredBeamTopEdge, float)
        self.assertIsInstance(beam.scatteredBeamBottomEdge, float)
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
        self.assertIsInstance(
            normalisation.forceCalculationOfCorrections, bool
        )
        self.assertIsInstance(normalisation.composition, Composition)
        self.assertIsInstance(normalisation.geometry, str)
        self.assertIsInstance(normalisation.thickness, tuple)
        self.assertIsInstance(normalisation.angleOfRotationSampleWidth, tuple)
        self.assertIsInstance(normalisation.density, float)
        self.assertIsInstance(normalisation.densityUnits, UnitsOfDensity)
        self.assertIsInstance(normalisation.tempForNormalisationPC, int)
        self.assertIsInstance(normalisation.totalCrossSectionSource, str)
        self.assertIsInstance(
            normalisation.normalisationDifferentialCrossSectionFilename, str
        )
        self.assertIsInstance(
            normalisation.lowerLimitSmoothedNormalisation, float
        )
        self.assertIsInstance(
            normalisation.normalisationDegreeSmoothing, float
        )
        self.assertIsInstance(normalisation.minNormalisationSignalBR, float)

    def testSampleBackgroundInitDataTypes(self):

        sampleBackground = SampleBackground()

        self.assertIsInstance(sampleBackground, SampleBackground)
        self.assertIsInstance(
            sampleBackground.numberOfFilesPeriodNumber, tuple
        )
        self.assertIsInstance(sampleBackground.dataFiles, DataFiles)
        self.assertIsInstance(sampleBackground.samples, list)

    def testSampleInitDataTypes(self):

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
        self.assertIsInstance(sample.density, float)
        self.assertIsInstance(sample.densityUnits, UnitsOfDensity)
        self.assertIsInstance(sample.tempForNormalisationPC, int)
        self.assertIsInstance(sample.totalCrossSectionSource, str)
        self.assertIsInstance(sample.sampleTweakFactor, float)
        self.assertIsInstance(sample.topHatW, float)
        self.assertIsInstance(sample.minRadFT, float)

    def testContainerInitDataTypes(self):

        container = Container()

        self.assertIsInstance(container, Container)
        self.assertIsInstance(container.name, str)
        self.assertIsInstance(container.numberOfFilesPeriodNumber, tuple)
        self.assertIsInstance(container.dataFiles, DataFiles)
        self.assertIsInstance(container.composition, Composition)
        self.assertIsInstance(container.geometry, str)
        self.assertIsInstance(container.thickness, tuple)
        self.assertIsInstance(container.angleOfRotationSampleWidth, tuple)
        self.assertIsInstance(container.density, float)
        self.assertIsInstance(container.densityUnits, UnitsOfDensity)
        self.assertIsInstance(container.totalCrossSectionSource, str)
        self.assertIsInstance(container.tweakFactor, float)
        self.assertIsInstance(
            container.scatteringFractionAttenuationCoefficient, tuple
        )

    def testCompositionInitDataTypes(self):

        composition = Composition([], "test")

        self.assertIsInstance(composition, Composition)
        self.assertIsInstance(composition.elements, list)
        self.assertIsInstance(composition.type_, str)
        self.assertIsInstance(composition.str, list)

    def testElementInitDataTypes(self):

        element = Element("H", 0, 0.0)

        self.assertIsInstance(element, Element)
        self.assertIsInstance(element.atomicSymbol, str)
        self.assertIsInstance(element.massNo, int)
        self.assertIsInstance(element.abundance, float)
