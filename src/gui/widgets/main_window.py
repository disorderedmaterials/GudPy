from src.gudrun_classes.gudrun_file import GudrunFile, PurgeFile
from PyQt5.QtWidgets import (
    QAction,
    QHBoxLayout,
    QMainWindow,
    QMenu,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)
from PyQt5.QtGui import QResizeEvent
from src.gui.widgets.gudpy_tree import GudPyTreeView
from src.gui.widgets.view_input import ViewInput
from src.gui.widgets.sample_widget import SampleWidget
from src.gui.widgets.instrument_widget import InstrumentWidget
from src.gui.widgets.beam_widget import BeamWidget
from src.gui.widgets.sample_background_widget import SampleBackgroundWidget
from src.gui.widgets.container_widget import ContainerWidget
from src.gui.widgets.normalisation_widget import NormalisationWidget
import os
from PyQt5 import uic

class GudPyMainWindow(QMainWindow):
    def __init__(self):
        super(GudPyMainWindow, self).__init__()
        self.setWindowTitle("GudPy")
        self.show()
        self.initComponents()

    def initComponents(self):
        """
        Loads the UI file for the NormalisationWidget object,
        and then populates the child widgets with their
        corresponding data from the attributes of the Normalisation object.
        """
        current_dir = os.path.dirname(os.path.realpath(__file__))
        uifile = os.path.join(current_dir, "ui_files/mainWindow.ui")
        uic.loadUi(uifile, self)

        self.gudrunFile = GudrunFile("tests/TestData/NIMROD-water/water.txt")

        instrumentWidget = InstrumentWidget(self.gudrunFile.instrument, self)
        beamWidget = BeamWidget(self.gudrunFile.beam, self)
        normalisationWidget = NormalisationWidget(
            self.gudrunFile.normalisation, self
        )
        self.objectStack.addWidget(instrumentWidget)
        self.objectStack.addWidget(beamWidget)
        self.objectStack.addWidget(normalisationWidget)

        for sampleBackground in self.gudrunFile.sampleBackgrounds:
            sampleBackgroundWidget = SampleBackgroundWidget(
                sampleBackground, self
            )
            self.objectStack.addWidget(sampleBackgroundWidget)

            for sample in sampleBackground.samples:
                sampleWidget = SampleWidget(sample, self)
                self.objectStack.addWidget(sampleWidget)

                for container in sample.containers:
                    containerWidget = ContainerWidget(container, self)
                    self.objectStack.addWidget(containerWidget)

        self.objectTree.buildTree(self.gudrunFile, self.objectStack)


        self.runPurge.triggered.connect(lambda: PurgeFile(self.gudrunFile).purge())
        self.runGudrun.triggered.connect(lambda: self.gudrunFile.dcs(path="gudpy.txt"))

        self.viewInputFile.triggered.connect(
            lambda: ViewInput(self.gudrunFile, parent=self)
        )

    def updateFromFile(self):
        self.initComponents()

    def resizeEvent(self, a0: QResizeEvent) -> None:

        super().resizeEvent(a0)
