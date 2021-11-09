import os
from PySide6.QtCore import QFile
from PySide6.QtWidgets import QDialog
from PySide6.QtUiTools import QUiLoader
import sys


class CompositionDialog(QDialog):
    """
    Class to represent the CompositionDialog. Inherits QDialog.
    This is the dialog window opened when a user wishes to
    view the live input file.

    ...

    Attributes
    ----------
    parent : QWidget
        Parent widget.
    Methods
    -------
    initComponents():
        Loads the UI file for the CompositionDialog
    """
    def __init__(self, parent, component):
        super(CompositionDialog, self).__init__(parent=parent)
        self.component = component
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
                    current_dir, "..", "ui_files", "compositionDialog.ui"
                )
            )
        loader = QUiLoader()
        self.widget = loader.load(uifile)
        self.widget.setWindowTitle("Compositon")

        self.widget.infoLabel.setText(
            f"{self.component.name} looks like a chemical formula.\n"
            f"Do you want the atomic composition resolved automatically?"
            f" It looks like:\n"
        )

        self.widget.compositionLookAheadTable.makeModel(
            self.component.parse(persistent=False), farm=False
        )
