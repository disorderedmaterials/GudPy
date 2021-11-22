from unittest import TestCase

from src.gudrun_classes.exception import ParserException
from src.gudrun_classes.gudrun_file import GudrunFile
from src.gudrun_classes.beam import Beam
from src.gudrun_classes.composition import Composition
from src.gudrun_classes.container import Container
from src.gudrun_classes.data_files import DataFiles
from src.gudrun_classes.element import Element
from src.gudrun_classes.instrument import Instrument
from src.gudrun_classes.normalisation import Normalisation
from src.gudrun_classes.sample_background import SampleBackground
from src.gudrun_classes.sample import Sample
from src.gudrun_classes.enums import (
    Instruments, Scales, UnitsOfDensity, MergeWeights, NormalisationType,
    OutputUnits, Geometry, CrossSectionSource
)


class TestGudrunClasses(TestCase):

    def testEmptyPath(self):

        emptyPath = ""
        self.assertRaises(ParserException, GudrunFile, path=emptyPath)

    def testInvalidPath(self):

        invalidPath = "invalid_path"
        self.assertRaises(ParserException, GudrunFile, path=invalidPath)

    def testInstrumentInitDataTypes(self):

        instrument = Instrument()

        self.assertIsInstance(instrument, Instrument)
        self.assertIsInstance(instrument.name, Instruments)
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
        self.assertIsInstance(instrument.spikeAnalysisAcceptanceFactor, float)
        self.assertIsInstance(instrument.wavelengthMin, float)
        self.assertIsInstance(instrument.wavelengthMax, float)
        self.assertIsInstance(instrument.wavelengthStep, float)
        self.assertIsInstance(instrument.NoSmoothsOnMonitor, int)
        self.assertIsInstance(instrument.XMin, float)
        self.assertIsInstance(instrument.XMax, float)
        self.assertIsInstance(instrument.XStep, float)
        self.assertIsInstance(instrument.useLogarithmicBinning, bool)
        self.assertIsInstance(instrument.groupingParameterPanel, list)
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
        self.assertIsInstance(instrument.nxsDefinitionFile, str)

    def testBeamInitDataTypes(self):

        beam = Beam()

        self.assertIsInstance(beam, Beam)
        self.assertIsInstance(beam.sampleGeometry, Geometry)
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
        self.assertIsInstance(normalisation.periodNumber, int)
        self.assertIsInstance(normalisation.dataFiles, DataFiles)
        self.assertIsInstance(normalisation.periodNumberBg, int)
        self.assertIsInstance(normalisation.dataFilesBg, DataFiles)
        self.assertIsInstance(
            normalisation.forceCalculationOfCorrections, bool
        )
        self.assertIsInstance(normalisation.composition, Composition)
        self.assertIsInstance(normalisation.geometry, Geometry)
        self.assertIsInstance(normalisation.upstreamThickness, float)
        self.assertIsInstance(normalisation.downstreamThickness, float)
        self.assertIsInstance(normalisation.angleOfRotation, float)
        self.assertIsInstance(normalisation.sampleWidth, float)
        self.assertIsInstance(normalisation.innerRadius, float)
        self.assertIsInstance(normalisation.outerRadius, float)
        self.assertIsInstance(normalisation.sampleHeight, float)
        self.assertIsInstance(normalisation.density, float)
        self.assertIsInstance(normalisation.densityUnits, UnitsOfDensity)
        self.assertIsInstance(normalisation.tempForNormalisationPC, float)
        self.assertIsInstance(
            normalisation.totalCrossSectionSource, CrossSectionSource
        )
        self.assertIsInstance(
            normalisation.normalisationDifferentialCrossSectionFile, str
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
        self.assertIsInstance(sampleBackground.periodNumber, int)
        self.assertIsInstance(sampleBackground.dataFiles, DataFiles)
        self.assertIsInstance(sampleBackground.samples, list)

    def testSampleInitDataTypes(self):

        sample = Sample()

        self.assertIsInstance(sample, Sample)
        self.assertIsInstance(sample.name, str)
        self.assertIsInstance(sample.periodNumber, int)
        self.assertIsInstance(sample.dataFiles, DataFiles)
        self.assertIsInstance(sample.forceCalculationOfCorrections, bool)
        self.assertIsInstance(sample.composition, Composition)
        self.assertIsInstance(sample.geometry, Geometry)
        self.assertIsInstance(sample.upstreamThickness, float)
        self.assertIsInstance(sample.downstreamThickness, float)
        self.assertIsInstance(sample.angleOfRotation, float)
        self.assertIsInstance(sample.sampleWidth, float)
        self.assertIsInstance(sample.innerRadius, float)
        self.assertIsInstance(sample.outerRadius, float)
        self.assertIsInstance(sample.sampleHeight, float)
        self.assertIsInstance(sample.density, float)
        self.assertIsInstance(sample.densityUnits, UnitsOfDensity)
        self.assertIsInstance(sample.tempForNormalisationPC, float)
        self.assertIsInstance(
            sample.totalCrossSectionSource, CrossSectionSource
        )
        self.assertIsInstance(sample.sampleTweakFactor, float)
        self.assertIsInstance(sample.topHatW, float)
        self.assertIsInstance(sample.minRadFT, float)
        self.assertIsInstance(sample.grBroadening, float)
        self.assertIsInstance(sample.resonanceValues, list)
        self.assertIsInstance(sample.exponentialValues, list)
        self.assertIsInstance(sample.fileSelfScattering, str)
        self.assertIsInstance(sample.normaliseTo, NormalisationType)
        self.assertIsInstance(sample.maxRadFT, float)
        self.assertIsInstance(sample.outputUnits, OutputUnits)
        self.assertIsInstance(sample.powerForBroadening, float)
        self.assertIsInstance(sample.runThisSample, bool)
        self.assertIsInstance(sample.scatteringFraction, float)
        self.assertIsInstance(sample.attenuationCoefficient, float)
        self.assertIsInstance(sample.containers, list)

    def testContainerInitDataTypes(self):

        container = Container()

        self.assertIsInstance(container, Container)
        self.assertIsInstance(container.name, str)
        self.assertIsInstance(container.periodNumber, int)
        self.assertIsInstance(container.dataFiles, DataFiles)
        self.assertIsInstance(container.composition, Composition)
        self.assertIsInstance(container.geometry, Geometry)
        self.assertIsInstance(container.upstreamThickness, float)
        self.assertIsInstance(container.downstreamThickness, float)
        self.assertIsInstance(container.angleOfRotation, float)
        self.assertIsInstance(container.sampleWidth, float)
        self.assertIsInstance(container.innerRadius, float)
        self.assertIsInstance(container.outerRadius, float)
        self.assertIsInstance(container.sampleHeight, float)
        self.assertIsInstance(container.density, float)
        self.assertIsInstance(container.densityUnits, UnitsOfDensity)
        self.assertIsInstance(
            container.totalCrossSectionSource, CrossSectionSource
        )
        self.assertIsInstance(container.tweakFactor, float)
        self.assertIsInstance(container.scatteringFraction, float)
        self.assertIsInstance(container.attenuationCoefficient, float)

    def testCompositionInitDataTypes(self):

        composition = Composition("test", elements=[])

        self.assertIsInstance(composition, Composition)
        self.assertIsInstance(composition.elements, list)
        self.assertIsInstance(composition.type_, str)

    def testElementInitDataTypes(self):

        element = Element("H", 0, 0.0)

        self.assertIsInstance(element, Element)
        self.assertIsInstance(element.atomicSymbol, str)
        self.assertIsInstance(element.massNo, int)
        self.assertIsInstance(element.abundance, float)
