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

        parent = Path("tests").parent.absolute()
        GudrunStartFolder = parent / "bin"
        dataFileDir = Path("tests/TestData/NIMROD-water/raw").absolute()

        g.instrument.GudrunStartFolder = GudrunStartFolder
        g.instrument.dataFileDir = str(dataFileDir) + "/"
        g.instrument.groupFileName = (
            GudrunStartFolder / g.instrument.groupFileName
        )
        g.write_out(overwrite=True)
        self.g = g
        samples = self.g.sampleBackgrounds[0].samples
        TAB = "          "
        self.expectedPurgeFile = {
            "instrumentName": self.g.instrument.name,
            "inputFileDir": self.g.instrument.GudrunInputFileDir,
            "dataFileDir": self.g.instrument.dataFileDir,
            "detCalibFile": self.g.instrument.detectorCalibrationFileName,
            "groupsFile": self.g.instrument.groupFileName,
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
            "normalisationPeriodNo": (
                self.g.normalisation.periodNumber
                ),
            "normalisationPeriodNoBg": (
                self.g.normalisation.periodNumberBg
            ),
            "normalisationDataFiles": (
                f'{self.g.normalisation.dataFiles.dataFiles[0]}  1{TAB}\n'
            ),
            "normalisationBackgroundDataFiles": (
                f'{self.g.normalisation.dataFilesBg.dataFiles[0]}  1{TAB}\n'
                f'{self.g.normalisation.dataFilesBg.dataFiles[1]}  1{TAB}\n'
            ),
            "sampleBackgroundDataFiles": (
                f'{self.g.sampleBackgrounds[0].dataFiles.dataFiles[0]}  1'
                f'{TAB}\n'
                f'{self.g.sampleBackgrounds[0].dataFiles.dataFiles[1]}  1'
                f'{TAB}\n'
            ),
            "sampleDataFiles": (
                f'{samples[0].dataFiles.dataFiles[0]}  1{TAB}\n'
                f'{samples[0].dataFiles.dataFiles[1]}  1{TAB}\n'
                f'{samples[1].dataFiles.dataFiles[0]}  1{TAB}\n'
                f'{samples[1].dataFiles.dataFiles[1]}  1{TAB}\n'
                f'{samples[2].dataFiles.dataFiles[0]}  1{TAB}\n'
                f'{samples[2].dataFiles.dataFiles[1]}  1{TAB}\n'
                f'{samples[3].dataFiles.dataFiles[0]}  1{TAB}\n'
                f'{samples[3].dataFiles.dataFiles[1]}  1{TAB}\n'
            ),
            "containerDataFiles": (
                f'{samples[0].containers[0].dataFiles.dataFiles[0]}  1{TAB}\n'
                f'{samples[0].containers[0].dataFiles.dataFiles[1]}  1{TAB}\n'
                f'{samples[0].containers[0].dataFiles.dataFiles[2]}  1{TAB}\n'
                f'{samples[1].containers[0].dataFiles.dataFiles[0]}  1{TAB}\n'
                f'{samples[1].containers[0].dataFiles.dataFiles[1]}  1{TAB}\n'
                f'{samples[1].containers[0].dataFiles.dataFiles[2]}  1{TAB}\n'
                f'{samples[2].containers[0].dataFiles.dataFiles[0]}  1{TAB}\n'
                f'{samples[3].containers[0].dataFiles.dataFiles[0]}  1{TAB}\n'
            )

        }

        return super().setUp()

    def testCreatePurgeClass(self):

        purge = PurgeFile(self.g)
        purge.__dict__.pop("gudrunFile", None)
        purgeAttrsDict = purge.__dict__

        self.assertIsInstance(purge, PurgeFile)
        for key in purgeAttrsDict:
            self.assertEqual(
                self.expectedPurgeFile[key], purgeAttrsDict[key]
            )

    def testWritePurgeFile(self):

        purge = PurgeFile(self.g)
        purge.write_out()
        outlines = open("purge_det.dat", encoding="utf-8").read()
        self.assertEqual(outlines, str(purge))
