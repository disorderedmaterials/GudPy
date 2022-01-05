import os
from PySide6.QtCore import QFile
from PySide6.QtWidgets import QDialog
from PySide6.QtUiTools import QUiLoader
import sys


class ConfigurationDialog(QDialog):
    """
    Class to represent the ConfigurationDialog. Inherits QDialog.
    This is the dialog window opened when loading a configuration.

    ...

    Attributes
    ----------
    parent : QWidget
        Parent widget.
    Methods
    -------
    initComponents():
        Loads the UI file for the ConfigurationDialog
    """
    def __init__(self, parent):
        super(ConfigurationDialog, self).__init__(parent=parent)
        self.parent = parent
        self.initComponents()

    def initComponents(self):
        """
        Loads the UI file for the ViewInputDialog object.
        """
        if hasattr(sys, '_MEIPASS'):
            uifile = QFile(
                os.path.join(
                    sys._MEIPASS, "ui_files", "compositionDialog.ui"
                )
            )
        else:
            current_dir = os.path.dirname(os.path.realpath(__file__))
            uifile = QFile(
                os.path.join(
                    current_dir, "..", "ui_files", "configsDialog.ui"
                )
            )
        loader = QUiLoader()
        self.widget = loader.load(uifile)
        self.widget.setWindowTitle("Select Configuration")