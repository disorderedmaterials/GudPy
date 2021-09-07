from PyQt5.QtWidgets import QTableWidgetItem, QWidget
from PyQt5 import uic
import os
from src.gudrun_classes.enums import Geometry

class BeamWidget(QWidget):
    """
    Class to represent a BeamWidget. Inherits QWidget.

    ...

    Attributes
    ----------
    beam : Beam
        Beam object belonging to the GudrunFile.
    parent : QWidget
        Parent widget.
    Methods
    -------
    initComponents()
        Loads UI file, and then populates data from the Beam.
    """
    def __init__(self, beam, parent=None):
        """
        Constructs all the necessary attributes for the BeamWidget object.
        Calls the initComponents method, to load the UI file and populate data.
        Parameters
        ----------
        beam : Beam
            Beam object belonging to the GudrunFile
        parent : QWidget, optional
            Parent widget.
        """
        self.beam = beam
        self.parent = parent

        super(BeamWidget, self).__init__(object=self.beam, parent=self.parent)
        self.initComponents()
    
    def handleGeometryChanged(self, index):
        self.beam.sampleGeometry = self.sampleGeometryComboBox.itemData(index)

    def initComponents(self):
        """
        Loads the UI file for the BeamWidget object,
        and then populates the child widgets with their
        corresponding data from the attributes of the Beam object.
        Parameters
        """

        # Get the current directory that we are residing in.
        current_dir = os.path.dirname(os.path.realpath(__file__))
        # Join the current directory with the relative path of the UI file.
        uifile = os.path.join(current_dir, "ui_files/beamWidget.ui")
        
        # Use pyuic to load to the UI file into the BeamWidget.
        uic.loadUi(uifile, self)

        # Populate the Geometry combo box with the names of the members of the Geometry enum.
        for g in Geometry:
            self.sampleGeometryComboBox.addItem(g.name, g)
        # Set the selected item to that defined in the Beam object.
        self.sampleGeometryComboBox.setCurrentIndex(self.beam.sampleGeometry.value)
        self.sampleGeometryComboBox.currentIndexChanged.connect(self.handleGeometryChanged)


        # Load the rest of the attributes, by setting the text of their corresponding
        # QLineEdits to their string value.
        self.absorptionStepSizeSpinBox.setValue(self.beam.stepSizeAbsorption)
        self.msCalculationStepSizeSpinBox.setValue(self.beam.stepSizeMS)
        self.noSlicesSpinBox.setValue(self.beam.noSlices)
        self.stepForCorrectionsSpinBox.setValue(self.beam.angularStepForCorrections)

        self.leftIncidentBeamEdgeSpinBox.setValue(self.beam.incidentBeamLeftEdge)
        self.rightIncidentBeamEdgeSpinBox.setValue(self.beam.incidentBeamRightEdge)
        self.topIncidentBeamEdgeSpinBox.setValue(self.beam.incidentBeamTopEdge)
        self.bottomIncidentBeamEdgeSpinBox.setValue(self.beam.incidentBeamBottomEdge)

        self.leftScatteredBeamEdgeSpinBox.setValue(self.beam.scatteredBeamLeftEdge)
        self.rightScatteredBeamEdgeSpinBox.setValue(self.beam.scatteredBeamRightEdge)
        self.topScatteredBeamEdgeSpinBox.setValue(self.beam.scatteredBeamTopEdge)
        self.bottomScatteredBeamEdgeSpinBox.setValue(self.beam.scatteredBeamBottomEdge)

        self.incidentBeamSpectrumParametersLineEdit.setText(self.beam.filenameIncidentBeamSpectrumParams)

        self.overallBackgroundFactorSpinBox.setValue(self.beam.overallBackgroundFactor)
        self.sampleDependantBackgroundFactorSpinBox.setValue(self.beam.sampleDependantBackgroundFactor)
        self.shieldingSpinBox.setValue(self.beam.shieldingAttenuationCoefficient)

        # Fill the Beam Profile Values table.
        for i, val in enumerate(self.beam.beamProfileValues):
            # Integer division by 5 of the current beam profile values index gives the row.
            # The current beam profile values index modulo 5 gives the column.
            self.beamProfileValuesTable.setItem(i//5, i%5, QTableWidgetItem(str(val)))