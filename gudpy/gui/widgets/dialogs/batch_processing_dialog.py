import os
from queue import Queue
import sys
from PySide6.QtWidgets import QDialog
from PySide6.QtCore import QFile
from PySide6.QtUiTools import QUiLoader

from core.run_batch_files import BatchProcessor
from core.enums import Geometry, IterationModes
from core import config


class BatchProcessingDialog(QDialog):

    def __init__(self, gudrunFile, parent):
        super(BatchProcessingDialog, self).__init__(parent=parent)
        self.gudrunFile = gudrunFile
        self.batchProcessor = None
        self.batchSize = 1
        self.stepSize = 1
        self.useSameStep = True
        self.iterate = False
        self.iterateBy = IterationModes.NONE
        self.useRtol = False
        self.rtol = 10.0
        self.numberIterations = 1
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

    def useConvergenceToleranceToggled(self, state):
        self.useRtol = state
        self.widget.convergenceToleranceSpinBox.setEnabled(state)

    def convergenceToleranceChanged(self, value):
        self.rtol = value

    def numberIterationsChanged(self, value):
        self.numberIterations = value

    def process(self):
        self.queue = Queue()
        self.batchProcessor = BatchProcessor(self.gudrunFile)
        for task in self.batchProcessor.process(
            batchSize=self.batchSize,
            stepSize=self.stepSize,
            headless=False,
            iterationMode=self.iterateBy,
            rtol=self.rtol if self.useRtol else 0.0,
            maxIterations=self.numberIterations
        ):
            self.queue.put(task)
            self.text = (
                f"Batch Processing "
                f"(IterationMode={self.iterateBy.name} "
                f"BatchSize={self.batchSize} "
                f"StepSize={self.stepSize})"
            )
            self.widget.close()
