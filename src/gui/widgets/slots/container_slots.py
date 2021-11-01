from PySide6.QtWidgets import QFileDialog
from src.gudrun_classes import config
from src.gudrun_classes.enums import (
    CrossSectionSource, UnitsOfDensity, Geometry
)


class ContainerSlots():

    def __init__(self, widget, parent):
        self.widget = widget
        self.parent = parent
        self.setupContainerSlots()

    def setContainer(self, container):
        self.container = container
        # Acquire the lock
        self.widgetsRefreshing = True
        # Populate the period number.
        self.widget.containerPeriodNoSpinBox.setValue(
            self.container.periodNumber
        )

        # Populate data files.
        self.updateDataFilesList()

        # Populate geometry data.
        self.widget.containerGeometryComboBox.setCurrentIndex(
            self.container.geometry.value
        )

        # Ensure the correct attributes are being
        # shown for the correct geometry.
        self.widget.containerGeometryInfoStack.setCurrentIndex(
            config.geometry.value
        )

        # Populate geometry specific attributes.
        # Flatplate
        self.widget.containerUpstreamSpinBox.setValue(
            self.container.upstreamThickness
        )
        self.widget.containerDownStreamSPinBox.setValue(
            self.container.downstreamThickness
        )

        self.widget.containerAngleOfRotationSpinBox.setValue(
            self.container.angleOfRotation
        )
        self.widget.containerSampleWidthSpinBox.setValue(
            self.container.sampleWidth
        )

        # Cylindrical
        self.widget.containerInnerRadiiSpinBox.setValue(
            self.container.innerRadius
        )
        self.widget.containerOuterRadiiSpinBox.setValue(
            self.container.outerRadius
        )

        self.widget.containerSampleHeightSpinBox.setValue(
            self.container.sampleHeight
        )

        # Populate density data.
        self.widget.containerDensitySpinBox.setValue(self.container.density)
        self.widget.containerDensityUnitsComboBox.setCurrentIndex(
            self.container.densityUnits.value
        )

        # Populate other container configuration data.
        self.widget.containerTotalCrossSectionComboBox.setCurrentIndex(
            self.container.totalCrossSectionSource.value
        )
        self.widget.containerCrossSectionFileLineEdit.setText(
            self.container.crossSectionFilename
        )
        self.widget.containerCrossSectionFileWidget.setVisible(
            self.container.totalCrossSectionSource == CrossSectionSource.FILE
        )
        self.widget.containerTweakFactorSpinBox.setValue(
            self.container.tweakFactor
        )

        self.widget.containerScatteringFractionSpinBox.setValue(
            self.container.scatteringFraction
        )

        self.widget.containerAttenuationCoefficientSpinBox.setValue(
            self.container.attenuationCoefficient
        )

        # Populate composition table.
        self.updateCompositionTable()

        # Release the lock
        self.widgetsRefreshing = False

    def setupContainerSlots(self):
        # Setup slot for period number.
        self.widget.containerPeriodNoSpinBox.valueChanged.connect(
            self.handlePeriodNoChanged
        )

        # Setup slots for data files.
        self.widget.containerDataFilesList.itemChanged.connect(
            self.handleDataFilesAltered
        )
        self.widget.containerDataFilesList.itemEntered.connect(
            self.handleDataFileInserted
        )
        self.widget.addContainerDataFileButton.clicked.connect(
            lambda: self.addFiles(
                self.widget.containerDataFilesList,
                "Add data files",
                f"{self.parent.gudrunFile.instrument.dataFileType}"
                f" (*.{self.parent.gudrunFile.instrument.dataFileType})",
            )
        )
        self.widget.removeContainerDataFileButton.clicked.connect(
            lambda: self.removeFile(
                self.widget.containerDataFilesList, self.container.dataFiles
            )
        )

        # Populate geometry combo box.
        for g in Geometry:
            self.widget.containerGeometryComboBox.addItem(g.name, g)

        # Setup slots for geometry data.
        self.widget.containerGeometryComboBox.currentIndexChanged.connect(
            self.handleGeometryChanged
        )
        self.widget.containerGeometryComboBox.setDisabled(True)

        # Flatplate
        self.widget.containerUpstreamSpinBox.valueChanged.connect(
            self.handleUpstreamThicknessChanged
        )
        self.widget.containerDownStreamSPinBox.valueChanged.connect(
            self.handleDownstreamThicknessChanged
        )

        self.widget.containerAngleOfRotationSpinBox.valueChanged.connect(
            self.handleAngleOfRotationChanged
        )
        self.widget.containerSampleWidthSpinBox.valueChanged.connect(
            self.handleSampleWidthChanged
        )

        # Cylindrical
        self.widget.containerInnerRadiiSpinBox.valueChanged.connect(
            self.handleInnerRadiiChanged
        )
        self.widget.containerOuterRadiiSpinBox.valueChanged.connect(
            self.handleOuterRadiiChanged
        )

        self.widget.containerSampleHeightSpinBox.valueChanged.connect(
            self.handleSampleHeightChanged
        )

        # Setup slots for density data.
        (
            self.widget.containerDensitySpinBox
        ).valueChanged.connect(self.handleDensityChanged)

        # Populate density units combo box.
        for du in UnitsOfDensity:
            self.widget.containerDensityUnitsComboBox.addItem(du.name, du)

        # Setup slots for other container configuration data.
        # Populate cross section source combo box.
        for c in CrossSectionSource:
            self.widget.containerTotalCrossSectionComboBox.addItem(c.name, c)

        (
            self.widget.containerTotalCrossSectionComboBox
        ).currentIndexChanged.connect(
            self.handleTotalCrossSectionChanged
        )

        self.widget.containerCrossSectionFileLineEdit.textChanged.connect(
            self.handleCrossSectionFileChanged
        )

        self.widget.browseContainerCrossSectionFileButton.clicked.connect(
            self.handleBrowseCrossSectionFile
        )

        self.widget.containerTweakFactorSpinBox.valueChanged.connect(
            self.handleTweakFactorChanged
        )
        self.widget.containerScatteringFractionSpinBox.valueChanged.connect(
            self.handleScatteringFractionChanged
        )
        (
            self.widget.containerAttenuationCoefficientSpinBox
        ).valueChanged.connect(
            self.handleAttenuationCoefficientChanged
        )

        # Setup slots for composition table.
        self.widget.insertContainerElementButton.clicked.connect(
            self.handleInsertElement
        )
        self.widget.removeContainerElementButton.clicked.connect(
            self.handleRemoveElement
        )

        self.widget.insertContainerComponentButton.clicked.connect(
            self.handleInsertComponent
        )

        self.widget.removeContainerComponentButton.clicked.connect(
            self.handleRemoveComponent
        )

    def handlePeriodNoChanged(self, value):
        """
        Slot for handling change in the period number.
        Called when a valueChanged signal is emitted,
        from the containerPeriodNoSpinBox.
        Alters the container's period number as such.
        Parameters
        ----------
        value : float
            The new value of the containerPeriodNoSpinBox.
        """
        self.container.periodNo = value
        if not self.widgetsRefreshing:
            self.parent.setModified()
            if not self.parent.gudrunFile.purgeFile.excludeSampleAndCan:
                self.parent.gudrunFile.purged = False

    def handleGeometryChanged(self, index):
        """
        Slot for handling change in sample geometry.
        Called when a currentIndexChanged signal is emitted,
        from the containerGeometryComboBox.
        Alters the container geometry as such.
        Parameters
        ----------
        index : int
            The new current index of the containerGeometryComboBox.
        """
        self.container.geometry = (
            self.widget.containerGeometryComboBox.itemData(index)
        )
        self.widget.containerGeometryInfoStack.setCurrentIndex(
            self.container.geometry.value
        )

    def handleUpstreamThicknessChanged(self, value):
        """
        Slot for handling change in the upstream thickness.
        Called when a valueChanged signal is emitted,
        from the containerUpstreamSpinBox.
        Alters the container's upstream thickness as such.
        Parameters
        ----------
        value : float
            The new value of the containerUpstreamSpinBox.
        """
        self.container.upstreamThickness = value
        if not self.widgetsRefreshing:
            self.parent.setModified()

    def handleDownstreamThicknessChanged(self, value):
        """
        Slot for handling change in the downstream thickness.
        Called when a valueChanged signal is emitted,
        from the containerDownStreamSPinBox.
        Alters the container's downstream thickness as such.
        Parameters
        ----------
        value : float
            The new value of the containerDownStreamSPinBox.
        """
        self.container.downstreamThickness = value
        if not self.widgetsRefreshing:
            self.parent.setModified()

    def handleInnerRadiiChanged(self, value):
        """
        Slot for handling change in the inner radii.
        Called when a valueChanged signal is emitted,
        from the containerInnerRadiiSpinBox.
        Alters the container's inner radius as such.
        Parameters
        ----------
        value : float
            The new value of the containerInnerRadiiSpinBox.
        """
        self.container.innerRadius = value
        if not self.widgetsRefreshing:
            self.parent.setModified()

    def handleOuterRadiiChanged(self, value):
        """
        Slot for handling change in the outer radii.
        Called when a valueChanged signal is emitted,
        from the containerOuterRadiiSpinBox.
        Alters the container's outer radius as such.
        Parameters
        ----------
        value : float
            The new value of the containerOuterRadiiSpinBox.
        """
        self.container.outerRadius = value
        if not self.widgetsRefreshing:
            self.parent.setModified()

    def handleDensityChanged(self, value):
        """
        Slot for handling change in the density.
        Called when a valueChanged signal is emitted,
        from the containerDensitySpinBox.
        Alters the container's density as such.
        Parameters
        ----------
        value : float
            The new value of the containerDensitySpinBox.
        """
        self.container.density = value
        if not self.widgetsRefreshing:
            self.parent.setModified()

    def handleTotalCrossSectionChanged(self, index):
        """
        Slot for handling change in total cross section source.
        Called when a currentIndexChanged signal is emitted,
        from the containerTotalCrossSectionComboBox.
        Alters the container's total cross section source as such.
        Parameters
        ----------
        index : int
            The new current index of the containerTotalCrossSectionComboBox.
        """
        self.container.totalCrossSectionSource = (
            self.widget.containerTotalCrossSectionComboBox.itemData(index)
        )
        self.widget.containerCrossSectionFileWidget.setVisible(
            self.container.totalCrossSectionSource == CrossSectionSource.FILE
        )
        if not self.widgetsRefreshing:
            self.parent.setModified()

    def handleCrossSectionFileChanged(self, value):
        """
        Slot for handling change in total cross section source file name.
        Called when a textChanged signal is emitted,
        from the containerCrossSectionFileLineEdit.
        Alters the container's total cross section source file name as such.
        Parameters
        ----------
        value : str
            The new text of the containerCrossSectionFileLineEdit.
        """
        self.container.crossSectionFilename = value
        if not self.widgetsRefreshing:
            self.parent.setModified()

    def handleBrowseCrossSectionFile(self):
        """
        Slot for browsing for a cross section source file.
        Called when a clicked signal is emitted,
        from the browseContainerCrossSectionFileButton.
        Alters the corresponding line edit as such.
        as such.
        """
        filename, _ = QFileDialog.getOpenFileName(
            self.widget, "Total cross section source", "")
        if filename:
            self.widget.containerCrossSectionFileLineEdit.setText(filename)

    def handleTweakFactorChanged(self, value):
        """
        Slot for handling change in the sample tweak factor.
        Called when a valueChanged signal is emitted,
        from the containerTweakFactorSpinBox.
        Alters the container's density as such.
        Parameters
        ----------
        value : float
            The new value of the containerTweakFactorSpinBox.
        """
        self.container.tweakFactor = value
        if not self.widgetsRefreshing:
            self.parent.setModified()

    def handleAngleOfRotationChanged(self, value):
        """
        Slot for handling change in the angle of rotation.
        Called when a valueChanged signal is emitted,
        from the containerAngleOfRotationSpinBox.
        Alters the container's angle of rotation as such.
        Parameters
        ----------
        value : float
            The new value of the containerAngleOfRotationSpinBox.
        """
        self.container.angleOfRotation = value
        if not self.widgetsRefreshing:
            self.parent.setModified()

    def handleSampleWidthChanged(self, value):
        """
        Slot for handling change in the sample width.
        Called when a valueChanged signal is emitted,
        from the containerSampleWidthSpinBox.
        Alters the container's sample width as such.
        Parameters
        ----------
        value : float
            The new value of the containerSampleWidthSpinBox.
        """
        self.container.sampleWidth = value
        if not self.widgetsRefreshing:
            self.parent.setModified()

    def handleSampleHeightChanged(self, value):
        """
        Slot for handling change in the sample height.
        Called when a valueChanged signal is emitted,
        from the containerSampleHeightSpinBox.
        Alters the container's sample height as such.
        Parameters
        ----------
        value : float
            The new value of the containerSampleHeightSpinBox.
        """
        self.container.sampleHeight = value
        if not self.widgetsRefreshing:
            self.parent.setModified()

    def handleScatteringFractionChanged(self, value):
        """
        Slot for handling change in the container's environment
        scattering fraction.
        Called when a valueChanged signal is emitted,
        from the containerScatteringFractionSpinBox.
        Alters the container's scattering fraction as such.
        Parameters
        ----------
        value : float
            The new value of the containerScatteringFractionSpinBox.
        """
        self.container.scatteringFraction = value
        if not self.widgetsRefreshing:
            self.parent.setModified()

    def handleAttenuationCoefficientChanged(self, value):
        """
        Slot for handling change in the container's environment
        attenuation coefficient.
        Called when a valueChanged signal is emitted,
        from the containerAttenuationCoefficientSpinBox.
        Alters the container's attenuation coefficient as such.
        Parameters
        ----------
        value : float
            The new value of the containerAttenuationCoefficientSpinBox.
        """
        self.container.attenuationCoefficient = value
        if not self.widgetsRefreshing:
            self.parent.setModified()

    def handleDataFilesAltered(self, item):
        """
        Slot for handling an item in the data files list being changed.
        Called when an itemChanged signal is emitted,
        from the dataFilesList.
        Alters the container's data files as such.
        Parameters
        ----------
        item : QListWidgetItem
            The item altered.
        """
        index = item.row()
        value = item.text()
        if not value:
            self.container.dataFiles.dataFiles.remove(index)
        else:
            self.container.dataFiles.dataFiles[index] = value
        self.updateDataFilesList()
        if not self.widgetsRefreshing:
            self.parent.setModified()
            self.parent.gudrunFile.purged = False

    def handleDataFileInserted(self, item):
        """
        Slot for handling an item in the data files list being entered.
        Called when an itemEntered signal is emitted,
        from the dataFilesList.
        Alters the container's data files as such.
        Parameters
        ----------
        item : QListWidgetItem
            The item entered.
        """
        value = item.text()
        self.container.dataFiles.dataFiles.append(value)
        if not self.widgetsRefreshing:
            self.parent.setModified()
            self.parent.gudrunFile.purged = False

    def updateDataFilesList(self):
        """
        Fills the data files list.
        """
        self.widget.containerDataFilesList.clear()
        self.widget.containerDataFilesList.addItems(
            [df for df in self.container.dataFiles.dataFiles]
        )

    def addFiles(self, target, title, regex):
        """
        Slot for adding files to the data files list.
        Called when a clicked signal is emitted,
        from the addContainerDataFileButton.
        Parameters
        ----------
        target : QListWidget
            Target widget to add to.
        title : str
            Window title for QFileDialog.
        regex : str
            Regex-like expression to use for specifying file types.
        """
        files, _ = QFileDialog.getOpenFileNames(self.widget, title, ".", regex)
        for file in files:
            if file:
                target.addItem(file.split("/")[-1])
                self.handleDataFileInserted(target.item(target.count() - 1))
        if not self.widgetsRefreshing:
            self.parent.setModified()

    def removeFile(self, target, dataFiles):
        """
        Slot for removing files from the data files list.
        Called when a clicked signal is emitted,
        from the removeContainerDataFileButton.
        Parameters
        ----------
        target : QListWidget
            Target widget to add to.
        dataFiles : list
            dataFiles attribute belonging to DataFiles object.
        """
        if target.currentIndex().isValid():
            remove = target.takeItem(target.currentRow()).text()
            dataFiles.dataFiles.remove(remove)
            if not self.widgetsRefreshing:
                self.parent.setModified()
                self.parent.gudrunFile.purged = False

    def updateCompositionTable(self):
        """
        Fills the composition list.
        """
        if config.USE_USER_DEFINED_COMPONENTS:
            self.updateRatioCompositions()
            self.widget.containerExactCompositionTab.setEnabled(False)
            self.widget.containerRatioCompositionTab.setEnabled(True)
            self.widget.containerCompositionTabs.setCurrentIndex(1)
            (
                self.widget.containerRatioCompositionTable
                .model().dataChanged.connect(
                    self.updateExactCompositions
                )
            )
        else:
            self.updateExactCompositions()
            self.widget.containerExactCompositionTab.setEnabled(True)
            self.widget.containerRatioCompositionTab.setEnabled(False)
            self.widget.containerCompositionTabs.setCurrentIndex(0)
        if not self.widgetsRefreshing:
            self.parent.setModified()

    def updateRatioCompositions(self):
        self.widget.containerRatioCompositionTable.makeModel(
            self.container.composition, self.parent.gudrunFile
        )

    def updateExactCompositions(self):
        self.widget.containerCompositionTable.makeModel(
            self.container.composition.elements
        )

    def handleInsertElement(self):
        """
        Slot for handling insertion to the composition table.
        Called when a clicked signal is emitted, from the
        insertContainerElementButton.
        """
        self.widget.containerCompositionTable.insertRow()
        if not self.widgetsRefreshing:
            self.parent.setModified()

    def handleRemoveElement(self):
        """
        Slot for removing files from the data files list.
        Called when a clicked signal is emitted,
        from the removeContainerElementButton.
        """
        self.widget.containerCompositionTable.removeRow(
            self.widget.containerCompositionTable
            .selectionModel().selectedRows()
        )
        if not self.widgetsRefreshing:
            self.parent.setModified()

    def handleInsertComponent(self):
        self.widget.containerRatioCompositionTable.insertRow()
        if not self.widgetsRefreshing:
            self.parent.setModified()

    def handleRemoveComponent(self):
        self.widget.containerRatioCompositionTable.removeRow(
            self.widget.containerRatioCompositionTable
            .selectionModel().selectedRows()
        )
        if not self.widgetsRefreshing:
            self.parent.setModified()