import os
from queue import Queue
import sys
from copy import deepcopy
from PySide6.QtWidgets import QDialog
from PySide6.QtCore import QFile, Qt
from PySide6.QtUiTools import QUiLoader

from core.enums import Geometry
from core import config
from core.iterators.composition import (
    CompositionIterator, calculateTotalMolecules
)
from core.iterators.density import DensityIterator
from core.iterators.inelasticity_subtraction import (
    InelasticitySubtraction
)
from core.iterators.radius import RadiusIterator
from core.iterators.thickness import ThicknessIterator
from core.iterators.tweak_factor import TweakFactorIterator


class IterationDialog(QDialog):

    def __init__(self, name, gudrunFile, parent):
        super(IterationDialog, self).__init__(parent=parent)
        self.gudrunFile = gudrunFile
        self.name = name
        self.numberIterations = 1
        self.iterator = None
        self.text = ""
        self.loadUI()
        self.initComponents()

    def initComponents(self):
        self.widget.numberIterationsSpinBox.valueChanged.connect(
            self.numberIterationsChanged
        )

        self.widget.iterateButton.clicked.connect(
            self.iterate
        )

    def loadUI(self):
        """
        Loads the UI file for the IterationDialog object.
        """
        if hasattr(sys, '_MEIPASS'):
            uifile = QFile(
                os.path.join(
                    sys._MEIPASS, "ui_files", f"{self.name}.ui"
                )
            )
        else:
            current_dir = os.path.dirname(os.path.realpath(__file__))
            uifile = QFile(
                os.path.join(
                    current_dir, "..", "ui_files", f"{self.name}.ui"
                )
            )
        loader = QUiLoader()
        self.widget = loader.load(uifile)

    def iterate(self):
        pass

    def numberIterationsChanged(self, value):
        self.numberIterations = value

    def enqueueTasks(self):
        self.queue = Queue()
        for _ in range(self.numberIterations):
            self.queue.put(
                self.iterator.gudrunFile.dcs(
                    path=os.path.join(
                        self.gudrunFile.instrument.GudrunInputFileDir,
                        "gudpy.txt"
                    ), headless=False)
            )
