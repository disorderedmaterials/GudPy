import re
from PySide6.QtWidgets import QFileDialog

from core.enums import Geometry, Instruments
from core import config


class BeamSlots():

    def __init__(self, widget, parent):
        self.widget = widget
        self.parent = parent
        self.widgetsRefreshing = False
        self.setupBeamSlots()

    def setBeam(self, beam):
        self.beam = beam

        self.widget.beamChart.setBeam(self.beam)
        self.widgetsRefreshing = True

        self.widget.beamGeometryComboBox.setCurrentIndex(
            self.beam.sampleGeometry.value
        )

        self.widget.absorptionStepSizeSpinBox.setValue(
            self.beam.stepSizeAbsorption
        )

        self.widget.msCalculationStepSizeSpinBox.setValue(self.beam.stepSizeMS)

        self.widget.noSlicesSpinBox.setValue(self.beam.noSlices)

        self.widget.stepForCorrectionsSpinBox.setValue(
            self.beam.angularStepForCorrections
        )

        self.widget.leftIncidentBeamEdgeSpinBox.setValue(
            self.beam.incidentBeamLeftEdge
        )

        self.widget.rightIncidentBeamEdgeSpinBox.setValue(
            self.beam.incidentBeamRightEdge
        )

        self.widget.topIncidentBeamEdgeSpinBox.setValue(
            self.beam.incidentBeamTopEdge
        )
        self.widget.bottomIncidentBeamEdgeSpinBox.setValue(
            self.beam.incidentBeamBottomEdge
        )

        self.widget.incidentBeamSpectrumParametersLineEdit.setText(
            self.beam.filenameIncidentBeamSpectrumParams
        )

        self.widget.leftScatteredBeamEdgeSpinBox.setValue(
            self.beam.scatteredBeamLeftEdge
        )
        self.widget.rightScatteredBeamEdgeSpinBox.setValue(
            self.beam.scatteredBeamRightEdge
        )
        self.widget.topScatteredBeamEdgeSpinBox.setValue(
            self.beam.scatteredBeamTopEdge
        )
        self.widget.bottomScatteredBeamEdgeSpinBox.setValue(
            self.beam.scatteredBeamBottomEdge
        )

        self.widget.overallBackgroundFactorSpinBox.setValue(
            self.beam.overallBackgroundFactor
        )

        self.widget.sampleDependantBackgroundFactorSpinBox.setValue(
            self.beam.sampleDependantBackgroundFactor
        )

        self.widget.shieldingSpinBox.setValue(
            self.beam.shieldingAttenuationCoefficient
        )

        self.updateBeamProfileValues()
        self.widget.beamChart.plot()

        # Release the lock
        self.widgetsRefreshing = False

    def setupBeamSlots(self):

        # Populate the Geometry combo box
        # with the names of the members of the Geometry enum.
        for g in Geometry:
            if not g == Geometry.SameAsBeam:
                self.widget.beamGeometryComboBox.addItem(g.name, g)

        # Set up the widget and slot, for Geometry.

        self.widget.beamGeometryComboBox.currentIndexChanged.connect(
            self.handleGeometryChanged
        )

        # Setup widgets and slots, for
        # step sizes for absorption / m.s. calculation and no slices.
        self.widget.absorptionStepSizeSpinBox.valueChanged.connect(
            self.handleAbsorptionStepSizeChanged
        )

        self.widget.msCalculationStepSizeSpinBox.valueChanged.connect(
            self.handleMSStepSizeChanged
        )

        self.widget.noSlicesSpinBox.valueChanged.connect(
            self.handleNoSlicesChanged
        )

        # Setup widgets and slots, for Step size for angular corrections.

        self.widget.stepForCorrectionsSpinBox.valueChanged.connect(
            self.handleStepSizeForCorrectionsChanged
        )

        # Setup widgets and slots, for Incident beam.

        self.widget.leftIncidentBeamEdgeSpinBox.valueChanged.connect(
            self.handleLeftIncidentBeamEdgeChanged
        )

        self.widget.rightIncidentBeamEdgeSpinBox.valueChanged.connect(
            self.handleRightIncidentBeamEdgeChanged
        )

        self.widget.topIncidentBeamEdgeSpinBox.valueChanged.connect(
            self.handleTopIncidentBeamEdgeChanged
        )

        self.widget.bottomIncidentBeamEdgeSpinBox.valueChanged.connect(
            self.handleBottomIncidentBeamEdgeChanged
        )

        self.widget.incidentBeamSpectrumParametersLineEdit.textChanged.connect(
            self.handleIncidentBeamSpectrumParamsFileChanged
        )
        self.widget.browseIncidentBeamSpectrumParametersButton.clicked.connect(
            self.handleBrowseIncidentBeamSpectrumParams
        )

        self.widget.leftScatteredBeamEdgeSpinBox.valueChanged.connect(
            self.handleLeftScatteredBeamEdgeChanged
        )

        self.widget.rightScatteredBeamEdgeSpinBox.valueChanged.connect(
            self.handleRightScatteredBeamEdgeChanged
        )

        self.widget.topScatteredBeamEdgeSpinBox.valueChanged.connect(
            self.handleTopScatteredBeamEdgeChanged
        )

        self.widget.bottomScatteredBeamEdgeSpinBox.valueChanged.connect(
            self.handleBottomScatteredBeamEdgeChanged
        )

        self.widget.overallBackgroundFactorSpinBox.valueChanged.connect(
            self.handleOverallBackgroundFactorChanged
        )

        (
            self.widget.sampleDependantBackgroundFactorSpinBox
        ).valueChanged.connect(
            self.handleSampleDependantBackgroundFactorChanged
        )

        self.widget.shieldingSpinBox.valueChanged.connect(
            self.handleShieldingAbsorptionCoeffChanged
        )

        self.widget.addBeamValueButton.clicked.connect(
            self.handleAddBeamProfileValue
        )
        self.widget.removeBeamValueButton.clicked.connect(
            self.handleRemoveBeamProfileValue
        )

    def handleGeometryChanged(self, index):
        """
        Slot for handling change in sample geometry.
        Called when a currentIndexChanged signal is emitted,
        from the beamGeometryComboBox.
        Alters the beam geometry as such, and updates the global
        geometry too.
        Parameters
        ----------
        index : int
            The new current index of the beamGeometryComboBox.
        """
        self.beam.sampleGeometry = (
            self.widget.beamGeometryComboBox.itemData(index)
        )
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
        match = re.search(
            r"StartupFiles\S*",
            value
        )
        if match:
            self.beam.filenameIncidentBeamSpectrumParams = match.group()
        else:
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
        import os
        instrumentFilesDir = os.path.join(
            self.parent.gudrunFile.instrument.GudrunStartFolder,
            self.parent.gudrunFile.instrument.startupFileFolder,
            Instruments(self.parent.gudrunFile.instrument.name.value).name
        )
        filename, _ = QFileDialog.getOpenFileName(
            self.widget,
            "Incident beam spectrum parameters",
            instrumentFilesDir
        )
        if filename:
            match = re.search(r"StartupFiles\S*", filename)
            if match:
                self.widget.incidentBeamSpectrumParametersLineEdit.setText(
                    match.group()
                )
            else:
                self.widget.incidentBeamSpectrumParametersLineEdit.setText(
                    filename
                )

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
        self.widget.beamProfileValuesTable.makeModel(
            self.beam.beamProfileValues
        )
        self.widget.beamProfileValuesTable.model().dataChanged.connect(
            self.handleBeamProfileValueChanged
        )

    def handleAddBeamProfileValue(self):
        """
        Slot for adding a row to the beam profile values table.
        Called when a clicked signal is emitted,
        from the addBeamValueButton.
        """
        self.widget.beamProfileValuesTable.insertRow()
        if not self.widgetsRefreshing:
            self.parent.setModified()
        self.widget.beamChart.plot()

    def handleRemoveBeamProfileValue(self):
        """
        Slot for removing the selected row from the beam profile values table.
        Called when a clicked signal is emitted,
        from the addBeamValueButton.
        """
        self.widget.beamProfileValuesTable.removeRow(
            self.widget.beamProfileValuesTable.selectionModel().selectedRows()
        )
        if not self.widgetsRefreshing:
            self.parent.setModified()
        self.widget.beamChart.plot()

    def handleBeamProfileValueChanged(self):
        """
        Slot for modifying the current beam profile value in the table.
        Called when a dataChagned signal is emitted
        from the beamProfileValuesTable.
        """
        if not self.widgetsRefreshing:
            self.parent.setModified()
        self.widget.beamChart.plot()