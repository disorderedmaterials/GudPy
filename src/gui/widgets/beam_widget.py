from PyQt5.QtWidgets import QTableWidgetItem, QWidget
from PyQt5 import uic
import os
from src.gudrun_classes.enums import Geometry
from src.gudrun_classes import config


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

        super(BeamWidget, self).__init__(parent=self.parent)
        self.initComponents()

    def handleGeometryChanged(self, index):
        self.beam.sampleGeometry = self.sampleGeometryComboBox.itemData(index)
        config.geometry = self.beam.sampleGeometry

    def handleAbsorptionStepSizeChanged(self, value):
        self.beam.stepSizeAbsorption = value

    def handleMSStepSizeChanged(self, value):
        self.beam.stepSizeMS = value

    def handleNoSlicesChanged(self, value):
        self.beam.noSlices = value

    def handleStepSizeForCorrectionsChanged(self, value):
        self.beam.angularStepForCorrections = value

    def handleLeftIncidentBeamEdgeChanged(self, value):
        self.beam.incidentBeamLeftEdge = value

    def handleRightIncidentBeamEdgeChanged(self, value):
        self.beam.incidentBeamRightEdge = value

    def handleTopIncidentBeamEdgeChanged(self, value):
        self.beam.incidentBeamTopEdge = value

    def handleBottomIncidentBeamEdgeChanged(self, value):
        self.beam.incidentBeamBottomEdge = value

    def handleLeftScatteredBeamEdgeChanged(self, value):
        self.beam.scatteredBeamLeftEdge = value

    def handleRightScatteredBeamEdgeChanged(self, value):
        self.beam.scatteredBeamRightEdge = value

    def handleTopScatteredBeamEdgeChanged(self, value):
        self.beam.scatteredBeamTopEdge = value

    def handleBottomScatteredBeamEdgeChanged(self, value):
        self.beam.scatteredBeamBottomEdge = value

    def handleIncidentBeamSpectrumParamsFileChanged(self, value):
        self.beam.filenameIncidentBeamSpectrumParams = value

    def handleOverallBackgroundFactorChanged(self, value):
        self.beam.overallBackgroundFactor = value

    def handleSampleDependantBackgroundFactorChanged(self, value):
        self.beam.sampleDependantBackgroundFactor = value

    def handleShieldingAbsorptionFileChanged(self, value):
        self.beam.shieldingAttenuationCoefficient = value

    def updateBeamProfileValues(self):
        # Fill the Beam Profile table.
        self.beamProfileValuesTable.makeModel(self.beam.beamProfileValues)

    def handleAddBeamProfileValue(self):
        self.beamProfileValuesTable.insertRow()

    def handleRemoveBeamProfileValue(self):
        self.beamProfileValuesTable.removeRow(
            self.beamProfileValuesTable.selectionModel().selectedRows()
        )

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

        # Populate the Geometry combo box
        # with the names of the members of the Geometry enum.
        for g in Geometry:
            self.sampleGeometryComboBox.addItem(g.name, g)

        # Set the selected item to that defined in the Beam object.
        self.sampleGeometryComboBox.setCurrentIndex(
            self.beam.sampleGeometry.value
        )
        self.sampleGeometryComboBox.currentIndexChanged.connect(
            self.handleGeometryChanged
        )

        self.absorptionStepSizeSpinBox.setValue(self.beam.stepSizeAbsorption)
        self.absorptionStepSizeSpinBox.valueChanged.connect(
            self.handleAbsorptionStepSizeChanged
        )
        self.msCalculationStepSizeSpinBox.setValue(self.beam.stepSizeMS)
        self.msCalculationStepSizeSpinBox.valueChanged.connect(
            self.handleMSStepSizeChanged
        )
        self.noSlicesSpinBox.setValue(self.beam.noSlices)

        self.noSlicesSpinBox.valueChanged.connect(self.handleNoSlicesChanged)
        self.stepForCorrectionsSpinBox.setValue(
            self.beam.angularStepForCorrections
        )
        self.stepForCorrectionsSpinBox.valueChanged.connect(
            self.handleStepSizeForCorrectionsChanged
        )

        self.leftIncidentBeamEdgeSpinBox.setValue(
            self.beam.incidentBeamLeftEdge
        )
        self.leftIncidentBeamEdgeSpinBox.valueChanged.connect(
            self.handleLeftIncidentBeamEdgeChanged
        )
        self.rightIncidentBeamEdgeSpinBox.setValue(
            self.beam.incidentBeamRightEdge
        )
        self.rightIncidentBeamEdgeSpinBox.valueChanged.connect(
            self.handleRightIncidentBeamEdgeChanged
        )
        self.topIncidentBeamEdgeSpinBox.setValue(self.beam.incidentBeamTopEdge)
        self.topIncidentBeamEdgeSpinBox.valueChanged.connect(
            self.handleTopIncidentBeamEdgeChanged
        )
        self.bottomIncidentBeamEdgeSpinBox.setValue(
            self.beam.incidentBeamBottomEdge
        )
        self.bottomIncidentBeamEdgeSpinBox.valueChanged.connect(
            self.handleBottomIncidentBeamEdgeChanged
        )

        self.leftScatteredBeamEdgeSpinBox.setValue(
            self.beam.scatteredBeamLeftEdge
        )
        self.leftScatteredBeamEdgeSpinBox.valueChanged.connect(
            self.handleLeftScatteredBeamEdgeChanged
        )
        self.rightScatteredBeamEdgeSpinBox.setValue(
            self.beam.scatteredBeamRightEdge
        )
        self.rightScatteredBeamEdgeSpinBox.valueChanged.connect(
            self.handleRightScatteredBeamEdgeChanged
        )
        self.topScatteredBeamEdgeSpinBox.setValue(
            self.beam.scatteredBeamTopEdge
        )
        self.topScatteredBeamEdgeSpinBox.valueChanged.connect(
            self.handleTopScatteredBeamEdgeChanged
        )
        self.bottomScatteredBeamEdgeSpinBox.setValue(
            self.beam.scatteredBeamBottomEdge
        )
        self.bottomScatteredBeamEdgeSpinBox.valueChanged.connect(
            self.handleBottomScatteredBeamEdgeChanged
        )

        self.incidentBeamSpectrumParametersLineEdit.setText(
            self.beam.filenameIncidentBeamSpectrumParams
        )
        self.incidentBeamSpectrumParametersLineEdit.textChanged.connect(
            self.handleIncidentBeamSpectrumParamsFileChanged
        )

        self.overallBackgroundFactorSpinBox.setValue(
            self.beam.overallBackgroundFactor
        )
        self.overallBackgroundFactorSpinBox.valueChanged.connect(
            self.handleOverallBackgroundFactorChanged
        )

        self.sampleDependantBackgroundFactorSpinBox.setValue(
            self.beam.sampleDependantBackgroundFactor
        )
        self.sampleDependantBackgroundFactorSpinBox.valueChanged.connect(
            self.handleSampleDependantBackgroundFactorChanged
        )
        self.shieldingSpinBox.setValue(
            self.beam.shieldingAttenuationCoefficient
        )
        self.shieldingSpinBox.valueChanged.connect(
            self.handleShieldingAbsorptionFileChanged
        )

        self.updateBeamProfileValues()
        self.addBeamValueButton.clicked.connect(self.handleAddBeamProfileValue)
        self.removeBeamValueButton.clicked.connect(
            self.handleRemoveBeamProfileValue
        )
