import tempfile
import os
import sys
import subprocess
import shutil
import copy
import typing as typ

from core import utils
from core import enums
from core import exception as exc
from core import iterators
from core.gudrun_file import GudrunFile
from core.purge_file import PurgeFile
import core.output_file_handler as handlers
from core.file_library import GudPyFileLibrary
from data import GudrunParameters, GudPyData
from core import data_files

SUFFIX = ".exe" if os.name == "nt" else ""


class GudPy:
    def __init__(
        self
    ):
        self.data = GudPyData()

        self.purge: Purge = None
        self.gudrun: Gudrun = None
        self.gudrunIterator: GudrunIterator = None
        self.batchProcessor: BatchProcessing = None

    def loadFromGudrunFile(
        self,
        loadFile: str,
    ) -> None:
        """Loads GudPy from an input file

        Parameters
        ----------
        loadFile : str
            Path of input file to load from

        Raises
        ------
        FileNotFoundError
            Raised if input file does not exist
        """
        if not os.path.exists(loadFile):
            raise FileNotFoundError("Input file does not exist.")

        self.data = GudPyData()
        self.data.importGudrunFile(loadFile)

    def loadFromProject(self, projectDir: str) -> None:
        """Loads GudPy from a project directory

        Parameters
        ----------
        projectDir : str
            Path to GudPy project folder
        """
        self.data = GudPyData()
        self.data.importProject(projectDir)
        self.setSaveLocation(projectDir)

    def checkSaveLocation(self) -> bool:
        """Checks if user has set the save location

        Returns
        -------
        bool
            If the save location is set or not
        """
        return bool(self.data.projectDir)

    def setSaveLocation(self, projectDir: str) -> None:
        """Sets the save location

        Parameters
        ----------
        projectDir : str
            Path to the desired save location of project
        """
        self.data.filename = f"{os.path.basename(projectDir)}.yaml"
        self.data.projectDir = projectDir
        self.data.autosaveLocation = (
            f"{os.path.basename(projectDir)}.autosave"
        )

    def save(self) -> None:
        """Saves current GudPy input file

        Parameters
        ----------
        path : str, optional
            Path to desired save location, by default ""
        format : enums.Format, optional
            Desired format of save file, by default enums.Format.YAML
        """
        self.data.writeYAMLFile()

    def saveAs(self, targetDir: str) -> None:
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

        oldDir = self.data.projectDir
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
        self.data.filename = os.path.basename(targetDir)
        self.data.writeYAMLFile()
        self.loadFromProject(projectDir=targetDir)

    def exportAsGudrunFile(self, path) -> None:
        self.data.exportGudrunFile(path)

    def checkFilesExist(self) -> typ.Tuple[list[str], list[str]]:
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
        result = GudPyFileLibrary(self.data.gudrunParams).checkFilesExist()
        if not all(r[0] for r in result[0]) or not all(r[0]
                                                       for r in result[1]):
            undefined = [
                r[1] for r in result[0] if not r[0]
            ]
            unresolved = [r[2] for r in result[1] if not r[0] and r[2]]

        print(f"Undefined files: {undefined}")
        print(f"Unresolved files: {unresolved}")

        return (undefined, unresolved)

    def prepareRun(self) -> None:
        if not self.checkSaveLocation():
            raise RuntimeError("No save location specified."
                               "Use GudPy.setSaveLocation(<path>)")

    def runPurge(self) -> None:
        """Runs purge_det binary to purge detectors in data

        Raises
        ------
        exc.PurgeException
            Raised if purge_det failed to execute
        """
        self.prepareRun()
        self.purge = Purge()
        exitcode = self.purge.purge(params=self.data.gudrunParams)
        self.save()
        if exitcode:
            raise exc.PurgeException(
                "Purge failed to run with the following output:\n"
                f"{self.purge.error}"
            )

    def runGudrun(self, params: GudrunParameters = None) -> None:
        """Runs gudrun_dcs binary

        Parameters
        ----------
        params : GudrunParameters, optional
            Parameters to input to gudrun_dcs, by default None

        Raises
        ------
        exc.GudrunException
            Raised if gudrun_dcs failed to execute
        """
        if not params:
            params = self.data.gudrunParams
        self.prepareRun()
        self.gudrun = Gudrun()
        exitcode = self.gudrun.gudrun(params)
        if exitcode:
            raise exc.GudrunException(
                "Gudrun failed to run with the following output:\n"
                f"{self.gudrun.error}"
            )
        self.save()

    def iterateGudrun(self, iterator: iterators.Iterator) -> None:
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
            params=self.data.gudrunParams, iterator=iterator)
        exitcode, error = self.gudrunIterator.iterate()
        if exitcode:
            raise exc.GudrunException(
                "Gudrun failed to run with the following output:"
                f"{error}"
            )
        self.data.gudrunParams = self.gudrunIterator.params
        self.data.gudrunOutput = self.gudrunIterator.gudrunOutput

    def iterateComposition(self, iterator: iterators.Composition) -> None:
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
            params=self.data.gudrunParams, iterator=iterator,
            projectDir=self.data.projectDir
        )
        exitcode, error = self.gudrunIterator.iterate()
        if exitcode:
            raise exc.GudrunException(
                "Gudrun failed to run with the following output:"
                f"{error}"
            )
        self.data.gudrunParams = self.gudrunIterator.params

    def runContainersAsSample(self) -> None:
        """Run gudrun_dcs but convert all containers to samples
        """
        gudrunParams = self.runModes.convertContainersToSample(
            self.data.gudrunParams)
        self.runGudrun(gudrunParams)

    def runFilesIndividually(self) -> None:
        """Run gudrun_dcs but partition all data files
        """
        gudrunParams = self.runModes.partition(self.data.gudrunParams)
        self.runGudrun(gudrunParams)

    def batchProcessing(
        self,
        iterator: iterators.Iterator = None,
        batchSize=1,
        stepSize=1,
        offset: int = 0,
        rtol=0.0,
        separateFirstBatch=False
    ) -> None:
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
            params=self.data.gudrunParams,
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

    def _outputChanged(self, output: str) -> None:
        self.output += output

    def checkBinary(self) -> None:
        if not os.path.exists(self.BINARY_PATH):
            self.exitcode = 1
            raise FileNotFoundError(
                f"Missing {self.PROCESS} binary"
                f" in location {self.BINARY_PATH}")

    def checkError(self, line: str) -> bool:
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
        super().__init__(self.PROCESS)

    def organiseOutput(
            self, procDir: str, projectDir: str) -> handlers.GudrunOutput:
        outputHandler = handlers.OutputHandler(
            procDir,
            projectDir,
            "Purge"
        )
        return outputHandler.organiseOutput()

    def purge(self, params: GudrunParameters, projectDir: str = ""):
        self.checkBinary()
        purgeFile = PurgeFile(params)
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

            if projectDir:
                params.purgeLocation = self.organiseOutput(tmp, projectDir)

        self.exitcode = 0
        return self.exitcode


class Gudrun(Process):
    def __init__(self):
        self.PROCESS: str = "gudrun_dcs"
        self.gudrunOutput = None
        super().__init__(self.PROCESS)

    def organiseOutput(
        self,
        params: GudrunParameters,
        projectDir: str,
        exclude: list[str] = [],
        head: str = "",
        overwrite: bool = True
    ) -> handlers.GudrunOutput:

        outputHandler = handlers.GudrunOutputHandler(
            params=params, projectDir=projectDir,
            head=head, overwrite=overwrite
        )
        gudrunOutput = outputHandler.organiseOutput(exclude=exclude)
        return gudrunOutput

    def gudrun(
        self,
        params: GudrunParameters,
        iterator: iterators.Iterator = None,
        projectDir: str = ""
    ) -> int:
        self.checkBinary()
        if not params.purgeLocation:
            print(
                "\n=========================================================="
                "\n=========================================================="
                "\n\nWARNING: Gudrun running without purge.\n\n"
                "\n=========================================================="
                "\n==========================================================")
        with tempfile.TemporaryDirectory() as tmp:
            purgeFiles = []
            if params.purgeLocation:
                for f in os.listdir(params.purgeLocation.purgeLocation):
                    shutil.copyfile(
                        os.path.join(params.purgeLocation.purgeLocation, f),
                        os.path.join(tmp, f)
                    )
                    purgeFiles.append(os.path.join(tmp, f))
            gudrunFile = GudrunFile()
            params.setGudrunDir(tmp)
            path = os.path.join(
                tmp,
                GudrunFile.OUTPATH
            )
            gudrunFile.writeGudrunFile(params, path)
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
                    params, projectDir, exclude=purgeFiles)
            else:
                self.gudrunOutput = self.organiseOutput(
                    params, projectDir, exclude=purgeFiles)
            params.setGudrunDir(self.gudrunOutput.path)

        self.exitcode = 0
        return self.exitcode


class GudrunIterator:
    def __init__(
        self,
        params: GudrunParameters,
        iterator: iterators.Iterator,
        projectDir: str = ""
    ):

        # Create a copy of gudrun file
        self.params = copy.deepcopy(params)
        self.iterator = iterator
        self.gudrunObjects = []
        self.exitcode = (1, "Operation incomplete")
        self.gudrunOutput = None
        self.projectDir = projectDir
        self.result = {}

        for _ in range(
                iterator.nTotal + (1 if iterator.requireDefault else 0)):
            self.gudrunObjects.append(Gudrun())

        # If the iterator requires a prelimenary run
        if iterator.requireDefault:
            self.gudrunObjects.append(Gudrun())

    def singleIteration(
        self,
        gudrun: Gudrun,
        prevOutput: handlers.GudrunOutput
    ) -> typ.Tuple[int, str]:  # (exitcode, error)
        self.params = self.iterator.performIteration(self.params, prevOutput)
        exitcode = gudrun.gudrun(self.params, self.iterator, self.projectDir)
        if exitcode:
            return exitcode
        self.gudrunOutput = gudrun.gudrunOutput
        return 0

    def iterate(self) -> typ.Tuple[int, str]:
        prevOutput = None

        # If the iterator requires a prelimenary run
        if self.iterator.requireDefault:
            exitcode = self.gudrunObjects[0].gudrun(
                self.params, self.iterator, self.projectDir)
            if exitcode:  # An exit code != 0 indicates failure
                self.exitcode = (exitcode, self.gudrunObjects[0].error)
                return self.exitcode
            prevOutput = self.gudrunObjects[0].gudrunOutput

        # Iterate through gudrun objects
        for gudrun in self.gudrunObjects:
            if gudrun.output:
                # If object has already been run, skip
                continue
            exitcode = self.singleIteration(gudrun, prevOutput)
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
        params: GudrunParameters,
        iterator: iterators.Composition,
        projectDir: str = ""
    ):
        self.params = copy.deepcopy(params)
        self.iterator = iterator
        self.gudrunObjects = []
        self.result = {}
        self.projectDir = projectDir
        self.compositionMap = None
        self.currentIteration = 0

    def iterate(self) -> typ.Tuple[int, str]:
        for sampleArg in self.iterator.sampleArgs:
            self.gudrunObjects.append((Gudrun(), Gudrun()))
            for gudrunNC, gudrunCC in self.gudrunObjects:
                # Run the new center
                newCenter = self.iterator.iterateNewPotentialCenter(
                    self.params, sampleArg)
                exitcode = gudrunNC.gudrun(
                    params=newCenter,
                    iterator=self.iterator,
                    projectDir=self.projectDir)
                if exitcode:  # An exit code != 0 indicates failure
                    self.exitcode = (exitcode, gudrunNC.error)
                    return self.exitcode

                # Run the current center
                currentCenter = self.iterator.iterateCurrentCenter(
                    self.params, sampleArg)
                exitcode = gudrunCC.gudrun(
                    params=currentCenter,
                    iterator=self.iterator,
                    projectDir=self.projectDir)
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
    def convertContainersToSample(
            self, params: GudrunParameters) -> GudrunParameters:
        newParams = copy.deepcopy(params)
        containersAsSamples = []
        for sampleBackground in params.sampleBackgrounds:
            for sample in sampleBackground.samples:
                for container in sample.containers:
                    containersAsSamples.append(
                        container.convertToSample()
                    )
            newParams.sampleBackground.samples = containersAsSamples
        return newParams

    def partition(self, params: GudrunParameters) -> GudrunParameters:
        newParams = copy.deepcopy(params)
        # Deepcopy the sample backgrounds.
        sampleBackgrounds = copy.deepcopy(params.sampleBackgrounds)
        # Clear the original list.
        newParams.sampleBackgrounds = []

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

        # Update params to use the newly constructed sample background.
        newParams.sampleBackgrounds = sampleBackgrounds
        return newParams


class BatchProcessing:
    def __init___(
        self,
        params: GudrunParameters,
        iterator: iterators.Iterator = None,
        projectDir: str = "",
        batchSize=1,
        stepSize=1,
        offset: int = 0,
        rtol=0.0,
        separateFirstBatch=False
    ):
        self.iterator = iterator
        self.iterationMode = None
        self.exitcode = (1, "Operation incomplete")
        self.projectDir = projectDir
        self.BATCH_SIZE = batchSize
        self.STEP_SIZE = stepSize
        self.OFFSET = offset
        self.RTOL = rtol

        self.separateFirstBatch = separateFirstBatch

        self.firstBatch, self.batchedParams = self.batch(
            separateFirstBatch=self.separateFirstBatch,
            params=params
        )

        if self.iterator:
            self.iterationMode = self.iterator.iterationMode
            self.gudrunIterators = {
                "FIRST": GudrunIterator(
                    self.firstBatch, copy.deepcopy(iterator), self.projectDir
                ) if self.separateFirstBatch else None,
                "REST": GudrunIterator(
                    self.batchedParams, copy.deepcopy(
                        iterator), self.projectDir
                )
            }

    def batch(self, params: GudrunParameters, separateFirstBatch: bool
              ) -> typ.Tuple[
        typ.Union[GudrunParameters, None],
        GudrunParameters
    ]:
        if not separateFirstBatch:
            batch = copy.deepcopy(params)
            batch.sampleBackgrounds = []
            for sampleBackground in params.sampleBackgrounds:
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
            first = copy.deepcopy(params)
            first.sampleBackgrounds = []
            for sampleBackground in params.sampleBackgrounds:
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

    def canConverge(self, batch: GudrunParameters) -> bool:
        if self.RTOL == 0.0:
            return False
        for sampleBackground in batch.sampleBackgrounds:
            for sample in sampleBackground.samples:
                if abs(batch.determineError(sample)) > self.RTOL:
                    return False
        return True

    def writeDiagnosticsFile(self, path: str, batch: GudrunParameters) -> None:
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
        batchSize: int,
        iterator: iterators.Iterator = None,
    ) -> typ.Tuple[int, str]:
        batchDir = os.path.join(
            self.projectDir, f"BATCH_PROCESSING_BATCH_SIZE{batchSize}")
        exitcode = gudrun.gudrun(self.batchedParams, iterator, batchDir)

        self.writeDiagnosticsFile(
            os.path.join(batchDir, "batch_processing_diagnostics.txt",),
            self.batchedParams,
        )
        self.exitcode = (exitcode, gudrun.error)
        return self.exitcode

    def iterate(
        self,
        gudrunIterator: GudrunIterator,
        batchedParams: GudrunParameters,
        outputFolder: str,
    ) -> typ.Tuple[int, str]:
        prevOutput = None

        batchDir = os.path.join(
            self.projectDir,
            f"BATCH_PROCESSING_BATCH_SIZE{self.BATCH_SIZE}",
            outputFolder
        )
        gudrunIterator.params = batchedParams
        gudrunIterator.projectDir = batchDir

        # If the iterator requires a prelimenary run
        if gudrunIterator.iterator.requireDefault:
            exitcode, error = gudrunIterator.gudrunObjects[0].gudrun(
                params=gudrunIterator.params, iterator=gudrunIterator.iterator,
                projectDir=batchDir)
            if exitcode:  # An exit code != 0 indicates failure
                self.exitcode = (exitcode, error)
                return self.exitcode
            prevOutput = gudrunIterator.defaultRun.gudrunOutput

        # Iterate through gudrun objects
        for i, gudrun in enumerate(gudrunIterator.gudrunObjects[1:]):
            if self.canConverge(gudrunIterator.params, self.RTOL):
                # Keep only the processed objects in the list
                gudrunIterator.gudrunObjects = gudrunIterator.gudrunObjects[:i]
                self.exitcode = (0, )
                return self.exitcode

            exitcode = gudrunIterator.singleIteration(gudrun, prevOutput)

            self.writeDiagnosticsFile(os.path.join(
                batchDir, "batch_processing_diagnostics.txt"))

            if exitcode:
                self.exitcode = (exitcode, gudrun.error)
                return self.exitcode

            prevOutput = gudrun.gudrunOutput

        self.exitcode = (0, )
        return self.exitcode

    def process(self) -> None:
        if self.iterationMode == enums.IterationModes.NONE:
            return self.bactchProcess(Gudrun(), self.BATCH_SIZE)

        else:
            if self.separateFirstBatch:
                exitcode, error = self.iterate(
                    gudrunIterator=self.gudrunIterators["FIRST"],
                    batchedParams=self.firstBatch,
                    outputFolder="FIRST_BATCH"
                )
                if exitcode:
                    raise exc.GudrunException(
                        "Batch Processing failed with the following output:\n"
                        f"{error}"
                    )

                self.propogateResults(
                    self.firstBatch, self.batchedParams
                )

            iterator = copy.deepcopy(self.iterator)
            self.gudrunIterators.append(GudrunIterator(
                self.batchedParams, iterator, self.projectDir
            ))
            exitcode, error = self.iterate(
                gudrunIterator=self.gudrunIterators["REST"],
                batchedParams=self.batchedParams,
                outputFolder="REST"
            )
            if exitcode:
                raise exc.GudrunException(
                    "Batch Processing failed with the following output:\n"
                    f"{error}"
                )
