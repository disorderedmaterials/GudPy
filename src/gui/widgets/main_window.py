from PyQt5.QtCore import QProcess
from src.gui.widgets.iteration_dialog import IterationDialog
import sys
from src.gudrun_classes.gudrun_file import GudrunFile
from src.gudrun_classes.exception import ParserException
from src.gudrun_classes import config
from PyQt5.QtWidgets import (
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
from src.gui.widgets.sample_widget import SampleWidget
from src.gui.widgets.instrument_widget import InstrumentWidget
from src.gui.widgets.beam_widget import BeamWidget
from src.gui.widgets.sample_background_widget import SampleBackgroundWidget
from src.gui.widgets.container_widget import ContainerWidget
from src.gui.widgets.normalisation_widget import NormalisationWidget
from src.gudrun_classes.enums import Geometry
import os
from PyQt5 import uic
import math


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
        Updates compositions across objects.
    updateComponents()
        Updates geometries and compositions.
    del_()
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
        uic.loadUi(uifile, self)

        self.statusBar_ = QStatusBar(self)
        self.statusBarWidget = QWidget(self.statusBar_)
        self.statusBarLayout = QHBoxLayout(self.statusBarWidget)
        self.currentTaskLabel = QLabel(self.statusBarWidget)
        self.currentTaskLabel.setText("No task running.")
        self.currentTaskLabel.setSizePolicy(
            QSizePolicy(QSizePolicy.Minimum, QSizePolicy.Preferred)
        )
        self.progressBar = QProgressBar(self.statusBarWidget)
        self.progressBar.setSizePolicy(
            QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        )
        self.progressBar.setTextVisible(False)
        self.statusBarLayout.addWidget(self.currentTaskLabel)
        self.statusBarLayout.addWidget(self.progressBar)
        self.statusBarWidget.setLayout(self.statusBarLayout)
        self.statusBar_.addWidget(self.statusBarWidget)
        self.setStatusBar(self.statusBar_)
        self.setWindowTitle("GudPy")
        self.show()

        if not self.gudrunFile:
            # Hide the QStackedWidget and GudPyTreeView
            self.objectStack.setVisible(False)
            self.objectTree.setVisible(False)
            # Disabled the edit actions.
            self.insertSampleBackground.setDisabled(True)
            self.insertSample.setDisabled(True)
            self.insertContainer.setDisabled(True)
            self.copy.setDisabled(True)
            self.cut.setDisabled(True)
            self.paste.setDisabled(True)
            self.delete_.setDisabled(True)
            # Disable the run actions.
            self.runPurge.setDisabled(True)
            self.runGudrun.setDisabled(True)
            self.iterateGudrun.setDisabled(True)
            # Disable some file actions.
            self.viewLiveInputFile.setDisabled(True)
            self.save.setDisabled(True)
            self.saveAs.setDisabled(True)

        else:

            self.setWindowTitle(self.gudrunFile.path)
            self.instrumentWidget = InstrumentWidget(
                self.gudrunFile.instrument, self
            )
            self.beamWidget = BeamWidget(
                self.gudrunFile.beam, self
            )
            self.normalisationWidget = NormalisationWidget(
                self.gudrunFile.normalisation, self
            )

            self.objectStack.addWidget(self.instrumentWidget)
            self.objectStack.addWidget(self.beamWidget)
            self.objectStack.addWidget(self.normalisationWidget)

            self.sampleBackgroundWidget = SampleBackgroundWidget(self)
            self.sampleWidget = SampleWidget(self)
            self.containerWidget = ContainerWidget(self)

            self.objectStack.addWidget(self.sampleBackgroundWidget)
            self.objectStack.addWidget(self.sampleWidget)
            self.objectStack.addWidget(self.containerWidget)

            if len(self.gudrunFile.sampleBackgrounds):
                self.sampleBackgroundWidget.setSampleBackground(
                    self.gudrunFile.sampleBackgrounds[0]
                )
                if len(self.gudrunFile.sampleBackgrounds[0].samples):
                    self.sampleWidget.setSample(
                        self.gudrunFile.sampleBackgrounds[0].samples[0]
                    )
                    if len(
                        self.gudrunFile.sampleBackgrounds[0]
                        .samples[0].containers
                    ):
                        self.containerWidget.setContainer(
                            self.gudrunFile.sampleBackgrounds[0]
                            .samples[0].containers[0]
                        )

            self.objectTree.buildTree(self.gudrunFile, self.objectStack)

            self.runPurge.triggered.connect(
                self.runPurge_
            )
            self.runGudrun.triggered.connect(
                self.runGudrun_
            )
            self.iterateGudrun.triggered.connect(
                self.iterateGudrun_
            )
            self.save.triggered.connect(self.saveInputFile)

            self.saveAs.triggered.connect(self.saveInputFileAs)

            self.viewLiveInputFile.triggered.connect(
                lambda: ViewInput(self.gudrunFile, parent=self)
            )

            self.insertSampleBackground.triggered.connect(
                self.objectTree.insertSampleBackground
            )

            self.insertSample.triggered.connect(
                self.objectTree.insertSample
            )

            self.insertContainer.triggered.connect(
                self.objectTree.insertContainer
            )

            self.copy.triggered.connect(self.objectTree.copy)
            self.cut.triggered.connect(self.objectTree.cut)
            self.paste.triggered.connect(self.objectTree.paste)
            self.delete_.triggered.connect(self.objectTree.del_)

        self.loadInputFile.triggered.connect(self.loadInputFile_)
        self.objectStack.currentChanged.connect(self.updateComponents)
        self.exit.triggered.connect(self.exit_)

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
            except ParserException as e:
                QMessageBox.critical(self, "GudPy Error", str(e))
            self.initComponents()

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
            self.normalisationWidget.widgetsRefreshing = True
            self.normalisationWidget.geometryInfoStack.setCurrentIndex(
                config.geometry.value
            )
            self.normalisationWidget.widgetsRefreshing = False
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
        for i in range(self.objectStack.count()):
            target = self.objectStack.widget(i)
            if isinstance(target, NormalisationWidget):
                target.normalisationCompositionTable.farmCompositions()
            elif isinstance(target, SampleWidget):
                target.sampleCompositionTable.farmCompositions()
            elif isinstance(target, ContainerWidget):
                target.containerCompositionTable.farmCompositions()

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
        iterationDialog = IterationDialog(self.gudrunFile, self)
        iterationDialog.show()

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

    def progressDCS(self):
        data = self.proc.readAllStandardOutput()
        stdout = bytes(data).decode("utf8")
        print(stdout)
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
        ) + self.progressBar.value()
        self.progressBar.setValue(progress if progress <= 100 else 100)

    def progressPurge(self):
        pass
        data = self.proc.readAllStandardOutput()
        stdout = bytes(data).decode("utf8")
        print(stdout)

    def procStarted(self):
        self.currentTaskLabel.setText(
            self.proc.program().split(os.path.sep)[-1]
        )

    def procFinished(self):
        self.proc = None
        self.unlockControls()
        self.currentTaskLabel.setText("No task running.")
