import os
from queue import Queue
import sys

from PySide6.QtWidgets import QDialog
from PySide6.QtCore import QFile
from PySide6.QtUiTools import QUiLoader


class PeriodDialog(QDialog):

    def __init__(self, gudrunFile, parent):
        super(PeriodDialog, self).__init__(parent=parent)
        self.gudrunFile = gudrunFile
        self.cancelled = False
        self.loadUI()
        self.initComponents()

    def initComponents(self):
        self.widget.pulseTableView.makeModel(
            self.gudrunFile.modex.period.pulses, self.gudrunFile.modex
        )
        self.widget.addPulseButton.clicked.connect(
            self.widget.pulseTableView.insertRow
        )

    def cancel(self):
        self.cancelled = True
        self.widget.close()

    def loadUI(self):
        """
        Loads the UI file for the PeriodDialog object.
        """
        if hasattr(sys, '_MEIPASS'):
            uifile = QFile(
                os.path.join(
                    sys._MEIPASS, "ui_files", "periodDialog.ui"
                )
            )
        else:
            current_dir = os.path.dirname(os.path.realpath(__file__))
            uifile = QFile(
                os.path.join(
                    current_dir, "..", "ui_files", "periodDialog.ui"
                )
            )
        loader = QUiLoader()
        self.widget = loader.load(uifile)
        self.widget.buttonBox.accepted.connect(
            self.widget.close
        )
        self.widget.buttonBox.rejected.connect(
            self.cancel
        )