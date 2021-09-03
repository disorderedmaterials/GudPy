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
    
    def initComponents(self):
        """
        Loads the UI file for the SampleWidget object,
        and then populates the child widgets with their
        corresponding data from the attributes of the Sample object.
        """
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

        for g in Geometry:
            self.geometryComboBox.addItem(g.name, g)
        self.geometryComboBox.setCurrentIndex(self.sample.geometry.value)
        self.upstreamLineEdit.setText(str(self.sample.thickness[0]))
        self.downstreamLineEdit.setText(str(self.sample.thickness[1]))



        self.densityLineEdit.setText(str(self.sample.density))
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

        self.tweakFactorLineEdit.setText(str(self.sample.sampleTweakFactor))

        self.topHatWidthLineEdit.setText(str(self.sample.topHatW))
        self.minLineEdit.setText(str(self.sample.minRadFT))
        self.maxLineEdit.setText(str(self.sample.maxRadFT))

        self.broadeningFunctionLineEdit.setText(str(self.sample.grBroadening))
        self.broadeningPowerLineEdit.setText(str(self.sample.powerForBroadening))

        self.stepSizeLineEdit.setText(str(self.sample.stepSize))

        self.scatteringFileLineEdit.setText(self.sample.fileSelfScattering)

        for n in NormalisationType:
            self.normaliseToComboBox.addItem(n.name, n)
        self.normaliseToComboBox.setCurrentIndex(self.sample.normaliseTo.value)

        for u in OutputUnits:
            self.outputUnitsComboBox.addItem(u.name, u)
        self.outputUnitsComboBox.setCurrentIndex(self.sample.outputUnits.value)

        self.angleOfRotationLineEdit.setText(str(self.sample.angleOfRotationSampleWidth[0]))
        self.sampleWidthLineEdit.setText(str(self.sample.angleOfRotationSampleWidth[1]))

        self.correctionFactorLineEdit.setText(str(self.sample.normalisationCorrectionFactor))
        self.scatteringFractionLineEdit.setText(str(self.sample.environementScatteringFuncAttenuationCoeff[0]))
        self.attenuationCoefficientLineEdit.setText(str(self.sample.environementScatteringFuncAttenuationCoeff[1]))