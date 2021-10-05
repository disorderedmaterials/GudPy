from PyQt5.QtWidgets import QDialog
from PyQt5 import uic
import os
from enum import Enum
from src.gudrun_classes.tweak_factor_iterator import TweakFactorIterator
from src.gudrun_classes.wavelength_subtraction_iterator import (
    WavelengthSubtractionIterator
)


class Tweakables(Enum):
    TWEAK_FACTOR = 0


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
    tweak : Tweakables
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
        self.tweak = Tweakables.TWEAK_FACTOR
        self.performInelasticitySubtractions = False
        self.numberIterations = 1
        self.iterateCommand = None
        self.cancelled = False
        self.text = ""

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
        self.tweakWidget.setVisible(state)

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

    def iterate(self):
        """
        Iterate Gudrun with the specified configuration.
        Called when an accepted signal is emmited from the buttonBox.
        """
        if self.tweakValues:
            if self.tweak == Tweakables.TWEAK_FACTOR:
                tweakFactorIterator = TweakFactorIterator(self.gudrunFile)
                self.iterateCommand = (
                    tweakFactorIterator.iterate(
                        self.numberIterations,
                        headless=False
                    )
                )
                self.text = "Tweak by tweak factor"
                self.close()
            else:
                pass
        elif self.performInelasticitySubtractions:
            wavelengthSubtractionIterator = WavelengthSubtractionIterator(
                self.gudrunFile
            )
            self.iterateCommand = (
                wavelengthSubtractionIterator.iterate(
                    self.numberIterations,
                    headless=False
                )
            )
            self.text = "Inelasticity subtractions"
            self.close()
        else:
            pass

    def cancel(self):
        self.cancelled = True
        self.close()

    def initComponents(self):
        """
        Loads the UI file for the IterationDialog object.
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
            self.cancel
        )
