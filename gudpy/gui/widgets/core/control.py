import os
import re
import sys

from PySide6 import QtCore, QtGui, QtUiTools, QtWidgets
from PySide6.QtCore import (
    QFile,
    QFileInfo,
    QTimer,
    QThread,
    QProcess,
)

from PySide6.QtWidgets import (
    QDialogButtonBox,
    QFileDialog,
    QMessageBox,
)

from gui.widgets.core.main_window import GudPyMainWindow
import gui.widgets.dialogs.iteration_dialog as iterators
from core import enums, worker, dialogs
from core import exception as exc
from core import gudpy as gp


class GudPyController(QtCore.QObject):
    def __init__(self):
        """
        Constructs all the necessary attributes for the GudPyMainWindow object.
        Calls initComponents() to load the UI file.
        """
        super().__init__()
        self.gudpy = gp.GudPyGUI()

        self.mainWidget = GudPyMainWindow()
        self.modified = False
        self.clipboard = None
        self.iterator = None
        self.results = {}
        self.allPlots = []
        self.plotModes = {}
        self.proc = None
        self.output = ""
        self.outputIterations = {}
        self.previousProcTitle = ""
        self.error = ""
        self.cwd = os.getcwd()
        self.warning = ""
        self.worker = None
        self.workerThread = None
        self.initComponents()
        self.timer = QTimer(self)
        self.timer.setSingleShot(True)
        self.timer.timeout.connect(self.autosave)

        self.purged = False

        self.mainWidget.ui.runPurge.triggered.connect(
            lambda: self.runPurge(dialog=True)
        )
        self.mainWidget.ui.runGudrun.triggered.connect(self.runGudrun)

        self.mainWidget.ui.iterateInelasticitySubtractions.triggered.connect(
            lambda: self.iterateGudrun(
                iterators.InelasticitySubtractionIterationDialog,
                "InelasticitySubtractionsDialog",
            )
        )

        self.mainWidget.ui.iterateTweakFactor.triggered.connect(
            lambda: self.iterateGudrun(
                iterators.TweakFactorIterationDialog,
                "iterateTweakFactorDialog"
            )
        )

        self.mainWidget.ui.iterateDensity.triggered.connect(
            lambda: self.iterateGudrun(
                iterators.DensityIterationDialog, "iterateDensityDialog"
            )
        )

        self.mainWidget.ui.iterateThickness.triggered.connect(
            lambda: self.iterateGudrun(
                iterators.ThicknessIterationDialog, "iterateThicknessDialog"
            )
        )

        self.mainWidget.ui.iterateRadius.triggered.connect(
            lambda: self.iterateGudrun(
                iterators.RadiusIterationDialog, "iterateRadiusDialog"
            )
        )

        self.mainWidget.ui.iterateComposition.triggered.connect(
            lambda: self.iterateGudrun(
                iterators.CompositionIterationDialog,
                "iterateCompositionDialog"
            )
        )

        self.mainWidget.ui.runContainersAsSamples.triggered.connect(
            self.runContainersAsSamples
        )

        self.mainWidget.ui.runFilesIndividually.triggered.connect(
            self.runFilesIndividually
        )

        self.mainWidget.ui.batchProcessing.triggered.connect(
            self.batchProcessing)

        self.mainWidget.ui.checkFilesExist.triggered.connect(
            lambda: self.checkFilesExist_(True)
        )

        self.mainWidget.ui.save.triggered.connect(self.saveInputFile)

        self.mainWidget.ui.saveAs.triggered.connect(self.saveAs)

        self.mainWidget.ui.exportInputFile.triggered.connect(
            self.exportInputFile)

        self.mainWidget.ui.viewLiveInputFile.triggered.connect(self.viewInput)

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

        self.mainWidget.ui.loadInputFile.triggered.connect(self.loadInputFile)

        self.mainWidget.ui.loadProject.triggered.connect(self.loadProject)

        self.mainWidget.ui.new_.triggered.connect(self.newInputFile)

        self.mainWidget.ui.objectStack.currentChanged.connect(
            lambda: self.updateComponents(self.gudpy.gudrunFile)
        )

        self.mainWidget.ui.exportArchive.triggered.connect(self.export)

        self.mainWidget.ui.exit.triggered.connect(self.exit_)

    def tryLoadAutosaved(self, path):
        dir_ = os.path.dirname(path)
        for f in os.listdir(dir_):
            if os.path.abspath(f) == path + ".autosave":
                with open(path, "r", encoding="utf-8") as fp:
                    original = fp.readlines()
                with open(f, "r", encoding="utf-8") as fp:
                    auto = fp.readlines()
                if original[:-5] == auto[:-5]:
                    return path

                autoFileInfo = QFileInfo(f)
                autoLastModified = autoFileInfo.lastModified()

                fileInfo = QFileInfo(path)
                lastModified = fileInfo.lastModified()

                if autoLastModified > lastModified:
                    messageBox = QMessageBox(self.mainWidget)
                    messageBox.setWindowTitle("Autosave found")
                    messageBox.setText(
                        f"Found autosaved file: {os.path.abspath(f)}.\n"
                        f"This file is newer ({autoLastModified.toString()})"
                        f" than the loaded file"
                        f" ({lastModified.toString()}).\n"
                        f"Would you like to load the autosaved file instead?"
                    )
                    messageBox.addButton(QMessageBox.No)
                    messageBox.addButton(QMessageBox.Yes)
                    result = messageBox.exec()
                    if result == QMessageBox.Yes:
                        return os.path.abspath(f)
                    else:
                        return path
                else:
                    return path
        return path

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
        if filename:
            if not filter:
                filter = "YAML (*.yaml)"
            fmt = filters[filter]
            try:
                self.gudpy.loadFromFile(loadFile=filename, format=fmt)
            except (FileNotFoundError, exc.ParserException) as e:
                self.mainWidget.sendError(e)
            except IOError:
                self.mainWidget.sendError("Could not open file.")

            self.updateWidgets(self.gudpy.gudrunFile)
            self.mainWidget.setWindowTitle(
                f"GudPy - {self.gudpy.gudrunFile.filename}[*]")

    def loadFromProject(self):
        """Load from previous GudPy project
        """
        projectDir = QFileDialog.getExistingDirectory(self, 'Select Project')

        try:
            self.gudpy.loadFromProject(projectDir=projectDir)
        except (FileNotFoundError, exc.ParserException) as e:
            self.mainWidget.sendError(e)
        except IOError:
            self.mainWidget.sendError("Could not open file.")

        self.updateWidgets()
        self.mainWidget.setWindowTitle(
            f"GudPy - {self.gudpy.gudrunFile.filename}[*]")

    def newProject(self):
        save = QtWidgets.QMessageBox.question(
            self.mainWidget,
            "GudPy",
            "Would you like to save current project?"
        )
        if save == QtWidgets.QMessageBox.Yes:
            if not self.setSaveLocation():
                return
            self.gudpy.save()

        configurationDialog = dialogs.ConfigurationDialog(self)
        result = configurationDialog.widget.exec()

        if not configurationDialog.cancelled and result:
            self.gudpy = gp.GudPy(
                loadFile=configurationDialog.configuration,
                format=enums.Format.TXT,
                config=True
            )

        self.mainWidget.updateWidgets()

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
            self.gudpy(dirname)
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

    """

    PROCESSES

    """

    def updateProgressBar(self, progress):
        self.mainWidget.progressBar.setValue(
            progress if progress <= 100 else 100
        )

    def checkFilesExist_(self, showSuccessDialog: bool = False):
        result = GudPyFileLibrary(self.gudpy.gudrunFile).checkFilesExist()
        if not all(r[0] for r in result[0]) or not all(r[0]
                                                       for r in result[1]):
            undefined = [
                r[1] for r in result[0] if not r[0]
            ]
            unresolved = [r[2] for r in result[1] if not r[0] and r[2]]
            missingFilesDialog = MissingFilesDialog(
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

    def prepareRun(self):
        if not self.checkFilesExist_():
            return False

        if not self.gudpy.gudrunFile.checkNormDataFiles():
            self.mainWidget.sendWarning(
                "Please specify normalisation data files.")
            return False

        if not self.checkSaveLocation():
            dirname, _ = QFileDialog.getSaveFileName(
                self.mainWidget,
                "Choose save location",
                (os.path.dirname(self.gudpy.gudrunFile.loadFile)
                 if self.gudpy.gudrunFile.loadFile else "")
            )
            self.gudpy.gudrunFile.setSaveLocation(dirname)
        self.mainWidget.processStarted()
        return True

    def checkPurge(self):
        if not self.purged and os.path.exists(
            os.path.join(
                self.gudpy.gudrunFile.projectDir, "Purge", "purge_det.dat"
            )
        ):
            purgeResult = self.mainWidget.purgeOptionsMessageBox(
                "purge_det.dat found, but wasn't run in this session. "
                "Run Purge?",
            )
        elif not self.purged:
            purgeResult = self.mainWidget.purgeOptionsMessageBox(
                "It looks like you may not have purged detectors. Run Purge?",
            )

        return purgeResult

    def runPurge(self) -> bool:
        self.mainWidget.setControlsEnabled(False)
        purgeDialog = dialogs.PurgeDialog(self.gudpy.gudrunFile, self)
        result = purgeDialog.widget.exec_()
        if (purgeDialog.cancelled or result == QDialogButtonBox.No):
            self.mainWidget.setControlsEnabled(True)
            return False

        if not self.prepareRun():
            self.mainWidget.processStopped()
            return False

        self.gudpy.purge = worker.PurgeWorker(self.gudpy.purgeFile)
        self.gudpy.purge.outputChanged.connect(
            self.outputSlots.setOutputStream)
        self.gudpy.purge.progress.connect(self.updateProgressBar)
        self.gudpy.purge.finished.connect(self.purgeFinished)
        self.gudpy.purge.start()

    def purgeFinished(self, exitcode):
        self.purged = True
        self.mainWidget.processStopped()

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
        self.mainWidget.goodDetectorsLabel.setText(
            f"Number of Good Detectors: {self.detectors}"
        )
        self.outputSlots.setOutput(
            self.gudpy.purge.stdout, "purge_det",
            gudrunFile=self.gudpy.gudrunFile
        )

    def runGudrun(self, gudrunFile=None):
        if not self.prepareRun():
            self.mainWidget.processStopped()
            return

        if not gudrunFile:
            gudrunFile = self.gudpy.gudrunFile

        self.gudpy.gudrun = worker.GudrunWorker(gudrunFile)
        self.gudpy.gudrun.outputChanged.connect(
            self.outputSlots.setOutputStream)
        self.gudpy.gudrun.progress.connect(self.updateProgressBar)
        self.gudpy.gudrun.finished.connect(self.gudrunFinished)

        if not self.purged:
            purgeResult = self.checkPurge()
            if purgeResult == QMessageBox.Yes:
                self.runPurge()
                self.gudpy.purge.finished.connect(
                    self.gudpy.gudrun.start()
                )
                return
            elif purgeResult == QMessageBox.Cancel:
                self.gudpy.gudrun = None
                return

        self.gudpy.gudrun.start()

    def gudrunFinished(self, exitcode):
        if self.gudpy.gudrunIterator:
            if exitcode != 0:
                self.mainWidget.sendError(
                    f"Gudrun Iteration failed with the following output: "
                    f"\n{self.gudpy.gudrunIterator.error}"
                )
                return

            self.gudpy.outputIterations[
                f"{self.gudpy.gudrunIterator.iterationType}"
                f" {self.gudpy.gudrunIterator.nCurrent}"
            ] = self.gudpy.gudrun.stdout
            self.outputSlots.setOutput(self.gudpy.outputIterations)
            self.sampleSlots.setSample(self.sampleSlots.sample)
            self.gudpy.gudrunIterator = None

            self.mainWidget.iterationResultsDialog(
                self.gudpy.gudrunIterator.results)

            self.mainWidget.updateWidgets(
                gudrunFile=self.gudpy.gudrunIterator.gudrunFile)
        else:
            if exitcode != 0:
                self.mainWidget.sendError(
                    f"Gudrun failed with the following output: "
                    f"\n{self.gudpy.gudrun.error}"
                )
                return
            self.outputSlots.setOutput(self.gudpy.gudrun.output)
            self.mainWidget.updateWidgets(
                gudrunFile=self.gudpy.gudrun.gudrunFile)

    def iterateGudrun(self, dialog, name) -> bool:
        iterationDialog = dialog(name, self.gudpy.gudrunFile, self.mainWidget)
        iterationDialog.widget.exec()
        if not iterationDialog.iterator:
            self.mainWidget.processStopped()
            return False

        if not self.prepareRun() or not self.checkPurge():
            self.mainWidget.processStopped()
            return False

        if isinstance(iterationDialog,
                      dialogs.iteration_dialog.CompositionIterationDialog):
            self.gudpy.gudrunIterator = worker.CompositionWorker(
                iterationDialog.iterator, self.gudpy.gudrunFile)
            self.gudpy.gudrunIterator.finished.connect(
                self.compositionIterationFinished)
        else:
            self.gudpy.gudrunIterator = worker.GudrunIteratorWorker(
                iterationDialog.iterator, self.gudpy.gudrunFile)
            self.gudpy.gudrunIterator.finished.connect(self.gudrunFinished)

        self.gudpy.gudrunIterator.outputChanged.connect(
            self.outputSlots.setOutputStream)
        self.gudpy.gudrunIterator.progress.connect(self.updateProgressBar)
        self.gudpy.gudrunIterator.nextIteration.connect(self.gudrunFinished)
        self.gudpy.gudrunIterator.finishised.connect(
            self.mainWidget.processStopped)
        self.gudpy.gudrunIterator.start()

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
                if self.sampleSlots.sample == original:
                    self.sampleSlots.setSample(original)

    def runContainersAsSamples(self):
        if not self.prepareRun():
            self.mainWidget.processStopped()
            return

        gudrunFile = self.gudpy.runModes.convertContainersToSample(
            self.gudpy.gudrunFile
        )
        self.runGudrun(gudrunFile=gudrunFile)

    def runFilesIndividually(self):
        if not self.prepareRun():
            self.mainWidget.processStopped()
            return

        gudrunFile = self.gudpy.runModes.partition(self.gudpy.gudrunFile)
        self.runGudrun(gudrunFile=gudrunFile)

    """

    COMMUNICATION

    """

    def exit_(self):
        """
        Exits GudPy - questions user if they want to save on exit or not.
        """
        result = QtWidgets.QMessageBox.question(
            self.mainWidget,
            "",
            "Do you want to save before exiting?",
            QtWidgets.QMessageBox.No | QtWidgets.QMessageBox.Yes,
        )

        if result == QtWidgets.QMessageBox.Yes:
            self.gudpy.gudrunFile.save()
        sys.exit(0)
