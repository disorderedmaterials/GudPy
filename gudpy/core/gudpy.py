import tempfile
import os
import sys
import subprocess
import shutil
import copy
import typing as typ

from core import config
from core import utils
from core import enums
from core import exception as exc
from core import iterators
from core import instrument, beam, normalisation, composition

from core.gudrun_file import GudrunFile
from core.purge_file import PurgeFile
import core.output_file_handler as handlers
from core.file_library import GudPyFileLibrary

SUFFIX = ".exe" if os.name == "nt" else ""


class Parameters:
    def __init__(self):
        self.instrument = instrument.Instrument()
        self.beam = beam.Beam()
        self.normalisation = normalisation.Normalisation()
        self.sampleBackgrounds = []
        self.components = composition.Components(components=[])


class GudPy:
    def __init__(
        self,
        projectDir: str = "",
        loadFile: str = "",
        format: enums.Format = enums.Format.YAML,
        config: bool = False,
    ):

        if not projectDir and not loadFile:
            raise RuntimeError(
                "No project directory or load file specified"
            )

        self.gudrunFile = None
        self.purge = Purge()
        self.gudrun = Gudrun()
        self.runModes = RunModes()

        self.gudrunIterator = None
        self.gudrunOutput = None
        self.purgeOutput = None

        self.data = Parameters()

        self.projectDir = ""

        if projectDir:
            self.loadFromProject(projectDir)
        else:
            self.loadFromFile(loadFile, format=format, config=config)

        self.purgeFile = PurgeFile(self.gudrunFile)

    def loadFromFile(
        self,
        loadFile: str,
        format: enums.Format,
        config: bool = False
    ):
        if not config:
            self.setSaveLocation(self.projectDir)

        if not os.path.exists(loadFile):
            raise FileNotFoundError("Input file does not exist.")

        self.gudrunFile = GudrunFile(
            loadFile=loadFile,
            format=format,
            config=config
        )

    def loadFromProject(self, projectDir: str):
        loadFile = ""

        if os.path.exists(os.path.join(
            projectDir,
            f"{os.path.basename(projectDir)}.yaml"
        )):
            # If default file exists
            loadFile = os.path.join(
                projectDir,
                f"{os.path.basename(projectDir)}.yaml"
            )
        else:
            # Try to find yaml files
            for f in os.listdir(projectDir):
                if os.path.splitext(f)[1] == ".yaml":
                    # If file is yaml
                    loadFile = os.path.join(projectDir, f)
        if not loadFile:
            raise FileNotFoundError(
                "Could not find GudPy input file within the project")

        self.loadFromFile(loadFile, format=enums.Format.YAML)
        self.setSaveLocation(projectDir)

        if os.path.exists(os.path.join(projectDir, "Purge")):
            self.purgeOutput = os.path.join(projectDir, "Purge")
        if os.path.exists(os.path.join(projectDir, "Gudrun")):
            self.gudrun.gudrunOutput.path = os.path.join(projectDir, "Gudrun")

    def checkSaveLocation(self):
        return bool(self.projectDir)

    def setSaveLocation(self, projectDir: str):
        self.projectDir = projectDir
        self.gudrunFile.filename = f"{os.path.basename(projectDir)}.yaml"

    def save(self, path: str = "", format: enums.Format = enums.Format.YAML):
        if not path:
            path = self.gudrunFile.path()
        self.gudrunFile.save(path=path,
                             format=format)

    def saveAs(self, targetDir: str):
        if os.path.exists(targetDir):
            raise IsADirectoryError("Cannot be an existing directory")

        oldDir = self.projectDir
        self.setSaveLocation(targetDir)
        os.makedirs(targetDir)

        if os.path.exists(os.path.join(oldDir, "Purge")):
            shutil.copytree(
                os.path.join(oldDir, "Purge"),
                os.path.join(targetDir, "Purge")
            )
        if os.path.exists(os.path.join(oldDir, "Gudrun")):
            shutil.copytree(
                os.path.join(oldDir, "Gudrun"),
                os.path.join(targetDir, "Gudrun")
            )
        self.gudrunFile.save(path=self.gudrunFile.path(),
                             format=enums.Format.YAML)

    def checkFilesExist(self):
        result = GudPyFileLibrary(self.gudrunFile).checkFilesExist()
        if not all(r[0] for r in result[0]) or not all(r[0]
                                                       for r in result[1]):
            undefined = [
                r[1] for r in result[0] if not r[0]
            ]
            unresolved = [r[2] for r in result[1] if not r[0] and r[2]]

        print(f"Undefined files: {undefined}")
        print(f"Unresolved files: {unresolved}")

        return (undefined, unresolved)

    def runPurge(self):
        exitcode = self.purge.purge(self.gudrunFile)
        if exitcode:
            raise exc.PurgeException(
                "Purge failed to run with the following output:"
                f"{self.purge.error}"
            )

    def runGudrun(self, gudrunFile=None):
        if not gudrunFile:
            gudrunFile = self.gudrunFile
        exitcode = self.gudrun.gudrun(gudrunFile)
        if exitcode:
            raise exc.GudrunException(
                "Gudrun failed to run with the following output:"
                f"{self.gudrun.error}"
            )

    def iterateGudrun(self, iterator: iterators.Iterator):
        self.gudrunIterator = GudrunIterator(iterator, self.gudrunFile)
        exitcode = self.gudrunIterator.iterate()
        if exitcode:
            raise exc.GudrunException(
                "Gudrun failed to run with the following output:"
                f"{self.gudrun.error}"
            )
        self.gudrunFile = self.gudrunIterator.gudrunFile

    def iterateComposition(self, iterator: iterators.Composition):
        self.gudrunIterator = CompositionIterator(
            iterator, self.gudrunFile)
        exitcode = self.gudrunIterator.iterate()
        if exitcode:
            raise exc.GudrunException(
                "Gudrun failed to run with the following output:"
                f"{self.gudrun.error}"
            )
        self.gudrunFile = self.gudrunIterator.gudrunFile

    def runContainersAsSample(self):
        gudrunFile = self.runModes.convertContainersToSample(self.gudrunFile)
        self.runGudrun(gudrunFile=gudrunFile)

    def runFilesIndividually(self):
        gudrunFile = self.runModes.partition(self.gudrunFile)
        self.runGudrun(gudrunFile=gudrunFile)


class Process:
    def __init__(self, process: str):
        self.PROCESS = process
        self.BINARY_PATH = ""

        self.stdout = ""
        self.error = ""

        # Find binary
        if hasattr(sys, '_MEIPASS'):
            self.BINARY_PATH = os.path.join(
                sys._MEIPASS, f"{self.PROCESS}{SUFFIX}")
        else:
            self.BINARY_PATH = utils.resolve(
                os.path.join(
                    config.__rootdir__, "bin"
                ), f"{self.PROCESS}{SUFFIX}"
            )

    def _outputChanged(self, output: str):
        self.stdout += output

    def _checkBinary(self):
        if not os.path.exists(self.BINARY_PATH):
            raise FileNotFoundError(f"Missing {self.PROCESS} binary")

    def _prepareRun(self):
        self.stdout = ""
        self.error = ""

    def _checkError(self, line: str):
        # Check for errors.
        ERROR_KWDS = [
            "does not exist",
            "error",
            "Error"
        ]
        if [KWD for KWD in ERROR_KWDS if KWD in line]:
            self.error += line
            return True

        return False


class Purge(Process):
    def __init__(self):
        self.PROCESS = "purge_det"
        self.purgeOutput = ""
        self.detectors = None
        super().__init__(self.PROCESS)

    def organiseOutput(self, procDir: str):
        outputHandler = handlers.OutputHandler(procDir, "Purge")
        outputHandler.organiseOutput()

    def purge(self, purgeFile: PurgeFile):
        self._prepareRun()
        self._checkBinary()
        self.purgeOutput = ""

        with tempfile.TemporaryDirectory() as tmp:
            purgeFile.write_out(os.path.join(
                tmp,
                f"{self.PROCESS}.dat"
            ))

            with subprocess.Popen(
                [self.BINARY_PATH, f"{self.PROCESS}.dat"], cwd=tmp,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT
            ) as purge:
                for line in purge.stdout:
                    self._outputChanged(line.decode("utf8"))
                    if self._checkError(line):
                        return 1
                if purge.stderr:
                    self._errorOccured(
                        purge.stderr.decode("utf8"))
                    return 1

            self.purgeOutput = purgeFile.organiseOutput(tmp)

        return 0


class Gudrun(Process):
    def __init__(
        self,
    ):
        self.PROCESS: str = "gudrun_dcs"
        super().__init__(self.PROCESS)

    def organiseOutput(
        self, gudrunFile: GudrunFile,
        head: str = "",
        overwrite: bool = True
    ) -> handlers.GudrunOutput:

        outputHandler = handlers.GudrunOutputHandler(
            self, gudrunFile=gudrunFile, head=head, overwrite=overwrite
        )
        gudrunOutput = outputHandler.organiseOutput()
        return gudrunOutput

    def gudrun(
        self,
        gudrunFile: GudrunFile,
    ) -> int:
        self._prepareRun()
        self._checkBinary()

        with tempfile.TemporaryDirectory() as tmp:
            gudrunFile.setGudrunDir(tmp)
            path = os.path.join(
                tmp,
                gudrunFile.outpath
            )
            gudrunFile.save(
                path=os.path.join(
                    gudrunFile.projectDir,
                    f"{gudrunFile.filename}"
                ),
                format=enums.Format.YAML
            )
            gudrunFile.write_out(path)
            with subprocess.Popen(
                [self.BINARY_PATH, path], cwd=tmp,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT
            ) as gudrun:
                for line in gudrun.stdout:
                    if self._checkError(line):
                        return 1
                    self._outputChanged(line.decode("utf8"))
                if gudrun.stderr:
                    return 1

            self.gudrunOutput = self.organiseOutput(gudrunFile)
            gudrunFile.setGudrunDir(self.gudrunOutput.path)

        return 0


class GudrunIterator:
    def __init__(
        self,
        iterator: iterators.Iterator,
        gudrunFile: GudrunFile
    ):

        # Create a copy of gudrun file
        self.gudrunFile = copy.deepcopy(gudrunFile)
        self.iterator = iterator
        self.gudrunObjects = []
        self.defaultRun = None

        for _ in range(iterator.nTotal):
            self.gudrunObjects.append(Gudrun(
                organiseOutput=self.iterator.organiseOutput
            ))

    def _nextIteration(self):
        print(f"Iteration number: {self.iterator.nCurrent}")

    def iterate(self) -> int:
        prevOutput = None

        # If the iterator requires a prelimenary run
        if self.iterator.requireDefault:
            self.defaultRun = Gudrun()
            exitcode = self.defaultRun.gudrun(self.gudrunFile, self.iterator)
            if exitcode:  # An exit code != 0 indicates failure
                return exitcode
            prevOutput = self.defaultRun.gudrunOutput

        # Iterate through gudrun objects
        for gudrun in self.gudrunObjects:
            self.iterator.performIteration(self.gudrunFile, prevOutput)
            exitcode = gudrun.gudrun(self.gudrunFile, self.iterator)
            if exitcode:
                return exitcode

            prevOutput = gudrun.gudrunOutput
            self._nextIteration()

        return 0


class CompositionIterator(GudrunIterator):
    def __init__(
        self,
        iterator: iterators.Composition,
        gudrunFile: GudrunFile
    ):
        iterator.nTotal *= 2
        super().__init__(iterator, gudrunFile)

        self.result = None
        self.compositionMap = None
        self.currentIteration = 0

    def iterate(self) -> int:
        prevOutput = None

        for gudrun in self.gudrunObjects:
            if self.iterator.result:
                self.result = self.iterator.result
                self.compositionMap = self.iterator.compositionMap
                return 0

            gudrunFile = self.iterator.performIteration(
                self.gudrunFile, prevOutput)

            exitcode = gudrun.gudrun(gudrunFile, self.iterator)
            if exitcode:
                return exitcode

            prevOutput = gudrun.gudrunOutput

            if self.currentIteration != self.iterator.nCurrent:
                # Will be called every other iteration of this loop
                self._nextIteration()
                self.currentIteration += 1

        self.error = (
            "No iterations were queued."
            " It's likely no Samples selected for analysis"
            " use the Component(s) selected for iteration."
        )
        return 1


class RunModes:

    def convertContainersToSample(self, gudrunFile: GudrunFile):
        newGudrunFile = copy.deepcopy(gudrunFile)
        containersAsSamples = []
        for sampleBackground in gudrunFile.sampleBackgrounds:
            for sample in sampleBackground.samples:
                for container in sample.containers:
                    containersAsSamples.append(
                        container.convertToSample()
                    )
            newGudrunFile.sampleBackground.samples = containersAsSamples
        return newGudrunFile

    def partition(self, gudrunFile):
        newGudrunFile = copy.deepcopy(gudrunFile)
        # Deepcopy the sample backgrounds.
        sampleBackgrounds = copy.deepcopy(gudrunFile.sampleBackgrounds)
        # Clear the original list.
        newGudrunFile.sampleBackgrounds = []

        # Enumerate through all sample backgrounds
        # For each sample, create a copy for each
        # data file, and add it to the corresponding sample background.
        for i, sampleBackground in enumerate(sampleBackgrounds):
            samples = copy.deepcopy(sampleBackground.samples)
            sampleBackgrounds[i].samples = []

            for sample in samples:
                if sample.runThisSample:
                    for dataFile in sample.dataFiles:
                        childSample = copy.deepcopy(sample)

                        # Only run one data file.
                        childSample.dataFiles = (
                            DataFiles([dataFile], childSample.name)
                        )
                        childSample.name = f"{childSample.name} [{dataFile}]"

                        # Append sample
                        sampleBackgrounds[i].samples.append(childSample)

        # Update gudrunFile to use the newly constructed sample background.
        newGudrunFile.sampleBackgrounds = sampleBackgrounds
        return newGudrunFile


class BatchProcessing:
    def __init___(
            self,
            gudrunFile: GudrunFile,
            gudrun: Gudrun = None,
            gudrunIterator: GudrunIterator = None
    ):
        self.gudrunFile = gudrunFile
        self.gudrun = gudrun
        self.gudrunIterator = gudrunIterator

    def batch(self, batchSize, stepSize, separateFirstBatch, offset=0):
        if not separateFirstBatch:
            batch = copy.deepcopy(self.gudrunFile)
            batch.sampleBackgrounds = []
            for sampleBackground in self.gudrunFile.sampleBackgrounds:
                batchedSampleBackground = copy.deepcopy(sampleBackground)
                batchedSampleBackground.samples = []
                maxDataFiles = max(
                    [
                        len(sample.dataFiles)
                        for sample in sampleBackground.samples
                    ]
                )
                for sample in sampleBackground.samples:
                    for i in range(offset, maxDataFiles, stepSize):
                        batchedSample = copy.deepcopy(sample)
                        batchedSample.dataFiles.dataFiles = sample.dataFiles[
                            i: i + batchSize
                        ]
                        batchedSampleBackground.samples.append(batchedSample)
                batch.sampleBackgrounds.append(batchedSampleBackground)

            return batch

        else:
            first = copy.deepcopy(self.gudrunFile)
            first.sampleBackgrounds = []
            for sampleBackground in self.gudrunFile.sampleBackgrounds:
                batchedSampleBackground = copy.deepcopy(sampleBackground)
                batchedSampleBackground.samples = []
                for sample in sampleBackground.samples:
                    batchedSample = copy.deepcopy(sample)
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
                    if iterationMode == enums.IterationModes.TWEAK_FACTOR:
                        fp.write(f"Tweak Factor: {sample.sampleTweakFactor}\n")
                    elif iterationMode == enums.IterationModes.THICKNESS:
                        fp.write(
                            f"Upstream / Downstream Thickness: "
                            f"{sample.upstreamThickness} "
                            f"{sample.downstreamThickness}\n"
                        )
                    elif iterationMode == enums.IterationModes.INNER_RADIUS:
                        fp.write(f"Inner Radius: {sample.innerRadius}\n")
                    elif iterationMode == enums.IterationModes.OUTER_RADIUS:
                        fp.write(f"Outer Radius: {sample.outerRadius}\n")
                    elif iterationMode == enums.IterationModes.DENSITY:
                        fp.write(f"Density: {sample.density}\n")

    def propogateResults(self, current, next, iterationMode):
        for (
            sampleBackgroundA, sampleBackgroundB
        ) in zip(current.sampleBackgrounds, next.sampleBackgrounds):
            for (
                sampleA, sampleB
            ) in zip(sampleBackgroundA.samples, sampleBackgroundB.samples):
                if iterationMode == enums.IterationModes.TWEAK_FACTOR:
                    sampleB.sampleTweakFactor = sampleA.sampleTweakFactor
                elif iterationMode == enums.IterationModes.THICKNESS:
                    sampleB.upstreamThickness = sampleA.upstreamThickness
                    sampleB.downstreamThickness = sampleA.downstreamThickness
                elif iterationMode == enums.IterationModes.INNER_RADIUS:
                    sampleB.innerRadius = sampleA.innerRadius
                elif iterationMode == enums.IterationModes.OUTER_RADIUS:
                    sampleB.outerRadius = sampleA.outerRadius
                elif iterationMode == enums.IterationModes.DENSITY:
                    sampleB.density = sampleA.density

    def organiseOutput(
        self, gudrunFile: GudrunFile,
        head: str = "",
        overwrite: bool = True
    ) -> handlers.GudrunOutput:

        outputHandler = handlers.GudrunOutputHandler(
            self, gudrunFile=gudrunFile, head=head, overwrite=overwrite
        )
        gudrunOutput = outputHandler.organiseOutput()
        return gudrunOutput

    def process(
        self,
        batchSize=1,
        stepSize=1,
        headless=True,
        iterationMode=enums.IterationModes.NONE,
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

        if iterationMode == enums.IterationModes.TWEAK_FACTOR:
            iteratorType = iterators.TweakFactorIterator
            dirText = "IterateByTweakFactor"
        elif iterationMode == enums.IterationModes.THICKNESS:
            iteratorType = iterators.ThicknessIterator
            dirText = "IterateByThickness"
        elif iterationMode == enums.IterationModes.INNER_RADIUS:
            iteratorType = iterators.RadiusIterator
            dirText = "IterateByInnerRadius"
            targetRadius = "inner"
        elif iterationMode == enums.IterationModes.OUTER_RADIUS:
            iteratorType = iterators.RadiusIterator
            dirText = "IterateByOuterRadius"
            targetRadius = "outer"
        elif iterationMode == enums.IterationModes.DENSITY:
            iteratorType = iterators.DensityIterator
            dirText = "IterateByDensity"

        if iterationMode == enums.IterationModes.NONE:
            self.gudrun.gudrun(self.batchedGudrunFile)
            self.writeDiagnosticsFile(
                os.path.join(
                    self.batchedGudrunFile.path()
                ),
                self.batchedGudrunFile,
                iterationMode
            )

        else:
            if propogateFirstBatch:
                iterator = iteratorType(self.batchedGudrunFile)
                if isinstance(iterator, iterators.RadiusIterator):
                    self.iterator.setTargetRadius(targetRadius)

                self.gudrunIterator = GudrunIt

                for i in range(maxIterations):
                    initial.process(headless=headless)
                    iterator.performIteration(i)
                    initial.organiseOutput(
                        head=os.path.join(
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
