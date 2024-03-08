import os
import re
import sys
import traceback
import typing as typ

from PySide6 import QtCore, QtWidgets

from PySide6.QtWidgets import (
    QDialogButtonBox,
    QFileDialog,
    QMessageBox,
)

from gui.widgets.core.main_window import GudPyMainWindow
from core.purge_file import PurgeFile
from core import file_library, enums
from gui.widgets.core import worker
from gui.widgets import dialogs
from core import iterators
from core import exception as exc
from core import gudpy as gp


class GudPyController(QtCore.QObject):
    def __init__(self):
        """
        Constructs all the necessary attributes for the GudPyMainWindow object.
        Calls initComponents() to load the UI file.
        """
        super().__init__()
        self.gudpy: gp.GudPy = gp.GudPy()
        self.mainWidget: QtWidgets.QMainWindow = GudPyMainWindow()
        self.purged: bool = False

        # Current process thread running
        self.workerThread: QtCore.QThread = None

        self.connectUiSlots()

    def connectUiSlots(self):
        self.mainWidget.ui.runPurge.triggered.connect(self.runPurge)
        self.mainWidget.ui.runGudrun.triggered.connect(self.runGudrun)
        self.mainWidget.ui.iterateInelasticitySubtractions.triggered.connect(
            lambda: self.iterateGudrun(
                dialogs.iterators.InelasticitySubtractionIterationDialog)
        )
        self.mainWidget.ui.iterateTweakFactor.triggered.connect(
            lambda: self.iterateGudrun(
                dialogs.iterators.TweakFactorIterationDialog)
        )
        self.mainWidget.ui.iterateDensity.triggered.connect(
            lambda: self.iterateGudrun(
                dialogs.iterators.DensityIterationDialog)
        )
        self.mainWidget.ui.iterateThickness.triggered.connect(
            lambda: self.iterateGudrun(
                dialogs.iterators.ThicknessIterationDialog)
        )
        self.mainWidget.ui.iterateRadius.triggered.connect(
            lambda: self.iterateGudrun(dialogs.iterators.RadiusIterationDialog)
        )
        self.mainWidget.ui.iterateComposition.triggered.connect(
            lambda: self.iterateGudrun(
                dialogs.iterators.CompositionIterationDialog)
        )
        self.mainWidget.ui.runContainersAsSamples.triggered.connect(
            self.runContainersAsSamples
        )
        self.mainWidget.ui.runFilesIndividually.triggered.connect(
            self.runFilesIndividually
        )
        self.mainWidget.ui.batchProcessing.triggered.connect(
            self.runBatchProcessing)
        self.mainWidget.ui.checkFilesExist.triggered.connect(
            lambda: self.checkFilesExist(True)
        )
        self.mainWidget.timer.setSingleShot(True)
        self.mainWidget.timer.timeout.connect(self.autosave)
        self.mainWidget.ui.stopTaskButton.clicked.connect(self.stopProcess)
        self.mainWidget.ui.save.triggered.connect(self.save)
        self.mainWidget.ui.saveAs.triggered.connect(self.saveAs)
        self.mainWidget.ui.exportInputFile.triggered.connect(
            self.exportInputFile)
        self.mainWidget.ui.viewLiveInputFile.triggered.connect(
            self.mainWidget.viewInput)
        self.mainWidget.ui.insertSampleBackground.triggered.connect(
            self.mainWidget.ui.objectTree.insertSampleBackground
        )
        self.mainWidget.ui.insertSample.triggered.connect(
            self.mainWidget.ui.objectTree.insertSample
        )
        self.mainWidget.ui.insertDefaultContainer.triggered.connect(
            self.mainWidget.ui.objectTree.insertContainer
        )
        self.mainWidget.ui.copy.triggered.connect(
            self.mainWidget.ui.objectTree.copy)
        self.mainWidget.ui.cut.triggered.connect(
            self.mainWidget.ui.objectTree.cut)
        self.mainWidget.ui.paste.triggered.connect(
            self.mainWidget.ui.objectTree.paste
        )
        self.mainWidget.ui.delete_.triggered.connect(
            self.mainWidget.ui.objectTree.del_
        )
        self.mainWidget.ui.loadInputFile.triggered.connect(self.loadFromFile)
        self.mainWidget.ui.loadProject.triggered.connect(self.loadFromProject)
        self.mainWidget.ui.new_.triggered.connect(self.newProject)
        self.mainWidget.ui.objectStack.currentChanged.connect(
            self.mainWidget.updateComponents)
        self.mainWidget.ui.exportArchive.triggered.connect(self.exportArchive)
        self.mainWidget.ui.exit.triggered.connect(self.exit_)

    """

    INPUT / OUTPUT

    """

    def tryLoadAutosaved(self, projectDir):
        for f in os.listdir(projectDir):
            if f == self.gudpy.autosaveLocation:
                path = os.path.join(projectDir, f)
                autoFileInfo = QtCore.QFileInfo(path)
                autoDate = autoFileInfo.lastModified()

                fileInfo = QtCore.QFileInfo(self.gudpy.gudrunFile.path())
                currentDate = fileInfo.lastModified()

                if autoDate > currentDate:
                    if self.mainWidget.autosaveMessage(
                        path, autoDate.toString(), currentDate.toString()
                    ) == QMessageBox.Yes:
                        return path
        return ""

    def loadFromFile(self):
        """
        Opens a QFileDialog to load an input file.
        """
        filters = {
            "YAML (*.yaml)": enums.Format.YAML,
            "Gudrun Compatible (*.txt)": enums.Format.TXT,
            "Sample Parameters (*.sample)": enums.Format.TXT
        }
        filename, filter = QFileDialog.getOpenFileName(
            self.mainWidget,
            "Select Input file for GudPy",
            ".",
            f"{list(filters.keys())[0]};;" +
            f"{list(filters.keys())[1]};;" +
            f"{list(filters.keys())[2]}"
        )

        if not filename:
            return

        if not filter:
            filter = "YAML (*.yaml)"
        fmt = filters[filter]
        try:
            gudpy = gp.GudPy()
            gudpy.loadFromFile(loadFile=filename, format=fmt)
            self.gudpy = gudpy
        except (FileNotFoundError, exc.ParserException) as e:
            self.mainWidget.sendError(e)
            return
        except IOError:
            self.mainWidget.sendError("Could not open file.")
            return
        self.mainWidget.updateWidgets(self.gudpy.gudrunFile)
        self.mainWidget.setWindowTitle(
            f"GudPy - {self.gudpy.gudrunFile.filename}[*]")

    def loadFromProject(self):
        """Load from previous GudPy project
        """
        projectDir = QFileDialog.getExistingDirectory(
            self.mainWidget, 'Select Project')

        if not projectDir:
            return

        try:
            self.gudpy.loadFromProject(projectDir=projectDir)
            autosave = self.tryLoadAutosaved(projectDir)
            if autosave:
                filename = autosave
                gudpy = gp.GudPy()
                gudpy.loadFromFile(loadFile=filename)
                self.gudpy = gudpy
        except (FileNotFoundError, exc.ParserException) as e:
            self.mainWidget.sendError(e)
            return
        except IOError:
            self.mainWidget.sendError("Could not open file.")
            return
        self.mainWidget.updateWidgets(self.gudpy.gudrunFile)
        self.mainWidget.setWindowTitle(
            f"GudPy - {self.gudpy.gudrunFile.filename}[*]")

    def newProject(self):
        if self.gudpy.gudrunFile:
            save = QtWidgets.QMessageBox.question(
                self.mainWidget,
                "GudPy",
                "Would you like to save current project?"
            )
            if save == QtWidgets.QMessageBox.Yes:
                if not self.setSaveLocation():
                    return
                self.gudpy.save()

        configurationDialog = dialogs.configuration.ConfigurationDialog(
            self.mainWidget)
        result = configurationDialog.widget.exec()

        if not configurationDialog.cancelled and result:
            self.gudpy = gp.GudPy()
            self.gudpy.loadFromFile(
                loadFile=configurationDialog.configuration,
                format=enums.Format.TXT,
                config=True
            )
            self.mainWidget.updateWidgets(self.gudpy.gudrunFile)

    def setSaveLocation(self, saveAs=False):
        """Function to let the user choose where the project is saved to

        Parameters
        ----------
        saveAs : bool, optional
            Whether to saveAs (bypass current savelocation), by default False

        Returns
        -------
        bool
            Detects whether getting save file was successful or not
        """
        if saveAs or not self.gudpy.checkSaveLocation():
            dirname, _ = QFileDialog.getSaveFileName(
                self.mainWidget,
                "Choose save location",
            )
            if not dirname:
                return False
            self.gudpy.setSaveLocation(dirname)
            return True

    def save(self):
        # Check if save location has been set
        # override project input file or force save location to be chose
        if not self.gudpy.checkSaveLocation():
            # Check if save location has been specified
            # If not, call save dialog
            if not self.setSaveLocation():
                return
        self.gudpy.save()
        self.mainWidget.setUnModified()

    def saveAs(self):
        dirname, _ = QFileDialog.getSaveFileName(
            self.mainWidget,
            "Choose save location",
        )
        if not dirname:
            return

        try:
            self.gudpy.saveAs(dirname)
        except IsADirectoryError as e:
            self.mainWidget.sendError(e)

    def exportInputFile(self):
        """
        Saves the current state of the input file as...
        """
        filename, filter = QFileDialog.getSaveFileName(
            self,
            "Export input file as..",
            ".",
            "YAML (*.yaml);;Gudrun Compatible (*.txt)",
        )
        fmt = enums.Format.YAML
        if filename:
            ext = re.search(r"\((.+?)\)", filter).group(1).replace("*", "")
            fmt = enums.Format.TXT if ext == ".txt" else enums.Format.YAML
            if filter and sys.platform.startswith("linux"):
                filename += ext
            if os.path.dirname(filename) == self.gudpy.projectDir:
                self.mainWidget.sendWarning("Do not modify project folder.")
                return
        self.gudpy.save(path=filename, format=fmt)
        self.setUnModified()

    def exportArchive(self):
        if not self.gudpy.checkSaveLocation():
            if not self.setSaveLocation():
                return
        exportDialog = dialogs.io.ExportDialog(
            self.gudpy.gudrunFile, self.mainWidget)
        exportDialog.widget.exec()

    def autosave(self):
        if self.gudpy.checkSaveLocation() and not self.workerThread:
            self.gudpy.save(path=self.gudpy.autosaveLocation)

    """

    PROCESSES

    """

    def checkFilesExist(self, showSuccessDialog: bool = False):
        result = file_library.GudPyFileLibrary(
            self.gudpy.gudrunFile).checkFilesExist()
        if not all(r[0] for r in result[0]) or not all(r[0]
                                                       for r in result[1]):
            undefined = [
                r[1] for r in result[0] if not r[0]
            ]
            unresolved = [r[2] for r in result[1] if not r[0] and r[2]]
            missingFilesDialog = dialogs.io.MissingFilesDialog(
                undefined, unresolved, self.mainWidget
            )
            missingFilesDialog.widget.exec_()
            return False

        if showSuccessDialog:
            QMessageBox.information(
                self.mainWidget,
                "GudPy Information",
                "All files found!",
            )
        return True

    def connectProcessSignals(
        self,
        process: QtCore.QThread,
        onFinish: typ.Callable
    ):
        process.started.connect(self.mainWidget.processStarted)
        process.outputChanged.connect(
            self.mainWidget.outputSlots.setOutputStream)
        process.progressChanged.connect(
            self.mainWidget.updateProgressBar)
        process.finished.connect(
            self.mainWidget.processStopped)
        process.finished.connect(onFinish)

    def createPurgeProcess(self) -> bool:
        if not self.prepareRun():
            return False
        self.mainWidget.setControlsEnabled(False)
        purgeDialog = dialogs.purge.PurgeDialog(
            self.gudpy.gudrunFile, self.mainWidget)
        result = purgeDialog.widget.exec_()
        if (purgeDialog.cancelled or result == QDialogButtonBox.No):
            self.mainWidget.setControlsEnabled(True)
            return False

        self.gudpy.purgeFile = PurgeFile(self.gudpy.gudrunFile)
        self.gudpy.purge = worker.PurgeWorker(
            purgeFile=self.gudpy.purgeFile,
            gudrunFile=self.gudpy.gudrunFile,
        )
        self.connectProcessSignals(
            process=self.gudpy.purge, onFinish=self.purgeFinished
        )

        return True

    def prepareRun(self) -> bool:
        if not self.checkFilesExist():
            return False

        if not self.gudpy.gudrunFile.checkNormDataFiles():
            self.mainWidget.sendWarning(
                "Please specify normalisation data files.")
            return False

        if not self.gudpy.checkSaveLocation() and not self.setSaveLocation():
            return False

        return True

    def startProcess(self) -> None:
        if isinstance(self.workerThread, gp.Purge):
            self.workerThread.start()
            return

        # Check purge if process has purge attribute
        if not self.gudpy.purge:
            purgeResult = QMessageBox.No
            if os.path.exists(
                os.path.join(
                    self.gudpy.projectDir, "Purge", "purge_det.dat"
                )
            ):
                purgeResult = self.mainWidget.purgeOptionsMessageBox(
                    "purge_det.dat found, but wasn't run in this session. "
                    "Run Purge?",
                )
            else:
                purgeResult = self.mainWidget.purgeOptionsMessageBox(
                    "It looks like you may not have purged detectors."
                    "Run Purge?",
                )

            if purgeResult == QMessageBox.Yes:
                if self.createPurgeProcess():
                    self.gudpy.purge.start()
                    self.gudpy.purge.finished.connect(self.startProcess)
                    return
            else:
                self.mainWidget.processStopped()
                return
        self.workerThread.purge = self.gudpy.purge
        self.workerThread.start()

    def runPurge(self) -> bool:
        if self.createPurgeProcess():
            self.workerThread = self.gudpy.purge
            self.startProcess()

    def purgeFinished(self, exitcode):
        self.purged = True

        if exitcode != 0:
            self.mainWidget.sendError(
                "Purge failed with the following output: "
                f"{self.gudpy.purge.error}"
            )
            return

        thresh = self.gudpy.gudrunFile.instrument.goodDetectorThreshold
        if thresh and self.gudpy.purge.detectors < thresh:
            self.mainWidget.sendWarning(
                f"{self.gudpy.purge.detectors} "
                "detectors made it through the purge.\n"
                " The acceptable minimum for "
                f"{self.gudpy.gudrunFile.instrument.name} is {thresh}"
            )
        self.mainWidget.ui.goodDetectorsLabel.setText(
            f"Number of Good Detectors: {self.gudpy.purge.detectors}"
        )
        self.mainWidget.outputSlots.setOutput(
            self.gudpy.purge.output, "purge_det",
            gudrunFile=self.gudpy.gudrunFile
        )

        if isinstance(self.workerThread, gp.Purge):
            self.workerThread = None

    def runGudrun(self, gudrunFile=None):
        if not gudrunFile:
            gudrunFile = self.gudpy.gudrunFile

        if not self.prepareRun():
            return

        self.gudpy.gudrun = worker.GudrunWorker(gudrunFile)
        self.connectProcessSignals(
            process=self.gudpy.gudrun, onFinish=self.gudrunFinished
        )

        self.workerThread = self.gudpy.gudrun
        self.startProcess()

    def iterateGudrun(self, dialog):
        iterationDialog = dialog(
            self.mainWidget, self.gudpy.gudrunFile)
        iterationDialog.widget.exec()
        if not iterationDialog.params:
            return
        if not self.prepareRun():
            return
        # If it is a Composition iteration, the gudrunFile must be specified
        if iterationDialog.iteratorType == iterators.Composition:
            iterationDialog.params["gudrunFile"] = self.gudpy.gudrunFile

        self.gudpy.iterator = iterationDialog.iteratorType(
            **iterationDialog.params)

        # If Composition iterator, initialise Composition Worker
        if iterationDialog.iteratorType == iterators.Composition:
            self.gudpy.gudrunIterator = worker.CompositionWorker(
                self.gudpy.iterator, self.gudpy.gudrunFile)
            self.connectProcessSignals(
                process=self.gudpy.gudrunIterator,
                onFinish=self.compositionIterationFinished
            )
        # Else use standard GudrunIteratorWorker
        else:
            self.gudpy.gudrunIterator = worker.GudrunIteratorWorker(
                self.gudpy.iterator, self.gudpy.gudrunFile)
            self.connectProcessSignals(
                process=self.gudpy.gudrunIterator,
                onFinish=self.gudrunFinished
            )

        self.workerThread = self.gudpy.gudrunIterator
        self.startProcess()

    def gudrunFinished(self, exitcode):
        if self.workerThread == self.gudpy.gudrunIterator:
            if self.gudpy.gudrunIterator.exitcode[0] != 0:
                self.mainWidget.sendError(
                    f"Gudrun Iteration failed with the following output: "
                    f"\n{self.gudpy.gudrunIterator.error}"
                )
                return

            self.mainWidget.outputSlots.setOutput(
                self.gudpy.gudrunIterator.output,
                f"Gudrun {self.gudpy.gudrunIterator.iterator.name}")
            self.mainWidget.sampleSlots.setSample(
                self.mainWidget.sampleSlots.sample)
            self.mainWidget.iterationResultsDialog(
                self.gudpy.gudrunIterator.result,
                self.gudpy.gudrunIterator.iterator.name)
            self.mainWidget.updateWidgets(
                gudrunFile=self.gudpy.gudrunIterator.gudrunFile,
                gudrunOutput=self.gudpy.gudrunIterator.gudrunOutput
            )
        elif self.workerThread == self.gudpy.gudrun:
            if exitcode != 0:
                self.mainWidget.sendError(
                    f"Gudrun failed with the following output: "
                    f"\n{self.gudpy.gudrun.error}"
                )
                return
            self.mainWidget.outputSlots.setOutput(
                self.gudpy.gudrun.output, "Gudrun")
            self.mainWidget.updateWidgets(
                gudrunFile=self.gudpy.gudrunFile,
                gudrunOutput=self.gudpy.gudrun.gudrunOutput
            )
        self.workerThread = None

    def compositionIterationFinished(self, exitcode):
        if exitcode != 0:
            self.gudrunFinished(exitcode)
            return

        for original, new in self.gudrunIterator.compositionMap.items():
            d = dialogs.composition_acceptance.CompositionAcceptanceDialog(
                new, self.gudrunIterator.gudrunFile, self.mainWidget.ui)
            result = d.widget.exec()
            if result:
                original.composition = new.composition
                if self.mainWidget.sampleSlots.sample == original:
                    self.mainWidget.sampleSlots.setSample(original)

    def runContainersAsSamples(self):
        if not self.prepareRun():
            return
        gudrunFile = self.gudpy.runModes.convertContainersToSample(
            self.gudpy.gudrunFile
        )
        self.runGudrun(gudrunFile=gudrunFile)

    def runFilesIndividually(self):
        if not self.prepareRun():
            return
        gudrunFile = self.gudpy.runModes.partition(self.gudpy.gudrunFile)
        self.runGudrun(gudrunFile=gudrunFile)

    def runBatchProcessing(self):
        if not self.prepareRun():
            return
        dialog = dialogs.batch.BatchProcessingDialog(
            self.mainWidget
        )
        self.gudpy.gudrunIterator = worker.BatchWorker(
            gudrunFile=self.gudpy.gudrunFile,
            iterator=dialog.iterator,
            batchSize=dialog.batchSize,
            stepSize=dialog.stepSize,
            offset=dialog.offset,
            rtol=dialog.rtol,
            separateFirstBatch=dialog.separateFirstBatch
        )

        self.connectProcessSignals(
            process=self.gudpy.gudrunIterator,
            onFinish=self.gudrunFinished
        )
        self.workerThread = self.gudpy.gudrunIterator
        self.startProcess()

    def stopProcess(self):
        if self.workerThread:
            self.workerThread.requestInterruption()
            self.workerThread.wait()
            self.workerThread = None

    """

    COMMUNICATION

    """

    def cleanup(self):
        self.stopProcess()
        self.autosave()

    def onException(self, cls, exception, tb):
        self.mainWidget.sendError(
            f"{''.join(traceback.format_exception(cls, exception, tb))}",
        )

    def exit_(self):
        """
        Exits GudPy - questions user if they want to save on exit or not.
        """
        self.cleanup()
        result = QtWidgets.QMessageBox.question(
            self.mainWidget,
            "",
            "Do you want to save before exiting?",
            QtWidgets.QMessageBox.No | QtWidgets.QMessageBox.Yes,
        )

        if result == QtWidgets.QMessageBox.Yes:
            self.gudpy.gudrunFile.save()
        sys.exit(0)
