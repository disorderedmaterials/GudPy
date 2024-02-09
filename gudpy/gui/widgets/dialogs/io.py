from core.file_library import GudPyFileLibrary
from PySide6.QtWidgets import (
    QDialog, QFileDialog, QMessageBox, QListWidget, QLabel
)
import sys
import os
from PySide6.QtCore import QFile
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


class ExportDialog(QDialog):
    """
    Class to represent the ExportDialog. Inherits QDialog.
    This is the dialog window opened when a user wishes to export data.

    ...

    Attributes
    ----------
    gudrunFile : GudrunFile
        Object associated with the dialog.
    Methods
    -------
    initComponents()
        Loads the UI file for the MissingFilesDialog.
    loadFileList()
        Loads the initial file list.
    toggleRename()
        Toggles renaming files to the sample name.
    performExport(filename)
        Performs an export to a filename.
    export()
        Performs a standard export.
    exportAs()
        Allows exporting to a specific file.
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
            self.widget.close
        )

    def loadFilesList(self, rename=False):
        self.widget.filesList.clear()
        for sample in [
            s for sb in self.gudrunFile.sampleBackgrounds for s in sb.samples
        ]:
            if len(sample.dataFiles):
                mintFile = (
                    sample.dataFiles[0]
                    .replace(
                        self.gudrunFile.instrument.dataFileType,
                        "mint01"
                    )
                )
                namedAfterSample = sample.name.replace(" ", "_").translate(
                    {ord(x): '' for x in r'/\!*~,&|[]'}
                ) + ".mint01"

                if os.path.exists(os.path.join(
                    self.gudrunFile.instrument.GudrunInputFileDir, mintFile
                )) or os.path.exists(os.path.join(
                    self.gudrunFile.instrument.GudrunInputFileDir,
                    namedAfterSample
                )):
                    if rename:
                        mintFile = namedAfterSample
                    self.widget.filesList.addItem(mintFile)

    def toggleRename(self, state):
        self.loadFilesList(rename=bool(state))

    def performExport(self, filename=None):
        fl = GudPyFileLibrary(self.gudrunFile)
        archive = fl.exportMintData(
            [
                s
                for sb in self.gudrunFile.sampleBackgrounds
                for s in sb.samples
            ],
            renameDataFiles=self.widget.renameCheckBox.checkState(),
            exportTo=filename,
            includeParams=self.widget.includeParamsCheckBox.checkState()
        )
        QMessageBox.warning(
            self.widget,
            "GudPy Export",
            f"Archived to {archive}!"
        )
        self.widget.close()

    def export(self):
        self.performExport()

    def exportAs(self):

        dialog = QFileDialog()
        dialog.setDefaultSuffix("zip")
        dialog.setWindowTitle("Export to..")
        dialog.setDirectory(".")
        dialog.setAcceptMode(QFileDialog.AcceptSave)
        if dialog.exec() == dialog.Accepted:
            filename = dialog.selectedFiles()[0]

        if filename:
            self.performExport(filename=filename)
