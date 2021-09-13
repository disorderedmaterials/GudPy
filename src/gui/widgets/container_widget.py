from src.gudrun_classes.element import Element
from src.scripts.utils import isnumeric
from src.gudrun_classes.enums import Geometry, UnitsOfDensity
from PyQt5.QtWidgets import QFileDialog, QTableWidgetItem, QWidget
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

        super(ContainerWidget, self).__init__(parent=self.parent)
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
        self.container.totalCrossSectionSource = (
            self.totalCrossSectionComboBox.itemData(index)
        )

    def handleTweakFactorChanged(self, value):
        self.container.tweakFactor = value

    def handleAngleOfRotationChanged(self, value):
        self.container.angleOfRotation = value

    def handleSampleWidthChanged(self, value):
        self.container.sampleWidth = value

    def handleSampleHeightChanged(self, value):
        self.container.sampleHeight = value

    def handleScatteringFractionChanged(self, value):
        self.container.scatteringFraction = value

    def handleAttenuationCoefficientChanged(self, value):
        self.container.attenuationCoefficient = value

    def handleDataFilesAltered(self, item):
        index = item.row()
        value = item.text()
        if not value:
            self.container.dataFiles.dataFiles.remove(index)
        else:
            self.container.dataFiles.dataFiles[index] = value
        self.updateDataFilesList()

    def handleDataFileInserted(self, item):
        value = item.text()
        self.container.dataFiles.dataFiles.append(value)

    def updateDataFilesList(self):
        self.dataFilesList.clear()
        self.dataFilesList.addItems(
            [df for df in self.container.dataFiles.dataFiles]
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
        if row < len(self.container.composition.elements):
            element = self.container.composition.elements[row]
            attribute = {
                0: ("atomicSymbol", str),
                1: ("massNo", int),
                2: ("abundance", float)
            }[col]
            element.__dict__[attribute[0]] = attribute[1](value)
            self.container.composition.elements[row] = element
        else:
            self.handleElementInserted(item)

    def handleElementInserted(self, item):
        row = item.row()
        print(item.text())
        atomicSymbol = self.containerCompositionTable.itemAt(row, 0).text()
        massNo = self.containerCompositionTable.itemAt(row, 1).text()
        abundance = self.containerCompositionTable.itemAt(row, 2).text()
        if len(atomicSymbol) and isnumeric(massNo) and isnumeric(abundance):
            print(atomicSymbol, massNo, abundance)
            element = Element(atomicSymbol, int(massNo), float(abundance))
            self.container.composition.elements.append(element)

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
                self.container.dataFiles
            )
        )
        for i, element in enumerate(self.container.composition.elements):
            self.containerCompositionTable.setItem(
                i, 0, QTableWidgetItem(str(element.atomicSymbol))
            )
            self.containerCompositionTable.setItem(
                i, 1, QTableWidgetItem(str(element.massNo))
            )
            self.containerCompositionTable.setItem(
                i, 2, QTableWidgetItem(str(element.abundance))
            )

        self.containerCompositionTable.itemChanged.connect(
            self.handleElementChanged
        )
        self.containerCompositionTable.itemEntered.connect(
            self.handleElementInserted
        )

        self.geometryComboBox.addItems([g.name for g in Geometry])
        self.geometryComboBox.setCurrentIndex(self.container.geometry.value)
        self.geometryComboBox.currentIndexChanged.connect(
            self.handleGeometryChanged
        )
        self.geometryComboBox.setDisabled(True)

        self.upstreamSpinBox.setValue(self.container.upstreamThickness)
        self.upstreamSpinBox.valueChanged.connect(
            self.handleUpstreamThicknessChanged
        )
        self.downstreamSpinBox.setValue(self.container.downstreamThickness)
        self.downstreamSpinBox.valueChanged.connect(
            self.handleDownstreamThicknessChanged
        )

        self.densitySpinBox.setValue(self.container.density)
        self.densitySpinBox.valueChanged.connect(self.handleDensityChanged)

        for du in UnitsOfDensity:
            self.densityUnitsComboBox.addItem(du.name, du)
        self.densityUnitsComboBox.setCurrentIndex(
            self.container.densityUnits.value
        )

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

        self.geometryInfoStack.setCurrentIndex(config.geometry.value)
        self.angleOfRotationSpinBox.setValue(self.container.angleOfRotation)
        self.angleOfRotationSpinBox.valueChanged.connect(
            self.handleAngleOfRotationChanged
        )
        self.sampleWidthSpinBox.setValue(self.container.sampleWidth)
        self.sampleWidthSpinBox.valueChanged.connect(
            self.handleSampleWidthChanged
        )
        self.sampleHeightSpinBox.setValue(self.container.sampleHeight)
        self.sampleHeightSpinBox.valueChanged.connect(
            self.handleSampleHeightChanged
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
