import sys
import os
from unittest import TestCase, skip
import random
from copy import deepcopy
from shutil import copyfile

try:
    sys.path.insert(1, os.path.join(sys.path[0], "../gudrun_classes"))
    sys.path.insert(2, os.path.join(sys.path[0], "../scripts"))
    from utils import spacify, numifyBool
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
except ModuleNotFoundError:
    sys.path.insert(1, os.path.join(sys.path[0], "gudrun_classes"))
    sys.path.insert(2, os.path.join(sys.path[0], "scripts"))
    from scripts.utils import spacify, numifyBool
    from gudrun_classes.gudrun_file import GudrunFile
    from gudrun_classes.beam import Beam
    from gudrun_classes.composition import Composition
    from gudrun_classes.container import Container
    from gudrun_classes.data_files import DataFiles
    from gudrun_classes.element import Element
    from gudrun_classes.instrument import Instrument
    from gudrun_classes.normalisation import Normalisation
    from gudrun_classes.sample_background import SampleBackground
    from gudrun_classes.sample import Sample


class TestGudPyIO(TestCase):

    def setUp(self) -> None:
        self.expectedInstrument = {
            "name": "NIMROD",
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
            "groupingParameterPanel": (0, 0.0, 0.0, 0.0),
            "groupsAcceptanceFactor": 1.0,
            "mergePower": 4,
            "subSingleAtomScattering": False,
            "byChannel": 2,
            "incidentFlightPath": 20.0,
            "spectrumNumberForOutputDiagnosticFiles": 0,
            "neutronScatteringParametersFile":
                "StartupFiles/NIMROD/sears91_gudrun.dat",
            "scaleSelection": 1,
            "subWavelengthBinnedData": 0,
            "GudrunStartFolder": "/home/test/src/Gudrun2017/Gudrun",
            "startupFileFolder": "/oldwork/test/water",
            "logarithmicStepSize": 0.04,
            "hardGroupEdges": True,
            "numberIterations": 2,
            "tweakTweakFactors": False
        }

        self.expectedBeam = {
            "sampleGeometry": "FLATPLATE",
            "noBeamProfileValues": 2,
            "beamProfileValues": [1.0, 1.0],
            "stepSizeAbsorptionMSNoSlices": (0.05, 0.2, 100),
            "angularStepForCorrections": 10,
            "incidentBeamEdgesRelCentroid": (-1.5, 1.5, -1.5, 1.5),
            "scatteredBeamEdgesRelCentroid": (-2.1, 2.1, -2.1, 2.1),
            "filenameIncidentBeamSpectrumParams":
                "StartupFiles/NIMROD/spectrum000.dat",
            "overallBackgroundFactor": 1.0,
            "sampleDependantBackgroundFactor": 0.0,
            "shieldingAttenuationCoefficient": 0.0,
        }

        self.expectedNormalisation = {
            "numberOfFilesPeriodNumber": (1, 1),
            "dataFiles": DataFiles(["NIMROD00016702_V.raw"], "NORMALISATION"),
            "numberOfFilesPeriodNumberBg": (2, 1),
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
            "geometry": "SameAsBeam",
            "thickness": (0.15, 0.15),
            "angleOfRotationSampleWidth": (0.0, 5),
            "densityOfAtoms": -0.0721,
            "tempForNormalisationPC": 200,
            "totalCrossSectionSource": "TABLES",
            "normalisationDifferentialCrossSectionFilename": "*",
            "lowerLimitSmoothedNormalisation": 0.01,
            "normalisationDegreeSmoothing": 1.00,
            "minNormalisationSignalBR": 0.0,
        }

        self.expectedContainerA = {
            "name": "CONTAINER N9",
            "numberOfFilesPeriodNumber": (3, 1),
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
            "geometry": "SameAsBeam",
            "thickness": (0.1, 0.1),
            "angleOfRotationSampleWidth": (0, 5),
            "densityOfAtoms": -0.0542,
            "totalCrossSectionSource": "TABLES",
            "tweakFactor": 1.0,
            "scatteringFractionAttenuationCoefficient": (1.0, 0.0),
        }

        self.expectedContainerB = {
            "name": "CONTAINER N10",
            "numberOfFilesPeriodNumber": (3, 1),
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
            "geometry": "SameAsBeam",
            "thickness": (0.1, 0.1),
            "angleOfRotationSampleWidth": (0, 5),
            "densityOfAtoms": -0.0542,
            "totalCrossSectionSource": "TABLES",
            "tweakFactor": 1.0,
            "scatteringFractionAttenuationCoefficient": (1.0, 0.0),
        }

        self.expectedContainerC = {
            "name": "CONTAINER N6",
            "numberOfFilesPeriodNumber": (1, 1),
            "dataFiles": DataFiles(
                ["NIMROD00014908_Empty_N6.raw"], "CONTAINER N6"
            ),
            "composition": Composition(
                [Element("Ti", 0, 7.16), Element("Zr", 0, 3.438)], "Container"
            ),
            "geometry": "SameAsBeam",
            "thickness": (0.1, 0.1),
            "angleOfRotationSampleWidth": (0, 5),
            "densityOfAtoms": -0.0542,
            "totalCrossSectionSource": "TABLES",
            "tweakFactor": 1.0,
            "scatteringFractionAttenuationCoefficient": (1.0, 0.0),
        }

        self.expectedContainerD = {
            "name": "CONTAINER N8",
            "numberOfFilesPeriodNumber": (1, 1),
            "dataFiles": DataFiles(
                ["NIMROD00016994_Empty_N8.raw"], "CONTAINER N8"
            ),
            "composition": Composition(
                [Element("Ti", 0, 7.16), Element("Zr", 0, 3.438)], "Container"
            ),
            "geometry": "SameAsBeam",
            "thickness": (0.1, 0.1),
            "angleOfRotationSampleWidth": (0, 5),
            "densityOfAtoms": -0.0542,
            "totalCrossSectionSource": "TABLES",
            "tweakFactor": 1.0,
            "scatteringFractionAttenuationCoefficient": (1.0, 0.0),
        }

        self.expectedSampleA = {
            "name": "SAMPLE H2O, Can N9",
            "numberOfFilesPeriodNumber": (2, 1),
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
            "geometry": "SameAsBeam",
            "thickness": (0.05, 0.05),
            "angleOfRotationSampleWidth": (0, 5),
            "densityOfAtoms": -0.1,
            "tempForNormalisationPC": 0,
            "totalCrossSectionSource": "TRANSMISSION",
            "sampleTweakFactor": 1.0,
            "topHatW": -10.0,
            "minRadFT": 0.8,
            "grBroadening": 0.1,
            "expAandD": (0.0, 1.5, 0),
            "normalisationCorrectionFactor": 1.0,
            "fileSelfScattering": "NIMROD00016608_H2O_in_N9.msubw01",
            "normaliseTo": 0,
            "maxRadFT": 50.0,
            "outputUnits": 0,
            "powerForBroadening": 0.5,
            "stepSize": 0.03,
            "include": True,
            "environementScatteringFuncAttenuationCoeff": (1.0, 0.0),
            "containers": [self.expectedContainerA],
            "runThisSample": True
        }

        self.expectedSampleB = {
            "name": "SAMPLE D2O, Can N10",
            "numberOfFilesPeriodNumber": (2, 1),
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
            "geometry": "SameAsBeam",
            "thickness": (0.05, 0.05),
            "angleOfRotationSampleWidth": (0, 5),
            "densityOfAtoms": -0.1,
            "tempForNormalisationPC": 0,
            "totalCrossSectionSource": "TRANSMISSION",
            "sampleTweakFactor": 1.0,
            "topHatW": -10.0,
            "minRadFT": 0.8,
            "grBroadening": 0.0,
            "expAandD": (0.0, 1.5, 0),
            "normalisationCorrectionFactor": 1.0,
            "fileSelfScattering": "NIMROD00016609_D2O_in_N10.msubw01",
            "normaliseTo": 0,
            "maxRadFT": 50.0,
            "outputUnits": 0,
            "powerForBroadening": 0.0,
            "stepSize": 0.03,
            "include": True,
            "environementScatteringFuncAttenuationCoeff": (1.0, 0.0),
            "containers": [self.expectedContainerB],
            "runThisSample": True
        }

        self.expectedSampleC = {
            "name": "SAMPLE HDO, Can N6",
            "numberOfFilesPeriodNumber": (2, 1),
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
            "geometry": "SameAsBeam",
            "thickness": (0.05, 0.05),
            "angleOfRotationSampleWidth": (0, 5),
            "densityOfAtoms": -0.1,
            "tempForNormalisationPC": 0,
            "totalCrossSectionSource": "TRANSMISSION",
            "sampleTweakFactor": 1.0,
            "topHatW": -10.0,
            "minRadFT": 0.8,
            "grBroadening": 0.1,
            "expAandD": (0.0, 1.5, 0),
            "normalisationCorrectionFactor": 1.0,
            "fileSelfScattering": "NIMROD00016741_HDO_in_N6.msubw01",
            "normaliseTo": 0,
            "maxRadFT": 50.0,
            "outputUnits": 0,
            "powerForBroadening": 0.5,
            "stepSize": 0.03,
            "include": True,
            "environementScatteringFuncAttenuationCoeff": (1.0, 0.0),
            "containers": [self.expectedContainerC],
            "runThisSample": True
        }

        self.expectedSampleD = {
            "name": "SAMPLE Null Water, Can N8",
            "numberOfFilesPeriodNumber": (2, 1),
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
            "geometry": "SameAsBeam",
            "thickness": (0.05, 0.05),
            "angleOfRotationSampleWidth": (0, 5),
            "densityOfAtoms": -0.1,
            "tempForNormalisationPC": 0,
            "totalCrossSectionSource": "TRANSMISSION",
            "sampleTweakFactor": 1.0,
            "topHatW": -10.0,
            "minRadFT": 0.8,
            "grBroadening": 0.1,
            "expAandD": (0.0, 1.5, 0),
            "normalisationCorrectionFactor": 1.0,
            "fileSelfScattering": "NIMROD00016742_NullWater_in_N8.msubw01",
            "normaliseTo": 0,
            "maxRadFT": 50.0,
            "outputUnits": 0,
            "powerForBroadening": 0.5,
            "stepSize": 0.03,
            "include": True,
            "environementScatteringFuncAttenuationCoeff": (1.0, 0.0),
            "containers": [self.expectedContainerD],
            "runThisSample": True
        }

        self.expectedSampleBackground = {
            "numberOfFilesPeriodNumber": (2, 1),
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
        self.goodSampleBackground.numberOfFilesPeriodNumber = (
            self.expectedSampleBackground["numberOfFilesPeriodNumber"]
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

        if os.path.isfile("test_data.txt"):
            os.remove("test_data.txt")
        if os.path.isfile("tests/TestData/NIMROD-water/good_water.txt"):
            os.remove("tests/TestData/NIMROD-water/good_water.txt")

        for f in os.listdir():
            if f not in self.keepsakes:
                os.remove(f)

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
                if isinstance(value[0], dict):
                    for val in value:
                        for val_ in val.values():
                            valueInLines(val_, lines)
                else:
                    if value == (0, 0.0, 0.0, 0.0):
                        return
                    self.assertTrue(
                        spacify(value) in lines
                        or spacify(value, num_spaces=2) in lines
                    )
            elif isinstance(value, bool):
                self.assertTrue(str(numifyBool(value)) in lines)
            else:
                if "        " in str(value):
                    self.assertTrue(str(value).split("        ")[0] in lines)
                else:
                    self.assertTrue(str(value) in lines)

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
        with self.assertRaises(ValueError) as cm:
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
            f.write("BEAM        {\n\n" + str(self.goodBeam) + "\n\n}")
            f.write(
                "NORMALISATION        {\n\n"
                + str(self.goodNormalisation)
                + "\n\n}"
            )

        with self.assertRaises(ValueError) as cm:
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
                "INSTRUMENT        {\n\n" + str(self.goodInstrument) + "\n\n}"
            )
            f.write(
                "NORMALISATION        {\n\n"
                + str(self.goodNormalisation)
                + "\n\n}"
            )

        with self.assertRaises(ValueError) as cm:
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
                "INSTRUMENT        {\n\n" + str(self.goodInstrument) + "\n\n}"
            )
            f.write("BEAM        {\n\n" + str(self.goodBeam) + "\n\n}")

        with self.assertRaises(ValueError) as cm:
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

        with self.assertRaises(ValueError) as cm:
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

        with self.assertRaises(ValueError) as cm:
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

        with self.assertRaises(ValueError) as cm:
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

        for i, key in enumerate(expectedInstrument.keys()):
            if key == "groupingParameterPanel":
                continue

            badInstrument = str(self.goodInstrument).split("\n")
            del badInstrument[i]
            badInstrument = "\n".join(badInstrument)

            with open("test_data.txt", "w", encoding="utf-8") as f:
                f.write("'  '  '        '  '/'\n\n")
                f.write(
                    "INSTRUMENT        {\n\n" + str(badInstrument) + "\n\n}"
                )

            with self.assertRaises(ValueError) as cm:
                GudrunFile("test_data.txt")

            if key == "XMin":
                self.assertEqual(
                    'Whilst parsing INSTRUMENT, Xmin,'
                    ' Xmax, XStep was not found',
                    str(cm.exception),
                )
            elif key == "wavelengthMin":
                self.assertEqual(
                    'Whilst parsing INSTRUMENT'
                    ', wavelengthMin, wavelengthMax,'
                    ' wavelengthStep was not found',
                    str(cm.exception),
                )
            else:
                self.assertEqual(
                    "Whilst parsing INSTRUMENT, {} was not found".format(key),
                    str(cm.exception),
                )
            os.remove("test_data.txt")

    def testLoadMissingInstrumentAttributesRand(self):

        expectedInstrument = deepcopy(self.expectedInstrument)
        expectedInstrument.pop("XMax", None)
        expectedInstrument.pop("XStep", None)
        expectedInstrument.pop("wavelengthMax", None)
        expectedInstrument.pop("wavelengthStep", None)
        expectedInstrument.pop("useLogarithmicBinning", None)

        for i in range(50):

            key = random.choice(list(expectedInstrument))
            j = list(expectedInstrument).index(key)
            if key == "groupingParameterPanel":
                continue

            badInstrument = str(self.goodInstrument).split("\n")
            del badInstrument[j]
            badInstrument = "\n".join(badInstrument)

            with open("test_data.txt", "w", encoding="utf-8") as f:
                f.write("'  '  '        '  '/'\n\n")
                f.write(
                    "INSTRUMENT        {\n\n" + str(badInstrument) + "\n\n}"
                )
            with self.assertRaises(ValueError) as cm:
                GudrunFile("test_data.txt")
            if key == "XMin":
                self.assertEqual(
                    'Whilst parsing INSTRUMENT, Xmin,'
                    ' Xmax, XStep was not found',
                    str(cm.exception),
                )
            elif key == "wavelengthMin":
                self.assertEqual(
                    'Whilst parsing INSTRUMENT'
                    ', wavelengthMin, wavelengthMax,'
                    ' wavelengthStep was not found',
                    str(cm.exception),
                )
            else:
                self.assertEqual(
                    "Whilst parsing INSTRUMENT, {} was not found".format(key),
                    str(cm.exception),
                )
            os.remove("test_data.txt")

    def testLoadMissingBeamAttributesSeq(self):

        for i, key in enumerate(self.expectedBeam.keys()):

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

            with self.assertRaises(ValueError) as cm:
                GudrunFile("test_data.txt")
            self.assertEqual(
                "Whilst parsing BEAM, {} was not found".format(key),
                str(cm.exception),
            )
            os.remove("test_data.txt")

    def testLoadMissingBeamAttributesRand(self):

        for i in range(50):

            key = random.choice(list(self.expectedBeam))
            j = list(self.expectedBeam).index(key)

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

            with self.assertRaises(ValueError) as cm:
                GudrunFile("test_data.txt")
            self.assertEqual(
                "Whilst parsing BEAM, {} was not found".format(key),
                str(cm.exception),
            )
            os.remove("test_data.txt")

    def testLoadMissingNormalisationAttributesSeq(self):

        for i, key in enumerate(self.expectedNormalisation.keys()):

            if i > 3:
                i += 1
            if i > 5:
                i += 1

            if key in ["dataFiles", "dataFilesBg", "composition"]:
                continue

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

            with self.assertRaises(ValueError) as cm:
                GudrunFile("test_data.txt")
            self.assertEqual(
                "Whilst parsing NORMALISATION, {} was not found".format(key),
                str(cm.exception),
            )
            os.remove("test_data.txt")

    def testLoadMissingNormalisationAttributesRand(self):

        for i in range(50):

            key = random.choice(list(self.expectedNormalisation))

            if key in ["dataFiles", "dataFilesBg", "composition"]:
                continue

            j = list(self.expectedNormalisation).index(key)

            if j > 3:
                j += 1
            if j > 5:
                j += 1

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

            with self.assertRaises(ValueError) as cm:
                GudrunFile("test_data.txt")
            self.assertEqual(
                "Whilst parsing NORMALISATION, {} was not found".format(key),
                str(cm.exception),
            )
            os.remove("test_data.txt")

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

        with self.assertRaises(ValueError) as cm:
            GudrunFile("test_data.txt")
        self.assertEqual((
            'Whilst parsing SAMPLE BACKGROUND 1'
            ', numberOfFilesPeriodNumber was not found'),
            str(cm.exception),
        )
        os.remove("test_data.txt")

    def testLoadMissingSampleAttributesSeq(self):

        ignore = (
            [
                "name", "dataFiles",
                "composition", "containers",
                "runThisSample"
            ]
        )

        for i, key in enumerate(self.expectedSampleA.keys()):
            if key in ignore:
                continue

            if i == 1:
                i = 0
            if i >= 5:
                i += 2
            if i >= 17:
                i += 1
            if i >= 19:
                i += 1

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
            with self.assertRaises(ValueError) as cm:
                GudrunFile("test_data.txt")
            self.assertEqual(
                "Whilst parsing {}, {} was not found".format(
                    self.expectedSampleA["name"], key
                ),
                str(cm.exception),
            )
            os.remove("test_data.txt")

    def testLoadMissingSampleAttributesRand(self):

        ignore = (
            [
                "name", "dataFiles",
                "composition", "containers",
                "runThisSample"
            ]
        )

        for i in range(50):
            key = random.choice(list(self.expectedSampleA))
            j = list(self.expectedSampleA).index(key)
            if key in ignore:
                continue

            if j == 1:
                j = 0
            if j >= 5:
                j += 2
            if j >= 17:
                j += 1
            if j >= 19:
                j += 1
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
            with self.assertRaises(ValueError) as cm:
                GudrunFile("test_data.txt")
            self.assertEqual(
                "Whilst parsing {}, {} was not found".format(
                    self.expectedSampleA["name"], key
                ),
                str(cm.exception),
            )
            os.remove("test_data.txt")

    def testLoadMissingContainerAttributesSeq(self):
        for i, key in enumerate(self.expectedContainerA.keys()):
            if key in ["name", "dataFiles", "composition"]:
                continue
            if i == 1:
                i = 0
            if i >= 2:
                i += 3

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
            with self.assertRaises(ValueError) as cm:
                GudrunFile("test_data.txt")
            self.assertEqual(
                "Whilst parsing {}, {} was not found".format(
                    self.expectedContainerA["name"], key
                ),
                str(cm.exception),
            )
            os.remove("test_data.txt")

    def testLoadMissingContainerAttributesRand(self):
        for i in range(50):
            key = random.choice(list(self.expectedContainerA))
            j = list(self.expectedContainerA).index(key)
            if key in ["name", "dataFiles", "composition"]:
                continue

            if j == 1:
                j = 0
            if j >= 2:
                j += 3
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
            with self.assertRaises(ValueError) as cm:
                GudrunFile("test_data.txt")
            self.assertEqual(
                "Whilst parsing {}, {} was not found".format(
                    self.expectedContainerA["name"], key
                ),
                str(cm.exception),
            )
            os.remove("test_data.txt")

    def testZeroExitGudrun(self):

        g = GudrunFile("tests/TestData/NIMROD-water/good_water.txt")
        result = g.dcs()
        self.assertEqual(result.stderr, "")

    def testGudrunMakesSpikeFile(self):
        g = GudrunFile("tests/TestData/NIMROD-water/good_water.txt")
        g.dcs()
        self.assertTrue("spike.dat" in os.listdir())

    def testGudrunMakesDeadtimeFile(self):
        g = GudrunFile("tests/TestData/NIMROD-water/good_water.txt")
        g.dcs()
        self.assertTrue("deadtime.cor" in os.listdir())

    def testGudrunMakesParFile(self):
        g = GudrunFile("tests/TestData/NIMROD-water/good_water.txt")
        g.dcs()
        self.assertTrue("gudrun_run_par.dat" in os.listdir())

    def testGudrunMakesGrpFile(self):
        g = GudrunFile("tests/TestData/NIMROD-water/good_water.txt")
        g.dcs()
        self.assertTrue("gudrun_grp.dat" in os.listdir())

    def testGudrunMakesCalibFile(self):
        g = GudrunFile("tests/TestData/NIMROD-water/good_water.txt")
        g.dcs()
        self.assertTrue("gudrun_calib.dat" in os.listdir())

    def testGudrunMakesVanTcbFile(self):
        g = GudrunFile("tests/TestData/NIMROD-water/good_water.txt")
        g.dcs()
        self.assertTrue("gudrun_van_tcb.dat" in os.listdir())

    def testGudrunMakesSamTcbFile(self):
        g = GudrunFile("tests/TestData/NIMROD-water/good_water.txt")
        g.dcs()
        self.assertTrue("gudrun_sam_tcb.dat" in os.listdir())

    def testGudrunMakesVanFile(self):
        g = GudrunFile("tests/TestData/NIMROD-water/good_water.txt")
        g.dcs()
        self.assertTrue("vanadium.soq" in os.listdir())

    def testGudrunMakesVansmoFile(self):
        g = GudrunFile("tests/TestData/NIMROD-water/good_water.txt")
        g.dcs()
        self.assertTrue("vansmo.par" in os.listdir())

    def testGudrunMakesRan1File(self):
        g = GudrunFile("tests/TestData/NIMROD-water/good_water.txt")
        g.dcs()
        self.assertTrue("ran1.dat" in os.listdir())

    def testGudrunMakesPolyCoeffFile(self):
        g = GudrunFile("tests/TestData/NIMROD-water/good_water.txt")
        g.dcs()
        self.assertTrue("polyfitcoeff.text" in os.listdir())

    def testGudrunMakesRunfactorFile(self):
        g = GudrunFile("tests/TestData/NIMROD-water/good_water.txt")
        g.dcs()
        self.assertTrue("runfactor_list.dat" in os.listdir())

    def testGudrunMakesAbsFile(self):
        g = GudrunFile("tests/TestData/NIMROD-water/good_water.txt")
        g.dcs()
        for sampleBackground in g.sampleBackgrounds:
            for sample in sampleBackground.samples:
                file = sample.dataFiles.dataFiles[0].replace(
                    g.instrument.dataFileType, "abs01"
                )
                self.assertTrue(file in os.listdir())

    @skip
    def testGudrunMakesAbscorFile(self):
        g = GudrunFile("tests/TestData/NIMROD-water/good_water.txt")
        g.dcs()

        if g.instrument.spectrumNumberForOutputDiagnosticFiles:
            for sampleBackground in g.sampleBackgrounds:
                for sample in sampleBackground.samples:
                    file = sample.dataFiles.dataFiles[0].replace(
                        g.instrument.dataFileType, "abscor"
                    )
                    self.assertTrue(file in os.listdir())
        else:
            for sampleBackground in g.sampleBackgrounds:
                for sample in sampleBackground.samples:
                    file = sample.dataFiles.dataFiles[0].replace(
                        g.instrument.dataFileType, "abscor"
                    )
                    self.assertFalse(file in os.listdir())

    def testGudrunMakesBak(self):
        g = GudrunFile("tests/TestData/NIMROD-water/good_water.txt")
        g.dcs()
        for sampleBackground in g.sampleBackgrounds:
            for sample in sampleBackground.samples:
                file = sample.dataFiles.dataFiles[0].replace(
                    g.instrument.dataFileType, "bak"
                )
                self.assertTrue(file in os.listdir())

    @skip
    def testGudrunMakesCnt(self):
        g = GudrunFile("tests/TestData/NIMROD-water/good_water.txt")
        g.dcs()

        if g.instrument.spectrumNumberForOutputDiagnosticFiles:
            for sampleBackground in g.sampleBackgrounds:
                for sample in sampleBackground.samples:
                    file = sample.dataFiles.dataFiles[0].replace(
                        g.instrument.dataFileType, "cnt"
                    )
                    self.assertTrue(file in os.listdir())
        else:
            for sampleBackground in g.sampleBackgrounds:
                for sample in sampleBackground.samples:
                    file = sample.dataFiles.dataFiles[0].replace(
                        g.instrument.dataFileType, "cnt"
                    )
                    self.assertFalse(file in os.listdir())

    def testGudrunMakesGr1(self):
        g = GudrunFile("tests/TestData/NIMROD-water/good_water.txt")
        g.dcs()
        for sampleBackground in g.sampleBackgrounds:
            for sample in sampleBackground.samples:
                file = sample.dataFiles.dataFiles[0].replace(
                    g.instrument.dataFileType, "gr1"
                )
                self.assertTrue(file in os.listdir())

    def testGudrunMakesGr2(self):
        g = GudrunFile("tests/TestData/NIMROD-water/good_water.txt")
        g.dcs()
        for sampleBackground in g.sampleBackgrounds:
            for sample in sampleBackground.samples:
                file = sample.dataFiles.dataFiles[0].replace(
                    g.instrument.dataFileType, "gr2"
                )
                self.assertTrue(file in os.listdir())

    def testGudrunMakesGud(self):
        g = GudrunFile("tests/TestData/NIMROD-water/good_water.txt")
        g.dcs()
        for sampleBackground in g.sampleBackgrounds:
            for sample in sampleBackground.samples:
                file = sample.dataFiles.dataFiles[0].replace(
                    g.instrument.dataFileType, "gud"
                )
                self.assertTrue(file in os.listdir())

    @skip
    def testGudrunMakesMerge(self):
        g = GudrunFile("tests/TestData/NIMROD-water/good_water.txt")
        g.dcs()

        if g.instrument.spectrumNumberForOutputDiagnosticFiles:
            for sampleBackground in g.sampleBackgrounds:
                for sample in sampleBackground.samples:
                    file = sample.dataFiles.dataFiles[0].replace(
                        g.instrument.dataFileType, "merge"
                    )
                    self.assertTrue(file in os.listdir())
        else:
            for sampleBackground in g.sampleBackgrounds:
                for sample in sampleBackground.samples:
                    file = sample.dataFiles.dataFiles[0].replace(
                        g.instrument.dataFileType, "merge"
                    )
                    self.assertFalse(file in os.listdir())

    def testGudrunMakesModule(self):
        g = GudrunFile("tests/TestData/NIMROD-water/good_water.txt")
        g.dcs()

        self.assertTrue("vanadium.module" in os.listdir())
        self.assertTrue("vanadium_back.module" in os.listdir())
        self.assertTrue("sample_back.module" in os.listdir())
        if len(g.sampleBackgrounds[0].samples) > 0:
            self.assertTrue("sample.module" in os.listdir())

    def testGudrunMakesMul01(self):
        g = GudrunFile("tests/TestData/NIMROD-water/good_water.txt")
        g.dcs()

        file = g.normalisation.dataFiles.dataFiles[0].replace(
            g.instrument.dataFileType, "mul01"
        )

        self.assertTrue(file in os.listdir())

        for sampleBackground in g.sampleBackgrounds:
            for sample in sampleBackground.samples:
                file = sample.dataFiles.dataFiles[0].replace(
                    g.instrument.dataFileType, "mul01"
                )
                self.assertTrue(file in os.listdir())
                file = (
                    sample.containers[0]
                    .dataFiles.dataFiles[0]
                    .replace(g.instrument.dataFileType, "mul01")
                )
                self.assertTrue(file in os.listdir())

    @skip
    def testGudrunMakesMulcor(self):
        g = GudrunFile("tests/TestData/NIMROD-water/good_water.txt")
        g.dcs()

        if g.instrument.spectrumNumberForOutputDiagnosticFiles:
            for sampleBackground in g.sampleBackgrounds:
                for sample in sampleBackground.samples:
                    file = sample.dataFiles.dataFiles[0].replace(
                        g.instrument.dataFileType, "mulcor"
                    )
                    self.assertTrue(file in os.listdir())
        else:
            for sampleBackground in g.sampleBackgrounds:
                for sample in sampleBackground.samples:
                    file = sample.dataFiles.dataFiles[0].replace(
                        g.instrument.dataFileType, "mulcor"
                    )
                    self.assertFalse(file in os.listdir())

    def testGudrunMakesMut01(self):
        g = GudrunFile("tests/TestData/NIMROD-water/good_water.txt")
        g.dcs()

        file = g.normalisation.dataFiles.dataFiles[0].replace(
            g.instrument.dataFileType, "mut01"
        )

        self.assertTrue(file in os.listdir())

        for sampleBackground in g.sampleBackgrounds:
            for sample in sampleBackground.samples:
                file = sample.dataFiles.dataFiles[0].replace(
                    g.instrument.dataFileType, "mut01"
                )
                self.assertTrue(file in os.listdir())
                file = (
                    sample.containers[0]
                    .dataFiles.dataFiles[0]
                    .replace(g.instrument.dataFileType, "mul01")
                )
                self.assertTrue(file in os.listdir())

    @skip
    def testGudrunMakesNormmon(self):
        g = GudrunFile("tests/TestData/NIMROD-water/good_water.txt")
        g.dcs()

        if g.instrument.spectrumNumberForOutputDiagnosticFiles:
            for sampleBackground in g.sampleBackgrounds:
                for sample in sampleBackground.samples:
                    file = sample.dataFiles.dataFiles[0].replace(
                        g.instrument.dataFileType, "normmon"
                    )
                    self.assertTrue(file in os.listdir())
        else:
            for sampleBackground in g.sampleBackgrounds:
                for sample in sampleBackground.samples:
                    file = sample.dataFiles.dataFiles[0].replace(
                        g.instrument.dataFileType, "normmon"
                    )
                    self.assertFalse(file in os.listdir())

    @skip
    def testGudrunMakesNormvan(self):
        g = GudrunFile("tests/TestData/NIMROD-water/good_water.txt")
        g.dcs()

        if g.instrument.spectrumNumberForOutputDiagnosticFiles:
            for sampleBackground in g.sampleBackgrounds:
                for sample in sampleBackground.samples:
                    file = sample.dataFiles.dataFiles[0].replace(
                        g.instrument.dataFileType, "normvan"
                    )
                    self.assertTrue(file in os.listdir())
        else:
            for sampleBackground in g.sampleBackgrounds:
                for sample in sampleBackground.samples:
                    file = sample.dataFiles.dataFiles[0].replace(
                        g.instrument.dataFileType, "normvan"
                    )
                    self.assertFalse(file in os.listdir())

    def testGudrunMakesPla01(self):
        g = GudrunFile("tests/TestData/NIMROD-water/good_water.txt")
        g.dcs()

        file = g.normalisation.dataFiles.dataFiles[0].replace(
            g.instrument.dataFileType, "pla01"
        )

        self.assertTrue(file in os.listdir())

        for sampleBackground in g.sampleBackgrounds:
            for sample in sampleBackground.samples:
                file = sample.dataFiles.dataFiles[0].replace(
                    g.instrument.dataFileType, "pla01"
                )
                self.assertTrue(file in os.listdir())

    @skip
    def testGudrunMakesPreMerge(self):
        g = GudrunFile("tests/TestData/NIMROD-water/good_water.txt")
        g.dcs()

        if g.instrument.spectrumNumberForOutputDiagnosticFiles:
            for sampleBackground in g.sampleBackgrounds:
                for sample in sampleBackground.samples:
                    file = sample.dataFiles.dataFiles[0].replace(
                        g.instrument.dataFileType, "premerge"
                    )
                    self.assertTrue(file in os.listdir())
        else:
            for sampleBackground in g.sampleBackgrounds:
                for sample in sampleBackground.samples:
                    file = sample.dataFiles.dataFiles[0].replace(
                        g.instrument.dataFileType, "premerge"
                    )
                    self.assertFalse(file in os.listdir())

    def testGudrunMakesRawmon(self):
        g = GudrunFile("tests/TestData/NIMROD-water/good_water.txt")
        g.dcs()

        file = g.normalisation.dataFiles.dataFiles[0].replace(
            g.instrument.dataFileType, "rawmon"
        )

        self.assertTrue(file in os.listdir())

        for sampleBackground in g.sampleBackgrounds:

            file = sampleBackground.dataFiles.dataFiles[0].replace(
                g.instrument.dataFileType, "rawmon"
            )
            self.assertTrue(file in os.listdir())

            for sample in sampleBackground.samples:
                file = sample.dataFiles.dataFiles[0].replace(
                    g.instrument.dataFileType, "rawmon"
                )
                self.assertTrue(file in os.listdir())
                file = (
                    sample.containers[0]
                    .dataFiles.dataFiles[0]
                    .replace(g.instrument.dataFileType, "rawmon")
                )
                self.assertTrue(file in os.listdir())

    def testGudrunMakesRawtrans(self):
        g = GudrunFile("tests/TestData/NIMROD-water/good_water.txt")
        g.dcs()

        file = g.normalisation.dataFiles.dataFiles[0].replace(
            g.instrument.dataFileType, "rawtrans"
        )

        self.assertTrue(file in os.listdir())

        for sampleBackground in g.sampleBackgrounds:

            file = sampleBackground.dataFiles.dataFiles[0].replace(
                g.instrument.dataFileType, "rawtrans"
            )
            self.assertTrue(file in os.listdir())

            for sample in sampleBackground.samples:
                file = sample.dataFiles.dataFiles[0].replace(
                    g.instrument.dataFileType, "rawtrans"
                )
                self.assertTrue(file in os.listdir())
                file = (
                    sample.containers[0]
                    .dataFiles.dataFiles[0]
                    .replace(g.instrument.dataFileType, "rawtrans")
                )
                self.assertTrue(file in os.listdir())

    @skip
    def testGudrunMakeSmo(self):
        pass

    def testGudrunMakesSmomon(self):
        g = GudrunFile("tests/TestData/NIMROD-water/good_water.txt")
        g.dcs()

        file = g.normalisation.dataFiles.dataFiles[0].replace(
            g.instrument.dataFileType, "smomon"
        )

        self.assertTrue(file in os.listdir())

        for sampleBackground in g.sampleBackgrounds:

            file = sampleBackground.dataFiles.dataFiles[0].replace(
                g.instrument.dataFileType, "smomon"
            )
            self.assertTrue(file in os.listdir())

            for sample in sampleBackground.samples:
                file = sample.dataFiles.dataFiles[0].replace(
                    g.instrument.dataFileType, "smomon"
                )
                self.assertTrue(file in os.listdir())
                file = (
                    sample.containers[0]
                    .dataFiles.dataFiles[0]
                    .replace(g.instrument.dataFileType, "smomon")
                )
                self.assertTrue(file in os.listdir())

    @skip
    def testGudrunMakesSmovan(self):
        g = GudrunFile("tests/TestData/NIMROD-water/good_water.txt")
        g.dcs()

        if g.instrument.spectrumNumberForOutputDiagnosticFiles:
            for sampleBackground in g.sampleBackgrounds:
                for sample in sampleBackground.samples:
                    file = sample.dataFiles.dataFiles[0].replace(
                        g.instrument.dataFileType, "smovan"
                    )
                    self.assertTrue(file in os.listdir())
        else:
            for sampleBackground in g.sampleBackgrounds:
                for sample in sampleBackground.samples:
                    file = sample.dataFiles.dataFiles[0].replace(
                        g.instrument.dataFileType, "smovan"
                    )
                    self.assertFalse(file in os.listdir())

    @skip
    def testGudrunMakesSubbak(self):
        g = GudrunFile("tests/TestData/NIMROD-water/good_water.txt")
        g.dcs()

        if g.instrument.spectrumNumberForOutputDiagnosticFiles:
            for sampleBackground in g.sampleBackgrounds:
                for sample in sampleBackground.samples:
                    file = sample.dataFiles.dataFiles[0].replace(
                        g.instrument.dataFileType, "subbak"
                    )
                    self.assertTrue(file in os.listdir())
        else:
            for sampleBackground in g.sampleBackgrounds:
                for sample in sampleBackground.samples:
                    file = sample.dataFiles.dataFiles[0].replace(
                        g.instrument.dataFileType, "subbak"
                    )
                    self.assertFalse(file in os.listdir())

    def testGudrunMakesSub01(self):
        g = GudrunFile("tests/TestData/NIMROD-water/good_water.txt")
        g.dcs()

        for sampleBackground in g.sampleBackgrounds:
            for sample in sampleBackground.samples:
                file = sample.dataFiles.dataFiles[0].replace(
                    g.instrument.dataFileType, "sub01"
                )
                self.assertTrue(file in os.listdir())

    def testGudrunMakesTrans01(self):
        g = GudrunFile("tests/TestData/NIMROD-water/good_water.txt")
        g.dcs()

        file = g.normalisation.dataFiles.dataFiles[0].replace(
            g.instrument.dataFileType, "trans01"
        )

        self.assertTrue(file in os.listdir())

        for sampleBackground in g.sampleBackgrounds:

            for sample in sampleBackground.samples:
                file = sample.dataFiles.dataFiles[0].replace(
                    g.instrument.dataFileType, "trans01"
                )
                self.assertTrue(file in os.listdir())
                file = (
                    sample.containers[0]
                    .dataFiles.dataFiles[0]
                    .replace(g.instrument.dataFileType, "trans01")
                )
                self.assertTrue(file in os.listdir())

    @skip
    def testGudrunMakesVanbin(self):
        g = GudrunFile("tests/TestData/NIMROD-water/good_water.txt")
        g.dcs()

        if g.instrument.spectrumNumberForOutputDiagnosticFiles:
            for sampleBackground in g.sampleBackgrounds:
                for sample in sampleBackground.samples:
                    file = sample.dataFiles.dataFiles[0].replace(
                        g.instrument.dataFileType, "vanbin"
                    )
                    self.assertTrue(file in os.listdir())
        else:
            for sampleBackground in g.sampleBackgrounds:
                for sample in sampleBackground.samples:
                    file = sample.dataFiles.dataFiles[0].replace(
                        g.instrument.dataFileType, "vanbin"
                    )
                    self.assertFalse(file in os.listdir())

    @skip
    def testGudrunMakesVancor(self):
        g = GudrunFile("tests/TestData/NIMROD-water/good_water.txt")
        g.dcs()

        if g.instrument.spectrumNumberForOutputDiagnosticFiles:
            for sampleBackground in g.sampleBackgrounds:
                for sample in sampleBackground.samples:
                    file = sample.dataFiles.dataFiles[0].replace(
                        g.instrument.dataFileType, "vancor"
                    )
                    self.assertTrue(file in os.listdir())
        else:
            for sampleBackground in g.sampleBackgrounds:
                for sample in sampleBackground.samples:
                    file = sample.dataFiles.dataFiles[0].replace(
                        g.instrument.dataFileType, "vancor"
                    )
                    self.assertFalse(file in os.listdir())

    @skip
    def testGudrunMakesVdcsbin(self):
        pass

    @skip
    def testGudrunMakesVdcscor(self):
        pass

    def testGudrunMakesDcs01(self):
        g = GudrunFile("tests/TestData/NIMROD-water/good_water.txt")
        g.dcs()

        for sampleBackground in g.sampleBackgrounds:

            for sample in sampleBackground.samples:
                file = sample.dataFiles.dataFiles[0].replace(
                    g.instrument.dataFileType, "dcs01"
                )
                self.assertTrue(file in os.listdir())

    def testGudrunMakesMdcs01(self):
        g = GudrunFile("tests/TestData/NIMROD-water/good_water.txt")
        g.dcs()

        for sampleBackground in g.sampleBackgrounds:

            for sample in sampleBackground.samples:
                file = sample.dataFiles.dataFiles[0].replace(
                    g.instrument.dataFileType, "mdcs01"
                )
                self.assertTrue(file in os.listdir())

    def testGudrunMakesMgor01(self):
        g = GudrunFile("tests/TestData/NIMROD-water/good_water.txt")
        g.dcs()

        for sampleBackground in g.sampleBackgrounds:

            for sample in sampleBackground.samples:
                file = sample.dataFiles.dataFiles[0].replace(
                    g.instrument.dataFileType, "mgor01"
                )
                self.assertTrue(file in os.listdir())

    def testGudrunMakesMdor01(self):
        g = GudrunFile("tests/TestData/NIMROD-water/good_water.txt")
        g.dcs()

        for sampleBackground in g.sampleBackgrounds:

            for sample in sampleBackground.samples:
                file = sample.dataFiles.dataFiles[0].replace(
                    g.instrument.dataFileType, "mdor01"
                )
                self.assertTrue(file in os.listdir())

    def testGudrunMakesMsub01(self):
        g = GudrunFile("tests/TestData/NIMROD-water/good_water.txt")
        g.dcs()

        for sampleBackground in g.sampleBackgrounds:

            for sample in sampleBackground.samples:
                file = sample.dataFiles.dataFiles[0].replace(
                    g.instrument.dataFileType, "msub01"
                )
                self.assertTrue(file in os.listdir())

    def testGudrunMakesAbs01(self):
        g = GudrunFile("tests/TestData/NIMROD-water/good_water.txt")
        g.dcs()

        for sampleBackground in g.sampleBackgrounds:

            for sample in sampleBackground.samples:
                file = sample.dataFiles.dataFiles[0].replace(
                    g.instrument.dataFileType, "abs01"
                )
                self.assertTrue(file in os.listdir())

    def testGudrunMakesMint01(self):
        g = GudrunFile("tests/TestData/NIMROD-water/good_water.txt")
        g.dcs()

        for sampleBackground in g.sampleBackgrounds:

            for sample in sampleBackground.samples:
                file = sample.dataFiles.dataFiles[0].replace(
                    g.instrument.dataFileType, "mint01"
                )

                if sample.topHatW != 0.0:
                    self.assertTrue(file in os.listdir())
                else:
                    self.assertFalse(file in os.listdir())

    def testGudrunMakesChksum(self):
        g = GudrunFile("tests/TestData/NIMROD-water/good_water.txt")
        g.dcs()

        for sampleBackground in g.sampleBackgrounds:

            for sample in sampleBackground.samples:
                file = sample.dataFiles.dataFiles[0].replace(
                    g.instrument.dataFileType, "chksum"
                )
                self.assertTrue(file in os.listdir())

    def testGudrunMakesSamrat(self):
        g = GudrunFile("tests/TestData/NIMROD-water/good_water.txt")
        g.dcs()

        for sampleBackground in g.sampleBackgrounds:

            for sample in sampleBackground.samples:
                file = sample.dataFiles.dataFiles[0].replace(
                    g.instrument.dataFileType, "samrat"
                )
                self.assertTrue(file in os.listdir())
                file = (
                    sample.containers[0]
                    .dataFiles.dataFiles[0]
                    .replace(g.instrument.dataFileType, "samrat")
                )
                self.assertTrue(file in os.listdir())

    def testGudrunMakesTransnofit01(self):
        g = GudrunFile("tests/TestData/NIMROD-water/good_water.txt")
        g.dcs()

        file = g.normalisation.dataFiles.dataFiles[0].replace(
            g.instrument.dataFileType, "transnofit01"
        )

        self.assertTrue(file in os.listdir())

        for sampleBackground in g.sampleBackgrounds:

            for sample in sampleBackground.samples:
                file = sample.dataFiles.dataFiles[0].replace(
                    g.instrument.dataFileType, "transnofit01"
                )
                self.assertTrue(file in os.listdir())
                file = (
                    sample.containers[0]
                    .dataFiles.dataFiles[0]
                    .replace(g.instrument.dataFileType, "transnofit01")
                )
                self.assertTrue(file in os.listdir())

    def testGudrunMakesVanrat(self):
        g = GudrunFile("tests/TestData/NIMROD-water/good_water.txt")
        g.dcs()

        file = g.normalisation.dataFiles.dataFiles[0].replace(
            g.instrument.dataFileType, "vanrat"
        )
        self.assertTrue(file in os.listdir())

    """
    Unsure if the following tests are setup correctly.
    I have assumed from the manual,
    that when a diagnostic spectrum is specified,
    a file is created named after the first sample data file,
    for each file, using the format specified.

        - testGudrunMakesAbscorFile
        - testGudrunMakesCnt
        - testGudrunMakesMerge
        - testGudrunMakesMulcor
        - testGudrunMakesNormmon
        - testGudrunMakesNormvan
        - testGudrunMakesPreMerge
        - testGudrunMakesSmovan
        - testGudrunMakesSubbak
        - testGudrunMakesVanbin
        - testGudrunMakesVancor
        - testGudrunMakesVdcsbin
        - testGudrunMakesVdcscor
    """
