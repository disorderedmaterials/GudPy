import tempfile
import os
import sys
import subprocess
import shutil
import copy
import typing as typ

import gudpy_cli as cli
from core import utils
from core import enums
from core import exception as exc
from core import iterators
from core.gudrun_file import GudrunFile
from core.purge_file import PurgeFile
import core.output_file_handler as handlers
from core.file_library import GudPyFileLibrary
from core import data_files

SUFFIX = ".exe" if os.name == "nt" else ""


class GudPy:
    def __init__(
        self
    ):
        self.originalGudrunFile: GudrunFile = None
        self.gudrunFile: GudrunFile = None
        self.purgeFile = None

        self.purge: Purge = None
        self.gudrun: Gudrun = None
        self.runModes: RunModes = None
        self.gudrunIterator: GudrunIterator = None
        self.batchProcessor: BatchProcessing = None

        self.gudrunOutput = None

        self.projectDir = ""
        self.autosaveLocation = ""

    def loadFromFile(
        self,
        loadFile: str,
        format: enums.Format,
        config: bool = False
    ):
        """Loads GudPy from an input file

        Parameters
        ----------
        loadFile : str
            Path of input file to load from
        format : enums.Format
            Format of the input file (YAML or TXT)
        config : bool, optional
            If loading from preset config, by default False

        Raises
        ------
        FileNotFoundError
            Raised if input file does not exist
        """
        if not os.path.exists(loadFile):
            raise FileNotFoundError("Input file does not exist.")

        self.gudrunFile = GudrunFile(
            loadFile=loadFile,
            format=format,
            config=config
        )

        self.originalGudrunFile = copy.deepcopy(self.gudrunFile)
        self.originalGudrunFile.filename = "original"

        self.projectDir == ""
        self.autosaveLocation = ""

    def loadFromProject(self, projectDir: str):
        """Loads GudPy from a project directory

        Parameters
        ----------
        projectDir : str
            Path to GudPy project folder

        Raises
        ------
        FileNotFoundError
            Raised if there is no YAML input file in the
            project directory
        """
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

        self.loadFromFile(loadFile=loadFile, format=enums.Format.YAML)
        self.setSaveLocation(projectDir)

    def checkSaveLocation(self):
        """Checks if user has set the save location

        Returns
        -------
        bool
            If the save location is set or not
        """
        return bool(self.projectDir)

    def setSaveLocation(self, projectDir: str):
        """Sets the save location

        Parameters
        ----------
        projectDir : str
            Path to the desired save location of project
        """
        self.projectDir = projectDir
        self.gudrunFile.filename = f"{os.path.basename(projectDir)}.yaml"
        self.gudrunFile.projectDir = projectDir
        self.originalGudrunFile.projectDir = projectDir
        self.autosaveLocation = (
            f"{os.path.basename(projectDir)}.autosave"
        )

    def save(self, path: str = "", format: enums.Format = enums.Format.YAML):
        """Saves current GudPy input file

        Parameters
        ----------
        path : str, optional
            Path to desired save location, by default ""
        format : enums.Format, optional
            Desired format of save file, by default enums.Format.YAML
        """
        if not path:
            path = self.gudrunFile.path()
        self.originalGudrunFile.save(path=path)
        self.gudrunFile.save(path=path, format=format)

    def saveAs(self, targetDir: str):
        """Save GudPy project to a new location, set current
        project to the new location.

        Parameters
        ----------
        targetDir : str
            Target path to new save location

        Raises
        ------
        IsADirectoryError
            Raised if the requested save location already exists
        """
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
        self.gudrunFile.filename = os.path.basename(targetDir)
        self.gudrunFile.save(path=self.gudrunFile.path(),
                             format=enums.Format.YAML)
        self.loadFromProject(projectDir=targetDir)

    def checkFilesExist(self):
        """Check if all file parameters submitted exists and that
        all required paths are provided

        Returns
        -------
        Tuple [List[str], List[str]]
            Returns a tuple of two lists:
                Undefined files: Paths required by Gudrun that have not
                been provided
                Unresolved files: Paths sumbitted that do not exist
        """
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

    def prepareRun(self):
        if not self.checkSaveLocation():
            raise RuntimeError("No save location specified."
                               "Use GudPy.setSaveLocation(<path>)")

    def runPurge(self):
        """Runs purge_det binary to purge detectors in data

        Raises
        ------
        exc.PurgeException
            Raised if purge_det failed to execute
        """
        self.prepareRun()
        self.purge = Purge()
        self.purgeFile = PurgeFile(self.gudrunFile)
        exitcode = self.purge.purge(self.purgeFile)
        self.gudrunFile.save()
        if exitcode:
            raise exc.PurgeException(
                "Purge failed to run with the following output:\n"
                f"{self.purge.error}"
            )

    def runGudrun(self, gudrunFile: GudrunFile = None):
        """Runs gudrun_dcs binary

        Parameters
        ----------
        gudrunFile : GudrunFile, optional
            GudrunFile object to input to gudrun_dcs, by default None

        Raises
        ------
        exc.GudrunException
            Raised if gudrun_dcs failed to execute
        """
        self.prepareRun()

        if not gudrunFile:
            gudrunFile = self.gudrunFile
        self.gudrun = Gudrun()
        exitcode = self.gudrun.gudrun(gudrunFile=gudrunFile)
        if exitcode:
            raise exc.GudrunException(
                "Gudrun failed to run with the following output:\n"
                f"{self.gudrun.error}"
            )
        self.gudrunOutput = self.gudrun.gudrunOutput

    def iterateGudrun(self, iterator: iterators.Iterator):
        """Runs gudrun_dcs iteratively while tweaking parameters

        Parameters
        ----------
        iterator : iterators.Iterator
            Iterator to use

        Raises
        ------
        exc.GudrunException
            Raised if gudrun_dcs failed to execute
        """
        self.prepareRun()

        self.gudrunIterator = GudrunIterator(
            gudrunFile=self.gudrunFile, iterator=iterator)
        exitcode, error = self.gudrunIterator.iterate(purge=self.purge)
        if exitcode:
            raise exc.GudrunException(
                "Gudrun failed to run with the following output:"
                f"{error}"
            )
        self.gudrunFile = self.gudrunIterator.gudrunFile
        self.gudrunOutput = self.gudrunIterator.gudrunOutput

    def iterateComposition(self, iterator: iterators.Composition):
        """Runs gudrun_dcs iteratively while tweaking the composition

        Parameters
        ----------
        iterator : iterators.Composition
            Composition iterator to use

        Raises
        ------
        exc.GudrunException
            Raised if gudrun_dcs failed to execute
        """
        self.prepareRun()
        self.gudrunIterator = CompositionIterator(
            iterator=iterator, gudrunFile=self.gudrunFile)
        exitcode, error = self.gudrunIterator.iterate(purge=self.purge)
        if exitcode:
            raise exc.GudrunException(
                "Gudrun failed to run with the following output:"
                f"{error}"
            )
        self.gudrunFile = self.gudrunIterator.gudrunFile

    def runContainersAsSample(self):
        """Run gudrun_dcs but convert all containers to samples
        """
        gudrunFile = self.runModes.convertContainersToSample(self.gudrunFile)
        self.runGudrun(gudrunFile=gudrunFile)

    def runFilesIndividually(self):
        """Run gudrun_dcs but partition all data files
        """
        gudrunFile = self.runModes.partition(self.gudrunFile)
        self.runGudrun(gudrunFile=gudrunFile)

    def batchProcessing(
        self,
        iterator: iterators.Iterator = None,
        batchSize=1,
        stepSize=1,
        offset: int = 0,
        rtol=0.0,
        separateFirstBatch=False
    ):
        """Run gudrun_dcs using batch processing

        Parameters
        ----------
        iterator : iterators.Iterator, optional
            Iterator to apply, by default None
        batchSize : int, optional
            Size of batch, by default 1
        stepSize : int, optional
            Step size to use, by default 1
        offset : int, optional
            Offset to use, by default 0
        rtol : float, optional
            Relative tolerance to use, by default 0.0
        separateFirstBatch : bool, optional
            Whether or not to separate the first batch,
            by default False

        Raises
        ------
        exc.GudrunException
            Raised if gudrun_dcs failed to execute
        """
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
            self.batchProcessor.process(purge=self.purge)
        except exc.GudrunException as e:
            raise e


class Process:
    def __init__(self, process: str):
        self.PROCESS = process
        self.BINARY_PATH = ""

        self.output = ""
        self.error = ""
        self.exitcode = 1

        # Find binary
        if hasattr(sys, '_MEIPASS'):
            self.BINARY_PATH = os.path.join(
                sys._MEIPASS, f"{self.PROCESS}{SUFFIX}")
        else:
            self.BINARY_PATH = utils.resolve(
                "bin", f"{self.PROCESS}{SUFFIX}"
            )

    def _outputChanged(self, output: str):
        self.output += output

    def checkBinary(self):
        if not os.path.exists(self.BINARY_PATH):
            self.exitcode = 1
            raise FileNotFoundError(
                f"Missing {self.PROCESS} binary"
                f" in location {self.BINARY_PATH}")

    def checkError(self, line: str):
        # Check for errors.
        ERROR_KWDS = [
            "does not exist",
            "error",
            "Error",
            "Problems"
        ]
        if [KWD for KWD in ERROR_KWDS if KWD in line]:
            self.error += line
            self.exitcode = 1
            return True

        return False


class Purge(Process):
    def __init__(self):
        self.PROCESS = "purge_det"
        self.detectors = None
        self.purgeLocation = None
        super().__init__(self.PROCESS)

    def organiseOutput(self, procDir: str, projectDir: str):
        outputHandler = handlers.OutputHandler(
            procDir,
            projectDir,
            "Purge"
        )
        return outputHandler.organiseOutput()

    def purge(self, purgeFile: PurgeFile):
        self.checkBinary()
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
                    line = "\n".join(line.decode("utf8").split("\n"))
                    self._outputChanged(line)
                    if self.checkError(line):
                        return self.exitcode
                    if "spectra in" in line:
                        self.detectors = utils.nthint(line, 0)
                if purge.stderr:
                    self.error = purge.stderr.decode("utf8")
                    self.exitcode = 1
                    return self.exitcode

            self.purgeLocation = self.organiseOutput(
                tmp, purgeFile.gudrunFile.projectDir)

        self.exitcode = 0
        return self.exitcode


class Gudrun(Process):
    def __init__(self):
        self.PROCESS: str = "gudrun_dcs"
        super().__init__(self.PROCESS)

    def organiseOutput(
        self,
        gudrunFile: GudrunFile,
        exclude: list[str] = [],
        head: str = "",
        overwrite: bool = True
    ) -> handlers.GudrunOutput:

        outputHandler = handlers.GudrunOutputHandler(
            gudrunFile=gudrunFile, head=head, overwrite=overwrite
        )
        gudrunOutput = outputHandler.organiseOutput(exclude=exclude)
        return gudrunOutput

    def gudrun(
        self,
        gudrunFile: GudrunFile,
        purge: Purge = None,
        iterator: iterators.Iterator = None,
        save: bool = True
    ) -> int:
        self.checkBinary()
        if not purge:
            cli.echoWarning("Gudrun running without purge")
        with tempfile.TemporaryDirectory() as tmp:
            purgeFiles = []
            if purge:
                for f in os.listdir(purge.purgeLocation):
                    shutil.copyfile(
                        os.path.join(purge.purgeLocation, f),
                        os.path.join(tmp, f)
                    )
                    purgeFiles.append(os.path.join(tmp, f))

            gudrunFile.setGudrunDir(tmp)
            path = os.path.join(
                tmp,
                gudrunFile.OUTPATH
            )
            gudrunFile.write_out(path)
            with subprocess.Popen(
                [self.BINARY_PATH, path], cwd=tmp,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT
            ) as gudrun:
                for line in gudrun.stdout:
                    line = "\n".join(line.decode("utf8").split("\n"))
                    if self.checkError(line):
                        return self.exitcode
                    self._outputChanged(line)
                if gudrun.stderr:
                    self.error = gudrun.stderr.decode("utf8")
                    self.exitcode = 1
                    return self.exitcode

            if iterator:
                self.gudrunOutput = iterator.organiseOutput(
                    gudrunFile, exclude=purgeFiles)
            else:
                self.gudrunOutput = self.organiseOutput(
                    gudrunFile, exclude=purgeFiles)
            if save:
                gudrunFile.save(
                    path=os.path.join(
                        gudrunFile.projectDir,
                        f"{gudrunFile.filename}"
                    ),
                    format=enums.Format.YAML
                )
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
        self.exitcode = (1, "Operation incomplete")
        self.gudrunOutput = None
        self.result = {}

        for _ in range(
                iterator.nTotal + (1 if iterator.requireDefault else 0)):
            self.gudrunObjects.append(Gudrun())

        # If the iterator requires a prelimenary run
        if iterator.requireDefault:
            self.gudrunObjects.append(Gudrun())

    def singleIteration(
        self,
        gudrunFile: GudrunFile,
        gudrun: Gudrun,
        purge: Purge,
        prevOutput: handlers.GudrunOutput,
        save=True
    ) -> typ.Tuple[int, str]:  # (exitcode, error)
        modGfFile = self.iterator.performIteration(gudrunFile, prevOutput)
        exitcode = gudrun.gudrun(modGfFile, purge, self.iterator, save=save)
        if exitcode:
            return exitcode
        self.gudrunOutput = gudrun.gudrunOutput
        return 0

    def iterate(self, purge, save=True) -> typ.Tuple[int, str]:
        prevOutput = None

        # If the iterator requires a prelimenary run
        if self.iterator.requireDefault:
            exitcode = self.gudrunObjects[0].gudrun(
                self.gudrunFile, purge, self.iterator, save)
            if exitcode:  # An exit code != 0 indicates failure
                self.exitcode = (exitcode, self.gudrunObjects[0].error)
                return self.exitcode
            prevOutput = self.gudrunObjects[0].gudrunOutput

        # Iterate through gudrun objects
        for gudrun in self.gudrunObjects:
            if gudrun.output:
                # If object has already been run, skip
                continue
            exitcode = self.singleIteration(
                self.gudrunFile, gudrun, purge, prevOutput, save)
            if exitcode:  # An exit code != 0 indicates failure
                self.exitcode = (exitcode, gudrun.error)
                return self.exitcode

            prevOutput = gudrun.gudrunOutput

        self.result = self.iterator.result

        self.exitcode = (0, "")
        return self.exitcode


class CompositionIterator:
    def __init__(
        self,
        iterator: iterators.Composition,
        gudrunFile: GudrunFile,
    ):
        self.gudrunFile = copy.deepcopy(gudrunFile)
        self.iterator = iterator
        self.gudrunObjects = []
        self.result = {}
        self.compositionMap = None
        self.currentIteration = 0

    def iterate(self, purge) -> typ.Tuple[int, str]:
        for sampleArg in self.iterator.sampleArgs:
            self.gudrunObjects.append((Gudrun(), Gudrun()))
            for gudrunNC, gudrunCC in self.gudrunObjects:
                # Run the new center
                newCenter = self.iterator.iterateNewPotentialCenter(
                    self.gudrunFile, sampleArg)
                exitcode = gudrunNC.gudrun(
                    gudrunFile=newCenter,
                    purge=purge,
                    iterator=self.iterator)
                if exitcode:  # An exit code != 0 indicates failure
                    self.exitcode = (exitcode, gudrunNC.error)
                    return self.exitcode

                # Run the current center
                currentCenter = self.iterator.iterateCurrentCenter(
                    self.gudrunFile, sampleArg)
                exitcode = gudrunCC.gudrun(
                    gudrunFile=currentCenter,
                    purge=purge,
                    iterator=self.iterator)
                if exitcode:  # An exit code != 0 indicates failure
                    self.exitcode = (exitcode, gudrunCC.error)
                    return self.exitcode

                # Compare the cost of the two centers
                self.iterator.compareCost(
                    sampleArg=sampleArg,
                    currentCenterGudFile=gudrunCC.gudrunOutput.gudFile(
                        name=sampleArg["background"].samples[0].name),
                    newCenterGudFile=gudrunNC.gudrunOutput.gudFile(
                        name=sampleArg["background"].samples[0].name)
                )

                # Check if result has been achieved
                if sampleArg.get("result", ""):
                    self.result[sampleArg["sample"].name] = sampleArg["result"]
                    break
                # If the iterator has not reached max iterations, continue loop
                if not self.iterator.nCurrent == self.iterator.nTotal - 1:
                    self.gudrunObjects.append((Gudrun(), Gudrun()))

            # If max iterations are reached, set result as current center
            if not self.result.get(sampleArg["sample"].name, ""):
                self.result[sampleArg["sample"].name] = sampleArg["bounds"][1]

        error = (
            "No iterations were queued."
            " It's likely no Samples selected for analysis"
            " use the Component(s) selected for iteration."
        )
        if not self.result:
            self.exitcode = (1, error)
        else:
            self.exitcode = (0, "")
        return self.exitcode


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
                            data_files.DataFiles([dataFile], childSample.name)
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
        iterator: iterators.Iterator = None,
        batchSize=1,
        stepSize=1,
        offset: int = 0,
        rtol=0.0,
        separateFirstBatch=False
    ):
        self.iterator = iterator
        self.iterationMode = None
        self.exitcode = (1, "Operation incomplete")
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
                    self.firstBatch, self.purgeLocation, copy.deepcopy(
                        iterator)
                ) if self.separateFirstBatch else None,
                "REST": GudrunIterator(
                    self.batchedGudrunFile, self.purgeLocation,
                    copy.deepcopy(iterator)
                )
            }

    def batch(self, gudrunFile: GudrunFile, separateFirstBatch: bool
              ) -> typ.Tuple[typ.Union[GudrunFile, None], GudrunFile]:
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
        gudrun: Gudrun,
        purge: Purge,
        batchSize: int,
        iterator: iterators.Iterator = None,
    ):
        self.batchedGudrunFile.projectDir = (os.path.join(
            self.batchedGudrunFile.projectDir,
            f"BATCH_PROCESSING_BATCH_SIZE{batchSize}"
        ))
        exitcode = gudrun.gudrun(GudrunFile, purge, iterator)
        self.writeDiagnosticsFile(
            os.path.join(
                self.batchedGudrunFile.path(),
                "batch_processing_diagnostics.txt",
            ),
            self.batchedGudrunFile,
            self.iterationMode
        )
        self.exitcode = (exitcode, gudrun.error)
        return self.exitcode

    def iterate(
        self,
        gudrunIterator: GudrunIterator,
        batchedFile: GudrunFile,
        outputFolder: str,
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
                self.exitcode = (exitcode, error)
                return self.exitcode
            prevOutput = gudrunIterator.defaultRun.gudrunOutput

        # Iterate through gudrun objects
        for i, gudrun in enumerate(gudrunIterator.gudrunObjects):
            if self.canConverge(batchedFile, self.RTOL):
                # Keep only the processed objects in the list
                gudrunIterator.gudrunObjects = gudrunIterator.gudrunObjects[:i]
                self.exitcode = (0, )
                return self.exitcode

            exitcode = gudrunIterator.singleIteration(
                batchedFile, gudrun, prevOutput)

            self.writeDiagnosticsFile(
                os.path.join(batchedFile.path(),
                             "batch_processing_diagnostics.txt")
            )

            if exitcode:
                self.exitcode = (exitcode, gudrun.error)
                return self.exitcode

            prevOutput = gudrun.gudrunOutput

        self.exitcode = (0, )
        return self.exitcode

    def process(
        self,
        purge: Purge
    ):
        if self.iterationMode == enums.IterationModes.NONE:
            return self.bactchProcess(
                Gudrun(), self.BATCH_SIZE, purge=purge)

        else:
            if self.separateFirstBatch:
                exitcode, error = self.iterate(
                    gudrunIterator=self.gudrunIterators["FIRST"],
                    gudrunFile=self.firstBatch,
                    outputFolder="FIRST_BATCH"
                )
                if exitcode:
                    raise exc.GudrunException(
                        "Batch Processing failed with the following output:\n"
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
                    "Batch Processing failed with the following output:\n"
                    f"{error}"
                )
