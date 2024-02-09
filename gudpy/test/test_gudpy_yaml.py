from unittest import TestCase
import os

from core import gudpy
from core.enums import Format


class TestYAML(TestCase):
    def testYAML(self):
        gudpy1 = gudpy.GudPy()
        gudpy1.loadFromFile(
            loadFile="test/TestData/NIMROD-water/water.txt",
            format=Format.TXT
        )
        gudpy1.save(path="test/TestData/NIMROD-water/water.yaml")
        gf1 = gudpy1.gudrunFile

        gudpy2 = gudpy.GudPy()
        gudpy2.loadFromFile(
            path="test/TestData/NIMROD-water/water.yaml",
            format=Format.YAML
        )
        gf2 = gudpy2.gudrunFile

        gf1.instrument.GudrunInputFileDir = os.path.abspath(
            gf1.instrument.GudrunInputFileDir)
        gf2.instrument.GudrunInputFileDir = os.path.abspath(
            gf2.instrument.GudrunInputFileDir)

        self.self.assertDictEqual(
            gf1.instrument.__dict__, gf2.instrument.__dict__)
        self.self.assertDictEqual(gf2.beam.__dict__, gf2.beam.__dict__)

        normalisationDataFilesA = gf1.normalisation.__dict__.pop("dataFiles")
        normalisationDataFilesBgA = gf1.normalisation.__dict__.pop(
            "dataFilesBg"
        )
        normalisationCompositionA = gf1.normalisation.__dict__.pop(
            "composition"
        )
        normalisationElementsA = normalisationCompositionA.__dict__.pop(
            "elements"
        )

        normalisationDataFilesB = gf2.normalisation.__dict__.pop("dataFiles")
        normalisationDataFilesBgB = gf2.normalisation.__dict__.pop(
            "dataFilesBg"
        )
        normalisationCompositionB = gf2.normalisation.__dict__.pop(
            "composition"
        )
        normalisationElementsB = normalisationCompositionB.__dict__.pop(
            "elements"
        )

        self.assertDictEqual(
            normalisationDataFilesA.__dict__, normalisationDataFilesB.__dict__
        )
        self.assertDictEqual(
            normalisationDataFilesBgA.__dict__,
            normalisationDataFilesBgB.__dict__,
        )
        self.assertDictEqual(
            normalisationCompositionA.__dict__,
            normalisationCompositionB.__dict__,
        )
        self.assertDictEqual(
            gf1.normalisation.__dict__, gf2.normalisation.__dict__
        )

        for elementA, elementB in zip(
            normalisationElementsA, normalisationElementsB
        ):
            self.assertDictEqual(elementA.__dict__, elementB.__dict__)

        sampleBackgroundDataFilesA = gf1.sampleBackgrounds[0].__dict__.pop(
            "dataFiles"
        )
        sampleBackgroundSamplesA = gf1.sampleBackgrounds[0].__dict__.pop(
            "samples"
        )

        sampleBackgroundDataFilesB = gf2.sampleBackgrounds[0].__dict__.pop(
            "dataFiles"
        )
        sampleBackgroundSamplesB = gf2.sampleBackgrounds[0].__dict__.pop(
            "samples"
        )

        self.assertDictEqual(
            sampleBackgroundDataFilesA.__dict__,
            sampleBackgroundDataFilesB.__dict__,
        )
        self.assertDictEqual(
            gf1.sampleBackgrounds[0].__dict__,
            gf2.sampleBackgrounds[0].__dict__,
        )

        for sampleA, sampleB in zip(
            sampleBackgroundSamplesA, sampleBackgroundSamplesB
        ):
            sampleDataFilesA = sampleA.__dict__.pop("dataFiles")
            sampleCompositionA = sampleA.__dict__.pop("composition")
            sampleElementsA = sampleCompositionA.__dict__.pop("elements")
            sampleContainersA = sampleA.__dict__.pop("containers")

            sampleDataFilesB = sampleB.__dict__.pop("dataFiles")
            sampleCompositionB = sampleB.__dict__.pop("composition")
            sampleElementsB = sampleCompositionB.__dict__.pop("elements")
            sampleContainersB = sampleB.__dict__.pop("containers")

            self.assertDictEqual(
                sampleDataFilesA.__dict__, sampleDataFilesB.__dict__
            )
            self.assertDictEqual(
                sampleCompositionA.__dict__, sampleCompositionB.__dict__
            )
            for elementA, elementB in zip(sampleElementsA, sampleElementsB):
                self.assertDictEqual(elementA.__dict__, elementB.__dict__)

            self.assertDictEqual(sampleA.__dict__, sampleB.__dict__)

            for containerA, containerB in zip(
                sampleContainersA, sampleContainersB
            ):
                containerDataFilesA = containerA.__dict__.pop("dataFiles")
                containerCompositionA = containerA.__dict__.pop("composition")
                containerElementsA = containerCompositionA.__dict__.pop(
                    "elements"
                )

                containerDataFilesB = containerB.__dict__.pop("dataFiles")
                containerCompositionB = containerB.__dict__.pop("composition")
                containerElementsB = containerCompositionB.__dict__.pop(
                    "elements"
                )

                self.assertDictEqual(
                    containerDataFilesA.__dict__, containerDataFilesB.__dict__
                )
                self.assertDictEqual(
                    containerCompositionA.__dict__,
                    containerCompositionB.__dict__,
                )
                for elementA, elementB in zip(
                    containerElementsA, containerElementsB
                ):
                    self.assertDictEqual(elementA.__dict__, elementB.__dict__)

                self.assertDictEqual(containerA.__dict__, containerB.__dict__)
