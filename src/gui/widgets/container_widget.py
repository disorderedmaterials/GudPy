from src.gudrun_classes.enums import (
    CrossSectionSource, Geometry, UnitsOfDensity
)
from PyQt5.QtWidgets import QFileDialog, QWidget
from PyQt5 import uic
import os
from src.gudrun_classes import config


class ContainerWidget(QWidget):
    """
    Class to represent a ContainerWidget. Inherits QWidget.

    ...

    Attributes
    ----------
    container : Container
        Container object belonging to the GudrunFile.
    parent : QWidget
        Parent widget.
    Methods
    -------
    loadUI()
        Loads the UI file for the ContainerWidget object,
    initComponents()
        Loads UI file, and then populates data from the Container.
    setContainer(container)
        Gives the focus of the ContainerWidget to the container.
    handlePeriodNoChanged(value)
        Slot for handling change in the period number.
    handleGeometryChanged(index)
        Slot for handling change in the geometry.
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
    handleCrossSectionFileChanged(value)
        Slot for handling change in total cross section source file name.
    handleBrowseCrossSectionFile()
        Slot for browsing for a cross section source file.
    handleTweakFactorChanged(value)
        Slot for handling change in the sample tweak factor.
    handleAngleOfRotationChanged(value)
        Slot for handling change in the angle of rotation.
    handleSampleWidthChanged(value)
        Slot for handling change in the sample width.
    handleScatteringFractionChanged(value)
        Slot for handling change in the environment scattering fraction.
    handleAttenuationCoefficientChanged(value)
        Slot for handling change in the environment attenuation coefficient.
    handleDataFilesAltered(item)
        Slot for handling changes to the data files list.
    handleDataFileInserted(item)
        Slot for handling insertion to the data files list.
    updateDataFilesList()
        Fills the data files list.
    addFiles(target, title, regex)
        Slot for adding files to the data files list.
    removeFile(target, dataFiles)
        Slot for removing data files from the list.
    updateCompositionTable()
        Fills the composition table.
    handleInsertElement()
        Slot for handling insertion to the composition table.
    handleRemoveElement()
        Slot for removing the selected element from the composition table.
    """

    def __init__(self, parent=None):
        """
        Constructs all the necessary attributes for the ContainerWidget object.
        Parameters
        ----------
        parent : QWidget, optional
            Parent widget.
        """
        self.parent = parent

        super(ContainerWidget, self).__init__(parent=self.parent)
        self.loadUI()
        self.setupUI()

    def loadUI(self):
        """
        Loads the UI file for the ContainerWidget object,
        and then populates the child widgets with their
        corresponding data from the attributes of the Container object.
        """

        # Get the current directory that we are residing in.
        current_dir = os.path.dirname(os.path.realpath(__file__))
        # Join the current directory with the relative path of the UI file.
        uifile = os.path.join(current_dir, "ui_files/containerWidget.ui")

        # Use pyuic to load to the UI file into the ContainerWidget.
        uic.loadUi(uifile, self)

    def setContainer(self, container):
        """
        Gives the focus of the ContainerWidget to the container.
        Constructs all the necessary attributes for the ContainerWidget object.
        Parameters
        ----------
        container : Container
            Container object belonging to the GudrunFile.
        """
        self.container = container
        self.initComponents()

    def handlePeriodNoChanged(self, value):
        """
        Slot for handling change in the period number.
        Called when a valueChanged signal is emitted,
        from the periodNoSpinBox.
        Alters the container's period number as such.
        Parameters
        ----------
        value : float
            The new value of the periodNoSpinBox.
        """
        self.container.periodNo = value
        if not self.widgetsRefreshing:
            self.parent.setModified()

    def handleGeometryChanged(self, index):
        """
        Slot for handling change in sample geometry.
        Called when a currentIndexChanged signal is emitted,
        from the geometryComboBox.
        Alters the container geometry as such.
        Parameters
        ----------
        index : int
            The new current index of the geometryComboBox.
        """
        self.container.geometry = self.geometryComboBox.itemData(index)
        self.geometryInfoStack.setCurrentIndex(self.container.geometry.value)

    def handleUpstreamThicknessChanged(self, value):
        """
        Slot for handling change in the upstream thickness.
        Called when a valueChanged signal is emitted,
        from the upstreamSpinBox.
        Alters the container's upstream thickness as such.
        Parameters
        ----------
        value : float
            The new value of the upstreamSpinBox.
        """
        self.container.upstreamThickness = value
        if not self.widgetsRefreshing:
            self.parent.setModified()

    def handleDownstreamThicknessChanged(self, value):
        """
        Slot for handling change in the downstream thickness.
        Called when a valueChanged signal is emitted,
        from the downstreamSpinBox.
        Alters the container's downstream thickness as such.
        Parameters
        ----------
        value : float
            The new value of the downstreamSpinBox.
        """
        self.container.downstreamThickness = value
        if not self.widgetsRefreshing:
            self.parent.setModified()

    def handleInnerRadiiChanged(self, value):
        """
        Slot for handling change in the inner radii.
        Called when a valueChanged signal is emitted,
        from the innerRadiiSpinBox.
        Alters the container's inner radius as such.
        Parameters
        ----------
        value : float
            The new value of the innerRadiiSpinBox.
        """
        self.container.innerRadius = value
        if not self.widgetsRefreshing:
            self.parent.setModified()

    def handleOuterRadiiChanged(self, value):
        """
        Slot for handling change in the outer radii.
        Called when a valueChanged signal is emitted,
        from the outerRadiiSpinBox.
        Alters the container's outer radius as such.
        Parameters
        ----------
        value : float
            The new value of the outerRadiiSpinBox.
        """
        self.container.outerRadius = value
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
        self.container.density = value
        if not self.widgetsRefreshing:
            self.parent.setModified()

    def handleTotalCrossSectionChanged(self, index):
        """
        Slot for handling change in total cross section source.
        Called when a currentIndexChanged signal is emitted,
        from the totalCrossSectionComboBox.
        Alters the container's total cross section source as such.
        Parameters
        ----------
        index : int
            The new current index of the totalCrossSectionComboBox.
        """
        self.container.totalCrossSectionSource = (
            self.totalCrossSectionComboBox.itemData(index)
        )
        self.crossSectionFileWidget.setVisible(
            self.container.totalCrossSectionSource == CrossSectionSource.FILE
        )
        if not self.widgetsRefreshing:
            self.parent.setModified()

    def handleCrossSectionFileChanged(self, value):
        """
        Slot for handling change in total cross section source file name.
        Called when a textChanged signal is emitted,
        from the crossSectionFileLineEdit.
        Alters the container's total cross section source file name as such.
        Parameters
        ----------
        value : str
            The new text of the crossSectionFileLineEdit.
        """
        self.container.crossSectionFilename = value
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
            self, "Total cross section source", "")
        if filename:
            self.crossSectionFileLineEdit.setText(filename)

    def handleTweakFactorChanged(self, value):
        """
        Slot for handling change in the sample tweak factor.
        Called when a valueChanged signal is emitted,
        from the tweakFactorSpinBox.
        Alters the container's density as such.
        Parameters
        ----------
        value : float
            The new value of the tweakFactorSpinBox.
        """
        self.container.tweakFactor = value
        if not self.widgetsRefreshing:
            self.parent.setModified()

    def handleAngleOfRotationChanged(self, value):
        """
        Slot for handling change in the angle of rotation.
        Called when a valueChanged signal is emitted,
        from the angleOfRotationSpinBox.
        Alters the container's angle of rotation as such.
        Parameters
        ----------
        value : float
            The new value of the angleOfRotationSpinBox.
        """
        self.container.angleOfRotation = value
        if not self.widgetsRefreshing:
            self.parent.setModified()

    def handleSampleWidthChanged(self, value):
        """
        Slot for handling change in the sample width.
        Called when a valueChanged signal is emitted,
        from the sampleWidthSpinBox.
        Alters the container's sample width as such.
        Parameters
        ----------
        value : float
            The new value of the sampleWidthSpinBox.
        """
        self.container.sampleWidth = value
        if not self.widgetsRefreshing:
            self.parent.setModified()

    def handleSampleHeightChanged(self, value):
        """
        Slot for handling change in the sample height.
        Called when a valueChanged signal is emitted,
        from the sampleHeightSpinBox.
        Alters the container's sample height as such.
        Parameters
        ----------
        value : float
            The new value of the sampleHeightSpinBox.
        """
        self.container.sampleHeight = value
        if not self.widgetsRefreshing:
            self.parent.setModified()

    def handleScatteringFractionChanged(self, value):
        """
        Slot for handling change in the container's environment
        scattering fraction.
        Called when a valueChanged signal is emitted,
        from the scatteringFractionSpinBox.
        Alters the container's scattering fraction as such.
        Parameters
        ----------
        value : float
            The new value of the scatteringFractionSpinBox.
        """
        self.container.scatteringFraction = value
        if not self.widgetsRefreshing:
            self.parent.setModified()

    def handleAttenuationCoefficientChanged(self, value):
        """
        Slot for handling change in the container's environment
        attenuation coefficient.
        Called when a valueChanged signal is emitted,
        from the attenuationCoefficientSpinBox.
        Alters the container's attenuation coefficient as such.
        Parameters
        ----------
        value : float
            The new value of the attenuationCoefficientSpinBox.
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

    def updateDataFilesList(self):
        """
        Fills the data files list.
        """
        self.dataFilesList.clear()
        self.dataFilesList.addItems(
            [df for df in self.container.dataFiles.dataFiles]
        )

    def addFiles(self, target, title, regex):
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
        files, _ = QFileDialog.getOpenFileNames(self, title, ".", regex)
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
        from the removeDataFileButton.
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

    def updateCompositionTable(self):
        """
        Fills the composition list.
        """
        self.containerCompositionTable.makeModel(
            self.container.composition.elements
        )

    def handleInsertElement(self):
        """
        Slot for handling insertion to the composition table.
        Called when a clicked signal is emitted, from the
        insertElementButton.
        """
        self.containerCompositionTable.insertRow()
        if not self.widgetsRefreshing:
            self.parent.setModified()

    def handleRemoveElement(self):
        """
        Slot for removing files from the data files list.
        Called when a clicked signal is emitted,
        from the removeDataFileButton.
        """
        self.containerCompositionTable.removeRow(
            self.containerCompositionTable.selectionModel().selectedRows()
        )
        if not self.widgetsRefreshing:
            self.parent.setModified()

    def setupUI(self):
        # Setup slot for period number.
        self.periodNoSpinBox.valueChanged.connect(self.handlePeriodNoChanged)

        # Setup slots for data files.
        self.dataFilesList.itemChanged.connect(self.handleDataFilesAltered)
        self.dataFilesList.itemEntered.connect(self.handleDataFileInserted)
        self.addDataFileButton.clicked.connect(
            lambda: self.addFiles(
                self.dataFilesList,
                "Add data files",
                f"{self.parent.gudrunFile.instrument.dataFileType}"
                f" (*.{self.parent.gudrunFile.instrument.dataFileType})",
            )
        )
        self.removeDataFileButton.clicked.connect(
            lambda: self.removeFile(
                self.dataFilesList, self.container.dataFiles
            )
        )

        # Populate geometry combo box.
        for g in Geometry:
            self.geometryComboBox.addItem(g.name, g)

        # Setup slots for geometry data.
        self.geometryComboBox.currentIndexChanged.connect(
            self.handleGeometryChanged
        )
        self.geometryComboBox.setDisabled(True)

        # Flatplate
        self.upstreamSpinBox.valueChanged.connect(
            self.handleUpstreamThicknessChanged
        )
        self.downstreamSpinBox.valueChanged.connect(
            self.handleDownstreamThicknessChanged
        )

        self.angleOfRotationSpinBox.valueChanged.connect(
            self.handleAngleOfRotationChanged
        )
        self.sampleWidthSpinBox.valueChanged.connect(
            self.handleSampleWidthChanged
        )

        # Cylindrical
        self.innerRadiiSpinBox.valueChanged.connect(
            self.handleInnerRadiiChanged
        )
        self.outerRadiiSpinBox.valueChanged.connect(
            self.handleOuterRadiiChanged
        )

        self.sampleHeightSpinBox.valueChanged.connect(
            self.handleSampleHeightChanged
        )

        # Setup slots for density data.
        self.densitySpinBox.valueChanged.connect(self.handleDensityChanged)

        # Populate density units combo box.
        for du in UnitsOfDensity:
            self.densityUnitsComboBox.addItem(du.name, du)

        # Setup slots for other container configuration data.
        # Populate cross section source combo box.
        for c in CrossSectionSource:
            self.totalCrossSectionComboBox.addItem(c.name, c)

        self.totalCrossSectionComboBox.currentIndexChanged.connect(
            self.handleTotalCrossSectionChanged
        )

        self.crossSectionFileLineEdit.textChanged.connect(
            self.handleCrossSectionFileChanged
        )

        self.browseCrossSectionFileButton.clicked.connect(
            self.handleBrowseCrossSectionFile
        )

        self.tweakFactorSpinBox.valueChanged.connect(
            self.handleTweakFactorChanged
        )
        self.scatteringFractionSpinBox.valueChanged.connect(
            self.handleScatteringFractionChanged
        )
        self.attenuationCoefficientSpinBox.valueChanged.connect(
            self.handleAttenuationCoefficientChanged
        )

        # Setup slots for composition table.
        self.insertElementButton.clicked.connect(self.handleInsertElement)
        self.removeElementButton.clicked.connect(self.handleRemoveElement)

    def initComponents(self):
        """
        Populates the child widgets with their
        corresponding data from the attributes of the Container object.
        """
        # Acquire the lock
        self.widgetsRefreshing = True
        # Populate the period number.
        self.periodNoSpinBox.setValue(self.container.periodNumber)

        # Populate data files.
        self.updateDataFilesList()

        # Populate geometry data.
        self.geometryComboBox.setCurrentIndex(self.container.geometry.value)

        # Ensure the correct attributes are being
        # shown for the correct geometry.
        self.geometryInfoStack.setCurrentIndex(config.geometry.value)

        # Populate geometry specific attributes.
        # Flatplate
        self.upstreamSpinBox.setValue(self.container.upstreamThickness)
        self.downstreamSpinBox.setValue(self.container.downstreamThickness)

        self.angleOfRotationSpinBox.setValue(self.container.angleOfRotation)
        self.sampleWidthSpinBox.setValue(self.container.sampleWidth)

        # Cylindrical
        self.innerRadiiSpinBox.setValue(self.container.innerRadius)
        self.outerRadiiSpinBox.setValue(self.container.outerRadius)

        self.sampleHeightSpinBox.setValue(self.container.sampleHeight)

        # Populate density data.
        self.densitySpinBox.setValue(self.container.density)
        self.densityUnitsComboBox.setCurrentIndex(
            self.container.densityUnits.value
        )

        # Populate other container configuration data.
        self.totalCrossSectionComboBox.setCurrentIndex(
            self.container.totalCrossSectionSource.value
        )
        self.crossSectionFileLineEdit.setText(
            self.container.crossSectionFilename
        )
        self.crossSectionFileWidget.setVisible(
            self.container.totalCrossSectionSource == CrossSectionSource.FILE
        )
        self.tweakFactorSpinBox.setValue(self.container.tweakFactor)

        self.scatteringFractionSpinBox.setValue(
            self.container.scatteringFraction
        )

        self.attenuationCoefficientSpinBox.setValue(
            self.container.attenuationCoefficient
        )

        # Populate composition table.
        self.updateCompositionTable()

        # Release the lock
        self.widgetsRefreshing = False
