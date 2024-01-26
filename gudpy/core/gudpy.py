import tempfile
import os
import sys
import subprocess

from core import config
from core import utils
from core import enums

SUFFIX = ".exe" if os.name == "nt" else ""


class Process:
    def __init__(self, gudrunFile, process):
        self.PROCESS = process
        self.BINARY_PATH = ""

        self.gudrunFile = gudrunFile
        self.stdout = ""
        self.sterr = ""

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

    def _outputChanged(self, output):
        self.stdout += output

    def _errorOccured(self, stderr):
        self.stderr += stderr

    def checkBinary(self):
        if not os.path.exists(self.BINARY_PATH):
            raise FileNotFoundError(f"Missing {self.PROCESS} binary")

    def checkError(self, line):
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
    def __init__(self, gudrunFile):
        self.PROCESS = "purge_det"
        super().__init__(gudrunFile, self.PROCESS)

    def purge(self):
        self.checkBinary()

        with tempfile.TemporaryDirectory() as tmp:
            self.gudrunFile.setGudrunDir(tmp)
            self.gudrunFile.purgeFile.write_out(os.path.join(
                self.gudrunFile.instrument.GudrunInputFileDir,
                f"{self.PROCESS}.dat"
            ))

            with subprocess.Popen(
                [self.BINARY_PATH, f"{self.PROCESS}.dat"], cwd=tmp,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT
            ) as purge:
                for line in purge.stdout:
                    self._outputChanged(line.decode("utf8"))
                    if self.checkError(line):
                        self._errorOccured(line)
                if purge.stderr:
                    self._errorOccured(
                        purge.stderr.decode("utf8"))
                    return

            self.gudrunFile.purgeFile.organiseOutput()

        self.gudrunFile.setGudrunDir(
            self.gudrunFile.projectDir)


class Gudrun(Process):
    def __init__(self, gudrunFile, iterator=None):
        self.PROCESS = "gudrun_dcs"
        self.iterator = iterator
        super().__init__(gudrunFile, self.PROCESS)

    def gudrun(self):
        self.checkBinary()

        with tempfile.TemporaryDirectory() as tmp:
            self.gudrunFile.setGudrunDir(tmp)
            path = os.path.join(
                tmp,
                self.gudrunFile.outpath
            )
            self.gudrunFile.save(
                path=os.path.join(
                    self.gudrunFile.projectDir,
                    f"{self.gudrunFile.filename}"
                ),
                format=enums.Format.YAML
            )
            self.gudrunFile.write_out(path)
            with subprocess.Popen(
                [self.BINARY_PATH, path], cwd=tmp,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT
            ) as gudrun:
                for line in gudrun.stdout:
                    if self.checkError(line):
                        self._errorOccured(line)
                    self._outputChanged(line.decode("utf8"))
                if gudrun.stderr:
                    self._errorOccured(
                        gudrun.stderr.decode("utf8"))
                    return

            if self.iterator is not None:
                self.gudrunFile.gudrunOutput = self.iterator.organiseOutput()
            else:
                self.gudrunFile.gudrunOutput = self.gudrunFile.organiseOutput()
            self.gudrunFile.setGudrunDir(self.gudrunFile.gudrunOutput.path)
