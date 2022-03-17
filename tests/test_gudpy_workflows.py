import os
from shutil import copyfile
from unittest import TestCase
import re
import math

from src.gudrun_classes.gudrun_file import GudrunFile
from src.gudrun_classes.thickness_iterator import ThicknessIterator
from src.gudrun_classes.density_iterator import DensityIterator
from src.gudrun_classes.tweak_factor_iterator import TweakFactorIterator
from src.gudrun_classes.gud_file import GudFile
from src.gudrun_classes.wavelength_subtraction_iterator import (
    WavelengthSubtractionIterator
)


class TestGudPyWorkflows(TestCase):
    def setUp(self) -> None:

        path = os.path.abspath("tests/TestData/NIMROD-water/water.txt")

        self.g = GudrunFile(os.path.abspath(path))

        self.keepsakes = os.listdir()

        copyfile(self.g.path, "tests/TestData/NIMROD-water/good_water.txt")
        g = GudrunFile(
            os.path.abspath("tests/TestData/NIMROD-water/good_water.txt")
        )

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
        return super().setUp()

    def tearDown(self) -> None:

        [os.remove(f) for f in os.listdir() if f not in self.keepsakes]
        return super().tearDown()

    def testGudPyDCS(self):

        self.g.dcs()
        gfPath = self.g.sampleBackgrounds[0].samples[0].dataFiles.dataFiles[0]
        gfPath = gfPath.replace(self.g.instrument.dataFileType, 'gud')
        gf1 = GudFile(
            os.path.join(
                self.g.instrument.GudrunInputFileDir, gfPath
            )
        )
        dcsLevelPercentage = re.findall(r'\d*[.]?\d*%', gf1.err)[0]
        dcsLevelPercentage = float(dcsLevelPercentage.replace('%', ''))
        self.assertAlmostEqual(dcsLevelPercentage, 14.1, 0)

        gfPath = self.g.sampleBackgrounds[0].samples[1].dataFiles.dataFiles[0]
        gfPath = gfPath.replace(self.g.instrument.dataFileType, 'gud')
        gf2 = GudFile(
            os.path.join(
                self.g.instrument.GudrunInputFileDir, gfPath
            )
        )
        dcsLevelPercentage = re.findall(r'\d*[.]?\d*%', gf2.result)[0]
        dcsLevelPercentage = float(dcsLevelPercentage.replace('%', ''))
        self.assertAlmostEqual(dcsLevelPercentage, 100.0, 0)

        gfPath = self.g.sampleBackgrounds[0].samples[2].dataFiles.dataFiles[0]
        gfPath = gfPath.replace(self.g.instrument.dataFileType, 'gud')
        gf3 = GudFile(
            os.path.join(
                self.g.instrument.GudrunInputFileDir, gfPath
            )
        )
        dcsLevelPercentage = re.findall(r'\d*[.]?\d*%', gf3.result)[0]
        dcsLevelPercentage = float(dcsLevelPercentage.replace('%', ''))
        self.assertAlmostEqual(dcsLevelPercentage, 98.0, 0)

        gfPath = self.g.sampleBackgrounds[0].samples[3].dataFiles.dataFiles[0]
        gfPath = gfPath.replace(self.g.instrument.dataFileType, 'gud')
        gf4 = GudFile(
            os.path.join(
                self.g.instrument.GudrunInputFileDir, gfPath
            )
        )
        dcsLevelPercentage = re.findall(r'\d*[.]?\d*%', gf4.err)[0]
        dcsLevelPercentage = float(dcsLevelPercentage.replace('%', ''))
        self.assertAlmostEqual(dcsLevelPercentage, 13.0, 0)

        for sample in self.g.sampleBackgrounds[0].samples:

            mintFilename = (
                sample.dataFiles.dataFiles[0].replace(
                    self.g.instrument.dataFileType, "mint01"
                )
            )

            actualMintFile = f'tests/TestData/water-ref/plain/{mintFilename}'

            actualData = open(
                os.path.join(
                    self.g.instrument.GudrunInputFileDir, mintFilename
                ),
                "r", encoding="utf-8"
                ).readlines()[10:]
            expectedData = open(
                actualMintFile, "r", encoding="utf-8"
                ).readlines()[10:]
            close = 0
            total = 0
            for a, b in zip(actualData, expectedData):

                for x, y in zip(a.split(), b.split()):
                    if x == '#' or y == '#':
                        continue
                    total += 1
                    if math.isclose(
                        float(x.strip()),
                        float(y.strip()),
                        rel_tol=0.01
                            ):
                        close += 1
            self.assertTrue((close/total) >= 0.95)

    def testGudPyIterateByTweakFactor(self):

        self.g.purge()
        tweakFactorIterator = TweakFactorIterator(self.g)
        tweakFactorIterator.iterate(5)

        gfPath = self.g.sampleBackgrounds[0].samples[0].dataFiles.dataFiles[0]
        gfPath = gfPath.replace(self.g.instrument.dataFileType, 'gud')
        gf1 = GudFile(
            os.path.join(
                self.g.instrument.GudrunInputFileDir, gfPath
            )
        )
        dcsLevelPercentage = re.findall(r'\d*[.]?\d*%', gf1.result)[0]
        dcsLevelPercentage = float(dcsLevelPercentage.replace('%', ''))
        self.assertAlmostEqual(dcsLevelPercentage, 100.0, 0)

        gfPath = self.g.sampleBackgrounds[0].samples[1].dataFiles.dataFiles[0]
        gfPath = gfPath.replace(self.g.instrument.dataFileType, 'gud')
        gf2 = GudFile(
            os.path.join(
                self.g.instrument.GudrunInputFileDir, gfPath
            )
        )
        dcsLevelPercentage = re.findall(r'\d*[.]?\d*%', gf2.result)[0]
        dcsLevelPercentage = float(dcsLevelPercentage.replace('%', ''))
        self.assertAlmostEqual(dcsLevelPercentage, 100.0, 0)

        gfPath = self.g.sampleBackgrounds[0].samples[2].dataFiles.dataFiles[0]
        gfPath = gfPath.replace(self.g.instrument.dataFileType, 'gud')
        gf3 = GudFile(
            os.path.join(
                self.g.instrument.GudrunInputFileDir, gfPath
            )
        )
        dcsLevelPercentage = re.findall(r'\d*[.]?\d*%', gf3.result)[0]
        dcsLevelPercentage = float(dcsLevelPercentage.replace('%', ''))
        self.assertAlmostEqual(dcsLevelPercentage, 100.0, 0)

        gfPath = self.g.sampleBackgrounds[0].samples[3].dataFiles.dataFiles[0]
        gfPath = gfPath.replace(self.g.instrument.dataFileType, 'gud')
        gf4 = GudFile(
            os.path.join(
                self.g.instrument.GudrunInputFileDir, gfPath
            )
        )
        dcsLevelPercentage = re.findall(r'\d*[.]?\d*%', gf4.result)[0]
        dcsLevelPercentage = float(dcsLevelPercentage.replace('%', ''))
        self.assertAlmostEqual(dcsLevelPercentage, 100.0, 0)

    def testGudPyIterateByThickness(self):

        self.g.purge()
        thicknessIterator = ThicknessIterator(self.g)
        thicknessIterator.iterate(5)

        gfPath = self.g.sampleBackgrounds[0].samples[0].dataFiles.dataFiles[0]
        gfPath = gfPath.replace(self.g.instrument.dataFileType, 'gud')
        gf1 = GudFile(
            os.path.join(
                self.g.instrument.GudrunInputFileDir, gfPath
            )
        )
        dcsLevelPercentage = re.findall(r'\d*[.]?\d*%', gf1.result)[0]
        dcsLevelPercentage = float(dcsLevelPercentage.replace('%', ''))
        self.assertAlmostEqual(dcsLevelPercentage, 100.0, 0)

        gfPath = self.g.sampleBackgrounds[0].samples[1].dataFiles.dataFiles[0]
        gfPath = gfPath.replace(self.g.instrument.dataFileType, 'gud')
        gf2 = GudFile(
            os.path.join(
                self.g.instrument.GudrunInputFileDir, gfPath
            )
        )
        dcsLevelPercentage = re.findall(r'\d*[.]?\d*%', gf2.result)[0]
        dcsLevelPercentage = float(dcsLevelPercentage.replace('%', ''))
        self.assertAlmostEqual(dcsLevelPercentage, 100.0, 0)

        gfPath = self.g.sampleBackgrounds[0].samples[2].dataFiles.dataFiles[0]
        gfPath = gfPath.replace(self.g.instrument.dataFileType, 'gud')
        gf3 = GudFile(
            os.path.join(
                self.g.instrument.GudrunInputFileDir, gfPath
            )
        )
        dcsLevelPercentage = re.findall(r'\d*[.]?\d*%', gf3.result)[0]
        dcsLevelPercentage = float(dcsLevelPercentage.replace('%', ''))
        self.assertAlmostEqual(dcsLevelPercentage, 100.0, 0)

        gfPath = self.g.sampleBackgrounds[0].samples[3].dataFiles.dataFiles[0]
        gfPath = gfPath.replace(self.g.instrument.dataFileType, 'gud')
        gf4 = GudFile(
            os.path.join(
                self.g.instrument.GudrunInputFileDir, gfPath
            )
        )
        dcsLevelPercentage = re.findall(r'\d*[.]?\d*%', gf4.result)[0]
        dcsLevelPercentage = float(dcsLevelPercentage.replace('%', ''))
        self.assertAlmostEqual(dcsLevelPercentage, 100.0, 0)

    def testGudPyIterateByDensity(self):

        self.g.purge()
        densityIterator = DensityIterator(self.g)
        densityIterator.iterate(5)

        gfPath = self.g.sampleBackgrounds[0].samples[0].dataFiles.dataFiles[0]
        gfPath = gfPath.replace(self.g.instrument.dataFileType, 'gud')
        gf1 = GudFile(
            os.path.join(
                self.g.instrument.GudrunInputFileDir, gfPath
            )
        )
        dcsLevelPercentage = re.findall(r'\d*[.]?\d*%', gf1.result)[0]
        dcsLevelPercentage = float(dcsLevelPercentage.replace('%', ''))
        self.assertAlmostEqual(dcsLevelPercentage, 100.0, 0)

        gfPath = self.g.sampleBackgrounds[0].samples[1].dataFiles.dataFiles[0]
        gfPath = gfPath.replace(self.g.instrument.dataFileType, 'gud')
        gf2 = GudFile(
            os.path.join(
                self.g.instrument.GudrunInputFileDir, gfPath
            )
        )
        dcsLevelPercentage = re.findall(r'\d*[.]?\d*%', gf2.result)[0]
        dcsLevelPercentage = float(dcsLevelPercentage.replace('%', ''))
        self.assertAlmostEqual(dcsLevelPercentage, 100.0, 0)

        gfPath = self.g.sampleBackgrounds[0].samples[2].dataFiles.dataFiles[0]
        gfPath = gfPath.replace(self.g.instrument.dataFileType, 'gud')
        gf3 = GudFile(
            os.path.join(
                self.g.instrument.GudrunInputFileDir, gfPath
            )
        )
        dcsLevelPercentage = re.findall(r'\d*[.]?\d*%', gf3.result)[0]
        dcsLevelPercentage = float(dcsLevelPercentage.replace('%', ''))
        self.assertAlmostEqual(dcsLevelPercentage, 100.0, 0)

        gfPath = self.g.sampleBackgrounds[0].samples[3].dataFiles.dataFiles[0]
        gfPath = gfPath.replace(self.g.instrument.dataFileType, 'gud')
        gf4 = GudFile(
            os.path.join(
                self.g.instrument.GudrunInputFileDir, gfPath
            )
        )
        dcsLevelPercentage = re.findall(r'\d*[.]?\d*%', gf4.result)[0]
        dcsLevelPercentage = float(dcsLevelPercentage.replace('%', ''))
        self.assertAlmostEqual(dcsLevelPercentage, 100.0, 0)

    def testGudPyIterateBySubtractingWavelength(self):

        for i in range(1, 4):
            self.g.purge()
            wavelengthSubtractionIterator = (
                WavelengthSubtractionIterator(self.g)
            )
            wavelengthSubtractionIterator.iterate(i)

            for sample in [
                    x
                    for x in self.g.sampleBackgrounds[0].samples
                    if x.runThisSample
                    ]:
                mintFilename = (
                    sample.dataFiles.dataFiles[0].replace(
                        self.g.instrument.dataFileType, "mint01"
                    )
                )

                actualMintFile = (
                    f'tests/TestData/water-ref/wavelength{i}/'
                    f'{mintFilename}'
                )

                actualData = open(
                   os.path.join(
                       self.g.instrument.GudrunInputFileDir,
                       mintFilename
                   ), "r", encoding="utf-8"
                ).readlines()[10:]
                expectedData = open(
                    actualMintFile, "r", encoding="utf-8"
                    ).readlines()[10:]
                close = 0
                total = 0
                for a, b in zip(actualData, expectedData):

                    for x, y in zip(a.split(), b.split()):
                        if x == '#' or y == '#':
                            continue
                        total += 1
                        if math.isclose(
                            float(x.strip()),
                            float(y.strip()),
                            rel_tol=0.02
                                ):
                            close += 1
                self.assertTrue((close/total) >= 0.95)

                msubFilename = (
                    sample.dataFiles.dataFiles[0].replace(
                        self.g.instrument.dataFileType, "msubw01"
                    )
                )

                actualMsubFilename = (
                    f'tests/TestData/water-ref/wavelength{i}/{msubFilename}'
                )

                actualData = open(
                   os.path.join(
                       self.g.instrument.GudrunInputFileDir,
                       msubFilename
                   ), "r", encoding="utf-8"
                ).readlines()[10:]
                expectedData = open(
                    actualMsubFilename, "r", encoding="utf-8"
                    ).readlines()[10:]
                close = 0
                total = 0
                for a, b in zip(actualData, expectedData):

                    for x, y in zip(a.split(), b.split()):
                        if x == '#' or y == '#':
                            continue

                        total += 1
                        if math.isclose(
                            float(x.strip()),
                            float(y.strip()),
                            rel_tol=0.02
                                ):
                            close += 1
                self.assertTrue((close/total) >= 0.95)
