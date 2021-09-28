from src.gudrun_classes.enums import (
    CrossSectionSource, Geometry, UnitsOfDensity
)
from src.gudrun_classes import config
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
        Slot for handling change in the period number.
    handleGeometryChanged(index)
        Slot for handling change in the geometry.
    handleDensityUnitsChanged(index)
        Slot for handling change to the density units.
    handleUpstreamThicknessChanged(value)
        Slot for handling change in the upstream thickness.
    handleDownstreamThicknessChanged(value)
        Slot for handling change in the downstream thickness.
    handleInnerRadiiChanged(value)
        Slot for handling change in the inner radii.
    handleOuterRadiiChanged(value)
        Slot for handling change to the outer radii.
    handleDensityChanged(value)
        Slot for handling change in the density.
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
        if not self.widgetsRefreshing:
            self.parent.setModified()

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
        if not self.widgetsRefreshing:
            self.parent.setModified()

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
        if not self.widgetsRefreshing:
            self.parent.setModified()
        self.normalisation.geometry = self.geometryComboBox.itemData(index)
        if self.normalisation.geometry == Geometry.SameAsBeam:
            self.geometryInfoStack.setCurrentIndex(
                config.geometry.value
            )
        else:
            self.geometryInfoStack.setCurrentIndex(
                self.normalisation.geometry.value
            )
        # if not self.widgetsRefreshing:
        #     self.parent.setModified()
        #     if self.normalisation.geometry == Geometry.SameAsBeam:
        #         self.parent.updateGeometries()
        #         self.geometryComboBox.setCurrentIndex(index)
        #     else:
        #         self.geometryInfoStack.setCurrentIndex(
        #             self.normalisation.geometry.value
        #         )
        # self.normalisation.geometry = self.geometryComboBox.itemData(index)
        # self.geometryComboBox.setCurrentIndex(index)

    def handleDensityUnitsChanged(self, index):
        """
        Slot for handling change in density units.
        Called when a currentIndexChanged signal is emitted,
        from the densityUnitsComboBox.
        Alters the normalisation density units as such.
        Parameters
        ----------
        index : int
            The new current index of the densityUnitsComboBox.
        """
        self.normalisation.densityUnits = self.densityUnitsComboBox.itemData(
            index
        )
        if not self.widgetsRefreshing:
            self.parent.setModified()

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
        if not self.widgetsRefreshing:
            self.parent.setModified()

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
        if not self.widgetsRefreshing:
            self.parent.setModified()

    def handleInnerRadiiChanged(self, value):
        """
        Slot for handling change in the inner radii.
        Called when a valueChanged signal is emitted,
        from the innerRadiiSpinBox.
        Alters the normalisation's inner radius as such.
        Parameters
        ----------
        value : float
            The new value of the innerRadiiSpinBox.
        """
        self.normalisation.innerRadius = value
        if not self.widgetsRefreshing:
            self.parent.setModified()

    def handleOuterRadiiChanged(self, value):
        """
        Slot for handling change in the outer radii.
        Called when a valueChanged signal is emitted,
        from the outerRadiiSpinBox.
        Alters the normalisation's outer radius as such.
        Parameters
        ----------
        value : float
            The new value of the outerRadiiSpinBox.
        """
        self.normalisation.outerRadius = value
        if not self.widgetsRefreshing:
            self.parent.setModified()

    def handleDensityChanged(self, value):
        """
        Slot for handling change in the density.
        Called when a valueChanged signal is emitted,
        from the densitySpinBox.
        Alters the container's density as such.
        Parameters
        ----------
        value : float
            The new value of the densitySpinBox.
        """
        self.normalisation.density = value
        if not self.widgetsRefreshing:
            self.parent.setModified()

    def handleTotalCrossSectionChanged(self, index):
        """
        Slot for handling change in total cross section source.
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
        if not self.widgetsRefreshing:
            self.parent.setModified()

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
        if not self.widgetsRefreshing:
            self.parent.setModified()

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
        if not self.widgetsRefreshing:
            self.parent.setModified()

    def handleDifferentialCrossSectionFileChanged(self, value):
        """
        Slot for handling change to the differential cross section file name.
        Called when a textChanged signal is emitted,
        from the differentialCrossSectionFileLineEdit.
        Alters the normalisation's differential
        cross section file name as such.
        Parameters
        ----------
        value : str
            The new value of the differentialCrossSectionFileLineEdit.
        """
        self.normalisation.normalisationDifferentialCrossSectionFile = value
        if not self.widgetsRefreshing:
            self.parent.setModified()

    def handleBrowseDifferentialCrossSectionFile(self):
        """
        Slot for handling browsing for a differential cross section file.
        Called when a cliced signal is emitted,
        from the browseDifferentialCrossSectionButton.
        Alters the normalisation's differential
        cross section file name as such.
        """
        filename = QFileDialog.getOpenFileName(
            self, "Normalisation differential cross section file", ""
        )
        if filename[0]:
            self.differentialCrossSectionFileLineEdit.setText(filename[0])

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
        if not self.widgetsRefreshing:
            self.parent.setModified()

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
        if not self.widgetsRefreshing:
            self.parent.setModified()

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
        if not self.widgetsRefreshing:
            self.parent.setModified()

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
        if not self.widgetsRefreshing:
            self.parent.setModified()

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
        if not self.widgetsRefreshing:
            self.parent.setModified()

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
        if not self.widgetsRefreshing:
            self.parent.setModified()

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
            if not self.widgetsRefreshing:
                self.parent.setModified()

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
        if not self.widgetsRefreshing:
            self.parent.setModified()

    def handleInsertElement(self):
        """
        Slot for handling insertion to the composition table.
        Called when a clicked signal is emitted, from the
        insertElementButton.
        """
        self.normalisationCompositionTable.insertRow()
        if not self.widgetsRefreshing:
            self.parent.setModified()

    def handleRemoveElement(self):
        """
        Slot for removing files from the data files list.
        Called when a clicked signal is emitted,
        from the removeDataFileButton.
        """
        self.normalisationCompositionTable.removeRow(
            self.normalisationCompositionTable.selectionModel().selectedRows()
        )
        if not self.widgetsRefreshing:
            self.parent.setModified()

    def initComponents(self):
        """
        Loads the UI file for the NormalisationWidget object,
        and then populates the child widgets with their
        corresponding data from the attributes of the Normalisation object.
        """
        # Acquire the lock
        self.widgetsRefreshing = True
        current_dir = os.path.dirname(os.path.realpath(__file__))
        uifile = os.path.join(current_dir, "ui_files/normalisationWidget.ui")
        uic.loadUi(uifile, self)

        # Setup widgets and slots for the data files
        # and background data files.
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

        # Setup widgets and slots for the period numbers.
        self.periodNoSpinBox.setValue(self.normalisation.periodNumber)
        self.periodNoSpinBox.valueChanged.connect(self.handlePeriodNoChanged)
        self.backgroundPeriodNoSpinBox.setValue(
            self.normalisation.periodNumberBg
        )
        self.backgroundPeriodNoSpinBox.valueChanged.connect(
            self.handlePeriodNoBgChanged
        )

        # Setup widgets and slots for geometry.
        for g in Geometry:
            if self.geometryComboBox.findText(g.name) == -1:
                self.geometryComboBox.addItem(g.name, g)
        self.geometryComboBox.setCurrentIndex(
            self.normalisation.geometry.value
        )
        self.geometryComboBox.currentIndexChanged.connect(
            self.handleGeometryChanged
        )

        # Ensure the correct attributes are being
        # shown for the correct geometry.
        self.geometryInfoStack.setCurrentIndex(
            self.normalisation.geometry.value
        )

        # Setup the widgets and slots for the density.
        self.densitySpinBox.setValue(self.normalisation.density)
        self.densitySpinBox.valueChanged.connect(
            self.handleDensityChanged
        )

        for du in UnitsOfDensity:
            if self.densityUnitsComboBox.findText(du.name) == -1:
                self.densityUnitsComboBox.addItem(du.name, du)
        self.densityUnitsComboBox.setCurrentIndex(
            self.normalisation.densityUnits.value
        )
        self.densityUnitsComboBox.currentIndexChanged.connect(
            self.handleDensityUnitsChanged
        )

        # Setup the widgets and slots for geometry specific attributes.
        # Flatplate
        self.upstreamSpinBox.setValue(self.normalisation.upstreamThickness)
        self.upstreamSpinBox.valueChanged.connect(
            self.handleUpstreamThicknessChanged
        )
        self.downstreamSpinBox.setValue(self.normalisation.downstreamThickness)
        self.upstreamSpinBox.valueChanged.connect(
            self.handleDownstreamThicknessChanged
        )

        # Cylindrical
        self.innerRadiiSpinBox.setValue(self.normalisation.innerRadius)
        self.innerRadiiSpinBox.valueChanged.connect(
            self.handleInnerRadiiChanged
        )
        self.outerRadiiSpinBox.setValue(self.normalisation.outerRadius)
        self.outerRadiiSpinBox.valueChanged.connect(
            self.handleOuterRadiiChanged
        )

        # Setup the other normalisation configurations widgets and slots.
        for c in CrossSectionSource:
            if self.totalCrossSectionComboBox.findText(c.name) == -1:
                self.totalCrossSectionComboBox.addItem(c.name, c)
        self.totalCrossSectionComboBox.setCurrentIndex(
            self.normalisation.totalCrossSectionSource.value
        )
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
        self.browseDifferentialCrossSectionButton.clicked.connect(
            self.handleBrowseDifferentialCrossSectionFile
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

        # Setup the widgets and slots for the composition.
        self.updateCompositionTable()
        self.insertElementButton.clicked.connect(self.handleInsertElement)
        self.removeElementButton.clicked.connect(self.handleRemoveElement)
        # Release the lock
        self.widgetsRefreshing = False
