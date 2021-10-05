from PyQt6.QtWidgets import QFileDialog, QWidget
from PyQt6 import uic
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
    handleGeometryChanged(index)
        Slot for handling change in sample geometry.
    handleAbsorptionStepSizeChanged(value)
        Slot for handling change in step size for absorption.
    handleMSStepSizeChanged(value)
        Slot for handling change in step size for m.s. calculation.
    handleNoSlicesChanged(value)
        Slot for handling change in number of slices for m.s. calculation.
    handleStepSizeForCorrectionsChanged(value)
        Slot for handling change in angular step size for corrections.
    handleLeftIncidentBeamEdgeChanged(value)
        Slot for handling change in left incident beam edge.
    handleRightIncidentBeamEdgeChanged(value)
        Slot for handling change in right incident beam edge.
    handleTopIncidentBeamEdgeChanged(value)
        Slot for handling change in top incident beam edge.
    handleBottomIncidentBeamEdgeChanged(value)
        Slot for handling change in bottom incident beam edge.
    handleLeftScatteredBeamEdgeChanged(value)
        Slot for handling change in the left scattered beam edge.
    handleRightScatteredBeamEdgeChanged(value)
        Slot for handling change in the right scattered beam edge.
    handleTopScatteredBeamEdgeChanged(value)
        Slot for handling change in the top scattered beam edge.
    handleBottomScatteredBeamEdgeChanged(value)
        Slot for handling change in the bottom scattered beam edge.
    handleIncidentBeamSpectrumParamsFileChanged(value)
        Slot for handling change in the file
        for incident beam spectrum parameters.
    handleBrowseIncidentBeamSpectrumParams()
        Slot for browsing for an incident beam spectrum parameters file.
    handleOverallBackgroundFactorChanged(value)
        Slot for handling change in the overall background factor.
    handleSampleDependantBackgroundFactorChanged(value)
        Slot for handling change in the sample dependant background factor.
    handleShieldingAbsorptionCoeffChanged(value)
        Slot for handling change in the shielding absorption coefficient.
    updateBeamProfileValues()
        Fills the beam profile table.
    handleAddBeamProfileValue()
        Slot for adding a row to the beam profile values table.
    handleRemoveBeamProfileValue()
        Slot for removing the selected row from the beam profile values table.
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
        """
        Slot for handling change in sample geometry.
        Called when a currentIndexChanged signal is emitted,
        from the sampleGeometryComboBox.
        Alters the beam geometry as such, and updates the global
        geometry too.
        Parameters
        ----------
        index : int
            The new current index of the sampleGeometryComboBox.
        """
        self.beam.sampleGeometry = self.sampleGeometryComboBox.itemData(index)
        config.geometry = self.beam.sampleGeometry
        if not self.widgetsRefreshing:
            self.parent.setModified()

    def handleAbsorptionStepSizeChanged(self, value):
        """
        Slot for handling change in step size for absorption.
        Called when a valueChanged signal is emitted,
        from the absorptionStepSizeSpinBox.
        Alters the beam's step size fo absorption as such.
        Parameters
        ----------
        value : float
            The new value of the absorptionStepSizeSpinBox.
        """
        self.beam.stepSizeAbsorption = value
        if not self.widgetsRefreshing:
            self.parent.setModified()

    def handleMSStepSizeChanged(self, value):
        """
        Slot for handling change in step size for m.s. calculation.
        Called when a valueChanged signal is emitted,
        from the msCalculationStepSizeSpinBox.
        Alters the beam's step size for m.s. calculation as such.
        Parameters
        ----------
        value : float
            The new value of the absorptionStepSizeSpinBox.
        """
        self.beam.stepSizeMS = value
        if not self.widgetsRefreshing:
            self.parent.setModified()

    def handleNoSlicesChanged(self, value):
        """
        Slot for handling change in number of slices for m.s. calculation.
        Called when a valueChanged signal is emitted,
        from the noSlicesSpinBox.
        Alters the beam's no slices for m.s. calculation as such.
        Parameters
        ----------
        value : float
            The new value of the noSlicesSpinBox.
        """
        self.beam.noSlices = value
        if not self.widgetsRefreshing:
            self.parent.setModified()

    def handleStepSizeForCorrectionsChanged(self, value):
        """
        Slot for handling change in angular step size for corrections.
        Called when a valueChanged signal is emitted,
        from the stepForCorrectionsSpinBox.
        Alters the beam's step size for corrections as such.
        Parameters
        ----------
        value : float
            The new value of the stepForCorrectionsSpinBox.
        """
        self.beam.angularStepForCorrections = value
        if not self.widgetsRefreshing:
            self.parent.setModified()

    def handleLeftIncidentBeamEdgeChanged(self, value):
        """
        Slot for handling change in left incident beam edge.
        Called when a valueChanged signal is emitted,
        from the leftIncidentBeamEdgeSpinBox.
        Alters the beam's left incident beam edge as such.
        Parameters
        ----------
        value : float
            The new value of the leftIncidentBeamEdgeSpinBox.
        """
        self.beam.incidentBeamLeftEdge = value
        if not self.widgetsRefreshing:
            self.parent.setModified()

    def handleRightIncidentBeamEdgeChanged(self, value):
        """
        Slot for handling change in right incident beam edge.
        Called when a valueChanged signal is emitted,
        from the leftIncidentBeamEdgeSpinBox.
        Alters the beam's right incident beam edge as such.
        Parameters
        ----------
        value : float
            The new value of the rightIncidentBeamEdgeSpinBox.
        """
        self.beam.incidentBeamRightEdge = value
        if not self.widgetsRefreshing:
            self.parent.setModified()

    def handleTopIncidentBeamEdgeChanged(self, value):
        """
        Slot for handling change in top incident beam edge.
        Called when a valueChanged signal is emitted,
        from the topIncidentBeamEdgeSpinBox.
        Alters the beam's top incident beam edge as such.
        Parameters
        ----------
        value : float
            The new value of the topIncidentBeamEdgeSpinBox.
        """
        self.beam.incidentBeamTopEdge = value
        if not self.widgetsRefreshing:
            self.parent.setModified()

    def handleBottomIncidentBeamEdgeChanged(self, value):
        """
        Slot for handling change in bottom incident beam edge.
        Called when a valueChanged signal is emitted,
        from the bottomIncidentBeamEdgeSpinBox.
        Alters the beam's bottom incident beam edge as such.
        Parameters
        ----------
        value : float
            The new value of the bottomIncidentBeamEdgeSpinBox.
        """
        self.beam.incidentBeamBottomEdge = value
        if not self.widgetsRefreshing:
            self.parent.setModified()

    def handleLeftScatteredBeamEdgeChanged(self, value):
        """
        Slot for handling change in left scattered beam edge.
        Called when a valueChanged signal is emitted,
        from the leftScatteredBeamEdgeSpinBox.
        Alters the beam's left scattered beam edge as such.
        Parameters
        ----------
        value : float
            The new value of the leftScatteredBeamEdgeSpinBox.
        """
        self.beam.scatteredBeamLeftEdge = value
        if not self.widgetsRefreshing:
            self.parent.setModified()

    def handleRightScatteredBeamEdgeChanged(self, value):
        """
        Slot for handling change in right scattered beam edge.
        Called when a valueChanged signal is emitted,
        from the rightScatteredBeamEdgeSpinBox.
        Alters the beam's right scattered beam edge as such.
        Parameters
        ----------
        value : float
            The new value of the rightScatteredBeamEdgeSpinBox.
        """
        self.beam.scatteredBeamRightEdge = value
        if not self.widgetsRefreshing:
            self.parent.setModified()

    def handleTopScatteredBeamEdgeChanged(self, value):
        """
        Slot for handling change in top scattered beam edge.
        Called when a valueChanged signal is emitted,
        from the topScatteredBeamEdgeSpinBox.
        Alters the beam's top scattered beam edge as such.
        Parameters
        ----------
        value : float
            The new value of the topScatteredBeamEdgeSpinBox.
        """
        self.beam.scatteredBeamTopEdge = value
        if not self.widgetsRefreshing:
            self.parent.setModified()

    def handleBottomScatteredBeamEdgeChanged(self, value):
        """
        Slot for handling change in bottom scattered beam edge.
        Called when a valueChanged signal is emitted,
        from the bottomScatteredBeamEdgeSpinBox.
        Alters the beam's bottom scattered beam edge as such.
        Parameters
        ----------
        value : float
            The new value of the bottomScatteredBeamEdgeSpinBox.
        """
        self.beam.scatteredBeamBottomEdge = value
        if not self.widgetsRefreshing:
            self.parent.setModified()

    def handleIncidentBeamSpectrumParamsFileChanged(self, value):
        """
        Slot for handling change in the file
        for incident beam spectrum parameters.
        Called when a textChanged signal is emitted,
        from the incidentBeamSpectrumParametersLineEdit.
        Alters the beam's filename for incident beam spectrum parameters
        as such.
        Parameters
        ----------
        value : str
            The new value of the incidentBeamSpectrumParametersLineEdit.
        """
        self.beam.filenameIncidentBeamSpectrumParams = value
        if not self.widgetsRefreshing:
            self.parent.setModified()

    def handleBrowseIncidentBeamSpectrumParams(self):
        """
        Slot for browsing for an incident beam spectrum parameters file.
        Called when a clicked signal is emitted,
        from the browseIncidentBeamSpectrumParametersButton.
        Alters the corresponding line edit as such.
        as such.
        """
        filename, _ = QFileDialog.getOpenFileName(
            self, "Incident beam spectrum parameters", "")
        if filename:
            self.incidentBeamSpectrumParametersLineEdit.setText(filename)

    def handleOverallBackgroundFactorChanged(self, value):
        """
        Slot for handling change in overall background factor.
        Called when a valueChanged signal is emitted,
        from the overallBackgroundFactorSpinBox.
        Alters the beam's overall background factor as such.
        Parameters
        ----------
        value : float
            The new value of the overallBackgroundFactorSpinBox.
        """
        self.beam.overallBackgroundFactor = value
        if not self.widgetsRefreshing:
            self.parent.setModified()

    def handleSampleDependantBackgroundFactorChanged(self, value):
        """
        Slot for handling change in sample dependant background factor.
        Called when a valueChanged signal is emitted,
        from the sampleDependantBackgroundFactorSpinBox.
        Alters the beam's sample dependant background factor as such.
        Parameters
        ----------
        value : float
            The new value of the sampleDependantBackgroundFactorSpinBox.
        """
        self.beam.sampleDependantBackgroundFactor = value
        if not self.widgetsRefreshing:
            self.parent.setModified()

    def handleShieldingAbsorptionCoeffChanged(self, value):
        """
        Slot for handling change in the
        shielding absorption attenuation coefficient.
        Called when a valueChanged signal is emitted,
        from the shieldingSpinBox.
        Alters the beam's absorption shielding attenuation coefficient as such.
        Parameters
        ----------
        value : float
            The new value of the shieldingSpinBox.
        """
        self.beam.shieldingAttenuationCoefficient = value
        if not self.widgetsRefreshing:
            self.parent.setModified()

    def updateBeamProfileValues(self):
        """
        Fills the beam profile table.
        """
        self.beamProfileValuesTable.makeModel(self.beam.beamProfileValues)

    def handleAddBeamProfileValue(self):
        """
        Slot for adding a row to the beam profile values table.
        Called when a clicked signal is emitted,
        from the addBeamValueButton.
        """
        self.beamProfileValuesTable.insertRow()
        if not self.widgetsRefreshing:
            self.parent.setModified()

    def handleRemoveBeamProfileValue(self):
        """
        Slot for removing the selected row from the beam profile values table.
        Called when a clicked signal is emitted,
        from the addBeamValueButton.
        """
        self.beamProfileValuesTable.removeRow(
            self.beamProfileValuesTable.selectionModel().selectedRows()
        )
        if not self.widgetsRefreshing:
            self.parent.setModified()

    def initComponents(self):
        """
        Loads the UI file for the BeamWidget object,
        and then populates the child widgets with their
        corresponding data from the attributes of the Beam object.
        """
        # Acquire the lock
        self.widgetsRefreshing = True
        # Get the current directory that we are residing in.
        current_dir = os.path.dirname(os.path.realpath(__file__))
        # Join the current directory with the relative path of the UI file.
        uifile = os.path.join(current_dir, "ui_files/beamWidget.ui")

        # Use pyuic to load to the UI file into the BeamWidget.
        uic.loadUi(uifile, self)

        # Populate the Geometry combo box
        # with the names of the members of the Geometry enum.
        for g in Geometry:
            if not g == Geometry.SameAsBeam:
                self.sampleGeometryComboBox.addItem(g.name, g)

        # Set up the widget and slot, for Geometry.
        self.sampleGeometryComboBox.setCurrentIndex(
            self.beam.sampleGeometry.value
        )
        self.sampleGeometryComboBox.currentIndexChanged.connect(
            self.handleGeometryChanged
        )

        # Setup widgets and slots, for
        # step sizes for absorption / m.s. calculation and no slices.
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

        # Setup widgets and slots, for Step size for angular corrections.
        self.stepForCorrectionsSpinBox.setValue(
            self.beam.angularStepForCorrections
        )

        self.stepForCorrectionsSpinBox.valueChanged.connect(
            self.handleStepSizeForCorrectionsChanged
        )

        # Setup widgets and slots, for Incident beam.
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
        self.topIncidentBeamEdgeSpinBox.setValue(
            self.beam.incidentBeamTopEdge
        )
        self.topIncidentBeamEdgeSpinBox.valueChanged.connect(
            self.handleTopIncidentBeamEdgeChanged
        )
        self.bottomIncidentBeamEdgeSpinBox.setValue(
            self.beam.incidentBeamBottomEdge
        )
        self.bottomIncidentBeamEdgeSpinBox.valueChanged.connect(
            self.handleBottomIncidentBeamEdgeChanged
        )

        self.incidentBeamSpectrumParametersLineEdit.setText(
            self.beam.filenameIncidentBeamSpectrumParams
        )
        self.incidentBeamSpectrumParametersLineEdit.textChanged.connect(
            self.handleIncidentBeamSpectrumParamsFileChanged
        )
        self.browseIncidentBeamSpectrumParametersButton.clicked.connect(
            self.handleBrowseIncidentBeamSpectrumParams
        )

        # Setup widgets and slots, for Scattered beam.
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

        # Setup widgets and slots, foir background factors.
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

        # Setup widget and slot for the absorption coefficient for shielding.
        self.shieldingSpinBox.setValue(
            self.beam.shieldingAttenuationCoefficient
        )
        self.shieldingSpinBox.valueChanged.connect(
            self.handleShieldingAbsorptionCoeffChanged
        )

        # Setup widget and slot for the beam profile values.
        self.updateBeamProfileValues()
        self.addBeamValueButton.clicked.connect(self.handleAddBeamProfileValue)
        self.removeBeamValueButton.clicked.connect(
            self.handleRemoveBeamProfileValue
        )
        # Release the lock
        self.widgetsRefreshing = False
