import sys
from PySide6.QtCore import QFile
from PySide6.QtWidgets import QDialog
from PySide6.QtUiTools import QUiLoader
import os


class CompositionAcceptanceDialog(QDialog):

    def __init__(self, sample, parent):
        super(CompositionAcceptanceDialog, self).__init__(parent=parent)
        self.sample = sample
        self.accepted_ = False
        self.initComponents()

    def accepted(self):
        self.accepted_ = True
        self.widget.close()

    def initComponents(self):
        """
        Loads the UI file for the CompositionAcceptanceDialog object.
        """
        if hasattr(sys, '_MEIPASS'):
            uifile = QFile(
                os.path.join(
                    sys._MEIPASS, "ui_files",
                    "compositionAcceptanceDialog.ui"
                )
            )
        else:
            current_dir = os.path.dirname(os.path.realpath(__file__))
            uifile = QFile(
                os.path.join(
                    current_dir, "..", "ui_files",
                    "compositionAcceptanceDialog.ui"
                )
            )
        loader = QUiLoader()

        self.widget = loader.load(uifile)
        self.widget.titleLabel.setText(
            f"New composition for {self.sample.name}. Accept?"
        )
        self.widget.newRatioCompositionTable.makeModel(
            self.sample.composition.weightedComponents, self.sample
        )
        self.widget.buttonBox.accepted.connect(self.accepted)
