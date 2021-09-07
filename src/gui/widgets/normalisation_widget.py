from src.gui.widgets.gudpy_widget import GudPyWidget
from src.gudrun_classes.enums import Geometry, UnitsOfDensity
from PyQt5.QtWidgets import QTableWidgetItem, QWidget
from PyQt5 import uic
from PyQt5.QtCore import Qt
import os

class NormalisationWidget(GudPyWidget):
    """
    Class to represent a NormalisationWidget. Inherits QWidget.

    ...

    Attributes
    ----------
    normalisation : Normalisation
        Normalisation object belonging to the GudrunFile.
    parent : QWidget
        Parent widget.
    Methods
    -------
    initComponents()
        Loads UI file, and then populates data from the Normalisation.
    """
    def __init__(self, normalisation, parent=None):
        """
        Constructs all the necessary attributes for the NormalisationWidget object.
        Calls the initComponents method, to load the UI file and populate data.
        Parameters
        ----------
        normalisation : Normalisation
            Normalisation object belonging to the GudrunFile.
        parent : QWidget
            Parent widget.
        """
        self.normalisation = normalisation
        self.parent = parent

        super(NormalisationWidget, self).__init__(object=self.normalisation, parent=self.parent)
        self.initComponents()
    
    def initComponents(self):
        """
        Loads the UI file for the NormalisationWidget object,
        and then populates the child widgets with their
        corresponding data from the attributes of the Normalisation object.
        """
        current_dir = os.path.dirname(os.path.realpath(__file__))
        uifile = os.path.join(current_dir, "ui_files/normalisationWidget.ui")
        uic.loadUi(uifile, self)

        self.dataFilesList.addItems([df for df in self.normalisation.dataFiles.dataFiles])
        self.backgroundDataFilesList.addItems([df for df in self.normalisation.dataFilesBg.dataFiles])

        self.periodNoSpinBox.setValue(self.normalisation.periodNumber)
        self.backgroundPeriodNoSpinBox.setValue(self.normalisation.periodNumberBg)

        for i, element in enumerate(self.normalisation.composition.elements):
            self.normalisationCompositionTable.setItem(i, 0, QTableWidgetItem(str(element.atomicSymbol)))
            self.normalisationCompositionTable.setItem(i, 1, QTableWidgetItem(str(element.massNo)))
            self.normalisationCompositionTable.setItem(i, 2, QTableWidgetItem(str(element.abundance)))
        
        self.geometryComboBox.addItems([g.name for g in Geometry])
        self.geometryComboBox.setCurrentIndex(self.normalisation.geometry.value)

        self.densitySpinBox.setValue(self.normalisation.density)
        for du in UnitsOfDensity:
            self.densityUnitsComboBox.addItem(du.name, du)
        self.densityUnitsComboBox.setCurrentIndex(self.normalisation.densityUnits.value)
        
        self.upstreamSpinBox.setValue(self.normalisation.upstreamThickness)
        self.downstreamSpinBox.setValue(self.normalisation.downstreamThickness)

        crossSectionSources = ["TABLES", "TRANSMISSION MONITOR", "FILENAME"]
        if "TABLES" in self.normalisation.totalCrossSectionSource:
            index = 0
        elif "TRANSMISSION" in self.normalisation.totalCrossSectionSource:
            index = 1
        else:
            index = 2
        self.totalCrossSectionComboBox.addItems(crossSectionSources)
        self.totalCrossSectionComboBox.setCurrentIndex(index)

        self.forceCorrectionsCheckBox.setChecked(Qt.Checked if self.normalisation.forceCalculationOfCorrections else Qt.Unchecked)
        self.placzekCorrectionSpinBox.setValue(self.normalisation.tempForNormalisationPC)
        self.differentialCrossSectionFileLineEdit.setValue(self.normalisation.normalisationDifferentialCrossSectionFilename)
        self.smoothingDegreeSpinBox.setValue(self.normalisation.normalisationDegreeSmoothing)
        self.lowerLimitSmoothingSpinBox.setValue(self.normalisation.lowerLimitSmoothedNormalisation)
        self.minNormalisationSignalSpinBoxsetValue(self.normalisation.minNormalisationSignalBR)