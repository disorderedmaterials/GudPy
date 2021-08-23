from src.gui.widgets.gudpy_widget import GudPyWidget
from src.gudrun_classes.enums import Geometry, OutputUnits, UnitsOfDensity
from PyQt5.QtWidgets import QTableWidgetItem, QWidget
from PyQt5 import uic
import os

class ContainerWidget(GudPyWidget):
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
        parent : QWidget
            Parent widget.
        """
        self.container = container
        self.parent = parent

        super(ContainerWidget, self).__init__(object=self.container, parent=self.parent)
        self.initComponents()
    
    def initComponents(self):
        """
        Loads the UI file for the ContainerWidget object,
        and then populates the child widgets with their
        corresponding data from the attributes of the Container object.
        ----------
        Parameters
        container : Container
            Container object belonging to the GudrunFile.
        parent : QWidget
            Parent widget.
        """

        # Get the current directory that we are residing in.
        current_dir = os.path.dirname(os.path.realpath(__file__))
        # Join the current directory with the relative path of the UI file.
        uifile = os.path.join(current_dir, "ui_files/containerWidget.ui")
        
        # Use pyuic to load to the UI file into the ContainerWidget.
        uic.loadUi(uifile, self)

        self.periodNoLineEdit.setText(str(self.container.numberOfFilesPeriodNumber[1]))
        self.dataFilesList.addItems([df for df in self.container.dataFiles.dataFiles])

        for i, element in enumerate(self.container.composition.elements):
            self.containerCompositionTable.setItem(i, 0, QTableWidgetItem(str(element.atomicSymbol)))
            self.containerCompositionTable.setItem(i, 1, QTableWidgetItem(str(element.massNo)))
            self.containerCompositionTable.setItem(i, 2, QTableWidgetItem(str(element.abundance)))

        # self.geometryComboBox.addItems([g.name for g in Geometry])
        # self.geometryComboBox.setCurrentIndex(self.container.geometry.value)
        self.upstreamLineEdit.setText(str(self.container.thickness[0]))
        self.downstreamLineEdit.setText(str(self.container.thickness[1]))



        self.densityLineEdit.setText(str(self.container.density))
        self.densityUnitsComboBox.addItems([du.name for du in UnitsOfDensity])
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

        self.tweakFactorLineEdit.setText(str(self.container.tweakFactor))

        self.angleOfRotationLineEdit.setText(str(self.container.angleOfRotationSampleWidth[0]))
        self.sampleWidthLineEdit.setText(str(self.container.angleOfRotationSampleWidth[1]))

        self.scatteringFractionLineEdit.setText(str(self.container.scatteringFractionAttenuationCoefficient[0]))
        self.attenuationCoefficientLineEdit.setText(str(self.container.scatteringFractionAttenuationCoefficient[1]))