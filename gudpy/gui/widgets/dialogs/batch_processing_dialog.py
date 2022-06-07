import os
from queue import Queue
import sys
from PySide6.QtWidgets import QDialog
from PySide6.QtCore import QFile
from PySide6.QtUiTools import QUiLoader

from core.run_batch_files import BatchProcessor
from core.enums import IterationModes


class BatchProcessingDialog(QDialog):

    def __init__(self, gudrunFile, parent):
        super(BatchProcessingDialog, self).__init__(parent=parent)
        self.gudrunFile = gudrunFile
        self.batchProcessor = None
        self.batchSize = 1
        self.maintainAverage = False
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
        self.widget.iterateByComboBox.addItem(
            IterationModes.THICKNESS.name, IterationModes.THICKNESS
        )
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
        self.widget.maintainAverageCheckBox.toggled.connect(
            self.maintainAverageToggled
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

    def maintainAverageToggled(self, state):
        self.maintainAverage = state

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
            batchSize=self.batchSize, headless=False,
            iterationMode=self.iterateBy,
            rtol=self.rtol if self.useRtol else 0.0,
            maxIterations=self.numberIterations,
            maintainAverage=self.maintainAverage
        ):
            self.queue.put(task)
            self.text = (
                f"Batch Processing "
                f"(IterationMode={self.iterateBy.name} "
                f"BatchSize={self.batchSize})"
            )
            self.widget.close()
