from src.gudrun_classes.enums import Geometry, OutputUnits, UnitsOfDensity
from PyQt5.QtWidgets import QTableWidgetItem, QWidget
from PyQt5 import uic
import os

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
    initComponents()
        Loads UI file, and then populates data from the Container.
    """
    def __init__(self, container, parent=None):
        """
        Constructs all the necessary attributes for the ContainerWidget object.
        Calls the initComponents method, to load the UI file and populate data.
        Parameters
        ----------
        container : Container
            Container object belonging to the GudrunFile.
        parent : QWidget, optional
            Parent widget.
        """
        self.container = container
        self.parent = parent

        super(ContainerWidget, self).__init__(object=self.container, parent=self.parent)
        self.initComponents()
    
    def handlePeriodNoChanged(self, value):
        self.container.periodNo = value
    
    def handleGeometryChanged(self, index):
        self.container.geometry = self.geometryComboBox.itemData(index)

    def handleUpstreamThicknessChanged(self, value):
        self.container.upstreamThickness = value
    
    def handleDownstreamThicknessChanged(self, value):
        self.container.downstreamThickness = value
    
    def handleDensityChanged(self, value):
        self.container.density = value
    
    def handleTotalCrossSectionChanged(self, index):
        self.container.totalCrossSectionSource = self.totalCrossSectionComboBox.itemData(index)
    
    def handleTweakFactorChanged(self, value):
        self.container.tweakFactor = value
    
    def handleAngleOfRotationChanged(self, value):
        self.container.angleOfRotation = value

    def handleSampleWidthChanged(self, value):
        self.container.sampleWidth = value
    
    def handleScatteringFractionChanged(self, value):
        self.container.scatteringFraction = value
    
    def handleAttenuationCoefficientChanged(self, value):
        self.container.attenuationCoefficient = value

    def initComponents(self):
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

        self.periodNoSpinBox.setValue(self.container.periodNumber)
        self.periodNoSpinBox.valueChanged.connect(self.handlePeriodNoChanged)
        self.dataFilesList.addItems([df for df in self.container.dataFiles.dataFiles])

        for i, element in enumerate(self.container.composition.elements):
            self.containerCompositionTable.setItem(i, 0, QTableWidgetItem(str(element.atomicSymbol)))
            self.containerCompositionTable.setItem(i, 1, QTableWidgetItem(str(element.massNo)))
            self.containerCompositionTable.setItem(i, 2, QTableWidgetItem(str(element.abundance)))

        self.geometryComboBox.addItems([g.name for g in Geometry])
        self.geometryComboBox.setCurrentIndex(self.container.geometry.value)
        self.geometryComboBox.currentIndexChanged.connect(self.handleGeometryChanged)

        self.upstreamSpinBox.setValue(self.container.upstreamThickness)
        self.upstreamSpinBox.valueChanged.connect(self.handleUpstreamThicknessChanged)
        self.downstreamSpinBox.setValue(self.container.downstreamThickness)
        self.downstreamSpinBox.valueChanged.connect(self.handleDownstreamThicknessChanged)

        self.densitySpinBox.setValue(self.container.density)
        self.densitySpinBox.valueChanged.connect(self.handleDensityChanged)

        for du in UnitsOfDensity:
            self.densityUnitsComboBox.addItem(du.name, du)
        self.densityUnitsComboBox.setCurrentIndex(self.container.densityUnits.value)

        crossSectionSources = ["TABLES", "TRANSMISSION MONITOR", "FILENAME"]
        if "TABLES" in self.container.totalCrossSectionSource:
            index = 0
        elif "TRANSMISSION" in self.container.totalCrossSectionSource:
            index = 1
        else:
            index = 2
        self.totalCrossSectionComboBox.addItems(crossSectionSources)
        self.totalCrossSectionComboBox.setCurrentIndex(index)
        self.totalCrossSectionComboBox.currentIndexChanged.connect(self.handleTotalCrossSectionChanged)

        self.tweakFactorSpinBox.setValue(self.container.tweakFactor)
        self.tweakFactorSpinBox.valueChanged.connect(self.handleTweakFactorChanged)

        self.angleOfRotationSpinBox.setValue(self.container.angleOfRotation)
        self.angleOfRotationSpinBox.valueChanged.connect(self.handleAngleOfRotationChanged)
        self.sampleWidthSpinBox.setValue(self.container.sampleWidth)
        self.sampleWidthSpinBox.valueChanged.connect(self.handleSampleWidthChanged)

        self.scatteringFractionSpinBox.setValue(self.container.scatteringFraction)
        self.scatteringFractionSpinBox.valueChanged.connect(self.handleScatteringFractionChanged)
        self.attenuationCoefficienSpinBox.setValue(self.container.attenuationCoefficient)
        self.attenuationCoefficienSpinBox.valueChanged.connect(self.handleAttenuationCoefficientChanged)
