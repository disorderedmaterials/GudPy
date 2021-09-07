from src.gui.widgets.gudpy_widget import GudPyWidget
from src.gudrun_classes.enums import Geometry, NormalisationType, OutputUnits, UnitsOfDensity
from PyQt5.QtWidgets import QTableWidgetItem, QWidget
from PyQt5 import uic
from PyQt5.QtCore import Qt
import os

class SampleWidget(GudPyWidget):
    """
    Class to represent a SampleWidget. Inherits QWidget.

    ...

    Attributes
    ----------
    sample : Sample
        Sample object belonging to the GudrunFile.
    parent : QWidget
        Parent widget.
    Methods
    -------
    initComponents()
        Loads UI file, and then populates data from the Sample.
    """
    def __init__(self, sample, parent=None):
        """
        Constructs all the necessary attributes for the SampleWidget object.
        Calls the initComponents method, to load the UI file and populate data.
        Parameters
        ----------
        sample : Sample
            Sample object belonging to the GudrunFile.
        parent : QWidget
            Parent widget.
        """
        self.sample = sample
        self.parent = parent

        super(SampleWidget, self).__init__(object=self.sample, parent=self.parent)
        self.initComponents()
    
    def handlePeriodNoChanged(self, value):
        self.sample.periodNo = value

    def handleForceCorrectionsSwitched(self, state):
        self.sample.forceCalculationOfCorrections = state

    def handleGeometryChanged(self, index):
        self.sample.geometry = self.geometryComboBox.itemData(index)
    


    def initComponents(self):
        """
        Loads the UI file for the SampleWidget object,
        and then populates the child widgets with their
        corresponding data from the attributes of the Sample object.
        """
        current_dir = os.path.dirname(os.path.realpath(__file__))
        uifile = os.path.join(current_dir, "ui_files/sampleWidget.ui")
        uic.loadUi(uifile, self)

        self.periodNoSpinBox.setValue(self.sample.periodNumber)
        self.dataFilesList.addItems([df for df in self.sample.dataFiles.dataFiles])

        self.forceCorrectionsCheckBox.setChecked(Qt.Checked if self.sample.forceCalculationOfCorrections else Qt.Unchecked)
        self.forceCorrectionsCheckBox.stateChanged.connect(self.handleForceCorrectionsSwitched)


        for i, element in enumerate(self.sample.composition.elements):
            self.sampleCompositionTable.setItem(i, 0, QTableWidgetItem(str(element.atomicSymbol)))
            self.sampleCompositionTable.setItem(i, 1, QTableWidgetItem(str(element.massNo)))
            self.sampleCompositionTable.setItem(i, 2, QTableWidgetItem(str(element.abundance)))

        for g in Geometry:
            self.geometryComboBox.addItem(g.name, g)
        self.geometryComboBox.setCurrentIndex(self.sample.geometry.value)
        self.geometryComboBox.currentIndexChanged.connect(self.handleGeometryChanged)

        self.upstreamSpinBox.setValue(self.sample.upstreamThickness)
        self.downstreamSpinBox.setValue(self.sample.downstreamThickness)



        self.densitySpinBox.setValue(self.sample.density)
        for du in UnitsOfDensity:
            self.densityUnitsComboBox.addItem(du.name, du)
        self.densityUnitsComboBox.setCurrentIndex(self.sample.densityUnits.value)
        

        crossSectionSources = ["TABLES", "TRANSMISSION MONITOR", "FILENAME"]
        if "TABLES" in self.sample.totalCrossSectionSource:
            index = 0
        elif "TRANSMISSION" in self.sample.totalCrossSectionSource:
            index = 1
        else:
            index = 2
        self.totalCrossSectionComboBox.addItems(crossSectionSources)
        self.totalCrossSectionComboBox.setCurrentIndex(index)

        self.tweakFactorSpinBox.setValue(self.sample.sampleTweakFactor)

        self.topHatWidthSpinBox.setValue(self.sample.topHatW)
        self.minSpinBox.setValue(self.sample.minRadFT)
        self.maxSpinBox.setValue(self.sample.maxRadFT)

        self.broadeningFunctionSpinBox.setValue(self.sample.grBroadening)
        self.broadeningPowerSpinBox.setValue(self.sample.powerForBroadening)

        self.stepSizeSpinBox.setValue(self.sample.stepSize)

        self.scatteringFileLineEdit.setText(self.sample.fileSelfScattering)

        for n in NormalisationType:
            self.normaliseToComboBox.addItem(n.name, n)
        self.normaliseToComboBox.setCurrentIndex(self.sample.normaliseTo.value)

        for u in OutputUnits:
            self.outputUnitsComboBox.addItem(u.name, u)
        self.outputUnitsComboBox.setCurrentIndex(self.sample.outputUnits.value)

        self.angleOfRotationSpinBox.setValue(self.sample.angleOfRotationSample)
        self.sampleWidthSpinBox.setValue(self.sample.sampleWidth)

        self.correctionFactorSpinBox.setValue(self.sample.normalisationCorrectionFactor)
        self.scatteringFractionSpinBox.setValue(self.sample.scatteringFraction)
        self.attenuationCoefficientSpinBox.setValue(self.sample.attenuationCoefficient)