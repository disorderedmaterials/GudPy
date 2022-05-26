import os
from PySide6.QtWidgets import QFileDialog


class SampleBackgroundSlots():

    def __init__(self, widget, parent):
        self.widget = widget
        self.parent = parent
        self.setupSampleBackgroundSlots()

    def setSampleBackground(self, sampleBackground):
        self.sampleBackground = sampleBackground
        # Acquire the lock
        self.widgetsRefreshing = True

        # Populate period number.
        self.widget.sampleBackgroundPeriodNoSpinBox.setValue(
            self.sampleBackground.periodNumber
        )

        # Populate data files list.
        self.widget.sampleBackgroundDataFilesList.makeModel(self.sampleBackground.dataFiles.dataFiles)

        self.widget.sampleBackgroundDataFilesList.model().dataChanged.connect(self.handleDataFilesAltered)
        self.widget.sampleBackgroundDataFilesList.model().rowsRemoved.connect(self.handleDataFilesAltered)

        # Release the lock
        self.widgetsRefreshing = False

    def setupSampleBackgroundSlots(self):
        # Setup slot for period number.
        self.widget.sampleBackgroundPeriodNoSpinBox.valueChanged.connect(
            self.handlePeriodNoChanged
        )

        # Setup slots for data files.
        self.widget.addSampleBackgroundDataFileButton.clicked.connect(
            lambda: self.addFiles(
                self.widget.sampleBackgroundDataFilesList,
                "Add data files",
                f"{self.parent.gudrunFile.instrument.dataFileType}"
                f" (*.{self.parent.gudrunFile.instrument.dataFileType})",
            )
        )
        self.widget.removeSampleBackgroundDataFileButton.clicked.connect(
            lambda: self.removeFile(
                self.widget.sampleBackgroundDataFilesList
            )
        )

    def handleDataFilesAltered(self):
        if not self.widgetsRefreshing:
            self.parent.setModified()
            self.parent.gudrunFile.purged = False
            self.sampleBackground.dataFiles.dataFiles = self.widget.sampleBackgroundDataFilesList.model().stringList()

    def addFiles(self, target, title, regex):
        files, _ = QFileDialog.getOpenFileNames(
            self.widget, title,
            self.parent.gudrunFile.instrument.dataFileDir, regex
        )
        for file in files:
            if file:
                target.insertRow(file.split(os.path.sep)[-1])

    def removeFile(self, target):
        target.removeItem()

    def handlePeriodNoChanged(self, value):
        self.sampleBackground.periodNumber = value
        if not self.widgetsRefreshing:
            self.parent.setModified()
