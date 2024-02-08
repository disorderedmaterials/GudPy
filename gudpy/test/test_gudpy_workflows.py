import os
from copy import deepcopy
from unittest import TestCase
import re
import math

from core.composition import Composition, Component
from core import iterators
from core.gud_file import GudFile
from core.enums import Format
from core import gudpy


class TestGudPyWorkflows(TestCase):
    def setUp(self) -> None:

        testDir = os.path.dirname(__file__)
        path = os.path.join(
            testDir, "TestData/NIMROD-water/good_water")

        self.gudpy = gudpy.GudPy()

        self.keepsakes = os.listdir()

        self.gudpy.loadFromProject(path)

        from pathlib import Path
        dataFileDir = Path("test/TestData/NIMROD-water/raw").absolute()
        self.gudpy.gudrunFile.instrument.dataFileDir = str(dataFileDir) + "/"

        return super().setUp()

    def tearDown(self) -> None:

        [os.remove(f) for f in os.listdir() if f not in self.keepsakes]
        return super().tearDown()

    def getGudFile(self, sampleIndex):
        return self.gudpy.gudrunOutput.sampleOutputs[
            self.gudpy.gudrunFile.sampleBackgrounds[0].samples[
                sampleIndex].name].gudFile

    def testGudPyDCS(self):
        self.gudpy.runGudrun()
        gfPath = self.getGudFile(0)
        gf1 = GudFile(gfPath)
        dcsLevelPercentage = re.findall(r'\d*[.]?\d*%', gf1.err)[0]
        dcsLevelPercentage = float(dcsLevelPercentage.replace('%', ''))
        self.assertAlmostEqual(dcsLevelPercentage, 14.1, 0)

        gfPath = self.getGudFile(1)
        gf2 = GudFile(gfPath)
        dcsLevelPercentage = re.findall(r'\d*[.]?\d*%', gf2.result)[0]
        dcsLevelPercentage = float(dcsLevelPercentage.replace('%', ''))
        self.assertAlmostEqual(dcsLevelPercentage, 100.0, 0)

        gfPath = self.getGudFile(2)
        gf3 = GudFile(gfPath)
        dcsLevelPercentage = re.findall(r'\d*[.]?\d*%', gf3.result)[0]
        dcsLevelPercentage = float(dcsLevelPercentage.replace('%', ''))
        self.assertAlmostEqual(dcsLevelPercentage, 98.0, 0)

        gfPath = self.getGudFile(3)
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
        self.gudpy.runPurge()
        iterator = iterators.TweakFactor(5)
        self.gudpy.iterateGudrun(iterator)

        self.assertEqual(self.gudpy.gudrunIterator.exitcode[0], 0)

        gfPath = self.getGudFile(0)
        gf1 = GudFile(gfPath)
        dcsLevelPercentage = re.findall(r'\d*[.]?\d*%', gf1.result)[0]
        dcsLevelPercentage = float(dcsLevelPercentage.replace('%', ''))
        self.assertAlmostEqual(dcsLevelPercentage, 100.0, 0)

        gfPath = self.getGudFile(1)
        gf2 = GudFile(gfPath)
        dcsLevelPercentage = re.findall(r'\d*[.]?\d*%', gf2.result)[0]
        dcsLevelPercentage = float(dcsLevelPercentage.replace('%', ''))
        self.assertAlmostEqual(dcsLevelPercentage, 100.0, 0)

        gfPath = self.getGudFile(2)
        gf3 = GudFile(gfPath)
        dcsLevelPercentage = re.findall(r'\d*[.]?\d*%', gf3.result)[0]
        dcsLevelPercentage = float(dcsLevelPercentage.replace('%', ''))
        self.assertAlmostEqual(dcsLevelPercentage, 100.0, 0)

        gfPath = self.getGudFile(3)
        gf4 = GudFile(gfPath)
        dcsLevelPercentage = re.findall(r'\d*[.]?\d*%', gf4.result)[0]
        dcsLevelPercentage = float(dcsLevelPercentage.replace('%', ''))
        self.assertAlmostEqual(dcsLevelPercentage, 100.0, 0)

    def testGudPyIterateByThickness(self):
        self.gudpy.runPurge()
        iterator = iterators.Thickness(5)
        self.gudpy.iterateGudrun(iterator)

        gfPath = self.getGudFile(0)
        gf1 = GudFile(gfPath)
        dcsLevelPercentage = re.findall(r'\d*[.]?\d*%', gf1.result)[0]
        dcsLevelPercentage = float(dcsLevelPercentage.replace('%', ''))
        self.assertAlmostEqual(dcsLevelPercentage, 100.0, 0)

        gfPath = self.getGudFile(1)
        gf2 = GudFile(gfPath)
        dcsLevelPercentage = re.findall(r'\d*[.]?\d*%', gf2.result)[0]
        dcsLevelPercentage = float(dcsLevelPercentage.replace('%', ''))
        self.assertAlmostEqual(dcsLevelPercentage, 100.0, 0)

        gfPath = self.getGudFile(2)
        gf3 = GudFile(gfPath)
        dcsLevelPercentage = re.findall(r'\d*[.]?\d*%', gf3.result)[0]
        dcsLevelPercentage = float(dcsLevelPercentage.replace('%', ''))
        self.assertAlmostEqual(dcsLevelPercentage, 100.0, 0)

        gfPath = self.getGudFile(3)
        gf4 = GudFile(gfPath)
        dcsLevelPercentage = re.findall(r'\d*[.]?\d*%', gf4.result)[0]
        dcsLevelPercentage = float(dcsLevelPercentage.replace('%', ''))
        self.assertAlmostEqual(dcsLevelPercentage, 100.0, 0)

    def testGudPyIterateByDensity(self):
        self.gudpy.runPurge()
        iterator = iterators.Density(5)
        self.gudpy.iterateGudrun(iterator)

        gfPath = self.getGudFile(0)
        gf1 = GudFile(gfPath)
        dcsLevelPercentage = re.findall(r'\d*[.]?\d*%', gf1.result)[0]
        dcsLevelPercentage = float(dcsLevelPercentage.replace('%', ''))
        self.assertAlmostEqual(dcsLevelPercentage, 100.0, 0)

        gfPath = self.getGudFile(1)
        gf2 = GudFile(gfPath)
        dcsLevelPercentage = re.findall(r'\d*[.]?\d*%', gf2.result)[0]
        dcsLevelPercentage = float(dcsLevelPercentage.replace('%', ''))
        self.assertAlmostEqual(dcsLevelPercentage, 100.0, 0)

        gfPath = self.getGudFile(2)
        gf3 = GudFile(gfPath)
        dcsLevelPercentage = re.findall(r'\d*[.]?\d*%', gf3.result)[0]
        dcsLevelPercentage = float(dcsLevelPercentage.replace('%', ''))
        self.assertAlmostEqual(dcsLevelPercentage, 100.0, 0)

        gfPath = self.getGudFile(3)
        gf4 = GudFile(gfPath)
        dcsLevelPercentage = re.findall(r'\d*[.]?\d*%', gf4.result)[0]
        dcsLevelPercentage = float(dcsLevelPercentage.replace('%', ''))
        self.assertAlmostEqual(dcsLevelPercentage, 100.0, 0)

    def testIterateByComposition(self):
        g = deepcopy(self.gudpy.gudrunFile)
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

        self.gudpy.gudrunFile = g

        self.gudpy.runPurge()
        iterator = iterators.CompositionIterator(
            gudrunFile=g,
            nTotal=10,
            rtol=3,
            components=[h2]
        )
        self.gudpy.iterateComposition(iterator)
        self.assertAlmostEqual(
            sample.composition.weightedComponents[0].ratio, 2, 1
        )

        self.assertEqual(
            sample.composition.weightedComponents[1].ratio, 1
        )

    def testGudPyIterateBySubtractingWavelength(self):
        for i in range(1, 4):
            self.gudpy.runPurge
            inelasitictyIterator = (
                iterators.InelasticitySubtraction(i)
            )
            self.gudpy.iterateGudrun(inelasitictyIterator)
            self.g = self.gudpy.gudrunFile

            for sample in [
                x
                for x in self.g.sampleBackgrounds[0].samples
                if x.runThisSample
            ]:
                dataFilename = (
                    os.path.splitext(sample.dataFiles[0])[0]
                )

                actualMintFile = (
                    f'test/TestData/water-ref/wavelength{i}/'
                    f'{dataFilename}.mint01'
                )

                actualData = open(
                    self.gudpy.gudrunOutput[
                        len(self.gudpy.gudrunOutput) - 1
                    ].output(
                        sample.name, sample.dataFiles[0], ".mint01"),
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
                            rel_tol=0.02
                        ):
                            close += 1
                self.assertTrue((close / total) >= 0.95)

                actualMsubFilename = (
                    f'test/TestData/water-ref/wavelength{i}/'
                    f'{dataFilename}.msubw01'
                )

                actualData = open(
                    self.gudpy.gudrunOutput[
                        len(self.gudpy.gudrunOutput) - 2
                    ].output(
                        sample.name, sample.dataFiles[0], ".msubw01"),
                    "r", encoding="utf-8"
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
