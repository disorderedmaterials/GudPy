from src.gudrun_classes.enums import Geometry, UnitsOfDensity
from PyQt5.QtWidgets import QTableWidgetItem, QWidget
from PyQt5 import uic
from PyQt5.QtCore import Qt
import os

class NormalisationWidget(QWidget):
    def __init__(self, normalisation, parent=None):
        self.normalisation = normalisation
        self.parent = parent

        super(NormalisationWidget, self).__init__(self.parent)
        self.initComponents()
    
    def initComponents(self):
        current_dir = os.path.dirname(os.path.realpath(__file__))
        uifile = os.path.join(current_dir, "ui_files/normalisationWidget.ui")
        uic.loadUi(uifile, self)

        self.dataFilesList.addItems([df for df in self.normalisation.dataFiles.dataFiles])
        self.backgroundDataFilesList.addItems([df for df in self.normalisation.dataFilesBg.dataFiles])

        self.periodNoLineEdit.setText(str(self.normalisation.numberOfFilesPeriodNumber[1]))
        self.backgroundPeriodNoLineEdit.setText(str(self.normalisation.numberOfFilesPeriodNumberBg[1]))

        for i, element in enumerate(self.normalisation.composition.elements):
            self.normalisationCompositionTable.setItem(i, 0, QTableWidgetItem(str(element.atomicSymbol)))
            self.normalisationCompositionTable.setItem(i, 1, QTableWidgetItem(str(element.massNo)))
            self.normalisationCompositionTable.setItem(i, 2, QTableWidgetItem(str(element.abundance)))
        
        # self.geometryComboBox.addItems([g.name for g in Geometry])
        # self.geometryComboBox.setCurrentIndex(self.normalisation.geometry.value)

        self.densityLineEdit.setText(str(self.normalisation.density))
        self.densityUnitsComboBox.addItems([du.name for du in UnitsOfDensity])
        self.densityUnitsComboBox.setCurrentIndex(self.normalisation.densityUnits.value)
        
        self.upstreamLineEdit.setText(str(self.normalisation.thickness[0]))
        self.downstreamLineEdit.setText(str(self.normalisation.thickness[1]))

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
        self.placzekCorrectionLineEdit.setText(str(self.normalisation.tempForNormalisationPC))
        self.differentialCrossSectionFileLineEdit.setText(self.normalisation.normalisationDifferentialCrossSectionFilename)
        self.smoothingDegreeLineEdit.setText(str(self.normalisation.normalisationDegreeSmoothing))
        self.lowerLimitSmoothingLineEdit.setText(str(self.normalisation.lowerLimitSmoothedNormalisation))
        self.minNormalisationSignalLineEdit.setText(str(self.normalisation.minNormalisationSignalBR))