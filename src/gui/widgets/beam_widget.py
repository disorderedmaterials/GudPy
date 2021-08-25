from src.gui.widgets.gudpy_widget import GudPyWidget
from PyQt5.QtWidgets import QTableWidgetItem, QWidget
from PyQt5 import uic
import os
from src.gudrun_classes.enums import Geometry

class BeamWidget(GudPyWidget):
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
        parent : QWidget
            Parent widget.
        """
        self.beam = beam
        self.parent = parent

        super(BeamWidget, self).__init__(object=self.beam, parent=self.parent)
        self.initComponents()
    

    def initComponents(self):
        """
        Loads the UI file for the BeamWidget object,
        and then populates the child widgets with their
        corresponding data from the attributes of the Beam object.
        Parameters
        ----------
        beam : Beam
            Beam object belonging to the GudrunFile
        parent : QWidget
            Parent widget.
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


        # Load the rest of the attributes, by setting the text of their corresponding
        # QLineEdits to their string value.
        self.absorptionStepSizeLineEdit.setText(str(self.beam.stepSizeAbsorption))
        self.msCalculationStepSizeLineEdit.setText(str(self.beam.stepSizeMS))
        self.noSlicesLineEdit.setText(str(self.beam.noSlices))
        self.stepForCorrectionsLineEdit.setText(str(self.beam.angularStepForCorrections))

        self.leftIncidentBeamLineEdit.setText(str(self.beam.incidentBeamLeftEdge))
        self.rightIncidentBeamLineEdit.setText(str(self.beam.incidentBeamRightEdge))
        self.topIncidentBeamLineEdit.setText(str(self.beam.incidentBeamTopEdge))
        self.bottomIncidentBeamLineEdit.setText(str(self.beam.incidentBeamBottomEdge))

        self.leftScatteredBeamLineEdit.setText(str(self.beam.scatteredBeamLeftEdge))
        self.rightScatteredBeamLineEdit.setText(str(self.beam.scatteredBeamRightEdge))
        self.topScatteredBeamLineEdit.setText(str(self.beam.scatteredBeamTopEdge))
        self.bottomScatteredBeamLineEdit.setText(str(self.beam.scatteredBeamBottomEdge))

        self.incidentBeamSpectrumParametersLineEdit.setText(self.beam.filenameIncidentBeamSpectrumParams)

        self.overallBackgroundFactorLineEdit.setText(str(self.beam.overallBackgroundFactor))
        self.sampleDependantBackgroundFactorLineEdit.setText(str(self.beam.sampleDependantBackgroundFactor))
        self.shieldingLineEdit.setText(str(self.beam.shieldingAttenuationCoefficient))

        # Fill the Beam Profile Values table.
        for i, val in enumerate(self.beam.beamProfileValues):
            # Integer division by 5 of the current beam profile values index gives the row.
            # The current beam profile values index modulo 5 gives the column.
            self.beamProfileValuesTable.setItem(i//5, i%5, QTableWidgetItem(str(val)))