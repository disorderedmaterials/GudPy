import os
from unittest import TestCase
from shutil import copyfile
import tempfile

from core.purge_file import PurgeFile
from core.enums import Format
from core import gudpy
from core.io.gudpy_io import GudPyIO


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
        self.gudpy = gudpy.GudPy()
        self.keepsakes = os.listdir()
        copyfile(dirpath, "test/TestData/NIMROD-water/good_water.txt")
        self.gudpy.loadFromFile(
            loadFile="test/TestData/NIMROD-water/good_water.txt",
            format=Format.TXT)

        self.gudpy.loadFromGudrunFile(
            path="test/TestData/NIMROD-water/good_water.txt"
        )
        self.g = self.gudpy.gudrunFile
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
        with tempfile.TemporaryDirectory() as tmp:
            os.chdir(tmp)
            purge = PurgeFile(self.g)
            GudPyIO.writeObject(purge, "purge_det.dat")
            with open("purge_det.dat", encoding="utf-8") as f:
                outlines = f.read()
                self.assertEqual(outlines, str(purge))
