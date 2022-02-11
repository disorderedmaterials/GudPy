import sys
from PySide6.QtCore import QFile
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
    TWEAK_FACTOR = 0
    THICKNESS = 1
    DENSITY = 2
    COMPOSITION_SINGLE_COMPONENT = 3
    COMPOSITION_TWO_COMPONENTS = 4


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
        self.tweak = Iterables.TWEAK_FACTOR
        self.performInelasticitySubtractions = False
        self.numberIterations = 1
        self.iterator = None
        self.cancelled = False
        self.text = ""
        self.components = [None, None]

    def handleTweakValuesChanged(self, state):
        """
        Slot for handling toggling iteration by tweaking.
        Caled when a toggled signal is emitted from the tweakButton.
        Updates the iteration configuration as such, and toggles the
        visibility of the tweakWidget as such.
        Parameters
        ----------
        state : int
            The new state of the tweakButton (1: True, 0: False).
        """
        self.tweakValues = state
        self.widget.tweakWidget.setVisible(state)

    def handlePerformInelasticitySubtractionsChanged(self, state):
        """
        Slot for handling toggling performing inelasticity subtractions.
        Caled when a toggled signal is emitted from the
        inelasticitySubtractionsButton.
        Updates the iteration configuration as such.
        Parameters
        ----------
        state : int
            The new state of the inelasticitySubtractionsButton
            (1: True, 0: False).
        """
        self.performInelasticitySubtractions = state

    def handleNumberIterationsChanged(self, value):
        """
        Slot for handling change in the number of iterations.
        Caled when a valueChanged signal is emitted from the
        noIterationsSpinBox.
        Updates the iteration configuration as such.
        Parameters
        ----------
        value : int
            The new value of the noIterationsSpinBox.
        """
        self.numberIterations = value

    def setTweakMode(self, state, tweakMode):
        if state:
            self.tweak = tweakMode
        if tweakMode == Iterables.COMPOSITION_SINGLE_COMPONENT:
            self.widget.componentBComboBox.setEnabled(not state)
        
    def iterate(self):
        """
        Iterate Gudrun with the specified configuration.
        Called when an accepted signal is emmited from the buttonBox.
        """
        if self.tweakValues:
            if self.tweak == Iterables.TWEAK_FACTOR:
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
            elif self.tweak == Iterables.THICKNESS:
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
            elif self.tweak == Iterables.DENSITY:
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
        elif self.performInelasticitySubtractions:
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

    def cancel(self):
        self.cancelled = True
        self.widget.close()

    def fillComboBoxA(self):
        self.widget.componentAComboBox.clear()
        for component in config.components.components:
            self.widget.componentAComboBox.addItem(component.name, component)

    def fillComboBoxB(self):
        self.widget.componentBComboBox.clear()
        for component in config.components.components:
            self.widget.componentBComboBox.addItem(component.name, component)    

    def componentAChanged(self, index):
        self.components[0] = self.widget.componentAComboBox.itemData(index)
        self.fillComboBoxB()
        self.self.widget.componentBComboBox.removeItem(index)

    def componentBChanged(self, index):
        self.components[1] = self.widget.componentBComboBox.itemData(index)
        self.fillComboBoxA()
        self.self.widget.componentAComboBox.removeItem(index)

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
        self.widget.tweakButton.toggled.connect(
            self.handleTweakValuesChanged
        )

        self.widget.tweakFactorButton.toggled.connect(
            lambda state: self.setTweakMode(state, Iterables.TWEAK_FACTOR)
        )

        self.widget.thicknessButton.toggled.connect(
            lambda state: self.setTweakMode(state, Iterables.THICKNESS)
        )
        self.widget.thicknessButton.setEnabled(config.geometry == Geometry.FLATPLATE)

        self.widget.densityButton.toggled.connect(
            lambda state: self.setTweakMode(state, Iterables.DENSITY)
        )

        self.widget.compositionButton.toggled.connect(
            self.widget.compositionIterationGroupBox.setVisible
        )

        self.widget.compositionIterationGroupBox.setVisible(False)

        self.widget.singleComponentButton.toggled.connect(
            lambda state: self.setTweakMode(state, Iterables.COMPOSITION_SINGLE_COMPONENT)
        )

        self.widget.twoComponentButton.toggled.connect(
            lambda state: self.setTweakMode(state, Iterables.COMPOSITION_TWO_COMPONENTS)
        )

        self.fillComboBoxA()
        self.fillComboBoxB()
        self.widget.componentBComboBox.removeItem(self.widget.componentAComboBox.currentIndex())

        self.widget.componentAComboBox.currentIndexChanged.connect(
            self.componentAChanged
        )

        self.widget.componentBComboBox.currentIndexChanged.connect(
            self.componentBChanged
        )

        self.widget.inelasticitySubtractionsButton.toggled.connect(
            self.handlePerformInelasticitySubtractionsChanged
        )
        self.widget.noIterationsSpinBox.valueChanged.connect(
            self.handleNumberIterationsChanged
        )
        self.widget.buttonBox.accepted.connect(
            self.iterate
        )
        self.widget.buttonBox.rejected.connect(
            self.cancel
        )

