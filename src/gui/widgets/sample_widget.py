from src.scripts.utils import isnumeric
from src.gudrun_classes.element import Element
from src.gudrun_classes.enums import (
    Geometry,
    NormalisationType,
    OutputUnits,
    UnitsOfDensity,
)
from PyQt5.QtWidgets import QFileDialog, QTableWidgetItem, QWidget
from PyQt5 import uic
from PyQt5.QtCore import Qt
import os
from src.gudrun_classes.config import geometry


class SampleWidget(QWidget):
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

        super(SampleWidget, self).__init__(parent=self.parent)
        self.initComponents()

    def handlePeriodNoChanged(self, value):
        self.sample.periodNo = value

    def handleForceCorrectionsSwitched(self, state):
        self.sample.forceCalculationOfCorrections = state

    def handleGeometryChanged(self, index):
        self.sample.geometry = self.geometryComboBox.itemData(index)
        self.geometryInfoStack.setCurrentIndex(self.sample.geometry.value)

    def handleUpstreamThicknessChanged(self, value):
        self.sample.upstreamThickness = value

    def handleDownstreamThicknessChanged(self, value):
        self.sample.downstreamThickness = value

    def handleDensityUnitsChanged(self, index):
        self.sample.densityUnits = self.densityUnitsComboBox.itemData(index)

    def handleCrossSectionSourceChanged(self, index):
        self.sample.totalCrossSectionSource = (
            self.totalCrossSectionComboBox.itemData(index)
        )

    def handleTweakFactorChanged(self, value):
        self.sample.tweakFactor = value

    def handleTopHatWidthChanged(self, value):
        self.sample.topHatW = value

    def handleMinChanged(self, value):
        self.sample.minRadFT = value

    def handleMaxChanged(self, value):
        self.sample.maxRadFT = value

    def handleBroadeningFunctionChanged(self, value):
        self.sample.grBroadening = value

    def handleBroadeningPowerChanged(self, value):
        self.sample.powerForBroadening = value

    def handleStepSizeChanged(self, value):
        self.sample.stepSize = value

    def handleSelfScatteringFileChanged(self, value):
        self.sample.fileSelfScattering = value

    def handleNormaliseToChanged(self, index):
        self.sample.normaliseTo = self.normaliseToComboBox.itemData(index)

    def handleOutputUnitsChanged(self, index):
        self.sample.outputUnits = self.outputUnitsComboBox.itemData(index)

    def handleAngleOfRotationChanged(self, value):
        self.sample.angleOfRotation = value

    def handleSampleWidthChanged(self, value):
        self.sample.sampleWidth = value

    def handleSampleHeightChanged(self, value):
        self.sample.sampleHeight = value

    def handleCorrectionFactorChanged(self, value):
        self.sample.normalisationCorrectionFactor = value

    def handleScatteringFractionChanged(self, value):
        self.sample.scatteringFraction = value

    def handleAttenuationCoefficientChanged(self, value):
        self.sample.attenuationCoefficient = value

    def handleDataFilesAltered(self, item):
        index = item.row()
        value = item.text()
        if not value:
            self.sample.dataFiles.dataFiles.remove(index)
        else:
            self.sample.dataFiles.dataFiles[index] = value
        self.updateDataFilesList()

    def handleDataFileInserted(self, item):
        value = item.text()
        self.sample.dataFiles.dataFiles.append(value)

    def updateDataFilesList(self):
        self.dataFilesList.clear()
        self.dataFilesList.addItems(
            [df for df in self.sample.dataFiles.dataFiles]
        )

    def addFiles(self, target, title, regex):
        paths = QFileDialog.getOpenFileNames(self, title, '.', regex)
        for path in paths:
            if path:
                target.addItem(path)
                self.handleDataFileInserted(target.item(target.count()-1))

    def removeFile(self, target, dataFiles):
        remove = target.takeItem(target.currentRow()).text()
        dataFiles.dataFiles.remove(remove)
        self.updateDataFilesList()

    def handleElementChanged(self, item):
        value = item.text()
        row = item.row()
        col = item.column()
        if row < len(self.sample.composition.elements):
            element = self.sample.composition.elements[row]
            attribute = {
                0: ("atomicSymbol", str),
                1: ("massNo", int),
                2: ("abundance", float)
            }[col]
            element.__dict__[attribute[0]] = attribute[1](value)
            self.sample.composition.elements[row] = element
        else:
            self.handleElementInserted(item)

    def handleElementInserted(self, item):
        row = item.row()
        atomicSymbol = self.sampleCompositionTable.itemAt(row, 0).text()
        massNo = self.sampleCompositionTable.itemAt(row, 1).text()
        abundance = self.sampleCompositionTable.itemAt(row, 2).text()
        if len(atomicSymbol) and isnumeric(massNo) and isnumeric(abundance):
            print(atomicSymbol, massNo, abundance)
            element = Element(atomicSymbol, int(massNo), float(abundance))
            self.sample.composition.elements.append(element)

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
        self.periodNoSpinBox.valueChanged.connect(self.handlePeriodNoChanged)

        self.updateDataFilesList()
        self.dataFilesList.itemChanged.connect(self.handleDataFilesAltered)
        self.dataFilesList.itemEntered.connect(self.handleDataFileInserted)
        self.addDataFileButton.clicked.connect(
            lambda: self.addFiles(
                self.dataFilesList,
                "Add data files",
                f"{self.parent.gudrunFile.instrument.dataFileType}"
                f" (*.{self.parent.gudrunFile.instrument.dataFileType})"
            )
        )
        self.removeDataFileButton.clicked.connect(
            lambda: self.removeFile(
                self.dataFilesList,
                self.sample.dataFiles
            )
        )
        self.forceCorrectionsCheckBox.setChecked(
            Qt.Checked
            if self.sample.forceCalculationOfCorrections
            else Qt.Unchecked
        )
        self.forceCorrectionsCheckBox.stateChanged.connect(
            self.handleForceCorrectionsSwitched
        )

        for i, element in enumerate(self.sample.composition.elements):
            self.sampleCompositionTable.setItem(
                i, 0, QTableWidgetItem(str(element.atomicSymbol))
            )
            self.sampleCompositionTable.setItem(
                i, 1, QTableWidgetItem(str(element.massNo))
            )
            self.sampleCompositionTable.setItem(
                i, 2, QTableWidgetItem(str(element.abundance))
            )
        self.sampleCompositionTable.itemChanged.connect(
            self.handleElementChanged
        )
        self.sampleCompositionTable.itemEntered.connect(
            self.handleElementInserted
        )

        for g in Geometry:
            self.geometryComboBox.addItem(g.name, g)
        self.geometryComboBox.setCurrentIndex(self.sample.geometry.value)
        self.geometryComboBox.currentIndexChanged.connect(
            self.handleGeometryChanged
        )
        self.geometryComboBox.setDisabled(True)

        self.upstreamSpinBox.setValue(self.sample.upstreamThickness)
        self.upstreamSpinBox.valueChanged.connect(
            self.handleUpstreamThicknessChanged
        )
        self.downstreamSpinBox.setValue(self.sample.downstreamThickness)
        self.downstreamSpinBox.valueChanged.connect(
            self.handleDownstreamThicknessChanged
        )

        self.densitySpinBox.setValue(self.sample.density)
        for du in UnitsOfDensity:
            self.densityUnitsComboBox.addItem(du.name, du)
        self.densityUnitsComboBox.setCurrentIndex(
            self.sample.densityUnits.value
        )
        self.densityUnitsComboBox.currentIndexChanged.connect(
            self.handleDensityUnitsChanged
        )

        crossSectionSources = ["TABLES", "TRANSMISSION MONITOR", "FILENAME"]
        if "TABLES" in self.sample.totalCrossSectionSource:
            index = 0
        elif "TRANSMISSION" in self.sample.totalCrossSectionSource:
            index = 1
        else:
            index = 2
        self.totalCrossSectionComboBox.addItems(crossSectionSources)
        self.totalCrossSectionComboBox.setCurrentIndex(index)
        self.totalCrossSectionComboBox.currentIndexChanged.connect(
            self.handleCrossSectionSourceChanged
        )

        self.tweakFactorSpinBox.setValue(self.sample.sampleTweakFactor)
        self.tweakFactorSpinBox.valueChanged.connect(
            self.handleTweakFactorChanged
        )

        self.topHatWidthSpinBox.setValue(self.sample.topHatW)
        self.topHatWidthSpinBox.valueChanged.connect(
            self.handleTopHatWidthChanged
        )
        self.minSpinBox.setValue(self.sample.minRadFT)
        self.minSpinBox.valueChanged.connect(self.handleMinChanged)
        self.maxSpinBox.setValue(self.sample.maxRadFT)
        self.maxSpinBox.valueChanged.connect(self.handleMaxChanged)

        self.broadeningFunctionSpinBox.setValue(self.sample.grBroadening)
        self.broadeningFunctionSpinBox.valueChanged.connect(
            self.handleBroadeningFunctionChanged
        )
        self.broadeningPowerSpinBox.setValue(self.sample.powerForBroadening)
        self.broadeningPowerSpinBox.valueChanged.connect(
            self.handleBroadeningPowerChanged
        )

        self.stepSizeSpinBox.setValue(self.sample.stepSize)
        self.stepSizeSpinBox.valueChanged.connect(self.handleStepSizeChanged)

        self.scatteringFileLineEdit.setText(self.sample.fileSelfScattering)
        self.scatteringFileLineEdit.textChanged.connect(
            self.handleSelfScatteringFileChanged
        )

        for n in NormalisationType:
            self.normaliseToComboBox.addItem(n.name, n)
        self.normaliseToComboBox.setCurrentIndex(
            self.sample.normaliseTo.value
        )
        self.normaliseToComboBox.currentIndexChanged.connect(
            self.handleNormaliseToChanged
        )

        for u in OutputUnits:
            self.outputUnitsComboBox.addItem(u.name, u)
        self.outputUnitsComboBox.setCurrentIndex(
            self.sample.outputUnits.value
        )
        self.outputUnitsComboBox.currentIndexChanged.connect(
            self.handleOutputUnitsChanged
        )

        self.geometryInfoStack.setCurrentIndex(geometry.value)

        self.angleOfRotationSpinBox.setValue(self.sample.angleOfRotation)
        self.angleOfRotationSpinBox.valueChanged.connect(
            self.handleAngleOfRotationChanged
        )
        self.sampleWidthSpinBox.setValue(self.sample.sampleWidth)
        self.sampleWidthSpinBox.valueChanged.connect(
            self.handleSampleWidthChanged
        )
        self.sampleHeightSpinBox.setValue(self.sample.sampleHeight)
        self.sampleHeightSpinBox.valueChanged.connect(
            self.handleSampleHeightChanged
        )

        self.correctionFactorSpinBox.setValue(
            self.sample.normalisationCorrectionFactor
        )
        self.correctionFactorSpinBox.valueChanged.connect(
            self.handleCorrectionFactorChanged
        )
        self.scatteringFractionSpinBox.setValue(
            self.sample.scatteringFraction
        )
        self.scatteringFractionSpinBox.valueChanged.connect(
            self.handleScatteringFractionChanged
        )
        self.attenuationCoefficientSpinBox.setValue(
            self.sample.attenuationCoefficient
        )
        self.attenuationCoefficientSpinBox.valueChanged.connect(
            self.handleAttenuationCoefficientChanged
        )
