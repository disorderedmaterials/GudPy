import os
import sys
from PySide6.QtWidgets import QDialog
from PySide6.QtCore import QFile
from PySide6.QtUiTools import QUiLoader

from core.enums import IterationModes

class BatchProcessingDialog(QDialog):

    def __init__(self, gudrunFile, parent):
        super(BatchProcessingDialog, self).__init__(parent=parent)
        self.gudrunFile = gudrunFile
        self.batchSize = 1
        self.iterate = False
        self.iterateBy = IterationModes.NONE
        self.useRtol = True
        self.rtol = 10.0
        self.numberIterations = 1
        self.loadUI()
        self.initComponents()

    def initComponents(self):
        
        self.widget.batchSizeSpinBox.valueChanged.connect(self.batchSizeChanged)
        self.widget.iterateGroupBox.toggled.connect(self.iterateToggled)
        self.widget.iterateByComboBox.currentIndexChanged.connect(self.iterateByChanged)
        self.widget.convergenceToleranceSpinBox.valueChanged.connect(self.convergenceToleranceChanged)
        self.widget.maxIterationsSpinBox.valueChanged.connect(self.numberIterationsChanged)

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

    def loadUI(self):
        """
        Loads the UI file for the IterationDialog object.
        """
        if hasattr(sys, '_MEIPASS'):
            uifile = QFile(
                os.path.join(
                    sys._MEIPASS, "ui_files", f"batchProcessingDialog.ui"
                )
            )
        else:
            current_dir = os.path.dirname(os.path.realpath(__file__))
            uifile = QFile(
                os.path.join(
                    current_dir, "..", "ui_files", f"batchProcessingDialog.ui"
                )
            )
        loader = QUiLoader()
        self.widget = loader.load(uifile)

    def batchSizeChanged(self, value):
        self.batchSize = value
    
    def iterateToggled(self, state):
        self.iterateBy = self.widget.iterateByComboBox.currentData() if state else IterationModes.NONE
    
    def iterateByChanged(self, index):
        self.iterateBy = self.widget.iterateByComboBox.itemData(index)
    
    def useConvergenceToleranceToggled(self, state):
        self.useRtol = state
        self.widget.convergenceToleranceSpinBox.setEnabled(state)
    
    def convergenceToleranceChanged(self, value):
        self.rtol = value

    def numberIterationsChanged(self, value):
        self.numberIterations = value
