from copy import deepcopy
import os
from core.enums import IterationModes
from core.iterators import (
    DensityIterator,
    TweakFactorIterator,
    ThicknessIterator,
    RadiusIterator
)


class BatchProcessor:
    def __init__(self, gudrunFile):
        self.gudrunFile = gudrunFile

    def batch(self, batchSize, stepSize, separateFirstBatch, offset=0):

        if not separateFirstBatch:
            batch = deepcopy(self.gudrunFile)
            batch.sampleBackgrounds = []
            for sampleBackground in self.gudrunFile.sampleBackgrounds:
                batchedSampleBackground = deepcopy(sampleBackground)
                batchedSampleBackground.samples = []
                maxDataFiles = max(
                    [
                        len(sample.dataFiles)
                        for sample in sampleBackground.samples
                    ]
                )
                for sample in sampleBackground.samples:
                    for i in range(offset, maxDataFiles, stepSize):
                        batchedSample = deepcopy(sample)
                        batchedSample.dataFiles.dataFiles = sample.dataFiles[
                            i: i + batchSize
                        ]
                        batchedSampleBackground.samples.append(batchedSample)
                batch.sampleBackgrounds.append(batchedSampleBackground)

            return batch
        else:
            first = deepcopy(self.gudrunFile)
            first.sampleBackgrounds = []
            for sampleBackground in self.gudrunFile.sampleBackgrounds:
                batchedSampleBackground = deepcopy(sampleBackground)
                batchedSampleBackground.samples = []
                for sample in sampleBackground.samples:
                    batchedSample = deepcopy(sample)
                    batchedSample.dataFiles.dataFiles = (
                        sample.dataFiles[:batchSize]
                    )
                    batchedSampleBackground.samples.append(batchedSample)
                first.sampleBackgrounds.append(batchedSampleBackground)
            return (
                first,
                self.batch(batchSize, stepSize, False, offset=stepSize)
            )

    def canConverge(self, batch, rtol):
        if rtol == 0.0:
            return False
        for sampleBackground in batch.sampleBackgrounds:
            for sample in sampleBackground.samples:
                if abs(batch.determineError(sample)) > rtol:
                    return False
        return True

    def checkConvergenceAndPropogate(self, current, next, rtol, iterationMode):
        if self.canConverge(current, rtol):
            self.propogateResults(current, next, iterationMode)
            return True, True
        return False, True

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

    def propogateResults(self, current, next, iterationMode):
        for (
            sampleBackgroundA, sampleBackgroundB
        ) in zip(current.sampleBackgrounds, next.sampleBackgrounds):
            for (
                sampleA, sampleB
            ) in zip(sampleBackgroundA.samples, sampleBackgroundB.samples):
                if iterationMode == IterationModes.TWEAK_FACTOR:
                    sampleB.sampleTweakFactor = sampleA.sampleTweakFactor
                elif iterationMode == IterationModes.THICKNESS:
                    sampleB.upstreamThickness = sampleA.upstreamThickness
                    sampleB.downstreamThickness = sampleA.downstreamThickness
                elif iterationMode == IterationModes.INNER_RADIUS:
                    sampleB.innerRadius = sampleA.innerRadius
                elif iterationMode == IterationModes.OUTER_RADIUS:
                    sampleB.outerRadius = sampleA.outerRadius
                elif iterationMode == IterationModes.DENSITY:
                    sampleB.density = sampleA.density

    def process(
        self,
        batchSize=1,
        stepSize=1,
        headless=True,
        iterationMode=IterationModes.NONE,
        rtol=0.0,
        maxIterations=1,
        propogateFirstBatch=False
    ):
        if propogateFirstBatch:
            initial, self.batchedGudrunFile = self.batch(
                batchSize, stepSize, propogateFirstBatch
            )
        else:
            self.batchedGudrunFile = self.batch(
                batchSize, stepSize, propogateFirstBatch
            )

        tasks = []

        if iterationMode == IterationModes.TWEAK_FACTOR:
            iteratorType = TweakFactorIterator
            dirText = "IterateByTweakFactor"
        elif iterationMode == IterationModes.THICKNESS:
            iteratorType = ThicknessIterator
            dirText = "IterateByThickness"
        elif iterationMode == IterationModes.INNER_RADIUS:
            iteratorType = RadiusIterator
            dirText = "IterateByInnerRadius"
            targetRadius = "inner"
        elif iterationMode == IterationModes.OUTER_RADIUS:
            iteratorType = RadiusIterator
            dirText = "IterateByOuterRadius"
            targetRadius = "outer"
        elif iterationMode == IterationModes.DENSITY:
            iteratorType = DensityIterator
            dirText = "IterateByDensity"

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
                    iterationMode
                )
            else:
                if propogateFirstBatch:
                    iterator = iteratorType(initial)
                    if isinstance(iterator, RadiusIterator):
                        iterator.setTargetRadius(targetRadius)
                    for i in range(maxIterations):
                        initial.process(headless=headless)
                        iterator.performIteration(i)
                        initial.iterativeOrganise(
                            maxIterations - 1,
                            i,
                            os.path.join(
                                self.gudrunFile.instrument.GudrunInputFileDir,
                                f"BATCH_PROCESSING_BATCH_SIZE{batchSize}",
                                "FIRST_BATCH",
                                f"{dirText}_{i+1}"
                            )
                        )
                        self.writeDiagnosticsFile(
                            os.path.join(
                                self.gudrunFile.instrument.GudrunInputFileDir,
                                f"BATCH_PROCESSING_BATCH_SIZE{batchSize}",
                                "FIRST_BATCH",
                                "batch_processing_diagnostics.txt"
                            )
                        )
                        if self.canConverge(initial, rtol):
                            break

                    self.propogateResults(
                        initial, self.batchedGudrunFile, iterationMode
                    )
                iterator = iteratorType(self.batchedGudrunFile)
                if isinstance(iterator, RadiusIterator):
                    iterator.setTargetRadius(targetRadius)

                for i in range(maxIterations):
                    self.batchedGudrunFile.process(headless=headless)
                    iterator.performIteration(i)
                    self.batchedGudrunFile.iterativeOrganise(
                        os.path.join(
                            maxIterations - 1,
                            i,
                            self.gudrunFile.instrument.GudrunInputFileDir,
                            f"BATCH_PROCESSING_BATCH_SIZE{batchSize}",
                            "REST",
                            f"{dirText}_{i+1}"
                        )
                    )
                    self.writeDiagnosticsFile(
                        os.path.join(
                            self.gudrunFile.instrument.GudrunInputFileDir,
                            f"BATCH_PROCESSING_BATCH_SIZE{batchSize}",
                            "REST",
                            "batch_processing_diagnostics.txt"
                        )
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
                        [0, 0, f"BATCH_PROCESSING_BATCH_SIZE_{batchSize}"],
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
                if propogateFirstBatch:
                    iterator = iteratorType(initial)
                    for i in range(maxIterations):
                        tasks.append(
                            initial.dcs(
                                headless=headless,
                                path=os.path.join(
                                    initial.instrument.GudrunInputFileDir,
                                    "gudpy.txt",
                                )
                            )
                        )
                        tasks.append([iterator.performIteration, [i]])
                        tasks.append(
                            [
                                initial.iterativeOrganise,
                                [
                                    maxIterations - 1,
                                    i,
                                    os.path.join(
                                        initial.GudrunInputFileDir,
                                        f"BATCH_PROCESSING_BATCH_SIZE"
                                        f"_{batchSize}",
                                        "FIRST_BATCH",
                                        f"{dirText}_{i+1}"
                                    )
                                ],
                            ]
                        )
                        tasks.append(
                            [
                                self.writeDiagnosticsFile,
                                [
                                    os.path.join(
                                        initial.GudrunInputFileDir,
                                        f"BATCH_PROCESSING_BATCH_SIZE"
                                        f"_{batchSize}",
                                        "FIRST_BATCH",
                                        "batch_processing_diagnostics.txt"
                                    ),
                                    initial,
                                    iterationMode
                                ]
                            ]
                        )
                        tasks.append(
                            [
                                self.checkConvergenceAndPropogate,
                                [
                                    initial,
                                    self.batchedGudrunFile,
                                    rtol,
                                    iterationMode
                                ]
                            ]
                        )
                    tasks.append(None)
                iterator = iteratorType(self.batchedGudrunFile)
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
                                maxIterations - 1,
                                i,
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
