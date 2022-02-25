from abc import abstractmethod
import sys
from PySide6.QtCore import QFile, Qt
from PySide6.QtWidgets import QDialog
from PySide6.QtUiTools import QUiLoader
import os
from enum import Enum
from src.gudrun_classes import config
from src.gudrun_classes.enums import Geometry
from src.gudrun_classes.tweak_factor_iterator import TweakFactorIterator
from src.gudrun_classes.wavelength_subtraction_iterator import (
    WavelengthSubtractionIterator
)
from src.gudrun_classes.thickness_iterator import ThicknessIterator
from src.gudrun_classes.density_iterator import DensityIterator

from queue import Queue


class Iterables(Enum):
    WAVELENGTH = 0
    TWEAK_FACTOR = 1
    THICKNESS = 2
    DENSITY = 3
    COMPOSITION_SINGLE_COMPONENT = 4
    COMPOSITION_TWO_COMPONENTS = 5


class IterationDialog(QDialog):
    """
    Class to represent the IterationDialog. Inherits QDialog.
    This is the dialog window opened when a user wishes to iterate Gudrun.

    ...

    Attributes
    ----------
    gudrunFile : GudrunFile
        GudrunFile object currently associated with the application.
    tweakValues: bool
        Should iteration by tweaking be performed?
    tweak : Iterables
        Attribute to tweak by.
    performInelasticitySubtractions : bool
        Should iteration by inelasticity subtractions be performed?
    numberIterations : int
        Number of iterations to perform.
    Methods
    -------
    initComponents()
        Loads the UI file for the IterationDialog
    handleTweakValuesChanged(state)
        Slot for handling toggling iteration by tweaking.
    handlePerformInelasticitySubtractionsChanged(state)
        Slot for handling toggling performing inelasticity subtractions.
    handleNumberIterationsChanged(value)
        Slot for handling change in the number of iterations.
    iterate()
        Iterate Gudrun with the specified configuration.
    """
    def __init__(self, gudrunFile, parent):
        super(IterationDialog, self).__init__(parent=parent)
        self.gudrunFile = gudrunFile
        self.initComponents()
        self.tweakValues = True
        self.iterateBy = Iterables.TWEAK_FACTOR
        self.numberIterations = 1
        self.rtol = 0.
        self.iterator = None
        self.cancelled = False
        self.text = ""
        self.components = [None, None]
        
    def iterate(self):
        """
        Iterate Gudrun with the specified configuration.
        Called when an accepted signal is emmited from the buttonBox.
        """
        if self.iterateBy == Iterables.TWEAK_FACTOR:
            self.iterator = TweakFactorIterator(self.gudrunFile)
            self.queue = Queue()
            for _ in range(self.numberIterations):
                self.queue.put(
                    self.gudrunFile.dcs(
                        path=os.path.join(
                            self.gudrunFile.instrument.GudrunInputFileDir,
                            "gudpy.txt"
                        ), headless=False)
                )
            self.text = "Tweak by tweak factor"
            self.widget.close()
        elif self.iterateBy == Iterables.THICKNESS:
            self.iterator = ThicknessIterator(self.gudrunFile)
            self.queue = Queue()
            for _ in range(self.numberIterations):
                self.queue.put(
                    self.gudrunFile.dcs(
                        path=os.path.join(
                            self.gudrunFile.instrument.GudrunInputFileDir,
                            "gudpy.txt"
                        ), headless=False)
                )
            self.text = "Tweak by thickness"
            self.widget.close()
        elif self.iterateBy == Iterables.DENSITY:
            self.iterator = DensityIterator(self.gudrunFile)
            self.queue = Queue()
            for _ in range(self.numberIterations):
                self.queue.put(
                    self.gudrunFile.dcs(
                        path=os.path.join(
                            self.gudrunFile.instrument.GudrunInputFileDir,
                            "gudpy.txt"
                        ), headless=False)
                )
            self.text = "Tweak by density"
            self.widget.close()
        elif self.iterateBy == Iterables.WAVELENGTH:
            self.iterator = WavelengthSubtractionIterator(
                self.gudrunFile
            )
            self.queue = Queue()
            for _ in range(self.numberIterations):
                self.queue.put(self.gudrunFile.dcs(
                    path="gudpy.txt", headless=False)
                )
                self.queue.put(
                    self.gudrunFile.dcs(
                        path=os.path.join(
                            self.gudrunFile.instrument.GudrunInputFileDir,
                            "gudpy.txt"
                        ), headless=False)
                )
            self.text = "Inelasticity subtractions"
            self.widget.close()
        else:
            pass

    def tabChanged(self, index):
        tabMap = {
            0: (self.widget.inelasticityIterationsSpinBox.value(), Iterables.WAVELENGTH),
            1: (self.widget.tweakFactorIterationsSpinBox.value(), Iterables.TWEAK_FACTOR),
            2: (self.widget.densityIterationsSpinBox.value(), Iterables.DENSITY),
            3: (
                self.widget.compositionIterationsSpinBox.value(),
                Iterables.COMPOSITION_SINGLE_COMPONENT
                if self.widget.singleComponentCheckBox.isChecked()
                else Iterables.COMPOSITION_TWO_COMPONENTS
            )
        }

        self.numberIterations, self.iterateBy = tabMap[index]

    def numberIterationsChanged(self, value):
        self.numberIterations = value

    def loadFirstComponentsComboBox(self):
        self.widget.firstComponentComboBox.clear()
        for component in config.components.components:
            self.widget.firstComponentComboBox.addItem(component.name, component)
    
    def loadSecondComponentsComboBox(self):
        self.widget.secondComponentComboBox.clear()
        for component in config.components.components:
            self.widget.secondComponentComboBox.addItem(component.name, component)

    def firstComponentChanged(self, index):
        self.components[0] = self.widget.firstComponentComboBox.itemData(index)
        other = self.widget.secondComponentComboBox.model().item(index)
        self.setItemDisabled(
            self.widget.secondComponentComboBox,
            other
        )

    def secondComponentChanged(self, index):
        self.components[1] = self.widget.secondComponentComboBox.itemData(index)
        other = self.widget.firstComponentComboBox.model().item(index)
        self.setItemDisabled(
            self.widget.firstComponentComboBox,
            other
        )

    def compositionRtolChanged(self, value):
        self.rtol = value

    def enableItems(self, comboBox):
        for i in range(len(config.components.components)):
            comboBox.model().item(i).setFlags(comboBox.model().item(i).flags() | Qt.ItemIsEnabled)

    def setItemDisabled(self, comboBox, item):
        self.enableItems(comboBox)
        item.setFlags(item.flags() & ~Qt.ItemIsEnabled)

    def toggleUseSingleComponent(self, state):
        self.widget.secondComponentComboBox.setEnabled(not state)
        if state:
            self.enableItems(self.widget.firstComponentComboBox)
        else:
            other = self.widget.firstComponentComboBox.model().item(self.widget.firstComponentComboBox.currentIndex())            
            self.setItemDisabled(
                self.widget.secondComponentComboBox,
                other
            )
            if self.widget.firstComponentComboBox.currentIndex() == self.widget.secondComponentComboBox.currentIndex():
                self.widget.secondComponentComboBox.setCurrentIndex(0)
            other = self.widget.secondComponentComboBox.model().item(self.widget.secondComponentComboBox.currentIndex())            
            self.setItemDisabled(
                self.widget.firstComponentComboBox,
                other
            )

    def initComponents(self):
        """
        Loads the UI file for the IterationDialog object.
        """
        if hasattr(sys, '_MEIPASS'):
            uifile = QFile(
                os.path.join(
                    sys._MEIPASS, "ui_files", "iterationDialog.ui"
                )
            )
        else:
            current_dir = os.path.dirname(os.path.realpath(__file__))
            uifile = QFile(
                os.path.join(
                    current_dir, "..", "ui_files", "iterationDialog.ui"
                )
            )
        loader = QUiLoader()
        self.widget = loader.load(uifile)

        self.widget.iterationTabs.currentChanged.connect(
            self.tabChanged
        )

        self.widget.inelasticityIterationsSpinBox.valueChanged.connect(self.numberIterationsChanged)
        self.widget.tweakFactorIterationsSpinBox.valueChanged.connect(self.numberIterationsChanged)
        self.widget.densityIterationsSpinBox.valueChanged.connect(self.numberIterationsChanged)
        self.widget.compositionIterationsSpinBox.valueChanged.connect(self.numberIterationsChanged)

        self.loadFirstComponentsComboBox()
        self.loadSecondComponentsComboBox()

        self.widget.firstComponentComboBox.currentIndexChanged.connect(self.firstComponentChanged)
        self.widget.secondComponentComboBox.currentIndexChanged.connect(self.secondComponentChanged)

        self.widget.compositionToleranceSpinBox.valueChanged.connect(self.compositionRtolChanged)
        self.widget.singleComponentCheckBox.toggled.connect(self.toggleUseSingleComponent)

        self.widget.iterateInelasticityPushButton.clicked.connect(self.iterate)
        self.widget.iterateTweakFactorPushButton.clicked.connect(self.iterate)
        self.widget.iterateDensityButton.clicked.connect(self.iterate)
        self.widget.iterateCompositionButton.clicked.connect(self.iterate)
