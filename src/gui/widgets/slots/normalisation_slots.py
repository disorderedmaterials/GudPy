from src.gudrun_classes.enums import (
    Geometry, CrossSectionSource, UnitsOfDensity
)
from src.gudrun_classes import config
from PySide6.QtWidgets import QFileDialog


class NormalisationSlots():

    def __init__(self, widget, parent):
        self.widget = widget
        self.parent = parent
        self.setupNormalisationSlots()

    def setNormalisation(self, normalisation):
        self.normalisation = normalisation

        self.widgetsRefreshing = True

        self.updateDataFilesList()

        self.updateBgDataFilesList()

        self.widget.periodNoSpinBox.setValue(self.normalisation.periodNumber)
        self.widget.backgroundPeriodNoSpinBox.setValue(
            self.normalisation.periodNumberBg
        )

        self.widget.normalisationGeometryComboBox.setCurrentIndex(
            self.normalisation.geometry.value
        )

        self.widget.geometryInfoStack.setCurrentIndex(
            self.normalisation.geometry.value
        )

        # Setup the widgets and slots for the density.
        self.widget.densitySpinBox.setValue(self.normalisation.density)

        self.widget.densityUnitsComboBox.setCurrentIndex(
            self.normalisation.densityUnits.value
        )

        self.widget.upstreamSpinBox.setValue(
            self.normalisation.upstreamThickness
        )
        self.widget.downstreamSpinBox.setValue(
            self.normalisation.downstreamThickness
        )

        self.widget.innerRadiiSpinBox.setValue(self.normalisation.innerRadius)
        self.widget.outerRadiiSpinBox.setValue(self.normalisation.outerRadius)

        self.widget.totalCrossSectionComboBox.setCurrentIndex(
            self.normalisation.totalCrossSectionSource.value
        )
        self.widget.crossSectionFileLineEdit.setText(
            self.normalisation.crossSectionFilename
        )
        self.widget.crossSectionFileWidget.setVisible(
            self.normalisation.totalCrossSectionSource ==
            CrossSectionSource.FILE
        )

        self.widget.forceCorrectionsCheckBox.setChecked(
            self.normalisation.forceCalculationOfCorrections
        )
        self.widget.placzekCorrectionSpinBox.setValue(
            self.normalisation.tempForNormalisationPC
        )
        self.widget.differentialCrossSectionFileLineEdit.setText(
            self.normalisation.normalisationDifferentialCrossSectionFile
        )

        self.widget.smoothingDegreeSpinBox.setValue(
            self.normalisation.normalisationDegreeSmoothing
        )
        self.widget.lowerLimitSmoothingSpinBox.setValue(
            self.normalisation.lowerLimitSmoothedNormalisation
        )
        self.widget.minNormalisationSignalSpinBox.setValue(
            self.normalisation.minNormalisationSignalBR
        )
        self.updateCompositionTable()
        # Release the lock
        self.widgetsRefreshing = False

    def setupNormalisationSlots(self):
        self.widget.dataFilesList.itemChanged.connect(
            self.handleDataFilesAltered
        )
        self.widget.dataFilesList.itemEntered.connect(
            self.handleDataFileInserted
        )

        self.widget.addDataFileButton.clicked.connect(
            lambda: self.addDataFiles(
                self.widget.dataFilesList,
                "Add data files",
                f"{self.parent.gudrunFile.instrument.dataFileType}"
                f" (*.{self.parent.gudrunFile.instrument.dataFileType})",
            )
        )

        self.widget.removeDataFileButton.clicked.connect(
            lambda: self.removeDataFile(
                self.widget.dataFilesList, self.normalisation.dataFiles
            )
        )

        self.widget.backgroundDataFilesList.itemChanged.connect(
            self.handleBgDataFilesAltered
        )
        self.widget.backgroundDataFilesList.itemEntered.connect(
            self.handleBgDataFileInserted
        )

        self.widget.addBackgroundDataFileButton.clicked.connect(
            lambda: self.addBgDataFiles(
                self.widget.backgroundDataFilesList,
                "Add background data files",
                f"{self.parent.gudrunFile.instrument.dataFileType}"
                f" (*.{self.parent.gudrunFile.instrument.dataFileType})",
            )
        )

        self.widget.removeBackgroundDataFileButton.clicked.connect(
            lambda: self.removeBgDataFile(
                self.widget.backgroundDataFilesList,
                self.normalisation.dataFilesBg
            )
        )

        self.widget.periodNoSpinBox.valueChanged.connect(
            self.handlePeriodNoChanged
        )
        self.widget.backgroundPeriodNoSpinBox.valueChanged.connect(
            self.handlePeriodNoBgChanged
        )

        for g in Geometry:
            self.widget.normalisationGeometryComboBox.addItem(g.name, g)
        self.widget.normalisationGeometryComboBox.currentIndexChanged.connect(
            self.handleGeometryChanged
        )

        self.widget.densitySpinBox.valueChanged.connect(
            self.handleDensityChanged
        )

        for du in UnitsOfDensity:
            self.widget.densityUnitsComboBox.addItem(du.name, du)
        self.widget.densityUnitsComboBox.currentIndexChanged.connect(
            self.handleDensityUnitsChanged
        )

        # Setup the widgets and slots for geometry specific attributes.
        # Flatplate
        self.widget.upstreamSpinBox.valueChanged.connect(
            self.handleUpstreamThicknessChanged
        )
        self.widget.upstreamSpinBox.valueChanged.connect(
            self.handleDownstreamThicknessChanged
        )

        # Cylindrical
        self.widget.innerRadiiSpinBox.valueChanged.connect(
            self.handleInnerRadiiChanged
        )
        self.widget.outerRadiiSpinBox.valueChanged.connect(
            self.handleOuterRadiiChanged
        )

        # Setup the other normalisation configurations widgets and slots.
        for c in CrossSectionSource:
            self.widget.totalCrossSectionComboBox.addItem(c.name, c)
        self.widget.totalCrossSectionComboBox.currentIndexChanged.connect(
            self.handleTotalCrossSectionChanged
        )
        self.widget.browseCrossSectionFileButton.clicked.connect(
            self.handleBrowseCrossSectionFile
        )

        self.widget.forceCorrectionsCheckBox.stateChanged.connect(
            self.handleForceCorrectionsSwitched
        )
        self.widget.placzekCorrectionSpinBox.valueChanged.connect(
            self.handlePlaczekCorrectionChanged
        )

        self.widget.differentialCrossSectionFileLineEdit.textChanged.connect(
            self.handleDifferentialCrossSectionFileChanged
        )
        self.widget.browseDifferentialCrossSectionButton.clicked.connect(
            self.handleBrowseDifferentialCrossSectionFile
        )

        self.widget.smoothingDegreeSpinBox.valueChanged.connect(
            self.handleNormalisationDegreeSmoothingChanged
        )

        self.widget.lowerLimitSmoothingSpinBox.valueChanged.connect(
            self.handleLowerlimitSmoothingChanged
        )

        self.widget.minNormalisationSignalSpinBox.valueChanged.connect(
            self.handleMinNormalisationSignalChanged
        )

        # Setup the widgets and slots for the composition.
        self.widget.insertElementButton.clicked.connect(
            self.handleInsertElement
        )
        self.widget.removeElementButton.clicked.connect(
            self.handleRemoveElement
        )

        self.widget.insertNormalisationComponentButton.clicked.connect(
            self.handleInsertComponent
        )

        self.widget.removeNormalisationComponentButton.clicked.connect(
            self.handleRemoveComponent
        )

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
            self.parent.gudrunFile.purged = False

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
            self.parent.gudrunFile.purged = False

    def handleGeometryChanged(self, index):
        """
        Slot for handling change in sample geometry.
        Called when a currentIndexChanged signal is emitted,
        from the normalisationGeometryComboBox.
        Alters the normalisation geometry as such.
        Parameters
        ----------
        index : int
            The new current index of the normalisationGeometryComboBox.
        """
        if not self.widgetsRefreshing:
            self.parent.setModified()
        self.normalisation.geometry = (
            self.widget.normalisationGeometryComboBox.itemData(index)
        )
        if self.normalisation.geometry == Geometry.SameAsBeam:
            self.widget.geometryInfoStack.setCurrentIndex(
                config.geometry.value
            )
        else:
            self.widget.geometryInfoStack.setCurrentIndex(
                self.normalisation.geometry.value
            )

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
        self.normalisation.densityUnits = (
            self.widget.densityUnitsComboBox.itemData(index)
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
            self.widget.totalCrossSectionComboBox.itemData(index)
        )
        self.widget.crossSectionFileWidget.setVisible(
            self.normalisation.totalCrossSectionSource ==
            CrossSectionSource.FILE
        )
        if not self.widgetsRefreshing:
            self.parent.setModified()

    def handleCrossSectionFileChanged(self, value):
        """
        Slot for handling change in total cross section source file name.
        Called when a textChanged signal is emitted,
        from the crossSectionFileLineEdit.
        Alters the normalisation's total cross
        section source file name as such.
        Parameters
        ----------
        value : str
            The new text of the crossSectionFileLineEdit.
        """
        self.normalisation.crossSectionFilename = value
        if not self.widgetsRefreshing:
            self.parent.setModified()

    def handleBrowseCrossSectionFile(self):
        """
        Slot for browsing for a cross section source file.
        Called when a clicked signal is emitted,
        from the browseCrossSectionFileButton.
        Alters the corresponding line edit as such.
        as such.
        """
        filename, _ = QFileDialog.getOpenFileName(
            self.widget, "Total cross section source", "")
        if filename:
            self.widget.crossSectionFileLineEdit.setText(filename)

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
        filename, _ = QFileDialog.getOpenFileName(
            self.widget, "Normalisation differential cross section file", ""
        )
        if filename[0]:
            self.widget.differentialCrossSectionFileLineEdit.setText(
                filename
            )

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
            self.parent.gudrunFile.purged = False

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
            self.parent.gudrunFile.purged = False

    def updateDataFilesList(self):
        """
        Fills the data files list.
        """
        self.widget.dataFilesList.clear()
        self.widget.dataFilesList.addItems(
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
        if not self.widgetsRefreshing:
            self.parent.setModified()
            self.parent.gudrunFile.purged = False

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
            self.parent.gudrunFile.purged = False

    def updateBgDataFilesList(self):
        self.widget.backgroundDataFilesList.clear()
        self.widget.backgroundDataFilesList.addItems(
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
        paths = QFileDialog.getOpenFileNames(self.widget, title, ".", regex)
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

    def removeBgDataFile(self, target, dataFiles):
        self.removeFile(target, dataFiles)

    def updateCompositionTable(self):
        """
        Fills the composition list.
        """
        if config.USE_USER_DEFINED_COMPONENTS:
            self.updateRatioCompositions()
            self.widget.exactCompositionTab.setEnabled(False)
            self.widget.ratioCompositionTab.setEnabled(True)
            self.widget.normalisationCompositionTabs.setCurrentIndex(1)
            self.widget.normalisationRatioCompositionTable.model().dataChanged.connect(
                self.updateExactCompositions
            )
        else:
            self.updateExactCompositions()
            self.widget.exactCompositionTab.setEnabled(True)
            self.widget.ratioCompositionTab.setEnabled(False)
            self.widget.normalisationCompositionTabs.setCurrentIndex(0)
        if not self.widgetsRefreshing:
            self.parent.setModified()

    def updateRatioCompositions(self):
        self.widget.normalisationRatioCompositionTable.makeModel(
            self.normalisation.composition, self.parent.gudrunFile
        )

    def updateExactCompositions(self):
        self.widget.normalisationCompositionTable.makeModel(
            self.normalisation.composition.elements
        )


    def handleInsertElement(self):
        """
        Slot for handling insertion to the composition table.
        Called when a clicked signal is emitted, from the
        insertElementButton.
        """
        self.widget.normalisationCompositionTable.insertRow()
        if not self.widgetsRefreshing:
            self.parent.setModified()

    def handleRemoveElement(self):
        """
        Slot for removing elements from the composition table.
        Called when a clicked signal is emitted,
        from the removeElementButton.
        """
        self.widget.normalisationCompositionTable.removeRow(
            self.widget.normalisationCompositionTable
            .selectionModel().selectedRows()
        )
        if not self.widgetsRefreshing:
            self.parent.setModified()

    def handleInsertComponent(self):
        self.widget.normalisationRatioCompositionTable.insertRow()
        if not self.widgetsRefreshing:
            self.parent.setModified()
    
    def handleRemoveComponent(self):
        self.widget.normalisationRatioCompositionTable.removeRow(
            self.widget.normalisationRatioCompositionTable
            .selectionModel().selectedRows()
        )
        if not self.widgetsRefreshing:
            self.parent.setModified()