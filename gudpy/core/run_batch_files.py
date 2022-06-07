from copy import deepcopy
import os

from core.enums import IterationModes
from core.tweak_factor_iterator import TweakFactorIterator
from core.thickness_iterator import ThicknessIterator
from core.radius_iterator import RadiusIterator
from core.density_iterator import DensityIterator

class BatchProcessor():

    def __init__(self, gudrunFile):
        self.gudrunFile = gudrunFile

    def batch(self, batchSize, maintainAverage=False):

        batch = deepcopy(self.gudrunFile)
        batch.sampleBackgrounds = []
        for sampleBackground in self.gudrunFile.sampleBackgrounds:
            batchedSampleBackground = deepcopy(sampleBackground)
            batchedSampleBackground.samples = []
            maxDataFiles = max([len(sample.dataFiles) for sample in sampleBackground.samples])
            for sample in sampleBackground.samples:
                if len(sample.dataFiles) % batchSize == 0:
                    nBatches = len(sample.dataFiles) // batchSize
                else:
                    nBatches = (len(sample.dataFiles) + (len(sample.dataFiles) % batchSize)) // batchSize
                if maintainAverage:
                    for i in range(maxDataFiles-batchSize):
                        batchedSample = deepcopy(sample)
                        batchedDataFiles = sample.dataFiles[i:i+batchSize]
                        batchedSample.dataFiles.dataFiles = batchedDataFiles
                        batchedSample.name += f"_batch{i}"
                        batchedSampleBackground.samples.append(batchedSample)
                else:
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
                if batch.determineError(sample) > rtol:
                    return False
        return True

    def writeDiagnosticsFile(self, path, batch, iterationMode):
        print(path)
        with open(path, "w", encoding="utf-8") as fp:
            for sampleBackground in batch.sampleBackgrounds:
                for i, sample in enumerate(sampleBackground.samples):
                    fp.write(f"Batch {i} {sample.name}\n")
                    fp.write(f"{str(sample.dataFiles)}\n")
                    fp.write(f"Error: {batch.determineError(sample)}\n")
                    if iterationMode == IterationModes.TWEAK_FACTOR:
                        fp.write(f"Tweak Factor: {sample.sampleTweakFactor}\n")
                    elif iterationMode == IterationModes.THICKNESS:
                        fp.write(f"Upstream / Downstream Thickness: {sample.upstreamThickness} {sample.downstreamThickness}\n")
                    elif iterationMode == IterationModes.INNER_RADIUS:
                        fp.write(f"Inner Radius: {sample.innerRadius}\n")
                    elif iterationMode == IterationModes.OUTER_RADIUS:
                        fp.write(f"Outer Radius: {sample.outerRadius}\n")
                    elif iterationMode == IterationModes.DENSITY:
                        fp.write(f"Density: {sample.density}")

    def process(self, batchSize=1, headless=True, iterationMode=IterationModes.NONE, rtol=0.0, maxIterations=1, maintainAverage=False):
        batch = self.batch(batchSize=batchSize, maintainAverage=maintainAverage)
        tasks = []
        if headless:
            if iterationMode == IterationModes.NONE:
                batch.process(headless=headless)
            else:            
                if iterationMode == IterationModes.TWEAK_FACTOR:
                    iterator = TweakFactorIterator(batch)
                    dirText = f"IterateByTweakFactor"
                elif iterationMode == IterationModes.THICKNESS:
                    iterator = ThicknessIterator(batch)
                    dirText = f"IterateByThickness"
                elif iterationMode == IterationModes.INNER_RADIUS:
                    iterator = RadiusIterator(batch)
                    iterator.setTargetRadius("inner")
                    iterator = ThicknessIterator(batch)
                    dirText = f"IterateByInnerRadius"
                elif iterationMode == IterationModes.OUTER_RADIUS:
                    iterator = RadiusIterator(batch)
                    iterator.setTargetRadius("outer")
                    dirText = f"IterateByOuterRadius"
                elif iterationMode == IterationModes.DENSITY:
                    iterator = DensityIterator(batch)
                    dirText = f"IterateByDensity"
                for i in range(maxIterations):
                    batch.process(headless=headless)
                    iterator.performIteration(i)
                    batch.iterativeOrganise(
                        os.path.join(
                            f"BATCH_PROCESSING_BATCH_SIZE_{batchSize}",
                            f"{dirText}_{i+1}"
                        )
                    )
                    self.writeDiagnosticsFile(
                        os.path.join(
                            batch.instrument.GudrunInputFileDir,
                            f"BATCH_PROCESSING_BATCH_SIZE_{batchSize}",
                            "batch_processing_diagnostics.txt"
                        ),
                        batch,
                        iterationMode
                    )
                    if self.canConverge(batch, rtol):
                        break
                
        else:
            if iterationMode == IterationModes.NONE:
                tasks.append(
                    batch.dcs(
                        headless=headless,
                        path=os.path.join(
                            self.gudrunFile.instrument.GudrunInputFileDir,
                            "gudpy.txt"
                        )
                    )
                )
                tasks.append(
                    [
                        batch.iterativeOrganise,
                        [
                            f"BATCH_PROCESSING_BATCH_SIZE_{batchSize}"
                        ]
                    ]
                )
            else:            
                if iterationMode == IterationModes.TWEAK_FACTOR:
                    iterator = TweakFactorIterator(batch)
                    dirText = f"IterateByTweakFactor"
                elif iterationMode == IterationModes.THICKNESS:
                    iterator = ThicknessIterator(batch)
                    dirText = f"IterateByThickness"
                elif iterationMode == IterationModes.INNER_RADIUS:
                    iterator = RadiusIterator(batch)
                    iterator.setTargetRadius("inner")
                    dirText = f"IterateByInnerRadius"
                elif iterationMode == IterationModes.OUTER_RADIUS:
                    iterator = RadiusIterator(batch)
                    iterator.setTargetRadius("outer")
                    dirText = f"IterateByOuterRadius"
                elif iterationMode == IterationModes.DENSITY:
                    iterator = DensityIterator(batch)
                    dirText = f"IterateByDensity"
                for i in range(maxIterations):
                    tasks.append(
                        batch.dcs(
                            headless=headless,
                            path=os.path.join(
                                self.gudrunFile.instrument.GudrunInputFileDir,
                                "gudpy.txt"
                            )
                        )
                    )
                    tasks.append([iterator.performIteration, [i]])
                    tasks.append(
                        [
                            batch.iterativeOrganise,
                            [
                                os.path.join(
                                    f"BATCH_PROCESSING_BATCH_SIZE_{batchSize}",
                                    f"{dirText}_{i+1}"
                                )
                            ]
                        ]
                    )
                    tasks.append(
                        [
                            self.writeDiagnosticsFile
                            [
                                os.path.join(
                                    batch.instrument.GudrunInputFileDir,
                                    f"BATCH_PROCESSING_BATCH_SIZE_{batchSize}",
                                    "batch_processing_diagnostics.txt"
                                ),
                                batch,
                                iterationMode
                            ]
                        ]
                    )
                    tasks.append(
                        [
                            self.canConverge,
                            [batch, rtol]
                        ]
                    )
        if not headless:
            return tasks