from copy import deepcopy
import os

from core.enums import IterationModes
from core.tweak_factor_iterator import TweakFactorIterator
from core.thickness_iterator import ThicknessIterator
from core.radius_iterator import RadiusIterator
from core.density_iterator import DensityIterator


class BatchProcessor:
    def __init__(self, gudrunFile):
        self.gudrunFile = gudrunFile

    def batch(self, batchSize, maintainAverage=False):

        batch = deepcopy(self.gudrunFile)
        batch.sampleBackgrounds = []
        for sampleBackground in self.gudrunFile.sampleBackgrounds:
            batchedSampleBackground = deepcopy(sampleBackground)
            batchedSampleBackground.samples = []
            maxDataFiles = max(
                [len(sample.dataFiles) for sample in sampleBackground.samples]
            )
            for sample in sampleBackground.samples:
                if len(sample.dataFiles) % batchSize == 0:
                    nBatches = len(sample.dataFiles) // batchSize
                else:
                    nBatches = (
                        len(sample.dataFiles)
                        + (len(sample.dataFiles) % batchSize)
                    ) // batchSize
                if maintainAverage:
                    for i in range(maxDataFiles - batchSize):
                        batchedSample = deepcopy(sample)
                        batchedDataFiles = sample.dataFiles[i: i + batchSize]
                        batchedSample.dataFiles.dataFiles = batchedDataFiles
                        batchedSample.name += f"_batch{i}"
                        batchedSampleBackground.samples.append(batchedSample)
                else:
                    for i in range(nBatches):
                        batchedSample = deepcopy(sample)
                        batchedDataFiles = sample.dataFiles[
                            i * batchSize: (i + 1) * batchSize
                        ]
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
                if abs(batch.determineError(sample)) > rtol:
                    return False
        return True

    def writeDiagnosticsFile(self, path, batch, iterationMode):
        with open(path, "w", encoding="utf-8") as fp:
            for sampleBackground in batch.sampleBackgrounds:
                for i, sample in enumerate(sampleBackground.samples):
                    fp.write(f"Batch {i} {sample.name}\n")
                    fp.write(f"{str(sample.dataFiles)}\n")
                    fp.write(f"Error: {batch.determineError(sample)}%\n")
                    if iterationMode == IterationModes.TWEAK_FACTOR:
                        fp.write(f"Tweak Factor: {sample.sampleTweakFactor}\n")
                    elif iterationMode == IterationModes.THICKNESS:
                        fp.write(
                            f"Upstream / Downstream Thickness: "
                            f"{sample.upstreamThickness} "
                            f"{sample.downstreamThickness}\n"
                        )
                    elif iterationMode == IterationModes.INNER_RADIUS:
                        fp.write(f"Inner Radius: {sample.innerRadius}\n")
                    elif iterationMode == IterationModes.OUTER_RADIUS:
                        fp.write(f"Outer Radius: {sample.outerRadius}\n")
                    elif iterationMode == IterationModes.DENSITY:
                        fp.write(f"Density: {sample.density}\n")

    def process(
        self,
        batchSize=1,
        headless=True,
        iterationMode=IterationModes.NONE,
        rtol=0.0,
        maxIterations=1,
        maintainAverage=False,
    ):
        self.batchedGudrunFile = self.batch(
            batchSize=batchSize, maintainAverage=maintainAverage
        )
        tasks = []
        if headless:
            if iterationMode == IterationModes.NONE:
                self.batchedGudrunFile.process(headless=headless)
                self.writeDiagnosticsFile(
                    os.path.join(
                        self.batchedGudrunFile.instrument.GudrunInputFileDir,
                        f"BATCH_PROCESSING_BATCH_SIZE_{batchSize}",
                        "batch_processing_diagnostics.txt",
                    ),
                    self.batchedGudrunFile,
                    iterationMode,
                )
            else:
                if iterationMode == IterationModes.TWEAK_FACTOR:
                    iterator = TweakFactorIterator(self.batchedGudrunFile)
                    dirText = "IterateByTweakFactor"
                elif iterationMode == IterationModes.THICKNESS:
                    iterator = ThicknessIterator(self.batchedGudrunFile)
                    dirText = "IterateByThickness"
                elif iterationMode == IterationModes.INNER_RADIUS:
                    iterator = RadiusIterator(self.batchedGudrunFile)
                    iterator.setTargetRadius("inner")
                    iterator = ThicknessIterator(self.batchedGudrunFile)
                    dirText = "IterateByInnerRadius"
                elif iterationMode == IterationModes.OUTER_RADIUS:
                    iterator = RadiusIterator(self.batchedGudrunFile)
                    iterator.setTargetRadius("outer")
                    dirText = "IterateByOuterRadius"
                elif iterationMode == IterationModes.DENSITY:
                    iterator = DensityIterator(self.batchedGudrunFile)
                    dirText = "IterateByDensity"
                for i in range(maxIterations):
                    self.batchedGudrunFile.process(headless=headless)
                    iterator.performIteration(i)
                    self.batchedGudrunFile.iterativeOrganise(
                        os.path.join(
                            f"BATCH_PROCESSING_BATCH_SIZE_{batchSize}",
                            f"{dirText}_{i+1}",
                        )
                    )
                    self.writeDiagnosticsFile(
                        os.path.join(
                            self.gudrunFile.instrument.GudrunInputFileDir,
                            f"BATCH_PROCESSING_BATCH_SIZE_{batchSize}",
                            "batch_processing_diagnostics.txt",
                        ),
                        self.batchedGudrunFile,
                        iterationMode,
                    )
                    if self.canConverge(self.batchedGudrunFile, rtol):
                        break

        else:
            if iterationMode == IterationModes.NONE:
                tasks.append(
                    self.batchedGudrunFile.dcs(
                        headless=headless,
                        path=os.path.join(
                            self.gudrunFile.instrument.GudrunInputFileDir,
                            "gudpy.txt",
                        ),
                    )
                )
                tasks.append(
                    [
                        self.batchedGudrunFile.iterativeOrganise,
                        [f"BATCH_PROCESSING_BATCH_SIZE_{batchSize}"],
                    ]
                )
                tasks.append(
                    [
                        self.writeDiagnosticsFile,
                        [
                            os.path.join(
                                self.gudrunFile.instrument.GudrunInputFileDir,
                                f"BATCH_PROCESSING_BATCH_SIZE_{batchSize}",
                                "batch_processing_diagnostics.txt",
                            ),
                            self.batchedGudrunFile,
                            iterationMode
                        ]
                    ]
                )
            else:
                if iterationMode == IterationModes.TWEAK_FACTOR:
                    iterator = TweakFactorIterator(self.batchedGudrunFile)
                    dirText = "IterateByTweakFactor"
                elif iterationMode == IterationModes.THICKNESS:
                    iterator = ThicknessIterator(self.batchedGudrunFile)
                    dirText = "IterateByThickness"
                elif iterationMode == IterationModes.INNER_RADIUS:
                    iterator = RadiusIterator(self.batchedGudrunFile)
                    iterator.setTargetRadius("inner")
                    dirText = "IterateByInnerRadius"
                elif iterationMode == IterationModes.OUTER_RADIUS:
                    iterator = RadiusIterator(self.batchedGudrunFile)
                    iterator.setTargetRadius("outer")
                    dirText = "IterateByOuterRadius"
                elif iterationMode == IterationModes.DENSITY:
                    iterator = DensityIterator(self.batchedGudrunFile)
                    dirText = "IterateByDensity"
                for i in range(maxIterations):
                    tasks.append(
                        self.batchedGudrunFile.dcs(
                            headless=headless,
                            path=os.path.join(
                                self.gudrunFile.instrument.GudrunInputFileDir,
                                "gudpy.txt",
                            ),
                        )
                    )
                    tasks.append([iterator.performIteration, [i]])
                    tasks.append(
                        [
                            self.batchedGudrunFile.iterativeOrganise,
                            [
                                os.path.join(
                                    f"BATCH_PROCESSING_BATCH_SIZE_{batchSize}",
                                    f"{dirText}_{i+1}",
                                )
                            ],
                        ]
                    )
                    tasks.append(
                        [
                            self.writeDiagnosticsFile,
                            [
                                os.path.join(
                                    (
                                        self.gudrunFile.instrument.
                                        GudrunInputFileDir
                                    ),
                                    f"BATCH_PROCESSING_BATCH_SIZE_{batchSize}",
                                    "batch_processing_diagnostics.txt",
                                ),
                                self.batchedGudrunFile,
                                iterationMode
                            ]
                        ]
                    )
                    tasks.append(
                        [
                            self.canConverge,
                            [
                                self.batchedGudrunFile, rtol
                            ]
                        ]
                    )
        if not headless:
            return tasks
