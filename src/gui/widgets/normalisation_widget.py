from src.scripts.utils import isnumeric
from src.gudrun_classes.element import Element
from src.gudrun_classes.enums import Geometry, UnitsOfDensity
from PyQt5.QtWidgets import QFileDialog, QTableWidget, QTableWidgetItem, QWidget
from PyQt5 import uic
from PyQt5.QtCore import Qt
import os


class NormalisationWidget(QWidget):
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
        Constructs all the necessary attributes
        for the NormalisationWidget object.
        Calls the initComponents method,
        to load the UI file and populate data.
        Parameters
        ----------
        normalisation : Normalisation
            Normalisation object belonging to the GudrunFile.
        parent : QWidget
            Parent widget.
        """
        self.normalisation = normalisation
        self.parent = parent

        super(NormalisationWidget, self).__init__(parent=self.parent)
        self.initComponents()

    def handlePeriodNoChanged(self, value):
        self.normalisation.periodNo = value

    def handlePeriodNoBgChanged(self, value):
        self.normalisation.periodNoBg = value

    def handleGeometryChanged(self, index):
        self.normalisation.geometry = self.geometryComboBox.itemData(index)

    def handleDensityUnitsChanged(self, index):
        self.normalisation.densityUnits = (
            self.densityUnitsComboBox.itemData(index)
        )

    def handleUpstreamThicknessChanged(self, value):
        self.normalisation.upstreamThickness = value

    def handleDownstreamThicknessChanged(self, value):
        self.normalisation.downstreamThickness = value

    def handleTotalCrossSectionChanged(self, index):
        self.normalisation.totalCrossSectionSource = (
            self.totalCrossSectionComboBox.itemData(index)
        )

    def handleForceCorrectionsSwitched(self, state):
        self.normalisation.forceCalculationsOfCorrections = state

    def handlePlaczekCorrectionChanged(self, value):
        self.normalisation.tempForNormalisationPC = value

    def handleDifferentialCrossSectionFileChanged(self, value):
        self.normalisation.normalisationDifferentialCrossSectionFile = value

    def handleNormalisationDegreeSmoothingChanged(self, value):
        self.normalisation.normalisationDegreeSmoothing = value

    def handleLowerlimitSmoothingChanged(self, value):
        self.normalisation.lowerLimitSmoothedNormalisation = value

    def handleMinNormalisationSignalChanged(self, value):
        self.normalisation.minNormalisationSignalBR = value

    def handleDataFilesAltered(self, item):
        index = item.row()
        value = item.text()
        if not value:
            self.normalisation.dataFiles.dataFiles.remove(index)
        else:
            self.normalisation.dataFiles.dataFiles[index] = value
        self.updateDataFilesList()

    def handleDataFileInserted(self, item):
        value = item.text()
        self.normalisation.dataFiles.dataFiles.append(value)

    def updateDataFilesList(self):
        self.dataFilesList.clear()
        self.dataFilesList.addItems(
            [df for df in self.normalisation.dataFiles.dataFiles]
        )

    def handleBgDataFilesAltered(self, item):
        index = item.row()
        value = item.text()
        if not value:
            self.normalisation.dataFilesBg.dataFiles.remove(index)
        else:
            self.normalisation.dataFilesBg.dataFiles[index] = value
        self.updateBgDataFilesList()

    def handleBgDataFileInserted(self, item):
        value = item.text()
        self.normalisation.dataFilesBg.dataFiles.append(value)

    def updateBgDataFilesList(self):
        self.backgroundDataFilesList.clear()
        self.backgroundDataFilesList.addItems(
            [df for df in self.normalisation.dataFilesBg.dataFiles]
        )

    def addFiles(self, target, title, regex):
        paths = QFileDialog.getOpenFileNames(self, title, '.', regex)
        for path in paths:
            if path:
                target.addItem(path)

    def addDataFiles(self, target, title, regex):
        self.addFiles(target, title, regex)
        self.handleDataFileInserted(target.item(target.count()-1))

    def addBgDataFiles(self, target, title, regex):
        self.addFiles(target, title, regex)
        self.handleBgDataFileInserted(target.item(target.count()-1))

    def removeFile(self, target, dataFiles):
        if target.currentIndex().isValid():
            remove = target.takeItem(target.currentRow()).text()
            dataFiles.dataFiles.remove(remove)

    def removeDataFile(self, target, dataFiles):
        self.removeFile(target, dataFiles)
        self.updateDataFilesList()

    def removeBgDataFile(self, target, dataFiles):
        self.removeFile(target, dataFiles)
        self.updateBgDataFilesList()

    def handleElementChanged(self, item):
        value = item.text()
        row = item.row()
        col = item.column()
        if row < len(self.normalisation.composition.elements):
            element = self.normalisation.composition.elements[row]
            attribute = {
                0: ("atomicSymbol", str),
                1: ("massNo", int),
                2: ("abundance", float)
            }[col]
            element.__dict__[attribute[0]] = attribute[1](value)
            self.normalisation.composition.elements[row] = element
        else:
            self.handleElementInserted(item)

    def handleElementInserted(self, item):
        row = item.row()
        print(item.text())
        atomicSymbol = self.normalisationCompositionTable.itemAt(row, 0).text()
        massNo = self.normalisationCompositionTable.itemAt(row, 1).text()
        abundance = self.normalisationCompositionTable.itemAt(row, 2).text()
        if len(atomicSymbol) and isnumeric(massNo) and isnumeric(abundance):
            print(atomicSymbol, massNo, abundance)
            element = Element(atomicSymbol, int(massNo), float(abundance))
            self.normalisation.composition.elements.append(element)

    def initComponents(self):
        """
        Loads the UI file for the NormalisationWidget object,
        and then populates the child widgets with their
        corresponding data from the attributes of the Normalisation object.
        """
        current_dir = os.path.dirname(os.path.realpath(__file__))
        uifile = os.path.join(current_dir, "ui_files/normalisationWidget.ui")
        uic.loadUi(uifile, self)

        self.updateDataFilesList()
        self.dataFilesList.itemChanged.connect(
            self.handleDataFilesAltered
        )
        self.dataFilesList.itemEntered.connect(
            self.handleDataFileInserted
        )

        self.addDataFileButton.clicked.connect(
            lambda: self.addDataFiles(
                self.dataFilesList,
                "Add data files",
                f"{self.parent.gudrunFile.instrument.dataFileType}"
                f" (*.{self.parent.gudrunFile.instrument.dataFileType})"
            )
        )

        self.removeDataFileButton.clicked.connect(
            lambda: self.removeDataFile(
                self.dataFilesList,
                self.normalisation.dataFiles
            )
        )

        self.updateBgDataFilesList()
        self.backgroundDataFilesList.itemChanged.connect(
            self.handleBgDataFilesAltered
        )
        self.backgroundDataFilesList.itemEntered.connect(
            self.handleBgDataFileInserted
        )

        self.addBackgroundDataFileButton.clicked.connect(
            lambda: self.addBgDataFiles(
                self.backgroundDataFilesList,
                "Add background data files",
                f"{self.parent.gudrunFile.instrument.dataFileType}"
                f" (*.{self.parent.gudrunFile.instrument.dataFileType})"
            )
        )

        self.removeBackgroundDataFileButton.clicked.connect(
            lambda: self.removeBgDataFile(
                self.backgroundDataFilesList,
                self.normalisation.dataFilesBg
            )
        )

        self.periodNoSpinBox.setValue(self.normalisation.periodNumber)
        self.periodNoSpinBox.valueChanged.connect(self.handlePeriodNoChanged)
        self.backgroundPeriodNoSpinBox.setValue(
            self.normalisation.periodNumberBg
        )
        self.backgroundPeriodNoSpinBox.valueChanged.connect(
            self.handlePeriodNoBgChanged
        )

        for i, element in enumerate(self.normalisation.composition.elements):
            self.normalisationCompositionTable.setItem(
                i, 0, QTableWidgetItem(str(element.atomicSymbol))
            )
            self.normalisationCompositionTable.setItem(
                i, 1, QTableWidgetItem(str(element.massNo))
            )
            self.normalisationCompositionTable.setItem(
                i, 2, QTableWidgetItem(str(element.abundance))
            )

        self.normalisationCompositionTable.itemChanged.connect(
            self.handleElementChanged
        )
        self.normalisationCompositionTable.itemEntered.connect(
            self.handleElementInserted
        )
        self.geometryComboBox.addItems([g.name for g in Geometry])
        self.geometryComboBox.setCurrentIndex(
            self.normalisation.geometry.value
        )
        self.geometryComboBox.currentIndexChanged.connect(
            self.handleGeometryChanged
        )

        self.densitySpinBox.setValue(self.normalisation.density)
        for du in UnitsOfDensity:
            self.densityUnitsComboBox.addItem(du.name, du)
        self.densityUnitsComboBox.setCurrentIndex(
            self.normalisation.densityUnits.value
        )
        self.densityUnitsComboBox.currentIndexChanged.connect(
            self.handleDensityUnitsChanged
        )

        self.upstreamSpinBox.setValue(
            self.normalisation.upstreamThickness
        )
        self.upstreamSpinBox.valueChanged.connect(
            self.handleUpstreamThicknessChanged
        )
        self.downstreamSpinBox.setValue(
            self.normalisation.downstreamThickness
        )
        self.upstreamSpinBox.valueChanged.connect(
            self.handleDownstreamThicknessChanged
        )

        crossSectionSources = ["TABLES", "TRANSMISSION MONITOR", "FILENAME"]
        if "TABLES" in self.normalisation.totalCrossSectionSource:
            index = 0
        elif "TRANSMISSION" in self.normalisation.totalCrossSectionSource:
            index = 1
        else:
            index = 2
        self.totalCrossSectionComboBox.addItems(crossSectionSources)
        self.totalCrossSectionComboBox.setCurrentIndex(index)
        self.totalCrossSectionComboBox.currentIndexChanged.connect(
            self.handleTotalCrossSectionChanged
        )

        self.forceCorrectionsCheckBox.setChecked(
            Qt.Checked
            if self.normalisation.forceCalculationOfCorrections
            else Qt.Unchecked
        )
        self.forceCorrectionsCheckBox.stateChanged.connect(
            self.handleForceCorrectionsSwitched
        )
        self.placzekCorrectionSpinBox.setValue(
            self.normalisation.tempForNormalisationPC
        )
        self.placzekCorrectionSpinBox.valueChanged.connect(
            self.handlePlaczekCorrectionChanged
        )
        self.differentialCrossSectionFileLineEdit.setText(
            self.normalisation.normalisationDifferentialCrossSectionFile
        )
        self.differentialCrossSectionFileLineEdit.textChanged.connect(
            self.handleDifferentialCrossSectionFileChanged
        )
        self.smoothingDegreeSpinBox.setValue(
            self.normalisation.normalisationDegreeSmoothing
        )
        self.smoothingDegreeSpinBox.valueChanged.connect(
            self.handleNormalisationDegreeSmoothingChanged
        )
        self.lowerLimitSmoothingSpinBox.setValue(
            self.normalisation.lowerLimitSmoothedNormalisation
        )
        self.lowerLimitSmoothingSpinBox.valueChanged.connect(
            self.handleLowerlimitSmoothingChanged
        )
        self.minNormalisationSignalSpinBox.setValue(
            self.normalisation.minNormalisationSignalBR
        )
        self.minNormalisationSignalSpinBox.valueChanged.connect(
                self.handleMinNormalisationSignalChanged
        )
