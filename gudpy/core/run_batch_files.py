from abc import abstractclassmethod
from copy import deepcopy
import os
from core.enums import IterationModes
from core.tweak_factor_iterator import TweakFactorIterator
from gudpy.core.gud_file import GudFile
import numpy as np

class BatchProcessor():

    def __init__(self, gudrunFile):
        self.gudrunFile = gudrunFile

    def batch(self, batchSize):
        samples = {
            sample : []
            for sampleBackground in self.gudrunFile.sampleBackgrounds
            for sample in sampleBackground.samples
        }

        batches = []
        for i, sampleBackground in enumerate(self.gudrunFile.sampleBackgrounds):
            gudrunFile = deepcopy(self.gudrunFile)
            gudrunFile.sampleBackgrounds = []
            batchedSampleBackground = deepcopy(sampleBackground)
            batchedSampleBackground.samples = []
            for sample in sampleBackground.samples:
                batchedSample = deepcopy(sample)
                batch = sample.dataFiles[i*batchSize:(i+1)*batchSize]
                batchedSample.dataFiles.dataFiles = batch
                batchedSampleBackground.samples.append(batchedSample)
                samples[sample].append(batchedSample)
            gudrunFile.append(batchedSampleBackground)
            batches.append(gudrunFile)
        
        return samples, batches

    def forwardUpdate(self, remappings, batch, iterationMode):
        if iterationMode == IterationModes.NONE:
            return
        for sampleBackground in batch.sampleBackgrounds:
            for sample in sampleBackground.samples:
                for ref in remappings.keys():
                    if ref == sample:
                        ref.tweakFactor = sample.tweakFactor
                    for child in remappings[ref]:
                        child.tweakFactor = sample.tweakFactor

    def canConverge(self, remappings, rtol):
        if rtol == 0.0:
            return False
        for sample in remappings.keys():
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
        remappings, batches = self.batch(batchSize=batchSize)
        for i, batch in enumerate(batches):
            if headless and not self.canConverge(remappings, rtol):
                if iterationMode == IterationModes.NONE:
                    batch.process(headless=headless)
                elif iterationMode == IterationModes.TWEAK_FACTOR:
                    n = 0
                    while n < maxIterations:
                        iterator = TweakFactorIterator(batch)
                        iterator.performIteration(n)
                        n+=1
                        if self.canConverge(remappings, batch, rtol):
                            break
                batch.iterativeOrganise(f"batch-{i}")
                self.forwardUpdate(remappings, iterationMode)
