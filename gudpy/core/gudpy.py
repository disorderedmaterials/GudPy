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

        self.gudrunFile: GudrunFile = None
        self.purgeFile = None

        self.purge: Purge = None
        self.gudrun: Gudrun = None
        self.runModes: RunModes = None
        self.gudrunIterator: GudrunIterator = None
        self.batchProcessor: BatchProcessing = None

        self.gudrunOutput = None
        self.purgeOutput = None

        self.data = Parameters()

        self.projectDir = ""

        if projectDir:
            self.loadFromProject(projectDir)
        elif loadFile:
            self.loadFromFile(loadFile, format=format, config=config)

        if self.gudrunFile:
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

    def batchProcessing(
        self,
        iterator: iterators.Iterator,
        batchSize=1,
        stepSize=1,
        offset: int = 0,
        rtol=0.0,
        separateFirstBatch=False
    ):
        self.batchProcessor = BatchProcessing(
            gudrunFile=self.gudrunFile,
            iterator=iterator,
            batchSize=batchSize,
            stepSize=stepSize,
            offset=offset,
            rtol=rtol,
            separateFirstBatch=separateFirstBatch
        )
        try:
            self.batchProcessor.process()
        except exc.GudrunException as e:
            raise e


class Process:
    def __init__(self, process: str):
        self.PROCESS = process
        self.BINARY_PATH = ""

        self.stdout = ""
        self.error = ""
        self.exitcode = 0

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
            self.exitcode = 1
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
            self.exitcode = 1
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
                        return self.exitcode
                if purge.stderr:
                    self.error = purge.stderr.decode("utf8")
                    self.exitcode = 1
                    return self.exitcode

            self.purgeOutput = purgeFile.organiseOutput(tmp)

        self.exitcode = 0
        return self.exitcode


class Gudrun(Process):
    def __init__(
        self
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
        iterator: iterators.Iterator = None
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
                        return self.exitcode
                    self._outputChanged(line.decode("utf8"))
                if gudrun.stderr:
                    self.error = gudrun.stderr.decode("utf8")
                    self.exitcode = 1
                    return self.exitcode

            if iterator:
                self.gudrunOutput = iterator.organiseOutput()
            else:
                self.gudrunOutput = self.organiseOutput()
            gudrunFile.setGudrunDir(self.gudrunOutput.path)

        self.exitcode = 0
        return self.exitcode


class GudrunIterator:
    def __init__(
        self,
        gudrunFile: GudrunFile,
        iterator: iterators.Iterator,
    ):

        # Create a copy of gudrun file
        self.gudrunFile = copy.deepcopy(gudrunFile)
        self.iterator = iterator
        self.gudrunObjects = []
        self.defaultRun = None

        for _ in range(iterator.nTotal):
            self.gudrunObjects.append(Gudrun())

    def _nextIteration(self):
        print(f"Iteration number: {self.iterator.nCurrent}")

    def defaultIteration(self, gudrunFile):
        self.defaultRun = Gudrun()
        exitcode = self.defaultRun.gudrun(gudrunFile, self.iterator)
        if exitcode:  # An exit code != 0 indicates failure
            return exitcode

    def singleIteration(
        self,
        gudrunFile: GudrunFile,
        gudrun: Gudrun,
        prevOutput: handlers.GudrunOutput
    ) -> tuple(int, str):  # (exitcode, error)
        self.iterator.performIteration(gudrunFile, prevOutput)
        exitcode = gudrun.gudrun(gudrunFile, self.iterator)
        if exitcode:
            return (exitcode, gudrun.error)

        self._nextIteration(self.iterator.nCurrent)
        return 0

    def iterate(self) -> int:
        prevOutput = None

        # If the iterator requires a prelimenary run
        if self.iterator.requireDefault:
            exitcode = self.defaultIteration(self.gudrunFile)
            if exitcode:  # An exit code != 0 indicates failure
                return (exitcode, self.defaultIteration.error)
            prevOutput = self.defaultRun.gudrunOutput

        # Iterate through gudrun objects
        for gudrun in self.gudrunObjects:
            exitcode = self.singleIteration(
                self.gudrunFile, gudrun, prevOutput)
            if exitcode:  # An exit code != 0 indicates failure
                return (exitcode, gudrun.error)

            prevOutput = gudrun.gudrunOutput

        return (0,)


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

    def iterate(self) -> tuple(int, str):
        prevOutput = None

        for gudrun in self.gudrunObjects:
            if self.iterator.result:
                self.result = self.iterator.result
                self.compositionMap = self.iterator.compositionMap
                return (0, )

            exitcode = self.singleIteration(
                self.gudrunFile, gudrun, prevOutput)
            if exitcode:  # An exit code != 0 indicates failure
                return (exitcode, gudrun.error)

            prevOutput = gudrun.gudrunOutput

            if self.currentIteration != self.iterator.nCurrent:
                # Will be called every other iteration of this loop
                self._nextIteration()
                self.currentIteration += 1

        error = (
            "No iterations were queued."
            " It's likely no Samples selected for analysis"
            " use the Component(s) selected for iteration."
        )
        return (1, error)


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


class BatchProcessing():
    def __init___(
        self,
        gudrunFile: GudrunFile,
        iterator: iterators.Iterator = None,
        batchSize=1,
        stepSize=1,
        offset: int = 0,
        rtol=0.0,
        separateFirstBatch=False
    ):
        self.iterator = iterator
        self.iterationMode = None

        self.BATCH_SIZE = batchSize
        self.STEP_SIZE = stepSize
        self.OFFSET = offset
        self.RTOL = rtol

        self.separateFirstBatch = separateFirstBatch

        self.firstBatch, self.batchedGudrunFile = self.batch(
            separateFirstBatch=self.separateFirstBatch,
            gudrunFile=gudrunFile
        )

        if self.iterator:
            self.iterationMode = self.iterator.iterationMode
            self.gudrunIterators = {
                "FIRST": GudrunIterator(
                    self.firstBatch, copy.deepcopy(iterator)
                ) if self.separateFirstBatch else None,
                "REST": GudrunIterator(
                    self.batchedGudrunFile, copy.deepcopy(iterator)
                )
            }

    def batch(self, gudrunFile: GudrunFile, separateFirstBatch: bool) -> tuple(
        typ.Union[GudrunFile, None], GudrunFile
    ):
        if not separateFirstBatch:
            batch = copy.deepcopy(gudrunFile)
            batch.sampleBackgrounds = []
            for sampleBackground in gudrunFile.sampleBackgrounds:
                batchedSampleBackground = copy.deepcopy(sampleBackground)
                batchedSampleBackground.samples = []
                maxDataFiles = max(
                    [
                        len(sample.dataFiles)
                        for sample in sampleBackground.samples
                    ]
                )
                for sample in sampleBackground.samples:
                    for i in range(self.OFFSET, maxDataFiles, self.STEP_SIZE):
                        batchedSample = copy.deepcopy(sample)
                        batchedSample.dataFiles.dataFiles = sample.dataFiles[
                            i: i + self.BATCH_SIZE
                        ]
                        batchedSampleBackground.samples.append(batchedSample)
                batch.sampleBackgrounds.append(batchedSampleBackground)

            return (None, batch)

        else:
            first = copy.deepcopy(gudrunFile)
            first.sampleBackgrounds = []
            for sampleBackground in gudrunFile.sampleBackgrounds:
                batchedSampleBackground = copy.deepcopy(sampleBackground)
                batchedSampleBackground.samples = []
                for sample in sampleBackground.samples:
                    batchedSample = copy.deepcopy(sample)
                    batchedSample.dataFiles.dataFiles = (
                        sample.dataFiles[:self.BATCH_SIZE]
                    )
                    batchedSampleBackground.samples.append(batchedSample)
                first.sampleBackgrounds.append(batchedSampleBackground)
            return (
                first,
                self.batch(separateFirstBatch=False)
            )

    def canConverge(self, batch):
        if self.RTOL == 0.0:
            return False
        for sampleBackground in batch.sampleBackgrounds:
            for sample in sampleBackground.samples:
                if abs(batch.determineError(sample)) > self.RTOL:
                    return False
        return True

    def writeDiagnosticsFile(self, path, batch):
        with open(path, "w", encoding="utf-8") as fp:
            for sampleBackground in batch.sampleBackgrounds:
                for i, sample in enumerate(sampleBackground.samples):
                    fp.write(f"Batch {i} {sample.name}\n")
                    fp.write(f"{str(sample.dataFiles)}\n")
                    fp.write(f"Error: {batch.determineError(sample)}%\n")
                    if self.iterationMode == enums.IterationModes.TWEAK_FACTOR:
                        fp.write(f"Tweak Factor: {sample.sampleTweakFactor}\n")
                    elif self.iterationMode == enums.IterationModes.THICKNESS:
                        fp.write(
                            f"Upstream / Downstream Thickness: "
                            f"{sample.upstreamThickness} "
                            f"{sample.downstreamThickness}\n"
                        )
                    elif (
                        self.iterationMode == enums.IterationModes.INNER_RADIUS
                    ):
                        fp.write(f"Inner Radius: {sample.innerRadius}\n")
                    elif (
                        self.iterationMode == enums.IterationModes.OUTER_RADIUS
                    ):
                        fp.write(f"Outer Radius: {sample.outerRadius}\n")
                    elif self.iterationMode == enums.IterationModes.DENSITY:
                        fp.write(f"Density: {sample.density}\n")

    def propogateResults(self, current, next):
        for (
            sampleBackgroundA, sampleBackgroundB
        ) in zip(current.sampleBackgrounds, next.sampleBackgrounds):
            for (
                sampleA, sampleB
            ) in zip(sampleBackgroundA.samples, sampleBackgroundB.samples):
                if self.iterationMode == enums.IterationModes.TWEAK_FACTOR:
                    sampleB.sampleTweakFactor = sampleA.sampleTweakFactor
                elif self.iterationMode == enums.IterationModes.THICKNESS:
                    sampleB.upstreamThickness = sampleA.upstreamThickness
                    sampleB.downstreamThickness = sampleA.downstreamThickness
                elif self.iterationMode == enums.IterationModes.INNER_RADIUS:
                    sampleB.innerRadius = sampleA.innerRadius
                elif self.iterationMode == enums.IterationModes.OUTER_RADIUS:
                    sampleB.outerRadius = sampleA.outerRadius
                elif self.iterationMode == enums.IterationModes.DENSITY:
                    sampleB.density = sampleA.density

    def bactchProcess(
        self,
        gudrun,
        batchSize,
        iterator=None
    ):
        self.batchedGudrunFile.projectDir = (os.path.join(
            self.batchedGudrunFile.projectDir,
            f"BATCH_PROCESSING_BATCH_SIZE{batchSize}"
        ))
        exitcode = gudrun.gudrun(GudrunFile, iterator)
        self.writeDiagnosticsFile(
            os.path.join(
                self.batchedGudrunFile.path(),
                "batch_processing_diagnostics.txt",
            ),
            self.batchedGudrunFile,
            self.iterationMode
        )
        return (exitcode, gudrun.error)

    def iterate(
        self,
        gudrunIterator: GudrunIterator,
        batchedFile: GudrunFile,
        outputFolder: str
    ) -> int:

        prevOutput = None

        batchedFile.projectDir = os.path.join(
            batchedFile.projectDir,
            f"BATCH_PROCESSING_BATCH_SIZE{self.BATCH_SIZE}",
            outputFolder
        )
        gudrunIterator.gudrunFile = batchedFile

        # If the iterator requires a prelimenary run
        if gudrunIterator.iterator.requireDefault:
            exitcode, error = self.gudrunIterators[-1].defaultIteration(
                batchedFile)
            if exitcode:  # An exit code != 0 indicates failure
                return (exitcode, error)
            prevOutput = gudrunIterator.defaultRun.gudrunOutput

        # Iterate through gudrun objects
        for i, gudrun in enumerate(gudrunIterator.gudrunObjects):
            if self.canConverge(batchedFile, self.RTOL):
                # Keep only the processed objects in the list
                gudrunIterator.gudrunObjects = gudrunIterator.gudrunObjects[:i]
                return (0, )

            exitcode = gudrunIterator.singleIteration(
                batchedFile, gudrun, prevOutput)

            self.writeDiagnosticsFile(
                os.path.join(
                    batchedFile.path(),
                    "batch_processing_diagnostics.txt"
                )
            )

            if exitcode:
                return (exitcode, gudrun.error)

            prevOutput = gudrun.gudrunOutput

        return (0, )

    def process(
        self,
    ):
        if self.iterationMode == enums.IterationModes.NONE:
            return self.bactchProcess(Gudrun(), self.BATCH_SIZE)

        else:
            if self.separateFirstBatch:
                exitcode, error = self.iterate(
                    gudrunIterator=self.gudrunIterators["FIRST"],
                    gudrunFile=self.firstBatch,
                    outputFolder="FIRST_BATCH"
                )
                if exitcode:
                    raise exc.GudrunException(
                        "Batch Processing failed with the following output: "
                        f"{error}"
                    )

                self.propogateResults(
                    self.firstBatch, self.batchedGudrunFile
                )

            iterator = copy.deepcopy(self.iterator)
            self.gudrunIterators.append(GudrunIterator(
                self.batchedGudrunFile,
                iterator
            ))
            exitcode, error = self.iterate(
                gudrunIterator=self.gudrunIterators["REST"],
                gudrunFile=self.batchedGudrunFile,
                outputFolder="REST"
            )
            if exitcode:
                raise exc.GudrunException(
                    "Batch Processing failed with the following output: "
                    f"{error}"
                )
