import sys
from src.gudrun_classes.container import Container
from src.gudrun_classes.sample import Sample
from src.gudrun_classes.sample_background import SampleBackground
from src.gudrun_classes.gudrun_file import GudrunFile, PurgeFile
from src.gudrun_classes.exception import ParserException
from src.gudrun_classes import config
from PyQt5.QtWidgets import (
    QFileDialog,
    QMainWindow,
    QMessageBox,
)
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
from copy import deepcopy


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
    insertSampleBackground_(sampleBackground)
        Inserts a SampleBackground into the GudrunFile.
    insertSample_(sample)
        Inserts a Sample into the GudrunFile.
    insertContainer_(container)
        Inserts a Container into the GudrunFile.
    copy_()
        Copies the current object to the clipboard.
    cut_()
        Cuts the current object to the clipboard.
    del_()
        Deletes the current object.
    paste_()
        Pastes the clipboard back into the GudrunFile.
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

    def initComponents(self):
        """
        Loads the UI file for the GudPyMainWindow.
        """
        current_dir = os.path.dirname(os.path.realpath(__file__))
        uifile = os.path.join(current_dir, "ui_files/mainWindow.ui")
        uic.loadUi(uifile, self)
        self.setWindowTitle("GudPy")
        self.show()
        if self.gudrunFile:
            instrumentWidget = InstrumentWidget(
                self.gudrunFile.instrument, self
            )
            beamWidget = BeamWidget(self.gudrunFile.beam, self)
            normalisationWidget = NormalisationWidget(
                self.gudrunFile.normalisation, self
            )
            self.objectStack.addWidget(instrumentWidget)
            self.objectStack.addWidget(beamWidget)
            self.objectStack.addWidget(normalisationWidget)

            sampleBackgroundWidget = SampleBackgroundWidget(self)
            sampleWidget = SampleWidget(self)
            containerWidget = ContainerWidget(self)

            self.objectStack.addWidget(sampleBackgroundWidget)
            self.objectStack.addWidget(sampleWidget)
            self.objectStack.addWidget(containerWidget)

            if len(self.gudrunFile.sampleBackgrounds):
                sampleBackgroundWidget.setSampleBackground(
                    self.gudrunFile.sampleBackgrounds[0]
                )
                if len(self.gudrunFile.sampleBackgrounds[0].samples):
                    sampleWidget.setSample(
                        self.gudrunFile.sampleBackgrounds[0].samples[0]
                    )
                    if len(
                        self.gudrunFile.sampleBackgrounds[0]
                        .samples[0].containers
                    ):
                        containerWidget.setContainer(
                            self.gudrunFile.sampleBackgrounds[0]
                            .samples[0].containers[0]
                        )

            self.objectTree.buildTree(self.gudrunFile, self.objectStack)

            self.runPurge.triggered.connect(
                lambda: PurgeFile(self.gudrunFile).purge()
            )
            self.runGudrun.triggered.connect(
                lambda: self.gudrunFile.dcs(path="gudpy.txt")
            )

            self.save.triggered.connect(
                lambda: self.gudrunFile.write_out(overwrite=True)
            )

            self.saveAs.triggered.connect(self.saveInputFile)

            self.viewLiveInputFile.triggered.connect(
                lambda: ViewInput(self.gudrunFile, parent=self)
            )

            self.insertSampleBackground.triggered.connect(
                self.insertSampleBackground_
            )

            self.insertSample.triggered.connect(
                self.insertSample_
            )

            self.insertContainer.triggered.connect(
                self.insertContainer_
            )

            self.copy.triggered.connect(self.copy_)
            self.cut.triggered.connect(self.cut_)
            self.paste.triggered.connect(self.paste_)
            self.delete_.triggered.connect(self.del_)

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
        filename = QFileDialog.getSaveFileName(
            self, "Save input file as..", "."
        )[0]
        if filename:
            self.gudrunFile.outpath = filename
            self.gudrunFile.write_out()

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
        for i in range(self.objectStack.count()):
            target = self.objectStack.widget(i)
            if isinstance(target, NormalisationWidget):
                if target.normalisation.geometry == Geometry.SameAsBeam:
                    target.geometryInfoStack.setCurrentIndex(
                        config.geometry.value
                    )
            elif isinstance(target, (SampleWidget, ContainerWidget)):
                target.geometryComboBox.setCurrentIndex(config.geometry.value)

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

    def insertSampleBackground_(self, sampleBackground=None):
        """
        Inserts a SampleBackground into the GudrunFile.
        Inserts it into the tree.
        Parameters
        ----------
        sampleBackground : SampleBackground, optional
            SampleBackground object to insert.
        """
        if not sampleBackground:
            sampleBackground = SampleBackground()
        self.objectTree.insertRow(sampleBackground)

    def insertSample_(self, sample=None):
        """
        Inserts a Sample into the GudrunFile.
        Inserts it into the tree.
        Parameters
        ----------
        sample : Sample, optional
            Sample object to insert.
        """
        if not sample:
            sample = Sample()
            sample.name = "SAMPLE"  # for now, give a default name.
        self.objectTree.insertRow(sample)

    def insertContainer_(self, container=None):
        """
        Inserts a Container into the GudrunFile.
        Inserts it into the tree.
        Parameters
        ----------
        container : Container, optional
            Container object to insert.
        """
        if not container:
            container = Container()
            container.name = "CONTAINER"  # for now, give a default name.
        self.objectTree.insertRow(container)

    def copy_(self):
        """
        Copies the current object to the clipboard.
        """
        self.clipboard = None
        obj = self.objectTree.currentObject()
        if isinstance(obj, (SampleBackground, Sample, Container)):
            self.clipboard = deepcopy(obj)

    def del_(self):
        """
        Deletes the current object.
        """
        self.objectTree.removeRow()

    def cut_(self):
        """
        Copies the current object to the clipboard, and removes
        the object from the tree.
        """
        self.copy_()
        if self.clipboard:
            self.objectTree.removeRow()

    def paste_(self):
        """
        Pastes the contents of the clipboard back into the GudrunFile.
        """
        if isinstance(self.clipboard, SampleBackground):
            self.insertSampleBackground_(
                sampleBackground=deepcopy(self.clipboard)
            )
        elif isinstance(self.clipboard, Sample):
            self.insertSample_(sample=deepcopy(self.clipboard))
        elif isinstance(self.clipboard, Container):
            self.insertContainer_(container=deepcopy(self.clipboard))

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
