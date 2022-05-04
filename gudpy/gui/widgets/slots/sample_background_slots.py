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
        self.updateDataFilesList()

        # Release the lock
        self.widgetsRefreshing = False

    def setupSampleBackgroundSlots(self):
        # Setup slot for period number.
        self.widget.sampleBackgroundPeriodNoSpinBox.valueChanged.connect(
            self.handlePeriodNoChanged
        )

        # Setup slots for data files.
        self.widget.sampleBackgroundDataFilesList.itemChanged.connect(
            self.handleDataFilesAltered
        )
        self.widget.sampleBackgroundDataFilesList.itemEntered.connect(
            self.handleDataFileInserted
        )
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
                self.widget.sampleBackgroundDataFilesList,
                self.sampleBackground.dataFiles
            )
        )

    def handleDataFilesAltered(self, item):
        index = item.row()
        value = item.text()
        if not value:
            self.sampleBackground.dataFiles.dataFiles.remove(index)
        else:
            self.sampleBackground.dataFiles[index] = value
        self.updateDataFilesList()
        if not self.widgetsRefreshing:
            self.parent.setModified()

    def handleDataFileInserted(self, item):
        value = item.text()
        self.sampleBackground.dataFiles.dataFiles.append(value)
        if not self.widgetsRefreshing:
            self.parent.setModified()

    def updateDataFilesList(self):
        self.widget.sampleBackgroundDataFilesList.clear()
        self.widget.sampleBackgroundDataFilesList.addItems(
            [df for df in self.sampleBackground.dataFiles]
        )

    def addFiles(self, target, title, regex):
        files, _ = QFileDialog.getOpenFileNames(
            self.widget, title,
            self.parent.gudrunFile.instrument.dataFileDir, regex
        )
        for file in files:
            if file:
                target.addItem(file.split(os.path.sep)[-1])
                self.handleDataFileInserted(target.item(target.count() - 1))
        if not self.widgetsRefreshing:
            self.parent.setModified()

    def removeFile(self, target, dataFiles):
        if target.currentIndex().isValid():
            remove = target.takeItem(target.currentRow()).text()
            dataFiles.dataFiles.remove(remove)
            if not self.widgetsRefreshing:
                self.parent.setModified()

    def handlePeriodNoChanged(self, value):
        self.sampleBackground.periodNumber = value
        if not self.widgetsRefreshing:
            self.parent.setModified()
