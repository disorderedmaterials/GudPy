from enum import Enum
import os
from src.gudrun_classes.exception import ParserException
from unittest import TestCase
import random
from copy import deepcopy
from shutil import copyfile

from src.scripts.utils import spacify, numifyBool
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
    Instruments, Scales, UnitsOfDensity,
    MergeWeights, NormalisationType, OutputUnits,
    Geometry
)


class TestGudPyIO(TestCase):

    def setUp(self) -> None:
        self.expectedInstrument = {
            "name": Instruments.NIMROD,
            "GudrunInputFileDir": "/home/test/gudpy-water/",
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
            "wavelengthRangeForMonitorNormalisation": (0, 0),
            "spectrumNumbersForTransmissionMonitor": [8, 9],
            "incidentMonitorQuietCountConst": 0.0001,
            "transmissionMonitorQuietCountConst": 0.0001,
            "channelNosSpikeAnalysis": (0, 0),
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
            "GudrunStartFolder": "/home/test/src/Gudrun2017/Gudrun",
            "startupFileFolder": "/oldwork/test/water",
            "logarithmicStepSize": 0.04,
            "hardGroupEdges": True,
            "nxsDefinitionFile": "",
            "numberIterations": 2,
            "tweakTweakFactors": False
        }

        self.expectedBeam = {
            "sampleGeometry": Geometry.FLATPLATE,
            "noBeamProfileValues": 2,
            "beamProfileValues": [1.0, 1.0],
            "stepSizeAbsorption": 0.05,
            "stepSizeMS": 0.2,
            "noSlices": 100,
            "angularStepForCorrections": 10,
            "incidentBeamLeftEdge": -1.5,
            "incidentBeamRightEdge": 1.5,
            "incidentBeamTopEdge": -1.5,
            "incidentBeamBottomEdge": 1.5,
            "scatteredBeamLeftEdge": -2.1,
            "scatteredBeamRightEdge": 2.1,
            "scatteredBeamTopEdge": -2.1,
            "scatteredBeamBottomEdge": 2.1,
            "filenameIncidentBeamSpectrumParams":
                "StartupFiles/NIMROD/spectrum000.dat",
            "overallBackgroundFactor": 1.0,
            "sampleDependantBackgroundFactor": 0.0,
            "shieldingAttenuationCoefficient": 0.0,
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
                [Element("V", 0, 1.0)], "Normalisation"
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
            "totalCrossSectionSource": "TABLES",
            "normalisationDifferentialCrossSectionFile": "*",
            "lowerLimitSmoothedNormalisation": 0.01,
            "normalisationDegreeSmoothing": 1.00,
            "minNormalisationSignalBR": 0.0,
        }

        self.expectedContainerA = {
            "name": "CONTAINER N9",
            "periodNumber": 1,
            "dataFiles": DataFiles(
                [
                    "NIMROD00016694_Empty_N9.raw",
                    "NIMROD00016699_Empty_N9.raw",
                    "NIMROD00016704_Empty_N9.raw",
                ],
                "CONTAINER N9",
            ),
            "composition": Composition(
                [Element("Ti", 0, 7.16), Element("Zr", 0, 3.438)], "Container"
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
            "totalCrossSectionSource": "TABLES",
            "tweakFactor": 1.0,
            "scatteringFraction": 1.0,
            "attenuationCoefficient": 0.0
        }

        self.expectedContainerB = {
            "name": "CONTAINER N10",
            "periodNumber": 1,
            "dataFiles": DataFiles(
                [
                    "NIMROD00016695_Empty_N10.raw",
                    "NIMROD00016700_Empty_N10.raw",
                    "NIMROD00016705_Empty_N10.raw",
                ],
                "CONTAINER N10",
            ),
            "composition": Composition(
                [Element("Ti", 0, 7.16), Element("Zr", 0, 3.438)], "Container"
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
            "totalCrossSectionSource": "TABLES",
            "tweakFactor": 1.0,
            "scatteringFraction": 1.0,
            "attenuationCoefficient": 0.0
        }

        self.expectedContainerC = {
            "name": "CONTAINER N6",
            "periodNumber": 1,
            "dataFiles": DataFiles(
                ["NIMROD00014908_Empty_N6.raw"], "CONTAINER N6"
            ),
            "composition": Composition(
                [Element("Ti", 0, 7.16), Element("Zr", 0, 3.438)], "Container"
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
            "totalCrossSectionSource": "TABLES",
            "tweakFactor": 1.0,
            "scatteringFraction": 1.0,
            "attenuationCoefficient": 0.0
        }

        self.expectedContainerD = {
            "name": "CONTAINER N8",
            "periodNumber": 1,
            "dataFiles": DataFiles(
                ["NIMROD00016994_Empty_N8.raw"], "CONTAINER N8"
            ),
            "composition": Composition(
                [Element("Ti", 0, 7.16), Element("Zr", 0, 3.438)], "Container"
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
            "totalCrossSectionSource": "TABLES",
            "tweakFactor": 1.0,
            "scatteringFraction": 1.0,
            "attenuationCoefficient": 0.0
        }

        self.expectedSampleA = {
            "name": "SAMPLE H2O, Can N9",
            "periodNumber": 1,
            "dataFiles": DataFiles(
                [
                    "NIMROD00016608_H2O_in_N9.raw",
                    "NIMROD00016610_H2O_in_N9.raw",
                ],
                "SAMPLE H2O, Can N9",
            ),
            "forceCalculationOfCorrections": True,
            "composition": Composition(
                [Element("H", 0, 2.0), Element("O", 0, 1.0)], "Sample"
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
            "totalCrossSectionSource": "TRANSMISSION",
            "sampleTweakFactor": 1.0,
            "topHatW": -10.0,
            "minRadFT": 0.8,
            "grBroadening": 0.1,
            "resonanceValues": [],
            "exponentialValues": [(0.0, 1.5, 0)],
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
            "containers": [self.expectedContainerA]
        }

        self.expectedSampleB = {
            "name": "SAMPLE D2O, Can N10",
            "periodNumber": 1,
            "dataFiles": DataFiles(
                [
                    "NIMROD00016609_D2O_in_N10.raw",
                    "NIMROD00016611_D2O_in_N10.raw",
                ],
                "SAMPLE D2O, Can N10",
            ),
            "forceCalculationOfCorrections": True,
            "composition": Composition(
                [Element("H", 2, 2.0), Element("O", 0, 1.0)], "Sample"
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
            "totalCrossSectionSource": "TRANSMISSION",
            "sampleTweakFactor": 1.0,
            "topHatW": -10.0,
            "minRadFT": 0.8,
            "grBroadening": 0.0,
            "resonanceValues": [],
            "exponentialValues": [(0.0, 1.5, 0)],
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
            "containers": [self.expectedContainerB]
        }

        self.expectedSampleC = {
            "name": "SAMPLE HDO, Can N6",
            "periodNumber": 1,
            "dataFiles": DataFiles(
                [
                    "NIMROD00016741_HDO_in_N6.raw",
                    "NIMROD00016743_HDO_in_N6.raw",
                ],
                "SAMPLE HDO, Can N6",
            ),
            "forceCalculationOfCorrections": True,
            "composition": Composition(
                [
                    Element("H", 0, 1.0),
                    Element("O", 0, 1.0),
                    Element("H", 2, 1.0),
                ],
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
            "totalCrossSectionSource": "TRANSMISSION",
            "sampleTweakFactor": 1.0,
            "topHatW": -10.0,
            "minRadFT": 0.8,
            "grBroadening": 0.1,
            "resonanceValues": [],
            "exponentialValues": [(0.0, 1.5, 0)],
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
            "containers": [self.expectedContainerC]
        }

        self.expectedSampleD = {
            "name": "SAMPLE Null Water, Can N8",
            "periodNumber": 1,
            "dataFiles": DataFiles(
                [
                    "NIMROD00016742_NullWater_in_N8.raw",
                    "NIMROD00016744_NullWater_in_N8.raw",
                ],
                "SAMPLE Null Water, Can N8",
            ),
            "forceCalculationOfCorrections": True,
            "composition": Composition(
                [
                    Element("H", 0, 1.281),
                    Element("O", 0, 1.0),
                    Element("H", 2, 0.7185),
                ],
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
            "totalCrossSectionSource": "TRANSMISSION",
            "sampleTweakFactor": 1.0,
            "topHatW": -10.0,
            "minRadFT": 0.8,
            "grBroadening": 0.1,
            "resonanceValues": [],
            "exponentialValues": [(0.0, 1.5, 0)],
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
            "containers": [self.expectedContainerD]
        }

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

        path = "TestData/NIMROD-water/water.txt"

        if os.name == "nt":
            from pathlib import Path
            dirpath = Path().resolve() / "tests/" / Path(path)
        else:
            dirpath = (
                "/".join(os.path.realpath(__file__).split("/")[:-1])
                + "/"
                + path
            )
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

        copyfile(self.g.path, "tests/TestData/NIMROD-water/good_water.txt")
        g = GudrunFile("tests/TestData/NIMROD-water/good_water.txt")

        from pathlib import Path

        parent = Path("tests").parent.absolute()
        GudrunStartFolder = parent / "bin"
        dataFileDir = Path("tests/TestData/NIMROD-water/raw").absolute()

        g.instrument.GudrunStartFolder = GudrunStartFolder
        g.instrument.dataFileDir = str(dataFileDir) + "/"
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
        outlines = open(self.g.outpath, encoding="utf-8").read()
        self.assertEqual(outlines, str(self.g))

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
                else:
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
                    valueInLines(value, inlines)

    def testRewriteGudrunFile(self):
        self.g.write_out()
        g1 = GudrunFile(self.g.outpath)
        g1.write_out()

        self.assertEqual(
            open(g1.outpath, encoding="utf-8").read()[:-5], str(self.g)[:-5]
        )
        self.assertEqual(
            open(g1.outpath, encoding="utf-8").read()[:-5], str(g1)[:-5]
        )
        self.assertEqual(
            open(g1.outpath, encoding="utf-8").read()[:-5],
            open(self.g.outpath, encoding="utf-8").read()[:-5],
        )

    def testReloadGudrunFile(self):
        self.g.write_out()
        g1 = GudrunFile(self.g.outpath)
        self.assertEqual(str(g1), str(self.g))

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
        expectedInstrument.pop("groupingParameterPanel")
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
        self.goodNormalisation.dataFiles = DataFiles([], "")
        self.goodNormalisation.composition = (
            Composition([], "")
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
        self.goodNormalisation.dataFiles = DataFiles([], "")
        self.goodNormalisation.composition = (
            Composition([], "")
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
        self.goodSampleBackground.samples[0].dataFiles = DataFiles([], "")
        self.goodSampleBackground.samples[0].composition = (
            Composition([], "")
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
        self.goodSampleBackground.samples[0].dataFiles = DataFiles([], "")
        self.goodSampleBackground.samples[0].composition = (
            Composition([], "")
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
        expectedContainerA.pop("attenuationCoefficient")
        self.goodSampleBackground.samples[0].containers[0].dataFiles = (
            DataFiles([], "")
        )
        self.goodSampleBackground.samples[0].containers[0].composition = (
            Composition([], "")
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
        expectedContainerA.pop("attenuationCoefficient")
        self.goodSampleBackground.samples[0].containers[0].dataFiles = (
            DataFiles([], "")
        )
        self.goodSampleBackground.samples[0].containers[0].composition = (
            Composition([], "")
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

        g = GudrunFile("tests/TestData/NIMROD-water/good_water.txt")
        result = g.dcs()
        self.assertEqual(result.stderr, "")
