import sys
from PySide6.QtCore import QFile
from PySide6.QtWidgets import QDialog, QFileDialog, QMessageBox
from PySide6.QtUiTools import QUiLoader
import os

from src.gudrun_classes.file_library import GudPyFileLibrary


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
    def __init__(self, gudrunFile, parent):
        super(ExportDialog, self).__init__(parent=parent)
        self.gudrunFile = gudrunFile
        self.initComponents()
        self.loadFilesList()

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

        self.widget.renameCheckBox.stateChanged.connect(
            self.toggleRename
        )

        self.widget.exportButton.clicked.connect(
            self.export
        )

        self.widget.exportAsButton.clicked.connect(
            self.exportAs
        )

        self.widget.cancelButton.clicked.connect(
            self.close
        )

    def loadFilesList(self, rename=False):
        self.widget.filesList.clear()
        for sample in [
            s for sb in self.gudrunFile.sampleBackgrounds for s in sb.samples
            ]:
            if len(sample.dataFiles.dataFiles):
                mintFile = sample.dataFiles.dataFiles[0].replace(self.gudrunFile.instrument.dataFileType, "mint01")
                if os.path.exists(os.path.join(
                    self.gudrunFile.instrument.GudrunInputFileDir, mintFile
                )):
                    if rename:
                        mintFile = sample.name.replace(" ", "_").replace(",", "") + ".mint01"
                    self.widget.filesList.addItem(mintFile)
    
    def toggleRename(self, state):
        self.loadFilesList(rename=bool(state))

    def performExport(self, filename=None):
        fl = GudPyFileLibrary(self.gudrunFile)
        archive = fl.exportMintData(
            [s for sb in self.gudrunFile.sampleBackgrounds for s in sb.samples],
            renameDataFiles=self.widget.renameCheckBox.checkState(),
            exportTo=filename
        )
        QMessageBox.warning(self.widget, "GudPy Export", f"Archived to {archive}!")
        self.widget.close()

    def export(self):
        self.performExport()

    def exportAs(self):
        filename, _ = QFileDialog.getSaveFileName(
            self, "Export to..", "."
        )
        self.performExport(filename=filename)