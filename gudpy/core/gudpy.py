import tempfile
import os
import sys
import subprocess
import shutil
import copy

from core import config
from core import utils
from core import enums
from core import exception as exc
from core import iterators

from core.gudrun_file import GudrunFile
from core.purge_file import PurgeFile
import core.output_file_handler as handlers
from core.file_library import GudPyFileLibrary

SUFFIX = ".exe" if os.name == "nt" else ""


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
        self.gudrunOutput = None
        self.purgeOutput = None

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

    def saveAs(self, oldDir: str, targetDir: str):
        if os.path.exists(targetDir):
            raise IsADirectoryError("Cannot be an existing directory")

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
                f"{self.purge.sdout}"
            )

    def runGudrun(self):
        exitcode = self.gudrun.gudrun(self.gudrunFile)
        if exitcode:
            raise exc.GudrunException(
                "Purge failed to run with the following output:"
                f"{self.gudrun.sdout}"
            )


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

    def _errorOccured(self, stderr: str):
        self.error += stderr

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
            self.stderr += line
            return True

        return False


class Purge(Process):
    def __init__(self):
        self.PROCESS = "purge_det"
        self.purgeOutput = ""
        self.purged = False
        super().__init__(self.PROCESS)

    def organiseOutput(self):
        outputHandler = handlers.OutputHandler(self.gudrunFile, "Purge")
        outputHandler.organiseOutput()

    def purge(self, gudrunFile: GudrunFile):
        self._prepareRun()
        self._checkBinary()
        self.purgeOutput = ""

        with tempfile.TemporaryDirectory() as tmp:
            gudrunFile.setGudrunDir(tmp)
            gudrunFile.purgeFile.write_out(os.path.join(
                gudrunFile.instrument.GudrunInputFileDir,
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
                        self._errorOccured(line)
                        return 1
                if purge.stderr:
                    self._errorOccured(
                        purge.stderr.decode("utf8"))
                    return 1

            self.purgeOutput = gudrunFile.purgeFile.organiseOutput()

        gudrunFile.setGudrunDir(
            gudrunFile.projectDir)

        return 0


class Gudrun(Process):
    def __init__(self, iterator: iterators.Iterator = None):
        self.PROCESS = "gudrun_dcs"
        self.iterator = iterator
        self.gudrunOutput = handlers.GudrunOutput()
        super().__init__(self.PROCESS)

    def organiseOutput(self, head: str = "", overwrite: bool = True):
        outputHandler = handlers.GudrunOutputHandler(
            self, head=head, overwrite=overwrite
        )
        gudrunOutput = outputHandler.organiseOutput()
        return gudrunOutput

    def gudrun(self, gudrunFile: GudrunFile):
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
                        self._errorOccured(line)
                        return 1
                    self._outputChanged(line.decode("utf8"))
                if gudrun.stderr:
                    self._errorOccured(
                        gudrun.stderr.decode("utf8"))
                    return 1

            if self.iterator is not None:
                self.gudrunOutput = self.iterator.organiseOutput()
            else:
                self.gudrunOutput = self.organiseOutput()
            gudrunFile.setGudrunDir(gudrunFile.gudrunOutput.path)

        return 0


class RunContainersAsSamples:

    def __init__(self, gudrunFile):

        self.gudrunFile = copy.deepcopy(gudrunFile)

    def convertContainers(self):
        containersAsSamples = []
        for sampleBackground in self.gudrunFile.sampleBackgrounds:
            for sample in sampleBackground.samples:
                for container in sample.containers:
                    containersAsSamples.append(
                        container.convertToSample()
                    )
            sampleBackground.samples = containersAsSamples

    def runContainersAsSamples(self, path='', headless=False):
        self.convertContainers()
        return self.gudrunFile.dcs(path=path, headless=headless)
