import os
from enum import Enum
from unittest import TestCase
import random
from copy import deepcopy
from shutil import copyfile

from core.exception import ParserException
from core.utils import spacify, numifyBool
from core.gudrun_file import GudrunFile
from core.beam import Beam
from core.composition import Composition
from core.container import Container
from core.data_files import DataFiles
from core.element import Element
from core.instrument import Instrument
from core.normalisation import Normalisation
from core.sample_background import SampleBackground
from core.sample import Sample
from core.enums import (
    CrossSectionSource, FTModes, Instruments, Scales, UnitsOfDensity,
    MergeWeights, NormalisationType, OutputUnits,
    Geometry
)


class TestGudPyIO(TestCase):

    def setUp(self) -> None:
        path = "TestData/NIMROD-water/water.txt"

        if os.name == "nt":
            from pathlib import Path
            dirpath = Path().resolve() / "test/" / Path(path)
        else:
            dirpath = (
                "/".join(os.path.realpath(__file__).split("/")[:-1])
                + "/"
                + path
            )
        self.expectedInstrument = {
            "name": Instruments.NIMROD,
            "GudrunInputFileDir":
            os.path.abspath(os.path.dirname(os.path.abspath(dirpath))),
            "dataFileDir": "NIMROD-water/raw/",
            "dataFileType": "raw",
            "detectorCalibrationFileName": (
                'StartupFiles/NIMROD/NIMROD84modules'
                '+9monitors+LAB5Oct2012Detector.dat'),
            "columnNoPhiVals": 4,
            "groupFileName": (
                'StartupFiles/NIMROD/NIMROD84modules'
                '+9monitors+LAB5Oct2012Groups.dat'),
            "deadtimeConstantsFileName":
                "StartupFiles/NIMROD/NIMRODdeadtimeNone.cor",
            "spectrumNumbersForIncidentBeamMonitor": [4, 5],
            "wavelengthRangeForMonitorNormalisation": [0, 0],
            "spectrumNumbersForTransmissionMonitor": [8, 9],
            "incidentMonitorQuietCountConst": 0.0001,
            "transmissionMonitorQuietCountConst": 0.0001,
            "channelNosSpikeAnalysis": [0, 0],
            "spikeAnalysisAcceptanceFactor": 5,
            "wavelengthMin": 0.05,
            "wavelengthMax": 12.0,
            "wavelengthStep": 0.1,
            "NoSmoothsOnMonitor": 200,
            "XMin": 0.01,
            "XMax": 50.0,
            "XStep": -0.025,
            "useLogarithmicBinning": False,
            "groupingParameterPanel": [],
            "groupsAcceptanceFactor": 1.0,
            "mergePower": 4,
            "subSingleAtomScattering": False,
            "mergeWeights": MergeWeights.CHANNEL,
            "incidentFlightPath": 20.0,
            "spectrumNumberForOutputDiagnosticFiles": 0,
            "neutronScatteringParametersFile":
                "StartupFiles/NIMROD/sears91_gudrun.dat",
            "scaleSelection": Scales.Q,
            "subWavelengthBinnedData": 0,
            "GudrunStartFolder": os.path.abspath("../bin"),
            "startupFileFolder": "StartupFiles",
            "logarithmicStepSize": 0.04,
            "hardGroupEdges": True,
            "nxsDefinitionFile": "",
            "goodDetectorThreshold": 0,
            "yamlignore": {
                "GudrunInputFileDir",
                "GudrunStartFolder",
                "startupFileFolder",
                "goodDetectorThreshold",
                "yamlignore"
            }
        }

        self.expectedBeam = {
            "sampleGeometry": Geometry.FLATPLATE,
            "beamProfileValues": [1.0, 1.0],
            "stepSizeAbsorption": 0.05,
            "stepSizeMS": 0.2,
            "noSlices": 100,
            "angularStepForCorrections": 10,
            "incidentBeamLeftEdge": -1.5,
            "incidentBeamRightEdge": 1.5,
            "incidentBeamBottomEdge": -1.5,
            "incidentBeamTopEdge": 1.5,
            "scatteredBeamLeftEdge": -2.1,
            "scatteredBeamRightEdge": 2.1,
            "scatteredBeamBottomEdge": -2.1,
            "scatteredBeamTopEdge": 2.1,
            "filenameIncidentBeamSpectrumParams":
                "StartupFiles/NIMROD/spectrum000.dat",
            "overallBackgroundFactor": 1.0,
            "sampleDependantBackgroundFactor": 0.0,
            "shieldingAttenuationCoefficient": 0.0,
            "yamlignore": {
               "yamlignore"
            }
        }

        self.expectedNormalisation = {
            "periodNumber": 1,
            "dataFiles": DataFiles(["NIMROD00016702_V.raw"], "NORMALISATION"),
            "periodNumberBg": 1,
            "dataFilesBg": DataFiles(
                [
                    "NIMROD00016698_EmptyInst.raw",
                    "NIMROD00016703_EmptyInst.raw",
                ],
                "NORMALISATION BACKGROUND",
            ),
            "forceCalculationOfCorrections": True,
            "composition": Composition(
                "Normalisation", [Element("V", 0.0, 1.0)]
            ),
            "geometry": Geometry.SameAsBeam,
            "upstreamThickness": 0.15,
            "downstreamThickness": 0.15,
            "angleOfRotation": 0.0,
            "sampleWidth": 5.0,
            "innerRadius": 0.0,
            "outerRadius": 0.0,
            "sampleHeight": 0.0,
            "density": 0.0721,
            "densityUnits": UnitsOfDensity.ATOMIC,
            "tempForNormalisationPC": 200.0,
            "totalCrossSectionSource": CrossSectionSource.TABLES,
            "crossSectionFilename": "",
            "normalisationDifferentialCrossSectionFile": "*",
            "lowerLimitSmoothedNormalisation": 0.01,
            "normalisationDegreeSmoothing": 1.00,
            "minNormalisationSignalBR": 0.0,
            "yamlignore": {
                "yamlignore"
            }
        }

        self.expectedContainerA = {
            "name": "N9",
            "periodNumber": 1,
            "dataFiles": DataFiles(
                [
                    "NIMROD00016694_Empty_N9.raw",
                    "NIMROD00016699_Empty_N9.raw",
                    "NIMROD00016704_Empty_N9.raw",
                ],
                "N9",
            ),
            "composition": Composition(
                "Container"
            ),
            "geometry": Geometry.SameAsBeam,
            "upstreamThickness": 0.1,
            "downstreamThickness": 0.1,
            "angleOfRotation": 0.0,
            "sampleWidth": 5.0,
            "innerRadius": 0.0,
            "outerRadius": 0.0,
            "sampleHeight": 0.0,
            "density": 0.0542,
            "densityUnits": UnitsOfDensity.ATOMIC,
            "totalCrossSectionSource": CrossSectionSource.TABLES,
            "crossSectionFilename": "",
            "tweakFactor": 1.0,
            "scatteringFraction": 1.0,
            "attenuationCoefficient": 0.0,
            "runAsSample": False,
            "topHatW": 0.0,
            "FTMode": FTModes.SUB_AVERAGE,
            "minRadFT": 0.0,
            "maxRadFT": 0.0,
            "grBroadening": 0.0,
            "powerForBroadening": 0.0,
            "stepSize": 0.0,
            "yamlignore": {
                "runAsSample",
                "topHatW",
                "FTMode",
                "minRadFT",
                "maxRadFT",
                "grBroadening",
                "powerForBroadening",
                "stepSize",
                "singleAtomBackgroundScatteringSubtractionMode",
                "yamlignore"
            }
        }

        self.expectedContainerA["composition"].elements = [
            Element("Ti", 0.0, 7.16),
            Element("Zr", 0.0, 3.438)
        ]

        self.expectedContainerB = {
            "name": "N10",
            "periodNumber": 1,
            "dataFiles": DataFiles(
                [
                    "NIMROD00016695_Empty_N10.raw",
                    "NIMROD00016700_Empty_N10.raw",
                    "NIMROD00016705_Empty_N10.raw",
                ],
                "N10",
            ),
            "composition": Composition(
                "Container"
            ),
            "geometry": Geometry.SameAsBeam,
            "upstreamThickness": 0.1,
            "downstreamThickness": 0.1,
            "angleOfRotation": 0.0,
            "sampleWidth": 5.0,
            "innerRadius": 0.0,
            "outerRadius": 0.0,
            "sampleHeight": 0.0,
            "density": 0.0542,
            "densityUnits": UnitsOfDensity.ATOMIC,
            "totalCrossSectionSource": CrossSectionSource.TABLES,
            "crossSectionFilename": "",
            "tweakFactor": 1.0,
            "scatteringFraction": 1.0,
            "attenuationCoefficient": 0.0,
            "runAsSample": False,
            "topHatW": 0.0,
            "FTMode": FTModes.SUB_AVERAGE,
            "minRadFT": 0.0,
            "maxRadFT": 0.0,
            "grBroadening": 0.0,
            "powerForBroadening": 0.0,
            "stepSize": 0.0,
            "yamlignore": {
                "runAsSample",
                "topHatW",
                "FTMode",
                "minRadFT",
                "maxRadFT",
                "grBroadening",
                "powerForBroadening",
                "stepSize",
                "singleAtomBackgroundScatteringSubtractionMode",
                "yamlignore"
            }
        }

        self.expectedContainerB["composition"].elements = [
            Element("Ti", 0.0, 7.16),
            Element("Zr", 0.0, 3.438)
        ]

        self.expectedContainerC = {
            "name": "N6",
            "periodNumber": 1,
            "dataFiles": DataFiles(
                ["NIMROD00014908_Empty_N6.raw"], "N6"
            ),
            "composition": Composition(
                "Container"
            ),
            "geometry": Geometry.SameAsBeam,
            "upstreamThickness": 0.1,
            "downstreamThickness": 0.1,
            "angleOfRotation": 0.0,
            "sampleWidth": 5.0,
            "innerRadius": 0.0,
            "outerRadius": 0.0,
            "sampleHeight": 0.0,
            "density": 0.0542,
            "densityUnits": UnitsOfDensity.ATOMIC,
            "totalCrossSectionSource": CrossSectionSource.TABLES,
            "crossSectionFilename": "",
            "tweakFactor": 1.0,
            "scatteringFraction": 1.0,
            "attenuationCoefficient": 0.0,
            "runAsSample": False,
            "topHatW": 0.0,
            "FTMode": FTModes.SUB_AVERAGE,
            "minRadFT": 0.0,
            "maxRadFT": 0.0,
            "grBroadening": 0.0,
            "powerForBroadening": 0.0,
            "stepSize": 0.0,
            "yamlignore": {
                "runAsSample",
                "topHatW",
                "FTMode",
                "minRadFT",
                "maxRadFT",
                "grBroadening",
                "powerForBroadening",
                "stepSize",
                "singleAtomBackgroundScatteringSubtractionMode",
                "yamlignore"
            }
        }

        self.expectedContainerC["composition"].elements = [
            Element("Ti", 0.0, 7.16),
            Element("Zr", 0.0, 3.438)
        ]

        self.expectedContainerD = {
            "name": "N8",
            "periodNumber": 1,
            "dataFiles": DataFiles(
                ["NIMROD00016994_Empty_N8.raw"], "N8"
            ),
            "composition": Composition(
                "Container"
            ),
            "geometry": Geometry.SameAsBeam,
            "upstreamThickness": 0.1,
            "downstreamThickness": 0.1,
            "angleOfRotation": 0.0,
            "sampleWidth": 5.0,
            "innerRadius": 0.0,
            "outerRadius": 0.0,
            "sampleHeight": 0.0,
            "density": 0.0542,
            "densityUnits": UnitsOfDensity.ATOMIC,
            "totalCrossSectionSource": CrossSectionSource.TABLES,
            "crossSectionFilename": "",
            "tweakFactor": 1.0,
            "scatteringFraction": 1.0,
            "attenuationCoefficient": 0.0,
            "runAsSample": False,
            "topHatW": 0.0,
            "FTMode": FTModes.SUB_AVERAGE,
            "minRadFT": 0.0,
            "maxRadFT": 0.0,
            "grBroadening": 0.0,
            "powerForBroadening": 0.0,
            "stepSize": 0.0,
            "yamlignore": {
                "runAsSample",
                "topHatW",
                "FTMode",
                "minRadFT",
                "maxRadFT",
                "grBroadening",
                "powerForBroadening",
                "stepSize",
                "singleAtomBackgroundScatteringSubtractionMode",
                "yamlignore"
            }
        }

        self.expectedContainerD["composition"].elements = [
            Element("Ti", 0.0, 7.16),
            Element("Zr", 0.0, 3.438)
        ]

        self.expectedSampleA = {
            "name": "H2O, Can N9",
            "periodNumber": 1,
            "dataFiles": DataFiles(
                [
                    "NIMROD00016608_H2O_in_N9.raw",
                    "NIMROD00016610_H2O_in_N9.raw",
                ],
                "H2O, Can N9",
            ),
            "forceCalculationOfCorrections": True,
            "composition": Composition(
                "Sample"
            ),
            "geometry": Geometry.SameAsBeam,
            "upstreamThickness": 0.05,
            "downstreamThickness": 0.05,
            "angleOfRotation": 0.0,
            "sampleWidth": 5.0,
            "innerRadius": 0.0,
            "outerRadius": 0.0,
            "sampleHeight": 0.0,
            "density": 0.1,
            "densityUnits": UnitsOfDensity.ATOMIC,
            "tempForNormalisationPC": 0.0,
            "totalCrossSectionSource": CrossSectionSource.TRANSMISSION,
            "crossSectionFilename": "",
            "sampleTweakFactor": 1.0,
            "topHatW": 10.0,
            "FTMode": FTModes.SUB_AVERAGE,
            "minRadFT": 0.8,
            "grBroadening": 0.1,
            "resonanceValues": [],
            "exponentialValues": [[0.0, 1.5, 0]],
            "normalisationCorrectionFactor": 1.0,
            "fileSelfScattering": "NIMROD00016608_H2O_in_N9.msubw01",
            "normaliseTo": NormalisationType.NOTHING,
            "maxRadFT": 50.0,
            "outputUnits": OutputUnits.BARNS_ATOM_SR,
            "powerForBroadening": 0.5,
            "stepSize": 0.03,
            "runThisSample": True,
            "scatteringFraction": 1.0,
            "attenuationCoefficient": 0.0,
            "containers": [self.expectedContainerA],
            "yamlignore": {
                "yamlignore",
                "singleAtomBackgroundScatteringSubtractionMode"
            }
        }

        self.expectedSampleA["composition"].elements = [
            Element("H", 0.0, 2.0),
            Element("O", 0.0, 1.0)
        ]

        self.expectedSampleB = {
            "name": "D2O, Can N10",
            "periodNumber": 1,
            "dataFiles": DataFiles(
                [
                    "NIMROD00016609_D2O_in_N10.raw",
                    "NIMROD00016611_D2O_in_N10.raw",
                ],
                "D2O, Can N10",
            ),
            "forceCalculationOfCorrections": True,
            "composition": Composition(
                "Sample"
            ),
            "geometry": Geometry.SameAsBeam,
            "upstreamThickness": 0.05,
            "downstreamThickness": 0.05,
            "angleOfRotation": 0.0,
            "sampleWidth": 5.0,
            "innerRadius": 0.0,
            "outerRadius": 0.0,
            "sampleHeight": 0.0,
            "density": 0.1,
            "densityUnits": UnitsOfDensity.ATOMIC,
            "tempForNormalisationPC": 0.0,
            "totalCrossSectionSource": CrossSectionSource.TRANSMISSION,
            "crossSectionFilename": "",
            "sampleTweakFactor": 1.0,
            "topHatW": 10.0,
            "FTMode": FTModes.SUB_AVERAGE,
            "minRadFT": 0.8,
            "grBroadening": 0.0,
            "resonanceValues": [],
            "exponentialValues": [[0.0, 1.5, 0]],
            "normalisationCorrectionFactor": 1.0,
            "fileSelfScattering": "NIMROD00016609_D2O_in_N10.msubw01",
            "normaliseTo": NormalisationType.NOTHING,
            "maxRadFT": 50.0,
            "outputUnits": OutputUnits.BARNS_ATOM_SR,
            "powerForBroadening": 0.0,
            "stepSize": 0.03,
            "runThisSample": True,
            "scatteringFraction": 1.0,
            "attenuationCoefficient": 0.0,
            "containers": [self.expectedContainerB],
            "yamlignore": {
                "yamlignore",
                "singleAtomBackgroundScatteringSubtractionMode"
            }
        }

        self.expectedSampleB["composition"].elements = [
            Element("H", 2.0, 2.0),
            Element("O", 0.0, 1.0)
        ]

        self.expectedSampleC = {
            "name": "HDO, Can N6",
            "periodNumber": 1,
            "dataFiles": DataFiles(
                [
                    "NIMROD00016741_HDO_in_N6.raw",
                    "NIMROD00016743_HDO_in_N6.raw",
                ],
                "HDO, Can N6",
            ),
            "forceCalculationOfCorrections": True,
            "composition": Composition(
                "Sample"
            ),
            "geometry": Geometry.SameAsBeam,
            "upstreamThickness": 0.05,
            "downstreamThickness": 0.05,
            "angleOfRotation": 0.0,
            "sampleWidth": 5.0,
            "innerRadius": 0.0,
            "outerRadius": 0.0,
            "sampleHeight": 0.0,
            "density": 0.1,
            "densityUnits": UnitsOfDensity.ATOMIC,
            "tempForNormalisationPC": 0.0,
            "totalCrossSectionSource": CrossSectionSource.TRANSMISSION,
            "crossSectionFilename": "",
            "sampleTweakFactor": 1.0,
            "topHatW": 10.0,
            "FTMode": FTModes.SUB_AVERAGE,
            "minRadFT": 0.8,
            "grBroadening": 0.1,
            "resonanceValues": [],
            "exponentialValues": [[0.0, 1.5, 0]],
            "normalisationCorrectionFactor": 1.0,
            "fileSelfScattering": "NIMROD00016741_HDO_in_N6.msubw01",
            "normaliseTo": NormalisationType.NOTHING,
            "maxRadFT": 50.0,
            "outputUnits": OutputUnits.BARNS_ATOM_SR,
            "powerForBroadening": 0.5,
            "stepSize": 0.03,
            "runThisSample": True,
            "scatteringFraction": 1.0,
            "attenuationCoefficient": 0.0,
            "containers": [self.expectedContainerC],
            "yamlignore": {
                "yamlignore",
                "singleAtomBackgroundScatteringSubtractionMode"
            }
        }

        self.expectedSampleC["composition"].elements = [
                    Element("H", 0.0, 1.0),
                    Element("O", 0.0, 1.0),
                    Element("H", 2.0, 1.0),
        ]

        self.expectedSampleD = {
            "name": "Null Water, Can N8",
            "periodNumber": 1,
            "dataFiles": DataFiles(
                [
                    "NIMROD00016742_NullWater_in_N8.raw",
                    "NIMROD00016744_NullWater_in_N8.raw",
                ],
                "Null Water, Can N8",
            ),
            "forceCalculationOfCorrections": True,
            "composition": Composition(
                "Sample",
            ),
            "geometry": Geometry.SameAsBeam,
            "upstreamThickness": 0.05,
            "downstreamThickness": 0.05,
            "angleOfRotation": 0.0,
            "sampleWidth": 5.0,
            "innerRadius": 0.0,
            "outerRadius": 0.0,
            "sampleHeight": 0.0,
            "density": 0.1,
            "densityUnits": UnitsOfDensity.ATOMIC,
            "tempForNormalisationPC": 0.0,
            "totalCrossSectionSource": CrossSectionSource.TRANSMISSION,
            "crossSectionFilename": "",
            "sampleTweakFactor": 1.0,
            "topHatW": 10.0,
            "FTMode": FTModes.SUB_AVERAGE,
            "minRadFT": 0.8,
            "grBroadening": 0.1,
            "resonanceValues": [],
            "exponentialValues": [[0.0, 1.5, 0]],
            "normalisationCorrectionFactor": 1.0,
            "fileSelfScattering": "NIMROD00016742_NullWater_in_N8.msubw01",
            "normaliseTo": NormalisationType.NOTHING,
            "maxRadFT": 50.0,
            "outputUnits": OutputUnits.BARNS_ATOM_SR,
            "powerForBroadening": 0.5,
            "stepSize": 0.03,
            "runThisSample": True,
            "scatteringFraction": 1.0,
            "attenuationCoefficient": 0.0,
            "containers": [self.expectedContainerD],
            "yamlignore": {
                "yamlignore",
                "singleAtomBackgroundScatteringSubtractionMode"
            }
        }

        self.expectedSampleD["composition"].elements = [
            Element("H", 0.0, 1.281),
            Element("O", 0.0, 1.0),
            Element("H", 2.0, 0.7185)
        ]

        self.expectedSampleBackground = {
            "periodNumber": 1,
            "dataFiles": DataFiles(
                [
                    "NIMROD00016698_EmptyInst.raw",
                    "NIMROD00016703_EmptyInst.raw",
                ],
                "SAMPLE BACKGROUND",
            ),
            "samples": [
                self.expectedSampleA,
                self.expectedSampleB,
                self.expectedSampleC,
            ],
            "writeAllSamples": True,
            "yamlignore": {
                "writeAllSamples",
                "yamlignore"
            }
        }

        self.goodInstrument = Instrument()
        self.goodInstrument.__dict__ = self.expectedInstrument
        self.goodBeam = Beam()
        self.goodBeam.__dict__ = self.expectedBeam
        self.goodNormalisation = Normalisation()
        self.goodNormalisation.__dict__ = self.expectedNormalisation
        self.goodSampleBackground = SampleBackground()
        self.goodSampleBackground.periodNumber = (
            self.expectedSampleBackground["periodNumber"]
        )
        self.goodSampleBackground.dataFiles = self.expectedSampleBackground[
            "dataFiles"
        ]
        self.goodSampleBackground.samples.append(Sample())
        self.goodSampleBackground.samples[0].__dict__ = deepcopy(
            self.expectedSampleBackground["samples"][0]
        )
        self.goodSampleBackground.samples[0].containers[0] = Container()
        self.goodSampleBackground.samples[0].containers[
            0
        ].__dict__ = self.expectedContainerA

        self.g = GudrunFile(dirpath)

        self.dicts = [
            self.expectedInstrument,
            self.expectedBeam,
            self.expectedNormalisation,
            self.expectedContainerA,
            self.expectedContainerB,
            self.expectedContainerC,
            self.expectedContainerD,
            self.expectedSampleA,
            self.expectedSampleB,
            self.expectedSampleC,
            self.expectedSampleD,
            self.expectedSampleBackground,
        ]

        self.keepsakes = os.listdir()

        copyfile(self.g.path, "test/TestData/NIMROD-water/good_water.txt")
        g = GudrunFile("test/TestData/NIMROD-water/good_water.txt")

        g.write_out(overwrite=True)
        return super().setUp()

    def tearDown(self) -> None:

        [os.remove(f) for f in os.listdir() if f not in self.keepsakes]
        return super().tearDown()

    def testLoadGudrunFile(self):

        self.assertIsInstance(self.g, GudrunFile)

        instrumentAttrsDict = self.g.instrument.__dict__

        for key in instrumentAttrsDict.keys():
            self.assertEqual(
                self.expectedInstrument[key], instrumentAttrsDict[key]
            )

        beamAttrsDict = self.g.beam.__dict__

        for key in beamAttrsDict.keys():
            self.assertEqual(self.expectedBeam[key], beamAttrsDict[key])

        normalisationAttrsDict = self.g.normalisation.__dict__

        for key in normalisationAttrsDict.keys():
            if isinstance(
                normalisationAttrsDict[key], (DataFiles, Composition)
            ):
                self.assertEqual(
                    str(self.expectedNormalisation[key]),
                    str(normalisationAttrsDict[key]),
                )
            else:
                self.assertEqual(
                    self.expectedNormalisation[key],
                    normalisationAttrsDict[key],
                )

        self.assertEqual(len(self.g.sampleBackgrounds), 1)

        sampleBackgroundsAttrsDict = self.g.sampleBackgrounds[0].__dict__

        for key in sampleBackgroundsAttrsDict.keys():
            if key == "samples":
                for i, sample in enumerate(self.expectedSampleBackground[key]):
                    sampleAttrsDict = (
                        deepcopy(
                            self.g.sampleBackgrounds[0].samples[i].__dict__
                        )
                    )
                    for key_ in sampleAttrsDict.keys():

                        if key_ == "containers":
                            for j, container in enumerate(sample[key_]):
                                containerAttrsDict = (
                                    self.g.sampleBackgrounds[0]
                                    .samples[i]
                                    .containers[j]
                                    .__dict__
                                )

                                for _key in containerAttrsDict.keys():

                                    if isinstance(
                                        container[_key],
                                        (DataFiles, Composition),
                                    ):
                                        self.assertEqual(
                                            str(container[_key]),
                                            str(containerAttrsDict[_key]),
                                        )
                                    else:
                                        self.assertEqual(
                                            container[_key],
                                            containerAttrsDict[_key],
                                        )

                        elif isinstance(
                            sample[key_], (DataFiles, Composition)
                        ):
                            self.assertEqual(
                                str(sample[key_]), str(sampleAttrsDict[key_])
                            )
                        else:
                            self.assertEqual(
                                sample[key_], sampleAttrsDict[key_]
                            )

            elif isinstance(sampleBackgroundsAttrsDict[key], DataFiles):
                self.assertEqual(
                    str(self.expectedSampleBackground[key]),
                    str(sampleBackgroundsAttrsDict[key]),
                )
            else:
                self.assertEqual(
                    self.expectedSampleBackground[key],
                    sampleBackgroundsAttrsDict[key],
                )

    def testWriteGudrunFile(self):
        self.g.write_out()
        outlines = "\n".join(open(
            os.path.join(
                self.g.instrument.GudrunInputFileDir,
                self.g.outpath
            ),
            encoding="utf-8"
        ).readlines()[:-5])
        self.assertEqual(
            outlines, "\n".join(str(self.g).splitlines(keepends=True)[:-5])
        )

        def valueInLines(value, lines):
            if isinstance(value, str):
                self.assertTrue(value in lines)
            elif isinstance(value, (list, tuple)):
                if len(value) == 0:
                    return
                elif isinstance(value[0], dict):
                    for val in value:
                        for val_ in val.values():
                            valueInLines(val_, lines)
                elif isinstance(value[0], (list, tuple)):
                    for val in value:
                        self.assertTrue(
                            spacify(val) in lines
                            or spacify(val, num_spaces=2) in lines
                        )
                else:
                    self.assertTrue(
                        spacify(value) in lines
                        or spacify(value, num_spaces=2) in lines
                        or spacify([int(x) for x in value]) in lines
                        or spacify(
                            [int(x) for x in value], num_spaces=2
                        ) in lines
                    )
            elif isinstance(value, bool):
                self.assertTrue(str(numifyBool(value)) in lines)
            elif isinstance(value, Enum):
                self.assertTrue(
                    str(value.value) in lines
                    or value.name in lines
                )
            else:
                if "        " in str(value):
                    self.assertTrue(str(value).split("        ")[0] in lines)
                elif isinstance(value, str):
                    self.assertTrue(
                        str(value) in lines
                        or str(int(value)) in lines
                    )

        for dic in self.dicts:
            for value in dic.values():
                if isinstance(value, list):
                    for val in value:
                        if isinstance(val, dict):
                            for val_ in val.values():
                                valueInLines(val_, outlines)
                        else:
                            valueInLines(val, outlines)
                else:
                    valueInLines(value, outlines)

        inlines = open(self.g.path).read()
        for dic in self.dicts:
            for value in dic.values():
                if isinstance(value, list):
                    for val in value:
                        if isinstance(val, dict):
                            for val_ in val.values():
                                valueInLines(val_, inlines)
                        else:
                            valueInLines(val, inlines)
                else:
                    if (
                        value == os.path.abspath("../bin")
                        or value == os.path.sep
                        or value == os.path.join("../bin", "StartupFiles")
                        or value == self.g.instrument.GudrunInputFileDir
                    ):
                        continue
                    valueInLines(value, inlines)

    def testRewriteGudrunFile(self):
        self.g.write_out()
        g1 = GudrunFile(
            os.path.join(
                self.g.instrument.GudrunInputFileDir,
                self.g.outpath
            )
        )
        g1.instrument.GudrunInputFileDir = self.g.instrument.GudrunInputFileDir
        g1.write_out()

        self.assertEqual(
            "\n".join(open(
                os.path.join(
                    g1.instrument.GudrunInputFileDir,
                    g1.outpath
                ),
                encoding="utf-8"
            ).readlines()[:-5]),
            "\n".join(str(self.g).splitlines(keepends=True)[:-5])
        )

        self.assertEqual(
            "\n".join(open(
                os.path.join(
                    g1.instrument.GudrunInputFileDir,
                    g1.outpath
                ),
                encoding="utf-8"
            ).readlines()[:-5]),
            "\n".join(str(g1).splitlines(keepends=True)[:-5])
        )

        self.assertEqual(
            "\n".join(
                open(
                    os.path.join(
                        g1.instrument.GudrunInputFileDir,
                        g1.outpath
                    ),
                    encoding="utf-8"
                ).readlines()[:-5]
            ),
            "\n".join(
                open(
                    os.path.join(
                        self.g.instrument.GudrunInputFileDir,
                        self.g.outpath
                    ),
                    encoding="utf-8"
                ).readlines()[:-5]
            )
        )

    def testReloadGudrunFile(self):
        self.g.write_out()
        g1 = GudrunFile(
            os.path.join(
                self.g.instrument.GudrunInputFileDir,
                self.g.outpath
            )
        )
        g1.instrument.GudrunInputFileDir = self.g.instrument.GudrunInputFileDir
        self.assertEqual(
            "\n".join(str(g1).splitlines(keepends=True)[:-5]),
            "\n".join(str(self.g).splitlines(keepends=True)[:-5])
        )

    def testLoadEmptyGudrunFile(self):
        f = open("test_data.txt", "w", encoding="utf-8")
        f.close()
        with self.assertRaises(ParserException) as cm:
            GudrunFile("test_data.txt")
        self.assertEqual((
                    'INSTRUMENT, BEAM and NORMALISATION'
                    ' were not parsed. It\'s possible the file'
                    ' supplied is of an incorrect format!'
                ),
            str(cm.exception),
        )

    def testLoadMissingInstrument(self):
        with open("test_data.txt", "w", encoding="utf-8") as f:
            f.write("'  '  '        '  '/'\n\n")
            f.write("BEAM        {\n\n" + str(self.goodBeam) + "\n\n}\n\n")
            f.write(
                "NORMALISATION        {\n\n"
                + str(self.goodNormalisation)
                + "\n\n}\n\n"
            )

        with self.assertRaises(ParserException) as cm:
            GudrunFile("test_data.txt")
        self.assertEqual((
                    'INSTRUMENT, BEAM and NORMALISATION'
                    ' were not parsed. It\'s possible the file'
                    ' supplied is of an incorrect format!'
                ),
            str(cm.exception),
        )

    def testLoadMissingBeam(self):
        with open("test_data.txt", "w", encoding="utf-8") as f:
            f.write("'  '  '        '  '/'\n\n")
            f.write(
                "INSTRUMENT        {\n\n" + str(self.goodInstrument)
                + "\n\n}\n\n"
            )
            f.write(
                "NORMALISATION        {\n\n"
                + str(self.goodNormalisation)
                + "\n\n}"
            )
        with self.assertRaises(ParserException) as cm:
            GudrunFile("test_data.txt")
        self.assertEqual((
                    'INSTRUMENT, BEAM and NORMALISATION'
                    ' were not parsed. It\'s possible the file'
                    ' supplied is of an incorrect format!'
                ),
            str(cm.exception),
        )

    def testLoadMissingNormalisation(self):
        with open("test_data.txt", "w", encoding="utf-8") as f:
            f.write("'  '  '        '  '/'\n\n")
            f.write(
                "INSTRUMENT        {\n\n" + str(self.goodInstrument)
                + "\n\n}\n\n"
            )
            f.write("BEAM        {\n\n" + str(self.goodBeam) + "\n\n}\n\n")

        with self.assertRaises(ParserException) as cm:
            GudrunFile("test_data.txt")
        self.assertEqual((
                    'INSTRUMENT, BEAM and NORMALISATION'
                    ' were not parsed. It\'s possible the file'
                    ' supplied is of an incorrect format!'
                ),
            str(cm.exception),
        )

    def testLoadMissingInstrumentAndBeam(self):
        with open("test_data.txt", "w", encoding="utf-8") as f:
            f.write("'  '  '        '  '/'\n\n")
            f.write(
                "NORMALISATION        {\n\n"
                + str(self.goodNormalisation)
                + "\n\n}"
            )

        with self.assertRaises(ParserException) as cm:
            GudrunFile("test_data.txt")
        self.assertEqual((
            'INSTRUMENT, BEAM and NORMALISATION'
            ' were not parsed. It\'s possible the file supplied'
            ' is of an incorrect format!'),
            str(cm.exception),
        )

    def testLoadMissingInstrumentAndNormalisation(self):
        with open("test_data.txt", "w", encoding="utf-8") as f:
            f.write("'  '  '        '  '/'\n\n")
            f.write("BEAM        {\n\n" + str(self.goodBeam) + "\n\n}")

        with self.assertRaises(ParserException) as cm:
            GudrunFile("test_data.txt")
        self.assertEqual((
                    'INSTRUMENT, BEAM and NORMALISATION'
                    ' were not parsed. It\'s possible the file'
                    ' supplied is of an incorrect format!'
                ),
            str(cm.exception),
        )

    def testLoadMissingNormalisationAndBeam(self):
        with open("test_data.txt", "w", encoding="utf-8") as f:
            f.write("'  '  '        '  '/'\n\n")
            f.write(
                "INSTRUMENT        {\n\n" + str(self.goodInstrument) + "\n\n}"
            )

        with self.assertRaises(ParserException) as cm:
            GudrunFile("test_data.txt")
        self.assertEqual((
                    'INSTRUMENT, BEAM and NORMALISATION'
                    ' were not parsed. It\'s possible the file'
                    ' supplied is of an incorrect format!'
                ),
            str(cm.exception),
        )

    def testLoadMissingInstrumentAttributesSeq(self):

        expectedInstrument = deepcopy(self.expectedInstrument)
        expectedInstrument.pop("XMax", None)
        expectedInstrument.pop("XStep", None)
        expectedInstrument.pop("wavelengthMax", None)
        expectedInstrument.pop("wavelengthStep", None)
        expectedInstrument.pop("useLogarithmicBinning", None)
        expectedInstrument.pop("nxsDefinitionFile", None)
        expectedInstrument.pop("groupingParameterPanel", None)
        expectedInstrument.pop("goodDetectorThreshold", None)
        expectedInstrument.pop("yamlignore", None)
        for i in range(len(expectedInstrument.keys())):

            badInstrument = str(self.goodInstrument).split("\n")
            del badInstrument[i]
            badInstrument = "\n".join(badInstrument)

            with open("test_data.txt", "w", encoding="utf-8") as f:
                f.write("'  '  '        '  '/'\n\n")
                f.write(
                    "INSTRUMENT        {\n\n" + str(badInstrument) + "\n\n}"
                )

            with self.assertRaises(ParserException) as cm:
                GudrunFile("test_data.txt")
                self.assertEqual(
                    "Whilst parsing Instrument, an exception occured."
                    " The input file is most likely of an incorrect format, "
                    "and some attributes were missing.",
                    str(cm.exception)
                )

    def testLoadMissingInstrumentAttributesRand(self):

        expectedInstrument = deepcopy(self.expectedInstrument)
        expectedInstrument.pop("XMax", None)
        expectedInstrument.pop("XStep", None)
        expectedInstrument.pop("wavelengthMax", None)
        expectedInstrument.pop("wavelengthStep", None)
        expectedInstrument.pop("useLogarithmicBinning", None)
        expectedInstrument.pop("nxsDefinitionFile", None)
        expectedInstrument.pop("groupingParameterPanel", None)
        expectedInstrument.pop("goodDetectorThreshold", None)
        expectedInstrument.pop("yamlignore", None)
        for i in range(50):

            key = random.choice(list(expectedInstrument))
            j = list(expectedInstrument).index(key)

            badInstrument = str(self.goodInstrument).split("\n")
            del badInstrument[j]
            badInstrument = "\n".join(badInstrument)

            with open("test_data.txt", "w", encoding="utf-8") as f:
                f.write("'  '  '        '  '/'\n\n")
                f.write(
                    "INSTRUMENT        {\n\n" + str(badInstrument) + "\n\n}"
                )
            with self.assertRaises(ParserException) as cm:
                GudrunFile("test_data.txt")
                self.assertEqual(
                    "Whilst parsing Instrument, an exception occured."
                    " The input file is most likely of an incorrect format, "
                    "and some attributes were missing.",
                    str(cm.exception)
                )

    def testLoadMissingBeamAttributesSeq(self):

        expectedBeam = deepcopy(self.expectedBeam)
        expectedBeam.pop("incidentBeamRightEdge", None)
        expectedBeam.pop("incidentBeamTopEdge", None)
        expectedBeam.pop("incidentBeamBottomEdge", None)
        expectedBeam.pop("scatteredBeamRightEdge", None)
        expectedBeam.pop("scatteredBeamTopEdge", None)
        expectedBeam.pop("scatteredBeamBottomEdge", None)
        expectedBeam.pop("stepSizeMS", None)
        expectedBeam.pop("noSlices", None)
        expectedBeam.pop("yamlignore", None)

        for i in range(len(expectedBeam.keys())):
            badBeam = str(self.goodBeam).split("\n")
            del badBeam[i]
            badBeam = "\n".join(badBeam)

            with open("test_data.txt", "w", encoding="utf-8") as f:
                f.write("'  '  '        '  '/'\n\n")
                f.write(
                    "INSTRUMENT        {\n\n"
                    + str(self.goodInstrument)
                    + "\n\n}"
                )
                f.write("\n\nBEAM        {\n\n" + str(badBeam) + "\n\n}")

            with self.assertRaises(ParserException) as cm:
                GudrunFile("test_data.txt")
                self.assertEqual(
                    "Whilst parsing Beam, an exception occured."
                    " The input file is most likely of an incorrect format, "
                    "and some attributes were missing.",
                    str(cm.exception)
                )

    def testLoadMissingBeamAttributesRand(self):

        expectedBeam = deepcopy(self.expectedBeam)
        expectedBeam.pop("incidentBeamRightEdge", None)
        expectedBeam.pop("incidentBeamTopEdge", None)
        expectedBeam.pop("incidentBeamBottomEdge", None)
        expectedBeam.pop("scatteredBeamRightEdge", None)
        expectedBeam.pop("scatteredBeamTopEdge", None)
        expectedBeam.pop("scatteredBeamBottomEdge", None)
        expectedBeam.pop("stepSizeMS", None)
        expectedBeam.pop("noSlices", None)
        expectedBeam.pop("yamlignore", None)

        for i in range(50):

            key = random.choice(list(expectedBeam))
            j = list(expectedBeam).index(key)

            badBeam = str(self.goodBeam).split("\n")
            del badBeam[j]
            badBeam = "\n".join(badBeam)

            with open("test_data.txt", "w", encoding="utf-8") as f:
                f.write("'  '  '        '  '/'\n\n")
                f.write(
                    "INSTRUMENT        {\n\n"
                    + str(self.goodInstrument)
                    + "\n\n}"
                )
                f.write("\n\nBEAM        {\n\n" + str(badBeam) + "\n\n}")

            with self.assertRaises(ParserException) as cm:
                GudrunFile("test_data.txt")
                self.assertEqual(
                    "Whilst parsing Beam, an exception occured."
                    " The input file is most likely of an incorrect format, "
                    "and some attributes were missing.",
                    str(cm.exception)
                )

    def testLoadMissingNormalisationAttributesSeq(self):

        expectedNormalisation = deepcopy(self.expectedNormalisation)
        expectedNormalisation.pop("dataFiles", None)
        expectedNormalisation.pop("dataFilesBg", None)
        expectedNormalisation.pop("composition", None)
        expectedNormalisation.pop("densityUnits", None)
        expectedNormalisation.pop("innerRadius", None)
        expectedNormalisation.pop("outerRadius", None)
        expectedNormalisation.pop("sampleHeight", None)
        expectedNormalisation.pop("crossSectionFilename")
        expectedNormalisation.pop("yamlignore", None)

        self.goodNormalisation.dataFiles = DataFiles([], "")
        self.goodNormalisation.composition = (
            Composition("")
        )
        for i in range(len(expectedNormalisation.keys())):

            badNormalisation = str(self.goodNormalisation).split("\n")
            del badNormalisation[i]
            badNormalisation = "\n".join(badNormalisation)

            with open("test_data.txt", "w", encoding="utf-8") as f:
                f.write("'  '  '        '  '/'\n\n")
                f.write(
                    "INSTRUMENT        {\n\n"
                    + str(self.goodInstrument)
                    + "\n\n}"
                )
                f.write("\n\nBEAM        {\n\n" + str(self.goodBeam) + "\n\n}")
                f.write(
                    "\n\nNORMALISATION        {\n\n"
                    + str(badNormalisation)
                    + "\n\n}"
                )

            with self.assertRaises(ParserException) as cm:
                GudrunFile("test_data.txt")
                self.assertEqual(
                    "Whilst parsing Beam, an exception occured."
                    " The input file is most likely of an incorrect format, "
                    "and some attributes were missing.",
                    str(cm.exception)
                )

    def testLoadMissingNormalisationAttributesRand(self):

        expectedNormalisation = deepcopy(self.expectedNormalisation)
        expectedNormalisation.pop("dataFiles", None)
        expectedNormalisation.pop("dataFilesBg", None)
        expectedNormalisation.pop("composition", None)
        expectedNormalisation.pop("densityUnits", None)
        expectedNormalisation.pop("innerRadius", None)
        expectedNormalisation.pop("outerRadius", None)
        expectedNormalisation.pop("sampleHeight", None)
        expectedNormalisation.pop("crossSectionFilename")
        expectedNormalisation.pop("yamlignore", None)

        self.goodNormalisation.dataFiles = DataFiles([], "")
        self.goodNormalisation.composition = (
            Composition("")
        )
        for i in range(50):

            key = random.choice(list(expectedNormalisation))

            j = list(expectedNormalisation).index(key)

            badNormalisation = str(self.goodNormalisation).split("\n")
            del badNormalisation[j]
            badNormalisation = "\n".join(badNormalisation)

            with open("test_data.txt", "w", encoding="utf-8") as f:
                f.write("'  '  '        '  '/'\n\n")
                f.write(
                    "INSTRUMENT        {\n\n"
                    + str(self.goodInstrument)
                    + "\n\n}"
                )
                f.write("\n\nBEAM        {\n\n" + str(self.goodBeam) + "\n\n}")
                f.write(
                    "\n\nNORMALISATION        {\n\n"
                    + str(badNormalisation)
                    + "\n\n}"
                )

            with self.assertRaises(ParserException) as cm:
                GudrunFile("test_data.txt")
                self.assertEqual(
                    "Whilst parsing Normalisation, an exception occured."
                    " The input file is most likely of an incorrect format, "
                    "and some attributes were missing.",
                    str(cm.exception)
                )

    def testLoadMissingSampleBackgroundAttributes(self):
        badSampleBackground = str(self.goodSampleBackground).split("\n")
        del badSampleBackground[2]
        badSampleBackground = "\n".join(badSampleBackground)
        with open("test_data.txt", "w", encoding="utf-8") as f:
            f.write("'  '  '        '  '/'\n\n")
            f.write(
                "INSTRUMENT        {\n\n" + str(self.goodInstrument) + "\n\n}"
            )
            f.write("\n\nBEAM        {\n\n" + str(self.goodBeam) + "\n\n}")
            f.write(
                "\n\nNORMALISATION        {\n\n"
                + str(self.goodNormalisation)
                + "\n\n}"
            )
            f.write("\n\n{}\n\nEND".format(str(badSampleBackground)))
        with self.assertRaises(ParserException) as cm:
            GudrunFile("test_data.txt")
            self.assertEqual(
                "Whilst parsing Sample Background, an exception occured."
                " The input file is most likely of an incorrect format, "
                "and some attributes were missing.",
                str(cm.exception)
            )

    def testLoadMissingSampleAttributesSeq(self):

        expectedSampleA = deepcopy(self.expectedSampleA)
        expectedSampleA.pop("name", None)
        expectedSampleA.pop("dataFiles", None)
        expectedSampleA.pop("composition", None)
        expectedSampleA.pop("containers", None)
        expectedSampleA.pop("densityUnits", None)
        expectedSampleA.pop("innerRadius", None)
        expectedSampleA.pop("outerRadius", None)
        expectedSampleA.pop("sampleHeight", None)
        expectedSampleA.pop("resonanceValues", None)
        expectedSampleA.pop("exponentialValues", None)
        expectedSampleA.pop("crossSectionFilename", None)
        expectedSampleA.pop("FTMode", None)
        expectedSampleA.pop("yamlignore", None)

        self.goodSampleBackground.samples[0].dataFiles = DataFiles([], "")
        self.goodSampleBackground.samples[0].composition = (
            Composition("")
        )
        self.goodSampleBackground.samples[0].resonanceValues = []
        self.goodSampleBackground.samples[0].exponentialValues = []
        for i in range(len(expectedSampleA.keys())):

            self.goodSampleBackground.samples = [
                self.goodSampleBackground.samples[0]
            ]
            sbgStr = str(self.goodSampleBackground)
            badSampleBackground = sbgStr.split("\n")
            del badSampleBackground[i + 10]
            badSampleBackground = "\n".join(badSampleBackground)
            with open("test_data.txt", "w", encoding="utf-8") as f:
                f.write("'  '  '        '  '/'\n\n")
                f.write(
                    "INSTRUMENT        {\n\n"
                    + str(self.goodInstrument)
                    + "\n\n}"
                )
                f.write("\n\nBEAM        {\n\n" + str(self.goodBeam) + "\n\n}")
                f.write(
                    "\n\nNORMALISATION        {\n\n"
                    + str(self.goodNormalisation)
                    + "\n\n}"
                )
                f.write("\n\n{}\n\nEND".format(str(badSampleBackground)))

            with self.assertRaises(ParserException) as cm:
                GudrunFile("test_data.txt")
                self.assertEqual(
                    "Whilst parsing Sample, an exception occured."
                    " The input file is most likely of an incorrect format, "
                    "and some attributes were missing.",
                    str(cm.exception)
                )

    def testLoadMissingSampleAttributesRand(self):

        expectedSampleA = deepcopy(self.expectedSampleA)
        expectedSampleA.pop("name", None)
        expectedSampleA.pop("dataFiles", None)
        expectedSampleA.pop("composition", None)
        expectedSampleA.pop("containers", None)
        expectedSampleA.pop("densityUnits", None)
        expectedSampleA.pop("innerRadius", None)
        expectedSampleA.pop("outerRadius", None)
        expectedSampleA.pop("sampleHeight", None)
        expectedSampleA.pop("resonanceValues", None)
        expectedSampleA.pop("exponentialValues", None)
        expectedSampleA.pop("crossSectionFilename", None)
        expectedSampleA.pop("FTMode", None)
        expectedSampleA.pop("yamlignore", None)

        self.goodSampleBackground.samples[0].dataFiles = DataFiles([], "")
        self.goodSampleBackground.samples[0].composition = (
            Composition("")
        )
        self.goodSampleBackground.samples[0].resonanceValues = []
        self.goodSampleBackground.samples[0].exponentialValues = []
        for i in range(50):
            key = random.choice(list(expectedSampleA))
            j = list(expectedSampleA).index(key)

            self.goodSampleBackground.samples = [
                self.goodSampleBackground.samples[0]
            ]
            sbgStr = str(self.goodSampleBackground)
            badSampleBackground = sbgStr.split("\n")
            del badSampleBackground[j + 10]

            badSampleBackground = "\n".join(badSampleBackground)
            with open("test_data.txt", "w", encoding="utf-8") as f:
                f.write("'  '  '        '  '/'\n\n")
                f.write(
                    "INSTRUMENT        {\n\n"
                    + str(self.goodInstrument)
                    + "\n\n}"
                )
                f.write("\n\nBEAM        {\n\n" + str(self.goodBeam) + "\n\n}")
                f.write(
                    "\n\nNORMALISATION        {\n\n"
                    + str(self.goodNormalisation)
                    + "\n\n}"
                )
                f.write("\n\n{}\n\nEND".format(str(badSampleBackground)))

            with self.assertRaises(ParserException) as cm:
                GudrunFile("test_data.txt")
                self.assertEqual(
                    "Whilst parsing Sample, an exception occured."
                    " The input file is most likely of an incorrect format, "
                    "and some attributes were missing.",
                    str(cm.exception)
                )

    def testLoadMissingContainerAttributesSeq(self):

        expectedContainerA = deepcopy(self.expectedContainerA)
        expectedContainerA.pop("name", None)
        expectedContainerA.pop("dataFiles", None)
        expectedContainerA.pop("composition", None)
        expectedContainerA.pop("densityUnits", None)
        expectedContainerA.pop("innerRadius", None)
        expectedContainerA.pop("outerRadius", None)
        expectedContainerA.pop("sampleHeight", None)
        expectedContainerA.pop("geometry", None)
        expectedContainerA.pop("attenuationCoefficient", None)
        expectedContainerA.pop("crossSectionFilename", None)
        expectedContainerA.pop("runAsSample", None)
        expectedContainerA.pop("topHatW", None)
        expectedContainerA.pop("FTMode", None)
        expectedContainerA.pop("minRadFT", None)
        expectedContainerA.pop("maxRadFT", None)
        expectedContainerA.pop("grBroadening", None)
        expectedContainerA.pop("powerForBroadening", None)
        expectedContainerA.pop("stepSize", None)
        expectedContainerA.pop("yamlignore", None)

        self.goodSampleBackground.samples[0].containers[0].dataFiles = (
            DataFiles([], "")
        )
        self.goodSampleBackground.samples[0].containers[0].composition = (
            Composition("")
        )
        for i in range(len(expectedContainerA.keys())):
            self.goodSampleBackground.samples = [
                self.goodSampleBackground.samples[0]
            ]
            sbgStr = str(self.goodSampleBackground)
            badSampleBackground = sbgStr.split("\n")
            del badSampleBackground[i + 44]
            badSampleBackground = "\n".join(badSampleBackground)

            with open("test_data.txt", "w", encoding="utf-8") as f:
                f.write("'  '  '        '  '/'\n\n")
                f.write(
                    "INSTRUMENT        {\n\n"
                    + str(self.goodInstrument)
                    + "\n\n}"
                )
                f.write("\n\nBEAM        {\n\n" + str(self.goodBeam) + "\n\n}")
                f.write(
                    "\n\nNORMALISATION        {\n\n"
                    + str(self.goodNormalisation)
                    + "\n\n}"
                )
                f.write("\n\n{}\n\nEND".format(str(badSampleBackground)))
            with self.assertRaises(ParserException) as cm:
                GudrunFile("test_data.txt")
                self.assertEqual(
                    "Whilst parsing Container, an exception occured."
                    " The input file is most likely of an incorrect format, "
                    "and some attributes were missing.",
                    str(cm.exception)
                )

    def testLoadMissingContainerAttributesRand(self):

        expectedContainerA = deepcopy(self.expectedContainerA)
        expectedContainerA.pop("name", None)
        expectedContainerA.pop("dataFiles", None)
        expectedContainerA.pop("composition", None)
        expectedContainerA.pop("densityUnits", None)
        expectedContainerA.pop("innerRadius", None)
        expectedContainerA.pop("outerRadius", None)
        expectedContainerA.pop("sampleHeight", None)
        expectedContainerA.pop("geometry", None)
        expectedContainerA.pop("attenuationCoefficient", None)
        expectedContainerA.pop("crossSectionFilename", None)
        expectedContainerA.pop("runAsSample", None)
        expectedContainerA.pop("topHatW", None)
        expectedContainerA.pop("FTMode", None)
        expectedContainerA.pop("minRadFT", None)
        expectedContainerA.pop("maxRadFT", None)
        expectedContainerA.pop("grBroadening", None)
        expectedContainerA.pop("powerForBroadening", None)
        expectedContainerA.pop("stepSize", None)
        expectedContainerA.pop("yamlignore", None)

        self.goodSampleBackground.samples[0].containers[0].dataFiles = (
            DataFiles([], "")
        )
        self.goodSampleBackground.samples[0].containers[0].composition = (
            Composition("")
        )
        for i in range(50):
            key = random.choice(list(expectedContainerA))
            j = list(expectedContainerA).index(key)

            self.goodSampleBackground.samples = [
                self.goodSampleBackground.samples[0]
            ]
            sbgStr = str(self.goodSampleBackground)
            badSampleBackground = sbgStr.split("\n")
            del badSampleBackground[j + 44]

            badSampleBackground = "\n".join(badSampleBackground)
            with open("test_data.txt", "w", encoding="utf-8") as f:
                f.write("'  '  '        '  '/'\n\n")
                f.write(
                    "INSTRUMENT        {\n\n"
                    + str(self.goodInstrument)
                    + "\n\n}"
                )
                f.write("\n\nBEAM        {\n\n" + str(self.goodBeam) + "\n\n}")
                f.write(
                    "\n\nNORMALISATION        {\n\n"
                    + str(self.goodNormalisation)
                    + "\n\n}"
                )
                f.write("\n\n{}\n\nEND".format(str(badSampleBackground)))
            with self.assertRaises(ParserException) as cm:
                GudrunFile("test_data.txt")
                self.assertEqual(
                    "Whilst parsing Container, an exception occured."
                    " The input file is most likely of an incorrect format, "
                    "and some attributes were missing.",
                    str(cm.exception)
                )

    def testZeroExitGudrun(self):

        g = GudrunFile("test/TestData/NIMROD-water/good_water.txt")
        result = g.dcs()
        self.assertEqual(result.stderr, "")
