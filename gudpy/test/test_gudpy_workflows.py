import os
from copy import deepcopy
from shutil import copyfile
from unittest import TestCase
import re
import math

from core.composition import Composition, Component
from core.gudrun_file import GudrunFile
from core.iterators.thickness import ThicknessIterator
from core.iterators.density import DensityIterator
from core.iterators.tweak_factor import TweakFactorIterator
from core.iterators.composition import CompositionIterator
from core.gud_file import GudFile
from core.iterators.inelasticity_subtraction import (
    InelasticitySubtraction
)
from core.enums import Format


class TestGudPyWorkflows(TestCase):
    def setUp(self) -> None:

        testDir = os.path.dirname(__file__)
        path = os.path.join(
            testDir, "TestData/NIMROD-water/water.txt")

        self.g = GudrunFile(path, format=Format.TXT)

        self.keepsakes = os.listdir()

        copyfile(self.g.path, os.path.join(
            testDir, "TestData/NIMROD-water/good_water.txt")
        )
        g = GudrunFile(
            os.path.join(testDir, "TestData/NIMROD-water/good_water.txt"),
            format=Format.TXT
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
        gfPath = self.g.gudrunOutput.sampleOutputs[
            self.g.sampleBackgrounds[0].samples[0].name].gudFile
        gf1 = GudFile(gfPath)
        dcsLevelPercentage = re.findall(r'\d*[.]?\d*%', gf1.err)[0]
        dcsLevelPercentage = float(dcsLevelPercentage.replace('%', ''))
        self.assertAlmostEqual(dcsLevelPercentage, 14.1, 0)

        gfPath = self.g.gudrunOutput.sampleOutputs[
            self.g.sampleBackgrounds[0].samples[1].name].gudFile
        gf2 = GudFile(gfPath)
        dcsLevelPercentage = re.findall(r'\d*[.]?\d*%', gf2.result)[0]
        dcsLevelPercentage = float(dcsLevelPercentage.replace('%', ''))
        self.assertAlmostEqual(dcsLevelPercentage, 100.0, 0)

        gfPath = self.g.gudrunOutput.sampleOutputs[
            self.g.sampleBackgrounds[0].samples[2].name].gudFile
        gf3 = GudFile(gfPath)
        dcsLevelPercentage = re.findall(r'\d*[.]?\d*%', gf3.result)[0]
        dcsLevelPercentage = float(dcsLevelPercentage.replace('%', ''))
        self.assertAlmostEqual(dcsLevelPercentage, 98.0, 0)

        gfPath = self.g.gudrunOutput.sampleOutputs[
            self.g.sampleBackgrounds[0].samples[3].name].gudFile
        gf4 = GudFile(gfPath)
        dcsLevelPercentage = re.findall(r'\d*[.]?\d*%', gf4.err)[0]
        dcsLevelPercentage = float(dcsLevelPercentage.replace('%', ''))
        self.assertAlmostEqual(dcsLevelPercentage, 13.0, 0)

        for sample in self.g.sampleBackgrounds[0].samples:
            mintFilename = (
                os.path.splitext(sample.dataFiles[0])[0]
            )

            actualMintFile = ("test/TestData/water-ref/plain/"
                              f"{mintFilename}.mint01")
            print(self.g.gudrunOutput.sampleOutputs[
                sample.name].outputs[sample.dataFiles[0]][".mint01"])
            actualData = open(self.g.gudrunOutput.sampleOutputs[
                sample.name].outputs[sample.dataFiles[0]][".mint01"],
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
            self.assertTrue((close / total) >= 0.95)

    def testGudPyIterateByTweakFactor(self):

        self.g.purge()
        tweakFactorIterator = TweakFactorIterator(self.g, 5)
        tweakFactorIterator.iterate()

        gfPath = self.g.gudrunOutput.sampleOutputs[
            self.g.sampleBackgrounds[0].samples[0].name].gudFile
        gf1 = GudFile(gfPath)
        dcsLevelPercentage = re.findall(r'\d*[.]?\d*%', gf1.result)[0]
        dcsLevelPercentage = float(dcsLevelPercentage.replace('%', ''))
        self.assertAlmostEqual(dcsLevelPercentage, 100.0, 0)

        gfPath = self.g.gudrunOutput.sampleOutputs[
            self.g.sampleBackgrounds[0].samples[1].name].gudFile
        gf2 = GudFile(gfPath)
        dcsLevelPercentage = re.findall(r'\d*[.]?\d*%', gf2.result)[0]
        dcsLevelPercentage = float(dcsLevelPercentage.replace('%', ''))
        self.assertAlmostEqual(dcsLevelPercentage, 100.0, 0)

        gfPath = self.g.gudrunOutput.sampleOutputs[
            self.g.sampleBackgrounds[0].samples[2].name].gudFile
        gf3 = GudFile(gfPath)
        dcsLevelPercentage = re.findall(r'\d*[.]?\d*%', gf3.result)[0]
        dcsLevelPercentage = float(dcsLevelPercentage.replace('%', ''))
        self.assertAlmostEqual(dcsLevelPercentage, 100.0, 0)

        gfPath = self.g.gudrunOutput.sampleOutputs[
            self.g.sampleBackgrounds[0].samples[3].name].gudFile
        gf4 = GudFile(gfPath)
        dcsLevelPercentage = re.findall(r'\d*[.]?\d*%', gf4.result)[0]
        dcsLevelPercentage = float(dcsLevelPercentage.replace('%', ''))
        self.assertAlmostEqual(dcsLevelPercentage, 100.0, 0)

    def testGudPyIterateByThickness(self):

        self.g.purge()
        thicknessIterator = ThicknessIterator(self.g, 5)
        thicknessIterator.iterate()

        gfPath = self.g.gudrunOutput.sampleOutputs[
            self.g.sampleBackgrounds[0].samples[0].name].gudFile
        gf1 = GudFile(gfPath)
        dcsLevelPercentage = re.findall(r'\d*[.]?\d*%', gf1.result)[0]
        dcsLevelPercentage = float(dcsLevelPercentage.replace('%', ''))
        self.assertAlmostEqual(dcsLevelPercentage, 100.0, 0)

        gfPath = self.g.gudrunOutput.sampleOutputs[
            self.g.sampleBackgrounds[0].samples[1].name].gudFile
        gf2 = GudFile(gfPath)
        dcsLevelPercentage = re.findall(r'\d*[.]?\d*%', gf2.result)[0]
        dcsLevelPercentage = float(dcsLevelPercentage.replace('%', ''))
        self.assertAlmostEqual(dcsLevelPercentage, 100.0, 0)

        gfPath = self.g.gudrunOutput.sampleOutputs[
            self.g.sampleBackgrounds[0].samples[2].name].gudFile
        gf3 = GudFile(gfPath)
        dcsLevelPercentage = re.findall(r'\d*[.]?\d*%', gf3.result)[0]
        dcsLevelPercentage = float(dcsLevelPercentage.replace('%', ''))
        self.assertAlmostEqual(dcsLevelPercentage, 100.0, 0)

        gfPath = self.g.gudrunOutput.sampleOutputs[
            self.g.sampleBackgrounds[0].samples[3].name].gudFile
        gf4 = GudFile(gfPath)
        dcsLevelPercentage = re.findall(r'\d*[.]?\d*%', gf4.result)[0]
        dcsLevelPercentage = float(dcsLevelPercentage.replace('%', ''))
        self.assertAlmostEqual(dcsLevelPercentage, 100.0, 0)

    def testGudPyIterateByDensity(self):

        self.g.purge()
        densityIterator = DensityIterator(self.g, 5)
        densityIterator.iterate()

        gfPath = self.g.gudrunOutput.sampleOutputs[
            self.g.sampleBackgrounds[0].samples[0].name].gudFile
        gf1 = GudFile(gfPath)
        dcsLevelPercentage = re.findall(r'\d*[.]?\d*%', gf1.result)[0]
        dcsLevelPercentage = float(dcsLevelPercentage.replace('%', ''))
        self.assertAlmostEqual(dcsLevelPercentage, 100.0, 0)

        gfPath = self.g.gudrunOutput.sampleOutputs[
            self.g.sampleBackgrounds[0].samples[1].name].gudFile
        gf2 = GudFile(gfPath)
        dcsLevelPercentage = re.findall(r'\d*[.]?\d*%', gf2.result)[0]
        dcsLevelPercentage = float(dcsLevelPercentage.replace('%', ''))
        self.assertAlmostEqual(dcsLevelPercentage, 100.0, 0)

        gfPath = self.g.gudrunOutput.sampleOutputs[
            self.g.sampleBackgrounds[0].samples[2].name].gudFile
        gf3 = GudFile(gfPath)
        dcsLevelPercentage = re.findall(r'\d*[.]?\d*%', gf3.result)[0]
        dcsLevelPercentage = float(dcsLevelPercentage.replace('%', ''))
        self.assertAlmostEqual(dcsLevelPercentage, 100.0, 0)

        gfPath = self.g.gudrunOutput.sampleOutputs[
            self.g.sampleBackgrounds[0].samples[3].name].gudFile
        gf4 = GudFile(gfPath)
        dcsLevelPercentage = re.findall(r'\d*[.]?\d*%', gf4.result)[0]
        dcsLevelPercentage = float(dcsLevelPercentage.replace('%', ''))
        self.assertAlmostEqual(dcsLevelPercentage, 100.0, 0)

    def testIterateByThickness(self):

        self.g.purge()
        thicknessIterator = ThicknessIterator(self.g, 5)
        thicknessIterator.iterate()

        gfPath = self.g.gudrunOutput.sampleOutputs[
            self.g.sampleBackgrounds[0].samples[0].name].gudFile
        gf1 = GudFile(gfPath)
        dcsLevelPercentage = re.findall(r'\d*[.]?\d*%', gf1.result)[0]
        dcsLevelPercentage = float(dcsLevelPercentage.replace('%', ''))
        self.assertAlmostEqual(dcsLevelPercentage, 100.0, 0)

        gfPath = self.g.gudrunOutput.sampleOutputs[
            self.g.sampleBackgrounds[0].samples[1].name].gudFile
        gf2 = GudFile(gfPath)
        dcsLevelPercentage = re.findall(r'\d*[.]?\d*%', gf2.result)[0]
        dcsLevelPercentage = float(dcsLevelPercentage.replace('%', ''))
        self.assertAlmostEqual(dcsLevelPercentage, 100.0, 0)

        gfPath = self.g.gudrunOutput.sampleOutputs[
            self.g.sampleBackgrounds[0].samples[2].name].gudFile
        gf3 = GudFile(gfPath)
        dcsLevelPercentage = re.findall(r'\d*[.]?\d*%', gf3.result)[0]
        dcsLevelPercentage = float(dcsLevelPercentage.replace('%', ''))
        self.assertAlmostEqual(dcsLevelPercentage, 100.0, 0)

        gfPath = self.g.gudrunOutput.sampleOutputs[
            self.g.sampleBackgrounds[0].samples[3].name].gudFile
        gf4 = GudFile(gfPath)
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
            inelasitictyIterator = (
                InelasticitySubtraction(self.g, i)
            )
            inelasitictyIterator.iterate()

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
                self.assertTrue((close / total) >= 0.95)

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
                self.assertTrue((close / total) >= 0.95)
