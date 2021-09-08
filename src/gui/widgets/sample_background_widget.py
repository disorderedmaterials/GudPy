from PyQt5.QtWidgets import QFileDialog, QWidget
from PyQt5 import uic
import os


class SampleBackgroundWidget(QWidget):
    """
    Class to represent a SampleBackgroundWidget. Inherits QWidget.

    ...

    Attributes
    ----------
    sampleBackground : SampleBackground
        SampleBackground object belonging to the GudrunFile.
    parent : QWidget
        Parent widget.
    Methods
    -------
    initComponents()
        Loads UI file, and then populates data from the SampleBackground.
    """

    def __init__(self, sampleBackground, parent=None):
        """
        Constructs all the necessary attributes
        for the SampleBackgroundWidget object.
        Calls the initComponents method,
        to load the UI file and populate data.
        Parameters
        ----------
        sampleBackground : SampleBackground
            SampleBackground object belonging to the GudrunFile.
        parent : QWidget
            Parent widget.
        """
        self.sampleBackground = sampleBackground
        self.parent = parent

        super(SampleBackgroundWidget, self).__init__(parent=self.parent)
        self.initComponents()

    def handleDataFilesAltered(self, item):
        index = item.row()
        value = item.text()
        if not value:
            self.sampleBackground.dataFiles.dataFiles.remove(index)
        else:
            self.sampleBackground.dataFiles.dataFiles[index] = value
        self.updateDataFilesList()

    def handleDataFileInserted(self, item):
        value = item.text()
        self.sampleBackground.dataFiles.dataFiles.append(value)

    def updateDataFilesList(self):
        self.dataFilesList.clear()
        self.dataFilesList.addItems(
            [df for df in self.sampleBackground.dataFiles.dataFiles]
        )

    def addFiles(self, target, title, regex):
        paths = QFileDialog.getOpenFileNames(self, title, '.', regex)
        for path in paths:
            if path:
                target.addItem(path)
                self.handleDataFileInserted(target.item(target.count()-1))

    def handlePeriodNoChanged(self, value):
        self.sampleBackground.periodNumber = value

    def initComponents(self):
        """
        Loads the UI file for the SampleBackgroundWidget object,
        and then populates the child widgets with their
        corresponding data from the attributes of the SampleBackground object.
        """
        current_dir = os.path.dirname(os.path.realpath(__file__))
        uifile = os.path.join(
            current_dir, "ui_files/sampleBackgroundWidget.ui"
        )
        uic.loadUi(uifile, self)

        self.updateDataFilesList()
        self.dataFilesList.itemChanged.connect(self.handleDataFilesAltered)
        self.dataFilesList.itemEntered.connect(self.handleDataFileInserted)
        self.addDataFileButton.clicked.connect(
            lambda : self.addFiles(
                self.dataFilesList,
                "Add data files",
                f"{self.parent.gudrunFile.instrument.dataFileType} (*.{self.parent.gudrunFile.instrument.dataFileType})"
            )
        )

        self.periodNoSpinBox.setValue(self.sampleBackground.periodNumber)
        self.periodNoSpinBox.valueChanged.connect(self.handlePeriodNoChanged)
