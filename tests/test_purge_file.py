import os
from unittest import TestCase
from shutil import copyfile


from src.gudrun_classes.gudrun_file import GudrunFile
from src.gudrun_classes.purge_file import PurgeFile


class TestPurgeFile(TestCase):
    def setUp(self) -> None:

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

        self.keepsakes = os.listdir()

        copyfile(self.g.path, "tests/TestData/NIMROD-water/good_water.txt")
        g = GudrunFile("tests/TestData/NIMROD-water/good_water.txt")

        from pathlib import Path

        dataFileDir = Path("tests/TestData/NIMROD-water/raw").absolute()

        g.instrument.dataFileDir = str(dataFileDir) + "/"
        g.write_out(overwrite=True)
        self.g = g
        samples = self.g.sampleBackgrounds[0].samples
        TAB = "          "
        self.expectedPurgeFile = {
            "instrumentName": self.g.instrument.name,
            "inputFileDir": self.g.instrument.GudrunInputFileDir,
            "dataFileDir": self.g.instrument.dataFileDir,
            "detCalibFile": os.path.join(
                self.g.instrument.GudrunStartFolder,
                self.g.instrument.detectorCalibrationFileName
            ),
            "groupsFile": os.path.join(
                self.g.instrument.GudrunStartFolder,
                self.g.instrument.groupFileName,
            ),
            "spectrumNumbers": (
                self.g.instrument.spectrumNumbersForIncidentBeamMonitor
            ),
            "channelNumbers": (
                self.g.instrument.channelNosSpikeAnalysis
            ),
            "acceptanceFactor": (
                self.g.instrument.spikeAnalysisAcceptanceFactor
                ),
            "standardDeviation": (10, 10),
            "ignoreBad": True,
            "excludeSampleAndCan": True,
            "normalisationPeriodNo": (
                self.g.normalisation.periodNumber
                ),
            "normalisationPeriodNoBg": (
                self.g.normalisation.periodNumberBg
            ),
            "normalisationDataFiles": (
                self.g.normalisation.dataFiles.dataFiles,  1
            ),
            "normalisationBackgroundDataFiles": (
                self.g.normalisation.dataFilesBg.dataFiles, 1
            ),
            "sampleBackgroundDataFiles": [
                (self.g.sampleBackgrounds[0].dataFiles.dataFiles, 1)
            ],
            "sampleDataFiles": [
                (samples[0].dataFiles.dataFiles, 1),
                (samples[1].dataFiles.dataFiles, 1),
                (samples[2].dataFiles.dataFiles, 1),
                (samples[3].dataFiles.dataFiles, 1)
            ],
            "containerDataFiles": [
                (samples[0].containers[0].dataFiles.dataFiles, 1),
                (samples[1].containers[0].dataFiles.dataFiles, 1),
                (samples[2].containers[0].dataFiles.dataFiles, 1),
                (samples[3].containers[0].dataFiles.dataFiles, 1)
            ]

        }

        return super().setUp()

    def tearDown(self) -> None:

        [os.remove(f) for f in os.listdir() if f not in self.keepsakes]
        return super().tearDown()

    def testCreatePurgeClass(self):
        purge = PurgeFile(self.g)
        purge.__dict__.pop("gudrunFile", None)
        purgeAttrsDict = purge.__dict__

        self.assertIsInstance(purge, PurgeFile)
        for key in self.expectedPurgeFile.keys():
            self.assertEqual(
                self.expectedPurgeFile[key], purgeAttrsDict[key]
            )

    def testWritePurgeFile(self):

        purge = PurgeFile(self.g)
        purge.write_out()
        outlines = open("purge_det.dat", encoding="utf-8").read()
        self.assertEqual(outlines, str(purge))
