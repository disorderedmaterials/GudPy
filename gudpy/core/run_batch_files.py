from abc import abstractclassmethod
from copy import deepcopy
import os
from core.enums import IterationModes
from core.tweak_factor_iterator import TweakFactorIterator
from core.thickness_iterator import ThicknessIterator
from core.radius_iterator import RadiusIterator
from core.density_iterator import DensityIterator
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
            gudrunFile.sampleBackgrounds.append(batchedSampleBackground)
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
                        ref.upstreamThickness = sample.upstreamThickness
                        ref.downstreamThickness = sample.downstreamThickness
                        ref.innerRadius = sample.innerRadius
                        ref.outerRadius = sample.outerRadius
                        ref.density = sample.density
                    for child in remappings[ref]:
                        child.tweakFactor = sample.tweakFactor
                        child.upstreamThickness = sample.upstreamThickness
                        child.downstreamThickness = sample.downstreamThickness
                        child.innerRadius = sample.innerRadius
                        child.outerRadius = sample.outerRadius
                        child.density = sample.density

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
                else:
                    n = 0
                    while n < maxIterations:
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
                        n+=1
                        if self.canConverge(remappings, batch, rtol):
                            break
                batch.iterativeOrganise(f"batch-{i}")
                self.forwardUpdate(remappings, iterationMode)
