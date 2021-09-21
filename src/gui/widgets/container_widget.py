from src.gudrun_classes.enums import Geometry, UnitsOfDensity
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
        self.geometryInfoStack_.setCurrentIndex(self.container.geometry.value)

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

    def handleTotalCrossSectionChanged(self, index):
        """
        Slot for handling change in total cross ection source.
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
        paths = QFileDialog.getOpenFileNames(self, title, ".", regex)
        for path in paths:
            if path:
                target.addItem(path)
                self.handleDataFileInserted(target.item(target.count() - 1))

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
            self.updateDataFilesList()

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

    def handleRemoveElement(self):
        """
        Slot for removing files from the data files list.
        Called when a clicked signal is emitted,
        from the removeDataFileButton.
        """
        self.containerCompositionTable.removeRow(
            self.containerCompositionTable.selectionModel().selectedRows()
        )

    def initComponents(self):
        """
        Populates the child widgets with their
        corresponding data from the attributes of the Container object.
        """

        # Setup widget and slot for the period number.
        self.periodNoSpinBox.setValue(self.container.periodNumber)
        self.periodNoSpinBox.valueChanged.connect(self.handlePeriodNoChanged)

        # Setup widgets and slots for the data files.
        self.updateDataFilesList()
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

        # Setup widgets and slots for geometry.
        for g in Geometry:
            self.geometryComboBox.addItem(g.name, g)
        self.geometryComboBox.setCurrentIndex(self.container.geometry.value)
        self.geometryComboBox.currentIndexChanged.connect(
            self.handleGeometryChanged
        )

        self.geometryComboBox.setDisabled(True)

        # Ensure the correct attributes are being
        # shown for the correct geometry.
        self.geometryInfoStack.setCurrentIndex(config.geometry.value)
        self.geometryInfoStack_.setCurrentIndex(config.geometry.value)

        # Setup the widgets and slots for geometry specific attributes.
        # Flatplate
        self.upstreamSpinBox.setValue(self.container.upstreamThickness)
        self.upstreamSpinBox.valueChanged.connect(
            self.handleUpstreamThicknessChanged
        )
        self.downstreamSpinBox.setValue(self.container.downstreamThickness)
        self.downstreamSpinBox.valueChanged.connect(
            self.handleDownstreamThicknessChanged
        )

        self.angleOfRotationSpinBox.setValue(self.container.angleOfRotation)
        self.angleOfRotationSpinBox.valueChanged.connect(
            self.handleAngleOfRotationChanged
        )
        self.sampleWidthSpinBox.setValue(self.container.sampleWidth)
        self.sampleWidthSpinBox.valueChanged.connect(
            self.handleSampleWidthChanged
        )

        # Cylindrical
        self.innerRadiiSpinBox.setValue(self.container.innerRadius)
        self.innerRadiiSpinBox.valueChanged.connect(
            self.handleInnerRadiiChanged
        )
        self.outerRadiiSpinBox.setValue(self.container.outerRadius)
        self.outerRadiiSpinBox.valueChanged.connect(
            self.handleOuterRadiiChanged
        )

        self.sampleHeightSpinBox.setValue(self.container.sampleHeight)
        self.sampleHeightSpinBox.valueChanged.connect(
            self.handleSampleHeightChanged
        )

        # Setup the widgets and slots for the density.
        self.densitySpinBox.setValue(self.container.density)
        self.densitySpinBox.valueChanged.connect(self.handleDensityChanged)

        for du in UnitsOfDensity:
            self.densityUnitsComboBox.addItem(du.name, du)
        self.densityUnitsComboBox.setCurrentIndex(
            self.container.densityUnits.value
        )

        # Setup the other container configurations widgets and slots.
        crossSectionSources = ["TABLES", "TRANSMISSION MONITOR", "FILENAME"]
        if "TABLES" in self.container.totalCrossSectionSource:
            index = 0
        elif "TRANSMISSION" in self.container.totalCrossSectionSource:
            index = 1
        else:
            index = 2
        self.totalCrossSectionComboBox.addItems(crossSectionSources)
        self.totalCrossSectionComboBox.setCurrentIndex(index)
        self.totalCrossSectionComboBox.currentIndexChanged.connect(
            self.handleTotalCrossSectionChanged
        )

        self.tweakFactorSpinBox.setValue(self.container.tweakFactor)
        self.tweakFactorSpinBox.valueChanged.connect(
            self.handleTweakFactorChanged
        )

        self.scatteringFractionSpinBox.setValue(
            self.container.scatteringFraction
        )
        self.scatteringFractionSpinBox.valueChanged.connect(
            self.handleScatteringFractionChanged
        )
        self.attenuationCoefficientSpinBox.setValue(
            self.container.attenuationCoefficient
        )
        self.attenuationCoefficientSpinBox.valueChanged.connect(
            self.handleAttenuationCoefficientChanged
        )

        # Setup the widgets and slots for the composition.
        self.updateCompositionTable()
        self.insertElementButton.clicked.connect(self.handleInsertElement)
        self.removeElementButton.clicked.connect(self.handleRemoveElement)
