import os
from queue import Queue
import sys
from PySide6.QtWidgets import QDialog
from PySide6.QtCore import QFile
from PySide6.QtUiTools import QUiLoader

from core.enums import Geometry, IterationModes
from core import config
from core import iterators


class BatchProcessingDialog(QDialog):

    def __init__(self, parent):
        super(BatchProcessingDialog, self).__init__(parent=parent)
        self.iterator = None
        self.batchProcessor = None
        self.batchSize = 1
        self.stepSize = 1
        self.useSameStep = True
        self.iterate = False
        self.iterateBy = IterationModes.NONE
        self.useRtol = False
        self.rtol = 10.0
        self.numberIterations = 1
        self.propogateFirstBatch = False
        self.queue = Queue()
        self.loadUI()
        self.initComponents()

    def initComponents(self):
        self.widget.iterateByComboBox.addItem(
            IterationModes.TWEAK_FACTOR.name, IterationModes.TWEAK_FACTOR
        )
        if config.geometry == Geometry.FLATPLATE:
            self.widget.iterateByComboBox.addItem(
                IterationModes.THICKNESS.name, IterationModes.THICKNESS
            )
        elif config.geometry == Geometry.CYLINDRICAL:
            self.widget.iterateByComboBox.addItem(
                IterationModes.INNER_RADIUS.name, IterationModes.INNER_RADIUS
            )
            self.widget.iterateByComboBox.addItem(
                IterationModes.OUTER_RADIUS.name, IterationModes.OUTER_RADIUS
            )
        self.widget.iterateByComboBox.addItem(
            IterationModes.DENSITY.name, IterationModes.DENSITY
        )

        self.widget.batchSizeSpinBox.valueChanged.connect(
            self.batchSizeChanged
        )
        self.widget.useSameStepCheckBox.toggled.connect(
            self.useSameStepToggled
        )
        self.widget.stepSizeSpinBox.valueChanged.connect(
            self.stepSizeChanged
        )
        self.widget.iterateGroupBox.toggled.connect(
            self.iterateToggled
        )
        self.widget.iterateByComboBox.currentIndexChanged.connect(
            self.iterateByChanged
        )
        self.widget.convergenceToleranceCheckBox.toggled.connect(
            self.useConvergenceToleranceToggled
        )
        self.widget.convergenceToleranceSpinBox.valueChanged.connect(
            self.convergenceToleranceChanged
        )
        self.widget.maxIterationsSpinBox.valueChanged.connect(
            self.numberIterationsChanged
        )
        self.widget.propogateFirstBatchCheckBox.toggled.connect(
            self.propogateFirstBatchToggled
        )
        self.widget.processButton.clicked.connect(
            self.process
        )

    def loadUI(self):
        """
        Loads the UI file for the IterationDialog object.
        """
        if hasattr(sys, '_MEIPASS'):
            uifile = QFile(
                os.path.join(
                    sys._MEIPASS, "ui_files", "batchProcessingDialog.ui"
                )
            )
        else:
            current_dir = os.path.dirname(os.path.realpath(__file__))
            uifile = QFile(
                os.path.join(
                    current_dir, "..", "ui_files", "batchProcessingDialog.ui"
                )
            )
        loader = QUiLoader()
        self.widget = loader.load(uifile)

    def batchSizeChanged(self, value):
        self.batchSize = value
        self.widget.stepSizeSpinBox.setMaximum(value)
        if self.useSameStep:
            self.widget.stepSizeSpinBox.setValue(value)

    def useSameStepToggled(self, state):
        self.useSameStep = state
        self.widget.stepSizeSpinBox.setReadOnly(self.useSameStep)
        if self.useSameStep:
            self.widget.stepSizeSpinBox.setValue(self.batchSize)

    def stepSizeChanged(self, value):
        self.stepSize = value

    def iterateToggled(self, state):
        self.iterateBy = (
            self.widget.iterateByComboBox.currentData()
            if state
            else IterationModes.NONE
        )
        self.widget.convergenceToleranceSpinBox.setEnabled(self.useRtol)

    def iterateByChanged(self, index):
        self.iterateBy = self.widget.iterateByComboBox.itemData(index)

        if self.iterateBy == IterationModes.TWEAK_FACTOR:
            self.iterator = iterators.TweakFactor()
        elif self.iterateBy == IterationModes.THICKNESS:
            self.iterator = iterators.Thickness()
        elif self.iterateBy == IterationModes.INNER_RADIUS:
            self.iterator = iterators.Radius()
            self.iterator.setTargetRadius("inner")
        elif self.iterateBy == IterationModes.OUTER_RADIUS:
            self.iterator = iterators.Radius()
            self.iterator.setTargetRadius("outer")
        elif self.iterateBy == IterationModes.DENSITY:
            self.iterator = iterators.Density()

    def useConvergenceToleranceToggled(self, state):
        self.useRtol = state
        self.widget.convergenceToleranceSpinBox.setEnabled(state)

    def convergenceToleranceChanged(self, value):
        self.rtol = value

    def numberIterationsChanged(self, value):
        self.numberIterations = value

    def propogateFirstBatchToggled(self, state):
        self.propogateFirstBatch = state
