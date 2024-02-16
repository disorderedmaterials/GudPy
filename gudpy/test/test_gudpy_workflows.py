import os
from copy import deepcopy
from unittest import TestCase
import re
import math
import tempfile
import traceback

from core.composition import Composition, Component
from core import iterators
from core.gud_file import GudFile
from core import gudpy


class GudPyContext:
    def __init__(self):
        self.tempdir = tempfile.TemporaryDirectory()
        testDir = os.path.dirname(__file__)
        path = os.path.join(
            testDir, "TestData/NIMROD-water/good_water")

        self.gudpy = gudpy.GudPy()

        self.gudpy.loadFromProject(projectDir=path)
        self.gudpy.saveAs(os.path.join(
            self.tempdir.name, "test_water"))

        from pathlib import Path
        dataFileDir = Path("test/TestData/NIMROD-water/raw").absolute()
        self.gudpy.gudrunFile.instrument.dataFileDir = str(dataFileDir) + "/"

    def __enter__(self):
        return self.gudpy

    def __exit__(self, exc_type, exc_value, tb):
        self.tempdir.cleanup()
        if exc_type is not None:
            traceback.print_exception(exc_type, exc_value, tb)
            return False
        return True


class TestGudPyWorkflows(TestCase):
    def getGudFile(self, gudpy, sampleIndex):
        return gudpy.gudrunOutput.sampleOutputs[
            gudpy.gudrunFile.sampleBackgrounds[0].samples[
                sampleIndex].name].gudFile

    def testGudPyDCS(self):
        with GudPyContext() as gudpy:
            gudpy.runGudrun()
            gfPath = self.getGudFile(gudpy, 0)
            with open(gfPath, "r", encoding="utf-8") as f:
                print(f.readlines())
            gf1 = GudFile(gfPath)
            dcsLevelPercentage = re.findall(r'\d*[.]?\d*%', gf1.err)[0]
            dcsLevelPercentage = float(dcsLevelPercentage.replace('%', ''))
            self.assertAlmostEqual(dcsLevelPercentage, 14.1, 0)

            gfPath = self.getGudFile(gudpy, 1)
            gf2 = GudFile(gfPath)
            dcsLevelPercentage = re.findall(r'\d*[.]?\d*%', gf2.result)[0]
            dcsLevelPercentage = float(dcsLevelPercentage.replace('%', ''))
            self.assertAlmostEqual(dcsLevelPercentage, 100.0, 0)

            gfPath = self.getGudFile(gudpy, 2)
            gf3 = GudFile(gfPath)
            dcsLevelPercentage = re.findall(r'\d*[.]?\d*%', gf3.result)[0]
            dcsLevelPercentage = float(dcsLevelPercentage.replace('%', ''))
            self.assertAlmostEqual(dcsLevelPercentage, 98.0, 0)

            gfPath = self.getGudFile(gudpy, 3)
            gf4 = GudFile(gfPath)
            dcsLevelPercentage = re.findall(r'\d*[.]?\d*%', gf4.err)[0]
            dcsLevelPercentage = float(dcsLevelPercentage.replace('%', ''))
            self.assertAlmostEqual(dcsLevelPercentage, 13.0, 0)

            for sample in gudpy.gudrunFile.sampleBackgrounds[0].samples:
                mintFilename = (
                    os.path.splitext(sample.dataFiles[0])[0]
                )

                actualMintFile = ("test/TestData/water-ref/plain/"
                                  f"{mintFilename}.mint01")
                actualData = open(gudpy.gudrunOutput.sampleOutputs[
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
        with GudPyContext() as gudpy:
            gudpy.runPurge()
            iterator = iterators.TweakFactor(5)
            gudpy.iterateGudrun(iterator)

            self.assertEqual(gudpy.gudrunIterator.exitcode[0], 0)

            gfPath = self.getGudFile(gudpy, 0)
            gf1 = GudFile(gfPath)
            dcsLevelPercentage = re.findall(r'\d*[.]?\d*%', gf1.result)[0]
            dcsLevelPercentage = float(dcsLevelPercentage.replace('%', ''))
            self.assertAlmostEqual(dcsLevelPercentage, 100.0, 0)

            gfPath = self.getGudFile(gudpy, 1)
            gf2 = GudFile(gfPath)
            dcsLevelPercentage = re.findall(r'\d*[.]?\d*%', gf2.result)[0]
            dcsLevelPercentage = float(dcsLevelPercentage.replace('%', ''))
            self.assertAlmostEqual(dcsLevelPercentage, 100.0, 0)

            gfPath = self.getGudFile(gudpy, 2)
            gf3 = GudFile(gfPath)
            dcsLevelPercentage = re.findall(r'\d*[.]?\d*%', gf3.result)[0]
            dcsLevelPercentage = float(dcsLevelPercentage.replace('%', ''))
            self.assertAlmostEqual(dcsLevelPercentage, 100.0, 0)

            gfPath = self.getGudFile(gudpy, 3)
            gf4 = GudFile(gfPath)
            dcsLevelPercentage = re.findall(r'\d*[.]?\d*%', gf4.result)[0]
            dcsLevelPercentage = float(dcsLevelPercentage.replace('%', ''))
            self.assertAlmostEqual(dcsLevelPercentage, 100.0, 0)

    def testGudPyIterateByThickness(self):
        with GudPyContext() as gudpy:
            gudpy.runPurge()
            iterator = iterators.Thickness(5)
            gudpy.iterateGudrun(iterator)

            gfPath = self.getGudFile(gudpy, 0)
            gf1 = GudFile(gfPath)
            dcsLevelPercentage = re.findall(r'\d*[.]?\d*%', gf1.result)[0]
            dcsLevelPercentage = float(dcsLevelPercentage.replace('%', ''))
            self.assertAlmostEqual(dcsLevelPercentage, 100.0, 0)

            gfPath = self.getGudFile(gudpy, 1)
            gf2 = GudFile(gfPath)
            dcsLevelPercentage = re.findall(r'\d*[.]?\d*%', gf2.result)[0]
            dcsLevelPercentage = float(dcsLevelPercentage.replace('%', ''))
            self.assertAlmostEqual(dcsLevelPercentage, 100.0, 0)

            gfPath = self.getGudFile(gudpy, 2)
            gf3 = GudFile(gfPath)
            dcsLevelPercentage = re.findall(r'\d*[.]?\d*%', gf3.result)[0]
            dcsLevelPercentage = float(dcsLevelPercentage.replace('%', ''))
            self.assertAlmostEqual(dcsLevelPercentage, 100.0, 0)

            gfPath = self.getGudFile(gudpy, 3)
            gf4 = GudFile(gfPath)
            dcsLevelPercentage = re.findall(r'\d*[.]?\d*%', gf4.result)[0]
            dcsLevelPercentage = float(dcsLevelPercentage.replace('%', ''))
            self.assertAlmostEqual(dcsLevelPercentage, 100.0, 0)

    def testGudPyIterateByDensity(self):
        with GudPyContext() as gudpy:
            gudpy.runPurge()
            iterator = iterators.Density(5)
            gudpy.iterateGudrun(iterator)

            gfPath = self.getGudFile(gudpy, 0)
            gf1 = GudFile(gfPath)
            dcsLevelPercentage = re.findall(r'\d*[.]?\d*%', gf1.result)[0]
            dcsLevelPercentage = float(dcsLevelPercentage.replace('%', ''))
            self.assertAlmostEqual(dcsLevelPercentage, 100.0, 0)

            gfPath = self.getGudFile(gudpy, 1)
            gf2 = GudFile(gfPath)
            dcsLevelPercentage = re.findall(r'\d*[.]?\d*%', gf2.result)[0]
            dcsLevelPercentage = float(dcsLevelPercentage.replace('%', ''))
            self.assertAlmostEqual(dcsLevelPercentage, 100.0, 0)

            gfPath = self.getGudFile(gudpy, 2)
            gf3 = GudFile(gfPath)
            dcsLevelPercentage = re.findall(r'\d*[.]?\d*%', gf3.result)[0]
            dcsLevelPercentage = float(dcsLevelPercentage.replace('%', ''))
            self.assertAlmostEqual(dcsLevelPercentage, 100.0, 0)

            gfPath = self.getGudFile(gudpy, 3)
            gf4 = GudFile(gfPath)
            dcsLevelPercentage = re.findall(r'\d*[.]?\d*%', gf4.result)[0]
            dcsLevelPercentage = float(dcsLevelPercentage.replace('%', ''))
            self.assertAlmostEqual(dcsLevelPercentage, 100.0, 0)

    def testIterateByComposition(self):
        with GudPyContext() as gudpy:
            g = deepcopy(gudpy.gudrunFile)
            gudpy.runPurge()
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

            gudpy.gudrunFile = g

            gudpy.runPurge()
            iterator = iterators.Composition(
                gudrunFile=g,
                nTotal=10,
                rtol=3,
                components=[h2]
            )
            gudpy.iterateComposition(iterator)
            newComp = iterator.updatedSample.composition
            self.assertAlmostEqual(
                newComp.weightedComponents[0].ratio, 2, 1
            )

            self.assertEqual(
                newComp.weightedComponents[1].ratio, 1
            )

    def testGudPyIterateBySubtractingWavelength(self):
        with GudPyContext() as gudpy:
            for i in range(1, 4):
                gudpy.runPurge()
                inelasitictyIterator = (
                    iterators.InelasticitySubtraction(i)
                )
                gudpy.iterateGudrun(inelasitictyIterator)
                self.g = gudpy.gudrunFile

                for sample in [
                    x
                    for x in gudpy.gudrunFile.sampleBackgrounds[0].samples
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
                        gudpy.gudrunIterator.iterator.gudrunOutputs[-1].output(
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
                        gudpy.gudrunIterator.iterator.gudrunOutputs[
                            len(
                                gudpy.gudrunIterator.iterator.gudrunOutputs
                            ) - 2
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
