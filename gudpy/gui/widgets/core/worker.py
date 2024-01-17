import os
import tempfile
from copy import deepcopy
from PySide6.QtCore import QObject, Signal, QThread
import subprocess
import sys

from core import config
from core.gud_file import GudFile
import core.utils as utils
from core.sample import Sample
from core import enums
from core.iterators.composition import gss

SUFFIX = ".exe" if os.name == "nt" else ""


class PurgeWorker(QObject):
    started = Signal(int)
    errorOccured = Signal(str)
    outputChanged = Signal(str)
    finished = Signal(int)

    def __init__(self, gudrunFile):
        super().__init__()
        self.gudrunFile = gudrunFile
        self.PROCESS = "purge_det"

    def purge(self):
        self.started.emit(1)

        if hasattr(sys, '_MEIPASS'):
            purge_det = os.path.join(sys._MEIPASS, f"{self.PROCESS}{SUFFIX}")
        else:
            purge_det = utils.resolve(
                os.path.join(
                    config.__rootdir__, "bin"
                ), f"{self.PROCESS}{SUFFIX}"
            )
        if not os.path.exists(purge_det):
            self.errorOccured.emit("MISSING_BINARY")
            return

        with tempfile.TemporaryDirectory() as tmp:
            self.gudrunFile.setGudrunDir(tmp)
            self.gudrunFile.purgeFile.write_out(os.path.join(
                self.gudrunFile.instrument.GudrunInputFileDir,
                f"{self.PROCESS}.dat"
            ))

            with subprocess.Popen(
                [purge_det, f"{self.PROCESS}.dat"], cwd=tmp,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT
            ) as purge:
                for line in purge.stdout:
                    self.outputChanged.emit(line.decode("utf8").rstrip("\n"))
                if purge.stderr:
                    self.errorOccured.emit(
                        purge.stderr.decode("utf8").rstrip("\n"))
                    return

            self.gudrunFile.purgeOutput = (
                self.gudrunFile.purgeFile.organiseOutput()
            )

        self.gudrunFile.setGudrunDir(
            self.gudrunFile.projectDir)

        self.finished.emit(1)


class GudrunWorker(QObject):
    started = Signal(int)
    outputChanged = Signal(str)
    nextIteration = Signal(int)
    errorOccured = Signal(str)
    finished = Signal(int)

    def __init__(self, gudrunFile, iterator):
        super().__init__()
        self.gudrunFile = gudrunFile
        self.iterator = iterator
        self.PROCESS = "gudrun_dcs"

    def gudrun(self):
        self.started.emit(1)

        if hasattr(sys, '_MEIPASS'):
            gudrun_dcs = os.path.join(sys._MEIPASS, f"{self.PROCESS}{SUFFIX}")
        else:
            gudrun_dcs = utils.resolve(
                os.path.join(
                    config.__rootdir__, "bin"
                ), f"{self.PROCESS}{SUFFIX}"
            )
        if not os.path.exists(gudrun_dcs):
            self.errorOccured.emit("MISSING_BINARY")
            return

        with tempfile.TemporaryDirectory() as tmp:
            path = self.gudrunFile.outpath
            self.gudrunFile.setGudrunDir(tmp)
            path = os.path.join(
                tmp,
                path
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
                [gudrun_dcs, path], cwd=tmp,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT
            ) as gudrun:
                for line in gudrun.stdout:
                    self.outputChanged.emit(line.decode("utf8").rstrip("\n"))
                if gudrun.stderr:
                    self.errorOccured.emit(
                        gudrun.stderr.decode("utf8").rstrip("\n"))
                    return

            if self.iterator is not None:
                self.gudrunFile.gudrunOutput = self.iterator.organiseOutput()
            else:
                self.gudrunFile.gudrunOutput = self.gudrunFile.organiseOutput()
            self.gudrunFile.setGudrunDir(self.gudrunFile.gudrunOutput.path)

        self.finished.emit(1)


class CompositionWorker(QObject):
    finished = Signal(Sample, Sample)
    started = Signal(Sample)
    nextIteration = Signal(int)
    errorOccured = Signal(str)

    def __init__(self, args, kwargs, sample, gudrunFile):
        self.args = args
        self.kwargs = kwargs
        self.sample = sample
        self.updatedSample = None
        self.errored = False
        self.gudrunFile = gudrunFile
        super(CompositionWorker, self).__init__()

    def work(self):
        self.started.emit(self.sample)
        # perform golden-section search.
        gss(
            self.costup,
            *self.args,
            **self.kwargs,
            startIterFunc=self.nextIteration.emit
        )
        if not self.errored:
            # If an error occurs emit appropiate signal.
            self.finished.emit(self.sample, self.updatedSample)

    def costup(
        self, x, gudrunFile, sampleBackground,
        components, totalMolecules=None
    ):

        if QThread.currentThread().isInterruptionRequested():
            return None
        gf = deepcopy(gudrunFile)
        gf.sampleBackgrounds = [sampleBackground]

        # Prevent negative x.
        x = abs(x)

        if len(components) == 1:
            # Determine instances where target components are used.
            weightedComponents = [
                wc for wc in sampleBackground.samples[0]
                .composition.weightedComponents
                for c in components
                if c.eq(wc.component)
            ]
            for component in weightedComponents:
                component.ratio = x

        elif len(components) == 2:
            wcA = wcB = None
            # Determine instances where target components are used.
            for weightedComponent in (
                sampleBackground.samples[0].composition.weightedComponents
            ):
                if weightedComponent.component.eq(components[0]):
                    wcA = weightedComponent
                elif weightedComponent.component.eq(components[1]):
                    wcB = weightedComponent

            if wcA and wcB:
                # Ensure combined ratio == totalMolecules.
                wcA.ratio = x
                wcB.ratio = abs(totalMolecules - x)

        # Update composition
        sampleBackground.samples[0].composition.translate()
        self.updatedSample = sampleBackground.samples[0]

        # Set up process and execute.
        outpath = os.path.join(
            gf.instrument.GudrunInputFileDir,
            "gudpy.txt"
        )
        self.proc, func, args = gf.dcs(path=outpath, headless=False)
        func(*args)
        self.proc.setWorkingDirectory(gf.instrument.GudrunInputFileDir)
        self.proc.start()
        # Block until process is finished.
        self.proc.waitForFinished(-1)
        # Read from stdout.
        if not self.proc:
            return None
        data = self.proc.readAllStandardOutput()
        result = bytes(data).decode("utf8")

        # Check for errors.
        ERROR_KWDS = [
            "does not exist",
            "error",
            "Error"
        ]
        if [KWD for KWD in ERROR_KWDS if KWD in result]:
            self.errorOccured.emit(result)
            self.errored = True
            return None

        gudPath = sampleBackground.samples[0].dataFiles[0].replace(
            gudrunFile.instrument.dataFileType,
            "gud"
        )

        gudFile = GudFile(
            os.path.join(
                gudrunFile.instrument.GudrunInputFileDir, gudPath
            )
        )

        # Determine cost.
        if gudFile.averageLevelMergedDCS == gudFile.expectedDCS:
            return 0
        else:
            return (gudFile.expectedDCS-gudFile.averageLevelMergedDCS)**2
