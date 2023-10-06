import os
from copy import deepcopy
from shutil import copyfile
from unittest import TestCase
import re
import math

from core.composition import Composition, Component
from core.gudrun_file import GudrunFile
from core.iterators.thickness_iterator import ThicknessIterator
from core.iterators.density_iterator import DensityIterator
from core.iterators.tweak_factor_iterator import TweakFactorIterator
from core.iterators.composition_iterator import CompositionIterator
from core.gud_file import GudFile
from core.iterators.wavelength_subtraction_iterator import (
    WavelengthSubtractionIterator
)


class TestGudPyWorkflows(TestCase):
    def setUp(self) -> None:

        path = os.path.abspath("test/TestData/NIMROD-water/water.txt")

        self.g = GudrunFile(os.path.abspath(path))

        self.keepsakes = os.listdir()

        copyfile(self.g.path, "test/TestData/NIMROD-water/good_water.txt")
        g = GudrunFile(
            os.path.abspath("test/TestData/NIMROD-water/good_water.txt")
        )

        from pathlib import Path
        dataFileDir = Path("test/TestData/NIMROD-water/raw").absolute()
        g.instrument.dataFileDir = str(dataFileDir) + "/"

        g.write_out(overwrite=True)
        self.g = g
        return super().setUp()

    def tearDown(self) -> None:

        [os.remove(f) for f in os.listdir() if f not in self.keepsakes]
        return super().tearDown()

    def testGudPyDCS(self):

        self.g.dcs()
        gfPath = self.g.sampleBackgrounds[0].samples[0].dataFiles[0]
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

        gfPath = self.g.sampleBackgrounds[0].samples[2].dataFiles[0]
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
                sample.dataFiles[0].replace(
                    self.g.instrument.dataFileType, "mint01"
                )
            )

            actualMintFile = f'test/TestData/water-ref/plain/{mintFilename}'

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

        gfPath = self.g.sampleBackgrounds[0].samples[1].dataFiles[0]
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

        gfPath = self.g.sampleBackgrounds[0].samples[3].dataFiles[0]
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

        gfPath = self.g.sampleBackgrounds[0].samples[1].dataFiles[0]
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

        gfPath = self.g.sampleBackgrounds[0].samples[3].dataFiles[0]
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

        gfPath = self.g.sampleBackgrounds[0].samples[1].dataFiles[0]
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

        gfPath = self.g.sampleBackgrounds[0].samples[3].dataFiles[0]
        gfPath = gfPath.replace(self.g.instrument.dataFileType, 'gud')
        gf4 = GudFile(
            os.path.join(
                self.g.instrument.GudrunInputFileDir, gfPath
            )
        )
        dcsLevelPercentage = re.findall(r'\d*[.]?\d*%', gf4.result)[0]
        dcsLevelPercentage = float(dcsLevelPercentage.replace('%', ''))
        self.assertAlmostEqual(dcsLevelPercentage, 100.0, 0)

    def testIterateByThickness(self):

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

        gfPath = self.g.sampleBackgrounds[0].samples[1].dataFiles[0]
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

        gfPath = self.g.sampleBackgrounds[0].samples[3].dataFiles[0]
        gfPath = gfPath.replace(self.g.instrument.dataFileType, 'gud')
        gf4 = GudFile(
            os.path.join(
                self.g.instrument.GudrunInputFileDir, gfPath
            )
        )
        dcsLevelPercentage = re.findall(r'\d*[.]?\d*%', gf4.result)[0]
        dcsLevelPercentage = float(dcsLevelPercentage.replace('%', ''))
        self.assertAlmostEqual(dcsLevelPercentage, 100.0, 0)

    def testIterateByComposition(self):

        g = deepcopy(self.g)
        g.purge()

        g.sampleBackgrounds[0].samples[0].runThisSample = False
        g.sampleBackgrounds[0].samples[2].runThisSample = False
        g.sampleBackgrounds[0].samples[3].runThisSample = False
        sample = g.sampleBackgrounds[0].samples[1]

        composition = Composition("Sample")

        h2 = Component("H[2]")
        h2.parse()
        o = Component("O")
        o.parse()

        composition.addComponent(h2, 1)
        composition.addComponent(o, 1)

        sample.composition = composition

        compositionIterator = CompositionIterator(g)
        compositionIterator.setComponent(h2, 1)
        compositionIterator.iterate(10, 3)
        self.assertAlmostEqual(
            sample.composition.weightedComponents[0].ratio, 2, 1
        )

        self.assertEqual(
            sample.composition.weightedComponents[1].ratio, 1
        )

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
                    sample.dataFiles[0].replace(
                        self.g.instrument.dataFileType, "mint01"
                    )
                )

                actualMintFile = (
                    f'test/TestData/water-ref/wavelength{i}/'
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
                    sample.dataFiles[0].replace(
                        self.g.instrument.dataFileType, "msubw01"
                    )
                )

                actualMsubFilename = (
                    f'test/TestData/water-ref/wavelength{i}/{msubFilename}'
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
