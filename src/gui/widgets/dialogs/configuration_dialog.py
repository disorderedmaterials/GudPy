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
        self.configuration = None
        self.cancelled = False
        self.initComponents()
        self.loadConfigurations()

    def initComponents(self):
        """
        Loads the UI file for the ViewInputDialog object.
        """
        if hasattr(sys, '_MEIPASS'):
            uifile = QFile(
                os.path.join(
                    sys._MEIPASS, "ui_files", "configsDialog.ui"
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
        self.widget.configList.currentItemChanged.connect(
            self.setConfiguration
        )

        self.widget.buttonBox.rejected.connect(
            self.cancel
        )
        self.widget.buttonBox.accepted.connect(
            self.widget.accept
        )

    def loadConfigurations(self):
        targetDir = (
            os.path.join(sys._MEIPASS, "bin", "configs")
            if hasattr(sys, "_MEIPASS")
            else os.path.join("bin", "configs")
        )
        self.widget.configList.addItems(
            [
                f for f in os.listdir(targetDir)
                if f.endswith('.config')
            ]
        )
        self.widget.configList.setCurrentRow(0)

    def setConfiguration(self, _prev, _curr):
        targetDir = (
            os.path.join(sys._MEIPASS, "bin", "configs")
            if hasattr(sys, "_MEIPASS")
            else os.path.join("bin", "configs")
        )
        self.configuration = os.path.abspath(
            os.path.join(
                targetDir,
                self.widget.configList.currentItem().text()
            )
        )
        self.widget.configDescriptionTextEdit.setText(
            open(self.configuration, "r").readlines()[-1]
        )

    def cancel(self):
        self.cancelled = True
        self.widget.reject()
