import sys
import os
from PySide6.QtCore import QFile
from PySide6.QtWidgets import QDialog, QListWidget, QLabel
from PySide6.QtUiTools import QUiLoader


class MissingFilesDialog(QDialog):
    """
    Class to represent the MissingFilesDialog. Inherits QDialog.
    This is the dialog window opened when a user wishes to iterate Gudrun.

    ...

    Attributes
    ----------
    missingFiles : str[]
        List of missing file names.
    Methods
    -------
    initComponents()
        Loads the UI file for the MissingFilesDialog.
    """

    def __init__(self, undefinedFiles, missingFiles, parent):
        super(MissingFilesDialog, self).__init__(parent=parent)
        self.undefinedFiles = undefinedFiles
        self.missingFiles = missingFiles
        self.initComponents()

    def initComponents(self):
        """
        Loads the UI file for the MissingFilesDialog object.
        """
        if hasattr(sys, "_MEIPASS"):
            uifile = QFile(
                os.path.join(sys._MEIPASS, "ui_files", "missingFilesDialog.ui")
            )
        else:
            current_dir = os.path.dirname(os.path.realpath(__file__))
            uifile = QFile(
                os.path.join(
                    current_dir, "..", "ui_files", "missingFilesDialog.ui"
                )
            )

        loader = QUiLoader()
        self.widget = loader.load(uifile)

        if self.undefinedFiles:
            undefinedFilesLabel = QLabel(self)
            undefinedFilesLabel.setText(
                "Please specify correct paths for the following fields:"
            )
            undefinedFilesList = QListWidget(self)
            undefinedFilesList.addItems(self.undefinedFiles)
            self.widget.missingSectionsLayout.addWidget(undefinedFilesLabel)
            self.widget.missingSectionsLayout.addWidget(undefinedFilesList)

        if self.missingFiles:
            missingFilesLabel = QLabel(self)
            missingFilesLabel.setText(
                "Couldn't resolve some files! "
                + "Check that all paths are correct:"
            )
            missingFilesList = QListWidget(self)
            missingFilesList.addItems(self.missingFiles)
            self.widget.missingSectionsLayout.addWidget(missingFilesLabel)
            self.widget.missingSectionsLayout.addWidget(missingFilesList)
