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
from PySide6.QtGui import QPainter, QIcon
from PySide6.QtUiTools import QUiLoader
from PySide6.QtWidgets import (
    QDialogButtonBox,
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMessageBox,
    QProgressBar,
    QSizePolicy,
    QStatusBar,
    QWidget,
    QMenu,
    QToolButton,
)

from core import enums
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
        self.queue = Queue()
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

            self.updateWidgets()
            self.mainWidget.setWindowTitle(
                f"GudPy - {self.gudrunFile.filename}[*]")

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
            f"GudPy - {self.gudrunFile.filename}[*]")

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
        progress += self.mainWidget.progressBar.value()
        self.mainWidget.progressBar.setValue(
            progress if progress <= 100 else 100
        )

    def checkFilesExist_(self, showSuccessDialog: bool = False):
        result = GudPyFileLibrary(self.gudrunFile).checkFilesExist()
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

        if not self.gudrunFile.checkNormDataFiles():
            self.mainWidget.sendWarning("Please specify normalisation data files.")
            return False

        if not self.checkSaveLocation():
            dirname, _ = QFileDialog.getSaveFileName(
                self.mainWidget,
                "Choose save location",
                (os.path.dirname(self.gudrunFile.loadFile)
                 if self.gudrunFile.loadFile else "")
            )
            self.gudrunFile.setSaveLocation(dirname)
        self.mainWidget.processStarted()
        return True

    def checkPurge(self):
        if not self.purged and os.path.exists(
            os.path.join(
                self.gudrunFile.projectDir, "Purge", "purge_det.dat"
            )
        ):
            purgeResult = self.mainWidget.purgeOptionsMessageBox(
                "purge_det.dat found, but wasn't run in this session. "
                "Run Purge?",
            )
        elif not self.gudrunFile.purged:
            purgeResult = self.mainWidget.purgeOptionsMessageBox(
                "It looks like you may not have purged detectors. Run Purge?",
            )
        else:
            purgeResult = True
        return purgeResult

    def runPurge(self, finished=None, dialog=False) -> bool:
        if dialog:
            self.mainWidget.setControlsEnabled(False)
            purgeDialog = dialogs.PurgeDialog(gudrunFile, self)
            result = purgeDialog.widget.exec_()

            if (purgeDialog.cancelled or result == QDialogButtonBox.No):
                self.mainWidget.setControlsEnabled(True)
                return False

        if not self.prepareRun():
            self.mainWidget.processStopped()
            return False
        
        self.gudpy.purge = worker.PurgeWorker(self.gudpy.purgeFile)
        self.gudpy.purge.outputChanged.connect(self.outputSlots.setOutputStream)
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
                f"{self.detectors} detectors made it through the purge."
                " The acceptable minimum for "
                f"{self.gudpy.gudrunFile.instrument.name.name} is {thresh}"
            )
        self.mainWidget.goodDetectorsLabel.setText(
            f"Number of Good Detectors: {self.detectors}"
        )
        self.outputSlots.setOutput(
                self.gudpy.purge.stdout, "purge_det", gudrunFile=self.gudpy.gudrunFile
        )

    def runGudrun(self, iterator=None):
        if not self.prepareRun() or not self.checkPurge():
            self.mainWidget.processStopped()
            return False

        self.gudpy.gudrun = worker.GudrunWorker(self.gudpy.gudrunFile, iterator)
        self.gudpy.gudrun.outputChanged.connect(self.outputSlots.setOutputStream)
        self.gudpy.gudrun.progress.connect(self.updateProgressBar)
        self.gudpy.gudrun.finished.connect(self.gudrunFinished)

        self.gudpy.gudrun.start()

    def gudrunFinished(self, exitcode):
        if exitcode != 0:
            self.mainWidget.sendError(
                f"Gudrun failed with the following output: "
                f"\n{self.gudpy.gudrun.error}"
            )
            return

        if self.gudpy.iterator:
            self.outputIterations[
                f"{self.gudpy.iterator.iterationType} {self.gudpy.iterator.nCurrent}"
            ] = self.gudpy.gudrun.stdout
            self.sampleSlots.setSample(self.sampleSlots.sample)
            self.gudpy.iterator = None
    
        self.outputSlots.setOutput(
            self.gudpy.gudrun.stdout, "gudrun_dcs", gudrunFile=self.gudpy.gudrunFile
        )



 


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
            self.gudrunFile.save()
        sys.exit(0)
