from PyQt5.QtWidgets import QWidget
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
        Constructs all the necessary attributes for the SampleBackgroundWidget object.
        Calls the initComponents method, to load the UI file and populate data.
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
    
    def handlePeriodNoChanged(self, value):
        self.sampleBackground.periodNumber = value
    
    def initComponents(self):
        """
        Loads the UI file for the SampleBackgroundWidget object,
        and then populates the child widgets with their
        corresponding data from the attributes of the SampleBackground object.
        """
        current_dir = os.path.dirname(os.path.realpath(__file__))
        uifile = os.path.join(current_dir, "ui_files/sampleBackgroundWidget.ui")
        uic.loadUi(uifile, self)

        self.dataFilesList.addItems([df for df in self.sampleBackground.dataFiles.dataFiles])

        self.periodNoSpinBox.setValue(self.sampleBackground.periodNumber)
        self.periodNoSpinBox.valueChanged.connect(self.handlePeriodNoChanged)