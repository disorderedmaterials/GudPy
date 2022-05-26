import os
from PySide6.QtWidgets import QFileDialog

from core.enums import (
    Geometry, CrossSectionSource, UnitsOfDensity, Instruments
)
from core import config


class NormalisationSlots():

    def __init__(self, widget, parent):
        self.widget = widget
        self.parent = parent
        self.setupNormalisationSlots()

    def setNormalisation(self, normalisation):
        self.normalisation = normalisation
        self.widgetsRefreshing = True

        self.widget.dataFilesList.makeModel(
            self.normalisation.dataFiles.dataFiles
        )
        self.widget.backgroundDataFilesList.makeModel(
            self.normalisation.dataFilesBg.dataFiles
        )

        self.widget.dataFilesList.model().dataChanged.connect(
            self.handleDataFilesAltered
        )
        self.widget.dataFilesList.model().rowsRemoved.connect(
            self.handleDataFilesAltered
        )

        self.widget.backgroundDataFilesList.model().dataChanged.connect(
            self.handleDataFilesBgAltered
        )
        self.widget.backgroundDataFilesList.model().rowsRemoved.connect(
            self.handleDataFilesBgAltered
        )

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

        total = (
            self.normalisation.upstreamThickness +
            self.normalisation.downstreamThickness
        )
        self.widget.totalNormalisationThicknessLabel.setText(
            f"Total: {total} cm"
        )

        self.widget.normalisationAngleOfRotationSpinBox.setValue(
            self.normalisation.angleOfRotation
        )
        self.widget.normalisationSampleWidthSpinBox.setValue(
            self.normalisation.sampleWidth
        )

        self.widget.innerRadiiSpinBox.setValue(self.normalisation.innerRadius)
        self.widget.outerRadiiSpinBox.setValue(self.normalisation.outerRadius)

        self.widget.normalisationSampleHeightSpinBox.setValue(
            self.normalisation.sampleHeight
        )

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
                self.widget.dataFilesList
            )
        )

        self.widget.duplicateDataFileButton.clicked.connect(
            lambda: self.duplicateDataFile(
                self.widget.dataFilesList
            )
        )

        self.widget.addBackgroundDataFileButton.clicked.connect(
            lambda: self.addDataFiles(
                self.widget.backgroundDataFilesList,
                "Add data files",
                f"{self.parent.gudrunFile.instrument.dataFileType}"
                f" (*.{self.parent.gudrunFile.instrument.dataFileType})",
            )
        )

        self.widget.removeBackgroundDataFileButton.clicked.connect(
            lambda: self.removeDataFile(
                self.widget.backgroundDataFilesList
            )
        )

        self.widget.duplicateBackgroundDataFileButton.clicked.connect(
            lambda: self.duplicateDataFile(
                self.widget.backgroundDataFilesList
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

        self.widget.normalisationAngleOfRotationSpinBox.valueChanged.connect(
            self.handleAngleOfRotationChanged
        )
        self.widget.normalisationSampleWidthSpinBox.valueChanged.connect(
            self.handleSampleWidthChanged
        )

        # Cylindrical
        self.widget.innerRadiiSpinBox.valueChanged.connect(
            self.handleInnerRadiiChanged
        )
        self.widget.outerRadiiSpinBox.valueChanged.connect(
            self.handleOuterRadiiChanged
        )

        self.widget.normalisationSampleHeightSpinBox.valueChanged.connect(
            self.handleSampleHeightChanged
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
        self.normalisation.periodNumber = value
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
        self.normalisation.periodNumberBg = value
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
        total = (
            self.normalisation.upstreamThickness +
            self.normalisation.downstreamThickness
        )
        self.widget.totalNormalisationThicknessLabel.setText(
            f"Total: {total} cm"
        )
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
        total = (
            self.normalisation.upstreamThickness +
            self.normalisation.downstreamThickness
        )
        self.widget.totalNormalisationThicknessLabel.setText(
            f"Total: {total} cm"
        )
        if not self.widgetsRefreshing:
            self.parent.setModified()

    def handleAngleOfRotationChanged(self, value):
        """
        Slot for handling change in the angle of rotation.
        Called when a valueChanged signal is emitted,
        from the normalisationAngleOfRotationSpinBox.
        Alters the normalisation's angle of rotation as such.
        Parameters
        ----------
        value : float
            The new value of the normalisationAngleOfRotationSpinBox.
        """
        self.normalisation.angleOfRotation = value
        if not self.widgetsRefreshing:
            self.parent.setModified()

    def handleSampleWidthChanged(self, value):
        """
        Slot for handling change in the angle of rotation.
        Called when a valueChanged signal is emitted,
        from the normalisationSampleWidthSpinBox.
        Alters the normalisation's sample width as such.
        Parameters
        ----------
        value : float
            The new value of the normalisationSampleWidthSpinBox.
        """
        self.normalisation.sampleWidth = value
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

    def handleSampleHeightChanged(self, value):
        """
        Slot for handling change in the angle of rotation.
        Called when a valueChanged signal is emitted,
        from the normalisationSampleHeightSpinBox.
        Alters the normalisation's sample height as such.
        Parameters
        ----------
        value : float
            The new value of the normalisationSampleHeightSpinBox.
        """
        self.normalisation.sampleHeight = value
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
        self.normalisation.forceCalculationOfCorrections = bool(state)
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
        dir = os.path.join(
            self.parent.gudrunFile.instrument.GudrunStartFolder,
            self.parent.gudrunFile.instrument.startupFileFolder,
            Instruments(self.parent.gudrunFile.instrument.name.value).name
        )
        filename, _ = QFileDialog.getOpenFileName(
            self.widget, "Normalisation differential cross section file", dir
        )
        if filename:
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

    def handleDataFilesAltered(self):
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
        if not self.widgetsRefreshing:
            self.parent.setModified()
            self.parent.gudrunFile.purged = False
            self.normalisation.dataFiles.dataFiles = (
                self.widget.dataFilesList.model().stringList()
            )

    def handleDataFilesBgAltered(self):
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
        if not self.widgetsRefreshing:
            self.parent.setModified()
            self.parent.gudrunFile.purged = False
            self.normalisation.dataFilesBg.dataFiles = (
                self.widget.backgroundDataFilesList.model().stringList()
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
        files, _ = QFileDialog.getOpenFileNames(
            self.widget, title,
            self.parent.gudrunFile.instrument.dataFileDir, regex
        )
        for file in files:
            if file:
                target.insertRow(file.split(os.path.sep)[-1])

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
        if not self.widgetsRefreshing:
            self.parent.setModified()

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
        if not self.widgetsRefreshing:
            self.parent.setModified()

    def removeDataFile(self, target):
        target.removeItem()

    def duplicateDataFile(self, target):
        target.duplicate()

    def updateCompositionTable(self):
        """
        Fills the composition list.
        """
        self.widget.normalisationCompositionTable.makeModel(
            self.normalisation.composition.elements, self.normalisation
        )
        if not self.widgetsRefreshing:
            self.parent.setModified()

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
