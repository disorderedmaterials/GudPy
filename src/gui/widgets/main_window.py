# from src.gui.widgets.iteration_dialog import IterationDialog
import sys
from src.gudrun_classes.gudrun_file import GudrunFile, PurgeFile
from src.gudrun_classes.exception import ParserException
from src.gudrun_classes import config
from PySide6.QtWidgets import (
    QFileDialog,
    QMainWindow,
    QMessageBox,
)
from src.gui.widgets.view_input import ViewInput
# from src.gui.widgets.sample_widget import SampleWidget
# from src.gui.widgets.instrument_widget import InstrumentWidget
# from src.gui.widgets.beam_widget import BeamWidget
# from src.gui.widgets.sample_background_widget import SampleBackgroundWidget
# from src.gui.widgets.container_widget import ContainerWidget
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
        self.mainWidget.setWindowTitle("GudPy")
        self.mainWidget.show()
        self.instrumentSlots = InstrumentSlots(self.mainWidget, self)
        self.beamSlots = BeamSlots(self.mainWidget, self)
        self.normalisationSlots = NormalisationSlots(self.mainWidget, self)
        self.sampleBackgroundSlots = SampleBackgroundSlots(self.mainWidget, self)
        self.sampleSlots = SampleSlots(self.mainWidget, self)
        self.containerSlots = ContainerSlots(self.mainWidget, self)

        if not self.gudrunFile:
            # Hide the QStackedWidget and GudPyTreeView
            self.mainWidget.tabWidget.setVisible(False)
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

        else:
            self.mainWidget.setVisible(True)
            self.instrumentSlots.setInstrument(self.gudrunFile.instrument)
            self.beamSlots.setBeam(self.gudrunFile.beam)
            self.normalisationSlots.setNormalisation(self.gudrunFile.normalisation)
            if len(self.gudrunFile.sampleBackgrounds):
                self.sampleBackgroundSlots.setSampleBackground(self.gudrunFile.sampleBackgrounds[0])

                if len(self.gudrunFile.sampleBackgrounds[0].samples):
                    self.sampleSlots.setSample(self.gudrunFile.sampleBackgrounds[0].samples[0])

                    if len(self.gudrunFile.sampleBackgrounds[0].samples[0].containers):                                                         
                        self.containerSlots.setContainer(self.gudrunFile.sampleBackgrounds[0].samples[0].containers[0])
            self.mainWidget.objectTree.buildTree(self.gudrunFile, self)

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

            self.mainWidget.copy.triggered.connect(self.mainWidget.objectTree.copy)
            self.mainWidget.cut.triggered.connect(self.mainWidget.objectTree.cut)
            self.mainWidget.paste.triggered.connect(self.mainWidget.objectTree.paste)
            self.mainWidget.delete_.triggered.connect(self.mainWidget.objectTree.del_)

        self.mainWidget.loadInputFile.triggered.connect(self.loadInputFile_)
        # self.mainWidget.objectStack.currentChanged.connect(self.updateComponents)
        self.mainWidget.exit.triggered.connect(self.exit_)

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

    def runPurge_(self):
        result = PurgeFile(self.gudrunFile).purge()
        if not result:
            QMessageBox.critical(
                self, "GudPy Error", "Couldn't find purge_det binary."
            )

    def runGudrun_(self):
        result = self.gudrunFile.dcs(path="gudpy.txt")
        if not result:
            QMessageBox.critical(
                self, "GudPy Error",
                "Couldn't find gudrun_dcs binary and/or purge_det binary."
            )

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
