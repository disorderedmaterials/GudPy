import sys
from PySide6.QtCore import QFile
from PySide6.QtWidgets import QDialog
from PySide6.QtUiTools import QUiLoader
import os


class ExportDialog(QDialog):
    """
    Class to represent the ExportDialog. Inherits QDialog.
    This is the dialog window opened when a user wishes to export data.

    ...

    Attributes
    ----------
    None
    Methods
    -------
    initComponents()
        Loads the UI file for the MissingFilesDialog.
    """
    def __init__(self, parent):
        super(ExportDialog, self).__init__(parent=parent)
        self.initComponents()

    def initComponents(self):
        """
        Loads the UI file for the ExportDialog object.
        """
        if hasattr(sys, '_MEIPASS'):
            uifile = QFile(
                os.path.join(
                    sys._MEIPASS, "ui_files", "exportDialog.ui"
                )
            )
        else:
            current_dir = os.path.dirname(os.path.realpath(__file__))
            uifile = QFile(
                os.path.join(
                    current_dir, "..", "ui_files", "exportDialog.ui"
                )
            )
        loader = QUiLoader()
        self.widget = loader.load(uifile)

