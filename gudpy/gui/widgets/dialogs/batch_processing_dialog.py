import os
from queue import Queue
import sys
from PySide6.QtWidgets import QDialog
from PySide6.QtCore import QFile
from PySide6.QtUiTools import QUiLoader


class BatchProcessingDialog(QDialog):

    def __init__(self, gudrunFile, parent):
        super(BatchProcessingDialog, self).__init__(parent=parent)
        self.gudrunFile = gudrunFile
        self.loadUI()
        self.initComponents()

    def initComponents(self):
        pass

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