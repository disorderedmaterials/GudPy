import os
from unittest import TestCase
from shutil import copyfile


from core.gudrun_file import GudrunFile
from core.purge_file import PurgeFile
from core.enums import Format


class TestPurgeFile(TestCase):
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
        self.g = GudrunFile(dirpath, format=Format.TXT)

        self.keepsakes = os.listdir()

        copyfile(self.g.loadFile, "test/TestData/NIMROD-water/good_water.txt")
        g = GudrunFile(
            "test/TestData/NIMROD-water/good_water.txt",
            format=Format.TXT)

        g.write_out(overwrite=True)
        self.g = g
        self.expectedPurgeFile = {
            "standardDeviation": (10, 10),
            "ignoreBad": True,
            "excludeSampleAndCan": True,
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
        with open("purge_det.dat", encoding="utf-8") as f:
            outlines = f.read()
            self.assertEqual(outlines, str(purge))
