from src.scripts.utils import nthint
from PySide6.QtCore import QProcess
from src.gudrun_classes.file_library import GudPyFileLibrary
from src.gui.widgets.iteration_dialog import IterationDialog
import sys
from src.gudrun_classes.gudrun_file import GudrunFile
from src.gudrun_classes.exception import ParserException
from src.gudrun_classes import config
from PySide6.QtWidgets import (
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMessageBox,
    QProgressBar,
    QSizePolicy,
    QStatusBar,
    QWidget
)
from src.gui.widgets.purge_dialog import PurgeDialog
from src.gui.widgets.view_input import ViewInput
from src.gui.widgets.gudpy_tree import GudPyTreeView
from src.gui.widgets.gudpy_tables import GroupingParameterTable
from src.gui.widgets.gudpy_tables import BeamProfileTable
from src.gui.widgets.gudpy_tables import ResonanceTable
from src.gui.widgets.gudpy_tables import CompositionTable
from src.gui.widgets.gudpy_tables import ExponentialTable
from src.gudrun_classes.enums import Geometry
import os
from PySide6.QtUiTools import QUiLoader
from src.gui.widgets.beam_slots import BeamSlots
from src.gui.widgets.container_slots import ContainerSlots
from src.gui.widgets.instrument_slots import InstrumentSlots
from src.gui.widgets.normalisation_slots import NormalisationSlots
from src.gui.widgets.sample_background_slots import SampleBackgroundSlots
from src.gui.widgets.sample_slots import SampleSlots


class GudPyMainWindow(QMainWindow):
    """
    Class to represent the GudPyMainWindow. Inherits QMainWindow.
    This is the main window for the GudPy application.

    ...

    Attributes
    ----------
    gudrunFile : GudrunFile
        GudrunFile object currently associated with the application.
    clipboard : SampleBackground | Sample | Container
        Stores copied objects.
    Methods
    -------
    initComponents()
        Loads the UI file for the GudPyMainWindow
    loadInputFile_()
        Loads an input file.
    saveInputFile()
        Saves the current GudPy file.
    updateFromFile()
        Updates from the original input file.
    updateGeometries()
        Updates geometries across objects.
    updateCompositions()
        Updates compositions across objects
        Deletes the current object.
    exit_()
        Exits GudPy.
    """
    def __init__(self):
        """
        Constructs all the necessary attributes for the GudPyMainWindow object.
        Calls initComponents() to load the UI file.
        """
        super(GudPyMainWindow, self).__init__()
        self.gudrunFile = None
        self.initComponents()
        self.clipboard = None
        self.modified = False

    def initComponents(self):
        """
        Loads the UI file for the GudPyMainWindow.
        """
        current_dir = os.path.dirname(os.path.realpath(__file__))
        uifile = os.path.join(current_dir, "ui_files/mainWindow.ui")

        loader = QUiLoader()
        loader.registerCustomWidget(GudPyTreeView)
        loader.registerCustomWidget(GroupingParameterTable)
        loader.registerCustomWidget(BeamProfileTable)
        loader.registerCustomWidget(CompositionTable)
        loader.registerCustomWidget(ExponentialTable)
        loader.registerCustomWidget(ResonanceTable)
        self.mainWidget = loader.load(uifile)

        self.mainWidget.statusBar_ = QStatusBar(self)
        self.mainWidget.statusBarWidget = QWidget(self.mainWidget.statusBar_)
        self.mainWidget.statusBarLayout = QHBoxLayout(self.mainWidget.statusBarWidget)
        self.mainWidget.currentTaskLabel = QLabel(self.mainWidget.statusBarWidget)
        self.mainWidget.currentTaskLabel.setText("No task running.")
        self.mainWidget.currentTaskLabel.setSizePolicy(
            QSizePolicy(QSizePolicy.Minimum, QSizePolicy.Preferred)
        )
        self.mainWidget.progressBar = QProgressBar(self.mainWidget.statusBarWidget)
        self.mainWidget.progressBar.setSizePolicy(
            QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        )
        self.mainWidget.progressBar.setTextVisible(False)
        self.mainWidget.statusBarLayout.addWidget(self.mainWidget.currentTaskLabel)
        self.mainWidget.statusBarLayout.addWidget(self.mainWidget.progressBar)
        self.mainWidget.statusBarWidget.setLayout(self.mainWidget.statusBarLayout)
        self.mainWidget.statusBar_.addWidget(self.mainWidget.statusBarWidget)
        self.mainWidget.setStatusBar(self.mainWidget.statusBar_)

        self.mainWidget.setWindowTitle("GudPy")
        self.mainWidget.show()
        self.instrumentSlots = InstrumentSlots(self.mainWidget, self)
        self.beamSlots = BeamSlots(self.mainWidget, self)
        self.normalisationSlots = NormalisationSlots(self.mainWidget, self)
        self.sampleBackgroundSlots = SampleBackgroundSlots(
            self.mainWidget, self
        )
        self.sampleSlots = SampleSlots(self.mainWidget, self)
        self.containerSlots = ContainerSlots(self.mainWidget, self)
        self.mainWidget.runPurge.triggered.connect(
            self.runPurge_
        )
        self.mainWidget.runGudrun.triggered.connect(
            self.runGudrun_
        )
        self.mainWidget.iterateGudrun.triggered.connect(
            self.iterateGudrun_
        )
        self.mainWidget.save.triggered.connect(self.saveInputFile)

        self.mainWidget.saveAs.triggered.connect(self.saveInputFileAs)

        self.mainWidget.viewLiveInputFile.triggered.connect(
            lambda: ViewInput(self.gudrunFile, parent=self)
        )

        self.mainWidget.insertSampleBackground.triggered.connect(
            self.mainWidget.objectTree.insertSampleBackground
        )

        self.mainWidget.insertSample.triggered.connect(
            self.mainWidget.objectTree.insertSample
        )

        self.mainWidget.insertContainer.triggered.connect(
            self.mainWidget.objectTree.insertContainer
        )

        self.mainWidget.copy.triggered.connect(
            self.mainWidget.objectTree.copy
        )
        self.mainWidget.cut.triggered.connect(
            self.mainWidget.objectTree.cut
        )
        self.mainWidget.paste.triggered.connect(
            self.mainWidget.objectTree.paste
        )
        self.mainWidget.delete_.triggered.connect(
            self.mainWidget.objectTree.del_
        )

        self.mainWidget.loadInputFile.triggered.connect(
            self.loadInputFile_
        )
        self.mainWidget.objectStack.currentChanged.connect(
            self.updateComponents
        )

        self.mainWidget.exit.triggered.connect(self.exit_)
        # Hide the QStackedWidget and GudPyTreeView
        # Disabled the edit actions.
        self.mainWidget.insertSampleBackground.setDisabled(True)
        self.mainWidget.insertSample.setDisabled(True)
        self.mainWidget.insertContainer.setDisabled(True)
        self.mainWidget.copy.setDisabled(True)
        self.mainWidget.cut.setDisabled(True)
        self.mainWidget.paste.setDisabled(True)
        self.mainWidget.delete_.setDisabled(True)
        # Disable the run actions.
        self.mainWidget.runPurge.setDisabled(True)
        self.mainWidget.runGudrun.setDisabled(True)
        self.mainWidget.iterateGudrun.setDisabled(True)
        # Disable some file actions.
        self.mainWidget.viewLiveInputFile.setDisabled(True)
        self.mainWidget.save.setDisabled(True)
        self.mainWidget.saveAs.setDisabled(True)
        self.mainWidget.tabWidget.setVisible(False)

    def updateWidgets(self):
        self.mainWidget.gudrunFile = self.gudrunFile
        self.mainWidget.tabWidget.setVisible(True)
        self.instrumentSlots.setInstrument(self.gudrunFile.instrument)
        self.beamSlots.setBeam(self.gudrunFile.beam)
        self.normalisationSlots.setNormalisation(self.gudrunFile.normalisation)

        if len(self.gudrunFile.sampleBackgrounds):
            self.sampleBackgroundSlots.setSampleBackground(
                self.gudrunFile.sampleBackgrounds[0]
            )

            if len(self.gudrunFile.sampleBackgrounds[0].samples):
                self.sampleSlots.setSample(
                    self.gudrunFile.sampleBackgrounds[0].
                    samples[0]
                )

                if len(
                    self.gudrunFile.sampleBackgrounds[0].
                    samples[0].containers
                ):
                    self.containerSlots.setContainer(
                        self.gudrunFile.sampleBackgrounds[0]
                        .samples[0].containers[0]
                    )
        self.mainWidget.objectTree.buildTree(self.gudrunFile, self)

    def loadInputFile_(self):
        """
        Opens a QFileDialog to load an input file.
        """
        filename = QFileDialog.getOpenFileName(
            self, "Select Input file for GudPy", ".", "GudPy input (*.txt)"
        )[0]
        if filename:
            try:
                self.gudrunFile = GudrunFile(filename)
                self.updateWidgets()
            except ParserException as e:
                QMessageBox.critical(self, "GudPy Error", str(e))

    def saveInputFile(self):
        """
        Saves the current state of the input file.
        """
        self.gudrunFile.write_out(overwrite=True)
        self.setUnModified()

    def saveInputFileAs(self):
        """
        Saves the current state of the input file as...
        """
        filename = QFileDialog.getSaveFileName(
            self, "Save input file as..", "."
        )[0]
        if filename:
            self.gudrunFile.outpath = filename
            self.gudrunFile.write_out()
            self.setUnModified()

    def updateFromFile(self):
        """
        Calls initComponents() again, to update the UI.
        """
        self.initComponents()

    def updateGeometries(self):
        """
        Iteratively updates geometries of objects,
        where the Geometry is SameAsBeam.
        """
        if self.gudrunFile.normalisation.geometry == Geometry.SameAsBeam:
            self.normalisationSlots.widgetsRefreshing = True
            self.mainWidget.geometryInfoStack.setCurrentIndex(
                config.geometry.value
            )
            self.widgetsRefreshing = False
        for i, sampleBackground in enumerate(
            self.gudrunFile.sampleBackgrounds
        ):
            for j, sample in enumerate(sampleBackground.samples):
                self.gudrunFile.sampleBackgrounds[i].samples[j].geometry = (
                    config.geometry
                )
                for k in range(len(sample.containers)):
                    sample = self.gudrunFile.sampleBackgrounds[i].samples[j]
                    sample.containers[k].geometry = config.geometry

    def updateCompositions(self):
        """
        Iteratively shares compositions between objects,
        for copying and pasting compositions between eachother.
        """
        self.mainWidget.normalisationCompositionTable.farmCompositions()
        self.mainWidget.sampleCompositionTable.farmCompositions()
        self.mainWidget.containerCompositionTable.farmCompositions()

    def updateComponents(self):
        """
        Updates geometries and compositions.
        """
        self.updateGeometries()
        self.updateCompositions()

    def exit_(self):
        """
        Exits GudPy - questions user if they want to save on exit or not.
        """
        messageBox = QMessageBox
        result = (
            messageBox.question(
                self, '',
                "Do you want to save?", messageBox.No | messageBox.Yes
            )
        )

        if result == messageBox.Yes:
            self.gudrunFile.write_out(overwrite=True)
        sys.exit(0)

    def makeProc(self, cmd, slot):
        self.proc = QProcess()
        self.proc.readyReadStandardOutput.connect(slot)
        self.proc.started.connect(self.procStarted)
        self.proc.finished.connect(self.procFinished)
        self.proc.start(*cmd)

    def runPurge_(self):
        self.lockControls()
        purgeDialog = PurgeDialog(self.gudrunFile, self)
        purgeDialog.exec()
        purge = purgeDialog.purge_det
        if purgeDialog.cancelled:
            self.unlockControls()
        elif not purge:
            QMessageBox.critical(
                self, "GudPy Error", "Couldn't find purge_det binary."
            )
            self.unlockControls()
        else:
            self.makeProc(purge, self.progressPurge)

    def runGudrun_(self):
        self.lockControls()
        dcs = self.gudrunFile.dcs(path="gudpy.txt", headless=False)
        if not dcs:
            QMessageBox.critical(
                self, "GudPy Error",
                "Couldn't find gudrun_dcs binary."
            )
        elif not self.gudrunFile.purged:
            choice = QMessageBox.warning(
                self, "GudPy Warning",
                "It looks like you may not have purged detectors. Continue?",
                QMessageBox.Yes | QMessageBox.No
            )
            if choice == QMessageBox.No:
                self.unlockControls()
            else:
                self.gudrunFile.write_out()
                self.makeProc(dcs, self.progressDCS)
        else:
            self.gudrunFile.write_out()
            self.makeProc(dcs, self.progressDCS)

    def iterateGudrun_(self):
        self.lockControls()
        iterationDialog = IterationDialog(self.gudrunFile, self)
        iterationDialog.exec()
        iterate = iterationDialog.iterateCommand
        if iterationDialog.cancelled:
            self.unlockControls()
        elif not iterate:
            QMessageBox.critical(
                self, "GudPy Error",
                "Couldn't find gudrun_dcs binary."
            )
            self.unlockControls()
        else:
            self.iterableProc(
                iterate,
                iterationDialog.numberIterations,
                iterationDialog.text
            )

    def iterableProc(self, cmdGenerator, numIterations, text):
        self.numberIterations = numIterations
        self.text = text
        for i, cmd in enumerate(cmdGenerator):
            self.queueIterableProc(cmd, i)
        self.nextIterableProc()

    def queueIterableProc(self, cmd, iteration):
        self.queue = Queue()
        self.queue.put((cmd, iteration))

    def nextIterableProc(self):
        proc, i = self.queue.get()
        self.proc = QProcess()
        self.proc.started.connect(
            lambda: self.markIteration(self.text, i+1, self.numberIterations)
        )
        self.proc.finished.connect(
            lambda: self.progressIteration(i+1, self.numberIterations)
        )
        self.proc.start(*proc)

    def checkFilesExist_(self):
        result = GudPyFileLibrary(self.gudrunFile).checkFilesExist()
        if not all(r[0] for r in result):
            unresolved = "\n".join(r[1] for r in result if not r[0])
            QMessageBox.critical(
                self, "GudPy Error",
                f"Couldn't resolve some files!"
                f" Check that all paths are correct and try again."
                f"{unresolved}"
            )

    def setModified(self):
        if not self.modified:
            self.setWindowTitle(self.gudrunFile.path + " *")
            self.modified = True

    def setUnModified(self):
        if self.modified:
            self.setWindowTitle(self.gudrunFile.path)
            self.modified = False

    def lockControls(self):
        # Lock controls
        self.instrumentWidget.setDisabled(True)
        self.beamWidget.setDisabled(True)
        self.normalisationWidget.setDisabled(True)
        self.sampleWidget.basicWidget.setDisabled(True)
        self.sampleWidget.advancedWidget.setDisabled(True)
        self.containerWidget.setDisabled(True)
        self.sampleBackgroundWidget.setDisabled(True)
        self.objectTree.setContextDisabled()

        # Lock actions
        self.insertSampleBackground.setDisabled(True)
        self.insertSample.setDisabled(True)
        self.insertContainer.setDisabled(True)
        self.copy.setDisabled(True)
        self.cut.setDisabled(True)
        self.paste.setDisabled(True)
        self.delete_.setDisabled(True)
        self.runPurge.setDisabled(True)
        self.runGudrun.setDisabled(True)
        self.iterateGudrun.setDisabled(True)
        self.viewLiveInputFile.setDisabled(True)
        self.save.setDisabled(True)
        self.saveAs.setDisabled(True)
        self.loadInputFile.setDisabled(True)
        self.loadConfiguration.setDisabled(True)

    def unlockControls(self):
        # Unlock controls
        self.instrumentWidget.setEnabled(True)
        self.beamWidget.setEnabled(True)
        self.normalisationWidget.setEnabled(True)
        self.sampleWidget.basicWidget.setEnabled(True)
        self.sampleWidget.advancedWidget.setEnabled(True)
        self.containerWidget.setEnabled(True)
        self.sampleBackgroundWidget.setEnabled(True)
        self.objectTree.setContextEnabled()

        # Unlock actions
        self.insertSampleBackground.setEnabled(True)
        self.insertSample.setEnabled(True)
        self.insertContainer.setEnabled(True)
        self.copy.setEnabled(True)
        self.cut.setEnabled(True)
        self.paste.setEnabled(True)
        self.runPurge.setEnabled(True)
        self.runGudrun.setEnabled(True)
        self.iterateGudrun.setEnabled(True)
        self.viewLiveInputFile.setEnabled(True)
        self.save.setEnabled(True)
        self.saveAs.setEnabled(True)
        self.loadInputFile.setEnabled(True)
        self.loadConfiguration.setEnabled(True)

    def progressIncrement(self):
        data = self.proc.readAllStandardOutput()
        stdout = bytes(data).decode("utf8")
        print(stdout)
        ERROR_KWDS = [
            "does not exist",
            "error",
            "Error"
        ]
        if [KWD for KWD in ERROR_KWDS if KWD in stdout]:
            self.error = stdout
            return -1
        # Number of GudPy objects.
        markers = (
            config.NUM_GUDPY_CORE_OBJECTS
            + len(self.gudrunFile.sampleBackgrounds)
            + sum(
                [
                    sum(
                        [
                            len(sampleBackground.samples), *[
                                len(sample.containers)
                                for sample in sampleBackground.samples
                            ]
                        ]
                    ) for sampleBackground in self.gudrunFile.sampleBackgrounds
                ]
            )
        )
        stepSize = math.ceil(100/markers)
        progress = stepSize * sum(
            [
                stdout.count("Got to: INSTRUMENT"),
                stdout.count("Got to: BEAM"),
                stdout.count("Got to: NORMALISATION"),
                stdout.count("Got to: SAMPLE BACKGROUND"),
                stdout.count("Finished merging data for sample"),
                stdout.count("Got to: CONTAINER")
            ]
        )
        return progress

    def progressDCS(self):
        progress = self.progressIncrement()
        if progress == -1:
            QMessageBox.critical(
                self, "GudPy Error",
                f"An error occurred. See the following traceback"
                f" from gudrun_dcs\n{self.error}"
            )
        progress += self.progressBar.value()
        self.progressBar.setValue(progress if progress <= 100 else 100)

    def progressPurge(self):
        data = self.proc.readAllStandardOutput()
        stdout = bytes(data).decode("utf8")
        print(stdout)
        if "Total run time" in stdout:
            QMessageBox.warning(
                self, "GudPy Warning",
                f"{nthint(stdout, 0)} detectors made it through the purge."
            )
        elif "Error" in stdout or "error" in stdout:
            QMessageBox.critical(
                self, "GudPy Error",
                f"An error occurred. See the following traceback"
                f" from purge_det\n{stdout}"
            )

    def markIteration(self, iterType, iteration, numIterations):
        self.currentTaskLabel.setText(
            f"gudrun_dcs {iterType} {iteration}/{numIterations}"
        )

    def progressIteration(self, iteration, numIterations):
        progress = (
            math.ceil(self.progressIncrement() / numIterations)
        ) + self.progressBar.value()
        self.progressBar.setValue(progress if progress <= 100 else 100)
        if iteration == numIterations:
            self.procFinished()
        else:
            self.nextIterableProc()

    def procStarted(self):
        self.currentTaskLabel.setText(
            self.proc.program().split(os.path.sep)[-1]
        )

    def procFinished(self):
        self.proc = None
        self.unlockControls()
        self.currentTaskLabel.setText("No task running.")
        self.progressBar.setValue(0)
