import os
import sys
from unittest import TestCase
from shutil import copyfile
import unittest

try:
    sys.path.insert(1, os.path.join(sys.path[0], "../gudrun_classes"))
    from gudrun_file import GudrunFile
    from purge_file import PurgeFile
except ModuleNotFoundError:
    sys.path.insert(1, os.path.join(sys.path[0], "gudrun_classes"))
    from gudrun_classes.gudrun_file import GudrunFile
    from gudrun_classes.purge_file import PurgeFile

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

        self.expectedPurgeFile = {
            "instrumentName" : self.g.instrument.name,
            "inputFileDir" : self.g.instrument.GudrunInputFileDir,
            "dataFileDir" : self.g.instrument.dataFileDir,
            "detCalibFile" : self.g.instrument.detectorCalibrationFileName,
            "groupsFile" : self.g.instrument.groupFileName,
            "spectrumNumbers" : self.g.instrument.spectrumNumbersForIncidentBeamMonitor,
            "channelNumbers" : self.g.instrument.channelNosSpikeAnalysis,
            "acceptanceFactor" : self.g.instrument.spikeAnalysisAcceptanceFactor,
            "standardDeviation" : (10, 10),
            "ignoreBad" : True,
            "normalisationPeriodNo" : self.g.normalisation.numberOfFilesPeriodNumber[1],
            "normalisationPeriodNoBg" : self.g.normalisation.numberOfFilesPeriodNumberBg[1],
            "normalisationDataFiles" : (
                f'{self.g.normalisation.dataFiles.dataFiles[0]}  1\n'
            ),
            "normalisationBackgroundDataFiles" : (
                f'{self.g.normalisation.dataFilesBg.dataFiles[0]}  1\n'
                f'{self.g.normalisation.dataFilesBg.dataFiles[1]}  1\n'
            ),
            "sampleBackgroundDataFiles" : (
                f'{self.g.sampleBackgrounds[0].dataFiles.dataFiles[0]}  1\n'
                f'{self.g.sampleBackgrounds[0].dataFiles.dataFiles[1]}  1\n'
            ),
            "sampleDataFiles" : (
                f'{self.g.sampleBackgrounds[0].samples[0].dataFiles.dataFiles[0]}  1\n'
                f'{self.g.sampleBackgrounds[0].samples[0].dataFiles.dataFiles[1]}  1\n'
                f'{self.g.sampleBackgrounds[0].samples[1].dataFiles.dataFiles[0]}  1\n'
                f'{self.g.sampleBackgrounds[0].samples[1].dataFiles.dataFiles[1]}  1\n'
                f'{self.g.sampleBackgrounds[0].samples[2].dataFiles.dataFiles[0]}  1\n'
                f'{self.g.sampleBackgrounds[0].samples[2].dataFiles.dataFiles[1]}  1\n'
                f'{self.g.sampleBackgrounds[0].samples[3].dataFiles.dataFiles[0]}  1\n'
                f'{self.g.sampleBackgrounds[0].samples[3].dataFiles.dataFiles[1]}  1\n'
            ),
            "containerDataFiles" : (
                f'{self.g.sampleBackgrounds[0].samples[0].containers[0].dataFiles.dataFiles[0]}  1\n'
                f'{self.g.sampleBackgrounds[0].samples[0].containers[0].dataFiles.dataFiles[1]}  1\n'
                f'{self.g.sampleBackgrounds[0].samples[0].containers[0].dataFiles.dataFiles[2]}  1\n'
                f'{self.g.sampleBackgrounds[0].samples[1].containers[0].dataFiles.dataFiles[0]}  1\n'
                f'{self.g.sampleBackgrounds[0].samples[1].containers[0].dataFiles.dataFiles[1]}  1\n'
                f'{self.g.sampleBackgrounds[0].samples[1].containers[0].dataFiles.dataFiles[2]}  1\n'
                f'{self.g.sampleBackgrounds[0].samples[2].containers[0].dataFiles.dataFiles[0]}  1\n'
                f'{self.g.sampleBackgrounds[0].samples[3].containers[0].dataFiles.dataFiles[0]}  1\n'
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
