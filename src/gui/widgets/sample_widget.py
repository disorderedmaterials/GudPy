from gudrun_classes.enums import Geometry, UnitsOfDensity
from PyQt5.QtWidgets import QTableWidgetItem, QWidget, QHeaderView
from PyQt5 import uic
from PyQt5.QtCore import Qt
import os
import sys

class SampleWidget(QWidget):
    def __init__(self, sample, parent=None):
        self.sample = sample
        self.parent = parent

        super(SampleWidget, self).__init__(self.parent)
        self.initComponents()
    
    def initComponents(self):
        current_dir = os.path.dirname(os.path.realpath(__file__))
        uifile = os.path.join(current_dir, "ui_files/sampleWidget.ui")
        uic.loadUi(uifile, self)

        self.periodNoLineEdit.setText(str(self.sample.numberOfFilesPeriodNumber[1]))
        self.dataFilesList.addItems([df for df in self.sample.dataFiles.dataFiles])

        self.forceCorrectionsCheckBox.setChecked(Qt.Checked if self.sample.forceCalculationOfCorrections else Qt.Unchecked)


        for i, element in enumerate(self.sample.composition.elements):
            self.sampleCompositionTable.setItem(i, 0, QTableWidgetItem(str(element.atomicSymbol)))
            self.sampleCompositionTable.setItem(i, 1, QTableWidgetItem(str(element.massNo)))
            self.sampleCompositionTable.setItem(i, 2, QTableWidgetItem(str(element.abundance)))

        self.geometryComboBox.addItems([g.name for g in Geometry])
        self.geometryComboBox.setCurrentIndex(self.sample.geometry.value)
        self.upstreamLineEdit.setText(str(self.sample.thickness[0]))
        self.downstreamLineEdit.setText(str(self.sample.thickness[1]))

        # angle of rotation an sample width

        self.densityLineEdit.setText(str(self.sample.density))
        self.densityUnitsComboBox.addItems([du.name for du in UnitsOfDensity])
        self.densityUnitsComboBox.setCurrentIndex(self.sample.densityUnits.value)
        
        #temp for normalisation pc


