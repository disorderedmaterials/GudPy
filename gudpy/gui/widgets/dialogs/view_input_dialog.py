import os
import sys
from PySide6.QtCore import QFile
from PySide6.QtWidgets import QDialog
from PySide6.QtUiTools import QUiLoader


class ViewInputDialog(QDialog):
    """
    Class to represent the ViewInputDialog. Inherits QDialog.
    This is the dialog window opened when a user wishes to
    view the live input file.

    ...

    Attributes
    ----------
    gudrunFile : GudrunFile
        GudrunFile object currently associated with the application.
    parent : QWidget
        Parent widget.
    Methods
    -------
    initComponents():
        Loads the UI file for the ViewInputDialog
    save():
        Saves the input file and updates the UI appropiately.
    """
    def __init__(self, gudrunFile, parent):
        super(ViewInputDialog, self).__init__(parent=parent)
        self.gudrunFile = gudrunFile
        self.parent = parent
        self.initComponents()

    def initComponents(self):
        """
        Loads the UI file for the ViewInputDialog object.
        """
        if hasattr(sys, '_MEIPASS'):
            uifile = QFile(
                os.path.join(
                    sys._MEIPASS, "ui_files", "viewInputDialog.ui"
                )
            )
        else:
            current_dir = os.path.dirname(os.path.realpath(__file__))
            uifile = QFile(
                os.path.join(
                    current_dir, "..", "ui_files", "viewInputDialog.ui"
                )
            )
        loader = QUiLoader()
        self.widget = loader.load(uifile)
        self.widget.setWindowTitle(self.gudrunFile.path)
        self.widget.saveAndCloseButton.clicked.connect(self.save)
        self.widget.closeButton.clicked.connect(self.widget.close)
        self.widget.textEdit.setText(str(self.gudrunFile))
        self.widget.textEdit.textChanged.connect(self.setChanged)

    def setChanged(self):
        self.widget.saveAndCloseButton.setEnabled(
            self.widget.textEdit.toPlainText() != str(self.gudrunFile)
        )

    def save(self):
        """
        Saves the input file and updates the UI appropiately.
        """
        with open(self.gudrunFile.path, "w", encoding="utf-8") as fp:
            fp.write(self.widget.textEdit.toPlainText())
        self.widget.close()
        self.parent.updateFromFile()
