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


class GudPyGUI(QtCore.QObject):
    def __init__(self):
        """
        Constructs all the necessary attributes for the GudPyMainWindow object.
        Calls initComponents() to load the UI file.
        """
        super().__init__()
        self.gudpy = gp.GudPy()

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
                self.sendErrorMesse(e)
            except IOError:
                self.sendError("Could not open file.")

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
            self.sendError(e)
        except IOError:
            self.sendError("Could not open file.")

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
            self.sendError(e)

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
                self.sendWarning("Do not modify project folder.")
                return
        self.gudpy.save(path=filename, format=fmt)
        self.setUnModified()

    """

    PROCESSES

    """

    def runPurge(self, finished=None, dialog=False) -> bool:
        if dialog:
            self.mainWidget.setControlsEnabled(False)
            purgeDialog = PurgeDialog(gudrunFile, self)
            result = purgeDialog.widget.exec_()

            if (purgeDialog.cancelled or result == QDialogButtonBox.No):
                self.mainWidget.setControlsEnabled(True)
                return False

        if not self.prepareRun():
            self.cleanupRun()
            return False

        self.worker = worker.PurgeWorker(gudrunFile)
        self.workerThread = QtGui.QThread()
        self.worker.moveToThread(self.workerThread)
        self.workerThread.started.connect(self.worker.purge)
        self.worker.started.connect(self.procStarted)
        self.worker.outputChanged.connect(self.progressPurge)
        self.worker.errorOccured.connect(self.sendError)
        self.worker.finished.connect(self.cleanupRun)
        self.worker.finished.connect(self.workerThread.quit)

        if finished:
            self.workerThread.finished.connect(finished)

        self.workerThread.start()

    def sendError(self, error: str):
        QtWidgets.QMessageBox.critical(
            self.mainWidget, "GudPy Error", str(error))

    def sendWarning(self, warning: str):
        QtWidgets.QMessageBox.warning(
            self.mainWidget,
            "GudPy Warning",
            warning
        )

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
