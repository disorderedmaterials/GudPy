from abc import abstractclassmethod
from copy import deepcopy
import os
from core.enums import IterationModes
from core.tweak_factor_iterator import TweakFactorIterator
from core.thickness_iterator import ThicknessIterator
from core.radius_iterator import RadiusIterator
from core.density_iterator import DensityIterator
from core.gud_file import GudFile
import numpy as np

class BatchProcessor():

    def __init__(self, gudrunFile):
        self.gudrunFile = gudrunFile

    def batch(self, batchSize):

        batch = deepcopy(self.gudrunFile)
        batch.sampleBackgrounds = []
        for sampleBackground in self.gudrunFile.sampleBackgrounds:
            batchedSampleBackground = deepcopy(sampleBackground)
            batchedSampleBackground.samples = []
            for sample in sampleBackground.samples:
                if len(sample.dataFiles) % batchSize == 0:
                    nBatches = len(sample.dataFiles) // batchSize
                else:
                    nBatches = (len(sample.dataFiles) + (len(sample.dataFiles) % batchSize)) // batchSize
                for i in range(nBatches):
                    batchedSample = deepcopy(sample)
                    batchedDataFiles = sample.dataFiles[i*batchSize:(i+1)*batchSize]
                    batchedSample.dataFiles.dataFiles = batchedDataFiles
                    batchedSample.name += f"_batch{i}"
                    batchedSampleBackground.samples.append(batchedSample)
            batch.sampleBackgrounds.append(batchedSampleBackground)

        return batch

    def canConverge(self, batch, rtol):
        if rtol == 0.0:
            return False
        for sampleBackground in batch.sampleBackgrounds:
            for sample in sampleBackground.samples:
                gudPath = sample.dataFiles[0].replace(
                            self.gudrunFile.instrument.dataFileType,
                            "gud"
                        )
                gudFile = GudFile(
                    os.path.join(
                        self.gudrunFile.instrument.GudrunInputFileDir, gudPath
                    )
                )
                error = round(
                    (
                        (
                            gudFile.averageLevelMergedDCS - gudFile.expectedDCS
                        ) 
                        / gudFile.averageLevelMergedDCS
                    )*100, 1
                )
                if abs(error) > rtol:
                    return False
        return True

    def process(self, batchSize=1, headless=True, iterationMode=IterationModes.NONE, rtol=0.0, maxIterations=1):
        batch = self.batch(batchSize=batchSize)
        print(f"BATCH_PROCESSING: Iteration mode is {iterationMode.name}")
        print(f"BATCH_PROCESSING: max iterations is {maxIterations}")
        print(f"BATCH_PROCESSING: rtol for convergence is {rtol}")

        for sample in batch.sampleBackgrounds[0].samples:
            print(f"BATCH_PROCESSING: starting tweak factor: {sample.sampleTweakFactor}")
        if headless:
            n = 0
            while n < maxIterations:
                print(f"BATCH_PROCESSING: iteration {n}")
                if iterationMode == IterationModes.TWEAK_FACTOR:
                    iterator = TweakFactorIterator(batch)
                elif iterationMode == IterationModes.THICKNESS:
                    iterator = ThicknessIterator(batch)
                elif iterationMode == IterationModes.INNER_RADIUS:
                    iterator = RadiusIterator(batch)
                    iterator.setTargetRadius("inner")
                elif iterationMode == IterationModes.OUTER_RADIUS:
                    iterator = RadiusIterator(batch)
                    iterator.setTargetRadius("outer")
                elif iterationMode == IterationModes.DENSITY:
                    iterator = DensityIterator(batch)
                iterator.performIteration(n)
                batch.process(headless=headless)
                n+=1
                if self.canConverge(batch, rtol):
                    print("BATCH_PROCESSING: convergence tolerance reached.")
                    break
            batch.iterativeOrganise(f"BATCH_PROCESSING_BATCH_SIZE_{batchSize}")
        for sample in batch.sampleBackgrounds[0].samples:
            print(f"BATCH_PROCESSING: ending tweak factor: {sample.sampleTweakFactor}")
