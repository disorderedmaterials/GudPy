from PyQt5.QtWidgets import QDialog
from PyQt5 import uic
from PyQt5.QtCore import Qt
import os
from enum import Enum
from src.gudrun_classes.tweak_factor_iterator import TweakFactorIterator
from src.gudrun_classes.wavelength_subtraction_iterator import WavelengthSubtractionIterator
class Tweakables(Enum):
    TWEAK_FACTOR = 0

class IterationDialog(QDialog):

    def __init__(self, gudrunFile, parent):
        super(IterationDialog, self).__init__(parent=parent)
        self.gudrunFile = gudrunFile
        self.initComponents()
        self.tweakValues = True
        self.tweak = Tweakables.TWEAK_FACTOR
        self.performInelasticitySubtractions = False
        self.numberIterations = 0

    def handleTweakValuesChanged(self, state):
        self.tweakValues = state
        self.tweakWidget.setVisible(state)

    def handlePerformInelasticitySubtractionsChanged(self, state):
        self.performInelasticitySubtractions = state

    def handleNumberIterationsChanged(self, value):
        self.numberIterations = value

    def iterate(self):
        if self.tweakValues:
            if self.tweak == Tweakables.TWEAK_FACTOR:
                tweakFactorIterator = TweakFactorIterator(self.gudrunFile)
                tweakFactorIterator.iterate(self.numberIterations)
            else:
                pass
        elif self.performInelasticitySubtractions:
            wavelengthSubtractionIterator = WavelengthSubtractionIterator(self.gudrunFile)
            wavelengthSubtractionIterator.iterate(self.numberIterations)
        else:
            pass

    def initComponents(self):
        """
        Loads the UI file for the SampleWidget object.
        """
        current_dir = os.path.dirname(os.path.realpath(__file__))
        uifile = os.path.join(current_dir, "ui_files/iterationDialog.ui")
        uic.loadUi(uifile, self)
        self.tweakButton.toggled.connect(
            self.handleTweakValuesChanged
        )
        self.inelasticitySubtractionsButton.toggled.connect(
            self.handlePerformInelasticitySubtractionsChanged
        )
        self.noIterationsSpinBox.valueChanged.connect(
            self.handleNumberIterationsChanged
        )
        self.buttonBox.accepted.connect(
            self.iterate
        )
        self.buttonBox.rejected.connect(
            self.close
        )