from src.gudrun_classes.enums import Geometry, UnitsOfDensity
from PyQt5.QtWidgets import (
    QFileDialog,
    QWidget,
)
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
    handlePeriodNoChanged(value)
        
    handlePeriodNoChanged(value)
        Slot for handling change in the period number.
    handleGeometryChanged(index)
        Slot for handling change in the geometry.
    handleDensityUnitsChanged(index)
    handleUpstreamThicknessChanged(value)
        Slot for handling change in the upstream thickness.
    handleDownstreamThicknessChanged(value)
        Slot for handling change in the downstream thickness.
    handleTotalCrossSectionChanged(index)
        Slot for handling change in the total cross section source.
    handleForceCorrectionsSwitched(state)
        Slot for handling switching forcing correction calculations on/off.
    handlePlaczekCorrectionChanged(value)
        Slot for handling change in the temperature for Placzek corrections.
    handleDifferentialCrossSectionFileChanged(value)
        Slot for handling change in the differential cross section file name.
    handleNormalisationDegreeSmoothingChanged(value)
        Slot for handling change in the degree for smoothing of normalisation.
    handleLowerlimitSmoothingChanged(value)
        Slot for handling change in the minimum accepted
        value for smoothed Vanadium.
    handleMinNormalisationSignalChanged(value)
        Slot for handling change in the vanadium signal to background
        acceptance ratio.
    handleDataFilesAltered(item)
        Slot for handling changes to the data files list.
    handleDataFileInserted(item)
        Slot for handling insertion to the data files list.
    updateDataFilesList()
        Fills the data files list.    
    handleBgDataFilesAltered(item)
        Slot for handling changes to the background data files list.
    handleBgDataFileInserted(item)
        Slot for handling insertion to the background data files list.
    updateBgDataFilesList()
        Fills the background data files list.
    addFiles(target, title, regex)
        Slot for adding files to a target list.
    addDataFiles(target, title, regex)
        Slot for adding files to the data files list.
    addBgDataFiles(target, title, regex)
        Slot for adding files to the background data files list.
    removeFile(target, dataFiles)
        Slot for removing data files from a target list.
    removeDataFile(target, dataFiles)
        Slot for removing data files from the list.
    removeBgDataFile(target, dataFiles)
        Slot for removing background data from the list.
    updateCompositionTable()
        Fills the composition table.
    handleInsertElement()
        Slot for handling insertion to the composition table.
    handleRemoveElement()
        Slot for removing the selected element from the composition table.
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
        """
        Slot for handling change in the period number.
        Called when a valueChanged signal is emitted,
        from the periodNoSpinBox.
        Alters the normalisation's period number as such.
        Parameters
        ----------
        value : float
            The new value of the periodNoSpinBox.
        """
        self.normalisation.periodNo = value

    def handlePeriodNoBgChanged(self, value):
        """
        Slot for handling change in the background period number.
        Called when a valueChanged signal is emitted,
        from the periodNoSpinBox.
        Alters the normalisation's background period number as such.
        Parameters
        ----------
        value : float
            The new value of the periodNoSpinBox.
        """
        self.normalisation.periodNoBg = value

    def handleGeometryChanged(self, index):
        """
        Slot for handling change in sample geometry.
        Called when a currentIndexChanged signal is emitted,
        from the geometryComboBox.
        Alters the normalisation geometry as such.
        Parameters
        ----------
        index : int
            The new current index of the geometryComboBox.
        """
        self.normalisation.geometry = self.geometryComboBox.itemData(index)

    def handleDensityUnitsChanged(self, index):
        self.normalisation.densityUnits = self.densityUnitsComboBox.itemData(
            index
        )

    def handleUpstreamThicknessChanged(self, value):
        """
        Slot for handling change in the upstream thickness.
        Called when a valueChanged signal is emitted,
        from the upstreamSpinBox.
        Alters the normalisation's upstream thickness as such.
        Parameters
        ----------
        value : float
            The new value of the upstreamSpinBox.
        """
        self.normalisation.upstreamThickness = value

    def handleDownstreamThicknessChanged(self, value):
        """
        Slot for handling change in the downstream thickness.
        Called when a valueChanged signal is emitted,
        from the downstreamSpinBox.
        Alters the normalisation's downstream thickness as such.
        Parameters
        ----------
        value : float
            The new value of the downstreamSpinBox.
        """
        self.normalisation.downstreamThickness = value

    def handleTotalCrossSectionChanged(self, index):
        """
        Slot for handling change in total cross ection source.
        Called when a currentIndexChanged signal is emitted,
        from the totalCrossSectionComboBox.
        Alters the normalisation's total cross section source as such.
        Parameters
        ----------
        index : int
            The new current index of the totalCrossSectionComboBox.
        """
        self.normalisation.totalCrossSectionSource = (
            self.totalCrossSectionComboBox.itemData(index)
        )

    def handleForceCorrectionsSwitched(self, state):
        """
        Slot for handling switching forcing correction calculations on/off.
        Called when a stateChanged signal is emitted,
        from the forceCorrectionsCheckBox.
        Alters the normalisation's forcing calculations of
        corrections as such.
        Parameters
        ----------
        state : int
            The new state of the forceCorrectionsCheckBox (1: True, 0: False)
        """
        self.normalisation.forceCalculationsOfCorrections = state

    def handlePlaczekCorrectionChanged(self, value):
        """
        Slot for handling change in the temperature for placzek corrections.
        Called when a valueChanged signal is emitted,
        from the placzekCorrectionSpinBox.
        Alters the normalisation's temperature for placzek
        corrections as such.
        Parameters
        ----------
        value : float
            The new value of the placzekCorrectionSpinBox.
        """
        self.normalisation.tempForNormalisationPC = value

    def handleDifferentialCrossSectionFileChanged(self, value):
        """
        Slot for handling change to the differential cross section file name.
        Called when a textChanged signal is emitted,
        from the handleDifferentialCrossSectionFileChanged.
        Alters the normalisation's differential cross section file name as such.
        Parameters
        ----------
        value : str
            The new value of the handleDifferentialCrossSectionFileChanged.
        """
        self.normalisation.normalisationDifferentialCrossSectionFile = value

    def handleNormalisationDegreeSmoothingChanged(self, value):
        """
        Slot for handling change in the degree for smoothing of normalisation.
        Called when a valueChanged signal is emitted,
        from the smoothingDegreeSpinBox.
        Alters the normalisation's degree of smoothing as such.
        Parameters
        ----------
        value : float
            The new value of the smoothingDegreeSpinBox.
        """
        self.normalisation.normalisationDegreeSmoothing = value

    def handleLowerlimitSmoothingChanged(self, value):
        """
        Slot for handling change in the minimum accepted
        value for smoothed Vanadium.
        Called when a valueChanged signal is emitted,
        from the lowerLimitSmoothingSpinBox.
        Alters the normalisation's degree of smoothing as such.
        Parameters
        ----------
        value : float
            The new value of the lowerLimitSmoothingSpinBox.
        """
        self.normalisation.lowerLimitSmoothedNormalisation = value

    def handleMinNormalisationSignalChanged(self, value):
        """
        Slot for handling change in the vanadium signal to background
        acceptance ratio.
        Called when a valueChanged signal is emitted,
        from the minNormalisationSignalSpinBox.
        Alters the normalisation's vanadium signal to background acceptance
        ratio as such.
        Parameters
        ----------
        value : float
            The new value of the minNormalisationSignalSpinBox.
        """
        self.normalisation.minNormalisationSignalBR = value

    def handleDataFilesAltered(self, item):
        """
        Slot for handling an item in the data files list being changed.
        Called when an itemChanged signal is emitted,
        from the dataFilesList.
        Alters the normalisation's data files as such.
        Parameters
        ----------
        item : QListWidgetItem
            The item altered.
        """
        index = item.row()
        value = item.text()
        if not value:
            self.normalisation.dataFiles.dataFiles.remove(index)
        else:
            self.normalisation.dataFiles.dataFiles[index] = value
        self.updateDataFilesList()

    def handleDataFileInserted(self, item):
        """
        Slot for handling an item in the data files list being entered.
        Called when an itemEntered signal is emitted,
        from the dataFilesList.
        Alters the normalisation's data files as such.
        Parameters
        ----------
        item : QListWidgetItem
            The item entered.
        """
        value = item.text()
        self.normalisation.dataFiles.dataFiles.append(value)

    def updateDataFilesList(self):
        """
        Fills the data files list.
        """
        self.dataFilesList.clear()
        self.dataFilesList.addItems(
            [df for df in self.normalisation.dataFiles.dataFiles]
        )

    def handleBgDataFilesAltered(self, item):
        """
        Slot for handling an item in the background data files
        list being entered.
        Called when an itemEntered signal is emitted,
        from the backgroundDataFilesList.
        Alters the normalisation's data files as such.
        Parameters
        ----------
        item : QListWidgetItem
            The item entered.
        """
        index = item.row()
        value = item.text()
        if not value:
            self.normalisation.dataFilesBg.dataFiles.remove(index)
        else:
            self.normalisation.dataFilesBg.dataFiles[index] = value
        self.updateBgDataFilesList()

    def handleBgDataFileInserted(self, item):
        """
        Slot for handling an item in the background data files
        list being inserted.
        Called when an itemEntered signal is emitted,
        from the backgroundDataFilesList.
        Alters the normalisation's data files as such.
        Parameters
        ----------
        item : QListWidgetItem
            The item entered.
        """
        value = item.text()
        self.normalisation.dataFilesBg.dataFiles.append(value)

    def updateBgDataFilesList(self):
        self.backgroundDataFilesList.clear()
        self.backgroundDataFilesList.addItems(
            [df for df in self.normalisation.dataFilesBg.dataFiles]
        )

    def addFiles(self, target, title, regex):
        """
        Helper method for adding files to the target data files list.
        Parameters
        ----------
        target : QListWidget
            Target widget to add to.
        title : str
            Window title for QFileDialog.
        regex : str
            Regex-like expression to use for specifying file types.
        """
        paths = QFileDialog.getOpenFileNames(self, title, ".", regex)
        for path in paths:
            if path:
                target.addItem(path)

    def addDataFiles(self, target, title, regex):
        """
        Slot for adding files to the data files list.
        Called when a clicked signal is emitted,
        from the addDataFileButton.
        Parameters
        ----------
        target : QListWidget
            Target widget to add to.
        title : str
            Window title for QFileDialog.
        regex : str
            Regex-like expression to use for specifying file types.
        """
        self.addFiles(target, title, regex)
        self.handleDataFileInserted(target.item(target.count() - 1))

    def addBgDataFiles(self, target, title, regex):
        """
        Slot for adding files to the background data files list.
        Called when a clicked signal is emitted,
        from the addBackgroundDataFileButton.
        Parameters
        ----------
        target : QListWidget
            Target widget to add to.
        title : str
            Window title for QFileDialog.
        regex : str
            Regex-like expression to use for specifying file types.
        """
        self.addFiles(target, title, regex)
        self.handleBgDataFileInserted(target.item(target.count() - 1))

    def removeFile(self, target, dataFiles):
        """
        Slot for removing files from the data files list.
        Called when a clicked signal is emitted,
        from the removeDataFileButton.
        """
        if target.currentIndex().isValid():
            remove = target.takeItem(target.currentRow()).text()
            dataFiles.dataFiles.remove(remove)

    def removeDataFile(self, target, dataFiles):
        self.removeFile(target, dataFiles)
        self.updateDataFilesList()

    def removeBgDataFile(self, target, dataFiles):
        self.removeFile(target, dataFiles)
        self.updateBgDataFilesList()

    def updateCompositionTable(self):
        """
        Fills the composition list.
        """
        self.normalisationCompositionTable.makeModel(
            self.normalisation.composition.elements
        )

    def handleInsertElement(self):
        """
        Slot for handling insertion to the composition table.
        Called when a clicked signal is emitted, from the
        insertElementButton.
        """
        self.normalisationCompositionTable.insertRow()

    def handleRemoveElement(self):
        """
        Slot for removing files from the data files list.
        Called when a clicked signal is emitted,
        from the removeDataFileButton.
        """
        self.normalisationCompositionTable.removeRow(
            self.normalisationCompositionTable.selectionModel().selectedRows()
        )

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
        self.dataFilesList.itemChanged.connect(self.handleDataFilesAltered)
        self.dataFilesList.itemEntered.connect(self.handleDataFileInserted)

        self.addDataFileButton.clicked.connect(
            lambda: self.addDataFiles(
                self.dataFilesList,
                "Add data files",
                f"{self.parent.gudrunFile.instrument.dataFileType}"
                f" (*.{self.parent.gudrunFile.instrument.dataFileType})",
            )
        )

        self.removeDataFileButton.clicked.connect(
            lambda: self.removeDataFile(
                self.dataFilesList, self.normalisation.dataFiles
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
                f" (*.{self.parent.gudrunFile.instrument.dataFileType})",
            )
        )

        self.removeBackgroundDataFileButton.clicked.connect(
            lambda: self.removeBgDataFile(
                self.backgroundDataFilesList, self.normalisation.dataFilesBg
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

        self.upstreamSpinBox.setValue(self.normalisation.upstreamThickness)
        self.upstreamSpinBox.valueChanged.connect(
            self.handleUpstreamThicknessChanged
        )
        self.downstreamSpinBox.setValue(self.normalisation.downstreamThickness)
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

        self.updateCompositionTable()
        self.insertElementButton.clicked.connect(self.handleInsertElement)
        self.removeElementButton.clicked.connect(self.handleRemoveElement)
