

from PySide6.QtCore import QRegularExpression
from PySide6.QtGui import QRegularExpressionValidator
from src.scripts.utils import spacify
from src.gudrun_classes.enums import Scales, MergeWeights, Instruments

class InstrumentSlots():

    def __init__(self, widget):
        self.widget = widget
        print(self.widget)
        self.widgetsRefreshing = False
        self.setupInstrumentSlots()

    def setInstrument(self, instrument):
        self.instrument = instrument
        self.widgetsRefreshing = True

        self.widget.nameComboBox.setCurrentIndex(self.instrument.name.value)
        # Setup the widgets and slots for configuration files.
        self.widget.dataFileDirectoryLineEdit.setText(self.instrument.dataFileDir)

        dataFileTypes = ["raw", "sav", "txt", "nxs", "*"]
        self.widget.dataFileTypeCombo.setCurrentIndex(
            dataFileTypes.index(self.instrument.dataFileType)
        )

        self.widget.detCalibrationLineEdit.setText(
            self.instrument.detectorCalibrationFileName
        )

        self.widget.groupsFileLineEdit.setText(self.instrument.groupFileName)

        self.widget.deadtimeFileLineEdit.setText(
            self.instrument.deadtimeConstantsFileName
        )

        self.widget.phiValuesColumnSpinBox.setValue(self.instrument.columnNoPhiVals)

        # Setup the widgets and slots for the wavelength range and step size
        # for monitor normalisation.
        self.widget.minWavelengthMonNormSpinBox.setValue(
            self.instrument.wavelengthRangeForMonitorNormalisation[0]
        )
        self.widget.maxWavelengthMonNormSpinBox.setValue(
            self.instrument.wavelengthRangeForMonitorNormalisation[1]
        )

        self.widget.spectrumNumbersIBLineEdit.setText(
            spacify(self.instrument.spectrumNumbersForIncidentBeamMonitor)
        )

        self.widget.incidentMonitorQuietCountConstSpinBox.setValue(
            self.instrument.incidentMonitorQuietCountConst
        )

        # Setup the widgets and slots for the spectrum numbers
        # and quiet count const for the transmission beam monitor.
        self.widget.spectrumNumbersTLineEdit.setText(
            spacify(self.instrument.spectrumNumbersForTransmissionMonitor)
        )

        self.widget.transmissionMonitorQuietCountConstSpinBox.setValue(
            self.instrument.transmissionMonitorQuietCountConst
        )

        # Setup the widgets and slots for the channel numbers
        # to be used for spike analysis.
        self.widget.channelNoASpinBox.setValue(
            self.instrument.channelNosSpikeAnalysis[0]
        )
        self.widget.channelNoBSpinBox.setValue(
            self.instrument.channelNosSpikeAnalysis[1]
        )

        # Setup the widget and slot for the
        # acceptance factor for spike analysis.
        self.widget.acceptanceFactorSpinBox.setValue(
            self.instrument.spikeAnalysisAcceptanceFactor
        )

        # Setup the widgets and slots for the wavelength range and step size.
        self.widget.minWavelengthSpinBox.setValue(self.instrument.wavelengthMin)
        self.widget.maxWavelengthSpinBox.setValue(self.instrument.wavelengthMax)
        self.widget.stepWavelengthSpinBox.setValue(self.instrument.wavelengthStep)

        # Setup the widget and slot for the number of smoothings on monitor.
        self.widget.noSmoothsOnMonitorSpinBox.setValue(
            self.instrument.NoSmoothsOnMonitor
        )

        # Setup the widgets and slots for the scales.
        selection, min_, max_, step = (
            self.scales[self.instrument.scaleSelection]
        )
        selection.setChecked(True)
        min_.setValue(self.instrument.XMin)
        max_.setValue(self.instrument.XMax)
        step.setValue(self.instrument.XStep)

        # Setup the widget and slot for enabling/disabling
        # logarithmic binning.
        self.widget.logarithmicBinningCheckBox.setChecked(
            self.instrument.useLogarithmicBinning
        )

        # Setup the widget and slot for the groups acceptance factor.
        self.widget.groupsAcceptanceFactorSpinBox.setValue(
            self.instrument.groupsAcceptanceFactor
        )

        # Setup the widgets and slots for merging.
        self.widget.mergePowerSpinBox.setValue(self.instrument.mergePower)

        self.widget.mergeWeightsComboBox.setCurrentIndex(
            self.instrument.mergeWeights.value
        )

        # Setup the widget and slot for the incident flight path.
        self.widget.incidentFlightPathSpinBox.setValue(
            self.instrument.incidentFlightPath
        )
        # Setup the widget and slot for the spectrum number
        # for output diagnostics.
        self.widget.outputDiagSpectrumSpinBox.setValue(
            self.instrument.spectrumNumberForOutputDiagnosticFiles
        )

        self.widget.neutronScatteringParamsFileLineEdit.setText(
            self.instrument.neutronScatteringParametersFile
        )

        self.widget.nexusDefintionFileLineEdit.setText(
            self.instrument.nxsDefinitionFile
        )

        self.widget.nexusDefintionFileLineEdit.setEnabled(
            self.instrument.dataFileType in ["nxs", "NXS"]
        )
        self.widget.browseNexusDefinitionButton.setEnabled(
            self.instrument.dataFileType in ["nxs", "NXS"]
        )

        # Setup the widget and slot for enabling/disablign hard group edges.
        self.widget.hardGroupEdgesCheckBox.setChecked(self.instrument.hardGroupEdges)

        self.widget.updateGroupingParameterPanel()

        # Release the lock
        self.widgetsRefreshing = False

    def setupInstrumentSlots(self):
        # Setup the widget and slot for the instrument name.
        for i in Instruments:
            self.widget.nameComboBox.addItem(i.name, i)
        self.widget.nameComboBox.currentIndexChanged.connect(
            self.handleInstrumentNameChanged
        )

        self.widget.dataFileDirectoryLineEdit.textChanged.connect(
            self.handleDataFileDirectoryChanged
        )

        self.widget.browseDataFileDirectoryButton.clicked.connect(
            lambda: self.handleBrowse(
                self.widget.dataFileDirectoryLineEdit, "Data file directory", dir=True
            )
        )

        dataFileTypes = ["raw", "sav", "txt", "nxs", "*"]
        self.widget.dataFileTypeCombo.addItems(dataFileTypes)

        self.widget.dataFileTypeCombo.currentIndexChanged.connect(
            self.handleDataFileTypeChanged
        )

        self.widget.detCalibrationLineEdit.textChanged.connect(
            self.handleDetectorCalibrationFileChanged
        )

        self.widget.browseDetCalibrationButton.clicked.connect(
            lambda: self.handleBrowse(
                self.widget.detCalibrationLineEdit, "Detector calibration file"
            )
        )

        self.widget.groupsFileLineEdit.textChanged.connect(
            self.handleGroupsFileChanged
        )
        self.widget.browseGroupsFileButton.clicked.connect(
            lambda: self.handleBrowse(
                self.widget.groupsFileLineEdit, "Groups file"
            )
        )

        self.widget.deadtimeFileLineEdit.textChanged.connect(
            self.handleDeadtimeFileChanged
        )

        self.widget.browseDeadtimeFileButton.clicked.connect(
            lambda: self.handleBrowse(
                self.widget.deadtimeFileLineEdit, "Deadtime constants file"
            )
        )

        self.widget.phiValuesColumnSpinBox.valueChanged.connect(
            self.handleColumnNoPhiValuesChanged
        )

        self.widget.minWavelengthMonNormSpinBox.valueChanged.connect(
            self.handleMinWavelengthMonNormChanged
        )
        self.widget.maxWavelengthMonNormSpinBox.valueChanged.connect(
            self.handleMaxWavelengthMonNormChanged
        )

        # Setup the widgets and slots for the spectrum numbers
        # and quiet count const for the incident beam monitor.
        # Regular expression to accept space delimited integers.
        spectrumNumbersRegex = QRegularExpression(r"^\d+(?:\s+\d+)*$")
        spectrumNumbersValidator = QRegularExpressionValidator(spectrumNumbersRegex)

        self.widget.spectrumNumbersIBLineEdit.textChanged.connect(
            self.handleSpectrumNumbersIBChanged
        )

        self.widget.spectrumNumbersIBLineEdit.setValidator(spectrumNumbersValidator)

        self.widget.incidentMonitorQuietCountConstSpinBox.valueChanged.connect(
            self.handleIncidentMonitorQuietCountConstChanged
        )

        self.widget.spectrumNumbersTLineEdit.textChanged.connect(
            self.handleSpectrumNumbersTChanged
        )

        self.widget.spectrumNumbersTLineEdit.setValidator(spectrumNumbersValidator)
        self.widget.transmissionMonitorQuietCountConstSpinBox.valueChanged.connect(
            self.handleTransmissionMonitorQuietCountConstChanged
        )
        self.widget.channelNoASpinBox.valueChanged.connect(
            self.handleChannelNoAChanged
        )
        self.widget.channelNoBSpinBox.valueChanged.connect(
            self.handleChannelNoBChanged
        )

        self.widget.acceptanceFactorSpinBox.valueChanged.connect(
            self.handleSpikeAnalysisAcceptanceFactorChanged
        )

        self.widget.minWavelengthSpinBox.valueChanged.connect(
            self.handleMinWavelengthChanged
        )
        self.widget.maxWavelengthSpinBox.valueChanged.connect(
            self.handleMaxWavelengthChanged
        )
        self.widget.stepWavelengthSpinBox.valueChanged.connect(
            self.handleStepWavelengthChanged
        )
        self.widget.noSmoothsOnMonitorSpinBox.valueChanged.connect(
            self.handleNoSmoothsOnMonitorChanged
        )
        # Dictionary, mapping enum members to tuples of widgets.
        self.scales = {
            Scales.Q: (
                self.widget.radioButtonQ_,
                self.widget.minQSpinBox,
                self.widget.maxQSpinBox,
                self.widget.stepQSpinBox,
            ),
            Scales.D_SPACING: (
                self.widget.DSpacingRadioButton,
                self.widget.minDSpacingSpinBox,
                self.widget.maxDSpacingSpinBox,
                self.widget.stepDSpacingSpinBox,
            ),
            Scales.WAVELENGTH: (
                self.widget.wavelengthRadioButton,
                self.widget.minWavelength_SpinBox,
                self.widget.maxWavelength_SpinBox,
                self.widget.stepWavelength_SpinBox,
            ),
            Scales.ENERGY: (
                self.widget.energyRadioButton,
                self.widget.minEnergySpinBox,
                self.widget.maxEnergySpinBox,
                self.widget.stepEnergySpinBox,
            ),
            Scales.TOF: (
                self.widget.TOFRadioButton,
                self.widget.minTOFSpinBox,
                self.widget.maxTOFSpinBox,
                self.widget.stepTOFSpinBox,
            ),
        }

        for scaleRadioButton, minSpinBox, maxSpinBox, stepSpinBox in (
            self.scales.values()
        ):
            scaleRadioButton.toggled.connect(self.handleScaleStateChanged)
            minSpinBox.valueChanged.connect(self.handleXMinChanged)
            maxSpinBox.valueChanged.connect(self.handleXMaxChanged)
            stepSpinBox.valueChanged.connect(self.handleXStepChanged)

        self.widget.logarithmicBinningCheckBox.stateChanged.connect(
            self.handleUseLogarithmicBinningSwitched
        )

        self.widget.groupsAcceptanceFactorSpinBox.valueChanged.connect(
            self.handleGroupsAcceptanceFactorChanged
        )

        self.widget.mergePowerSpinBox.valueChanged.connect(
            self.handleMergePowerChanged
        )

        for m in MergeWeights:
            self.widget.mergeWeightsComboBox.addItem(m.name, m)
        self.widget.mergeWeightsComboBox.currentIndexChanged.connect(
            self.handleMergeWeightsChanged
        )

        self.widget.incidentFlightPathSpinBox.valueChanged.connect(
            self.handleIncidentFlightPathChanged
        )

        self.widget.neutronScatteringParamsFileLineEdit.textChanged.connect(
            self.handleNeutronScatteringParamsFileChanged
        )

        self.widget.browseNeutronScatteringParamsButton.clicked.connect(
            lambda: self.handleBrowse(
                self.widget.neutronScatteringParamsFileLineEdit,
                "Neutron scattering parameters file",
            )
        )

        self.widget.nexusDefintionFileLineEdit.textChanged.connect(
            self.handleNexusDefinitionFileChanged
        )


        self.widget.browseNexusDefinitionButton.clicked.connect(
            lambda: self.handleBrowse(
                self.widget.nexusDefintionFileLineEdit, "NeXus defnition file"
            )
        )
        self.widget.hardGroupEdgesCheckBox.stateChanged.connect(
            self.handleHardGroupEdgesSwitched
        )

        # Setup the widgets and slots for the grouping parameter panel.

        self.widget.groupingParameterWidget.setVisible(False)
        self.widget.addGroupingParameterButton.clicked.connect(
            self.handleAddGroupingParameter
        )
        self.widget.removeGroupingParameterButton.clicked.connect(
            self.handleRemoveGroupingParameter
        )
        self.widget.groupingParameterGroupBox.setChecked(False)
        self.widget.groupingParameterGroupBox.toggled.connect(
            self.handleGroupingParameterPanelToggled
        )

    def handleInstrumentNameChanged(self, index):
        """
        Slot for handling change to the instrument name.
        Called when a valueChanged signal is emitted,
        from the nameComboBox.
        Alters the instrument's name as such.
        Parameters
        ----------
        index : int
            New current index of the nameComboBox.
        """
        self.instrument.name = self.nameComboBox.itemData(index)
        if not self.widgetsRefreshing:
            self.parent.setModified()

    def handleDataFileDirectoryChanged(self, text):
        """
        Slot for handling change to the instrument name.
        Called when a textChanged signal is emitted,
        from the dataFileDirectoryLineEdit.
        Alters the instrument's data file directory as such.
        Parameters
        ----------
        value : str
            The new value of the dataFileDirectoryLineEdit.
        """
        self.instrument.dataFileDir = text
        if not self.widgetsRefreshing:
            self.parent.setModified()
    def handleDataFileTypeChanged(self, index):
        """
        Slot for handling change to the data file type.
        Called when a valueChanged signal is emitted,
        from the dataFileTypeCombo.
        Alters the instrument's data file type as such.
        Parameters
        ----------
        index : int
            New current index of the dataFileTypeCombo.
        """
        self.instrument.dataFileType = self.dataFileTypeCombo.itemText(index)
        self.nexusDefintionFileLineEdit.setEnabled(
            self.instrument.dataFileType in ["nxs", "NXS"]
        )
        self.browseNexusDefinitionButton.setEnabled(
            self.instrument.dataFileType in ["nxs", "NXS"]
        )
        if not self.widgetsRefreshing:
            self.parent.setModified()

    def handleDetectorCalibrationFileChanged(self, text):
        """
        Slot for handling change to the detector calibration file name.
        Called when a textChanged signal is emitted,
        from the detCalibrationLineEdit.
        Alters the instrument's detector calibration file name as such.
        Parameters
        ----------
        value : str
            The new value of the detCalibrationLineEdit.
        """
        self.instrument.detectorCalibrationFileName = text
        if not self.widgetsRefreshing:
            self.parent.setModified()

    def handleGroupsFileChanged(self, text):
        """
        Slot for handling change to the groups file name.
        Called when a textChanged signal is emitted,
        from the groupsFileLineEdit.
        Alters the instrument's groups file name as such.
        Parameters
        ----------
        value : str
            The new value of the groupsFileLineEdit.
        """
        self.instrument.groupFileName = text
        if not self.widgetsRefreshing:
            self.parent.setModified()

    def handleDeadtimeFileChanged(self, text):
        """
        Slot for handling change to the deadtime constants file name.
        Called when a textChanged signal is emitted,
        from the deadtimeFileLineEdit.
        Alters the instrument's deadtime constants file name as such.
        Parameters
        ----------
        value : str
            The new value of the deadtimeFileLineEdit.
        """
        self.instrument.deadtimeConstantsFileName = text
        if not self.widgetsRefreshing:
            self.parent.setModified()

    def handleUseLogarithmicBinningSwitched(self, state):
        """
        Slot for handling switching logarithmic binning on/off.
        Called when the stateChanged signal is emitted,
        from the logarithmicBinningCheckBox.
        Updates the instrument as such.
        Parameters
        ----------
        state : int
            The new state of the logarithmicBinningCheckBox (1: True, 0: False)
        """
        self.instrument.useLogarithmicBinning = state
        if not self.widgetsRefreshing:
            self.parent.setModified()

    def handleMergeWeightsChanged(self, index):
        """
        Slot for handling change to what to merge weights by.
        Called when a valueChanged signal is emitted,
        from the mergeWeightsComboBox.
        Alters the instrument's name as such.
        Parameters
        ----------
        index : int
            New current index of the mergeWeightsComboBox.
        """
        self.instrument.mergeWeights = self.mergeWeightsComboBox.itemData(
            index
        )
        if not self.widgetsRefreshing:
            self.parent.setModified()

    def handleNeutronScatteringParamsFileChanged(self, text):
        """
        Slot for handling change to the neutron
        scattering parameters file name.
        Called when a textChanged signal is emitted,
        from the neutronScatteringParamsFileLineEdit.
        Alters the instrument's neutron scattering
        parameters file name as such.
        Parameters
        ----------
        value : str
            The new value of the neutronScatteringParamsFileLineEdit.
        """
        self.instrument.neutronScatteringParametersFile = text
        if not self.widgetsRefreshing:
            self.parent.setModified()

    def handleNexusDefinitionFileChanged(self, text):
        """
        Slot for handling change to the NeXus definition file name.
        Called when a textChanged signal is emitted,
        from the nexusDefintionFileLineEdit.
        Alters the instrument's NeXus definition file name as such.
        Parameters
        ----------
        value : str
            The new value of the nexusDefintionFileLineEdit.
        """
        self.instrument.nxsDefinitionFile = text
        if not self.widgetsRefreshing:
            self.parent.setModified()

    def handleHardGroupEdgesSwitched(self, state):
        """
        Slot for handling switching hard group edges on/off.
        Called when the stateChanged signal is emitted,
        from the hardGroupEdgesCheckBox.
        Updates the instrument as such.
        Parameters
        ----------
        state : int
            The new state of the hardGroupEdgesCheckBox (1: True, 0: False)
        """
        self.instrument.hardGroupEdges = state
        if not self.widgetsRefreshing:
            self.parent.setModified()

    def handleColumnNoPhiValuesChanged(self, value):
        """
        Slot for handling change to the column numbers for phi values.
        Called when a valueChanged signal is emitted,
        from the phiValuesColumnSpinBox.
        Alters the instrument's column no. for phi values as such.
        Parameters
        ----------
        value : int
            The new value of the phiValuesColumnSpinBox.
        """
        self.instrument.columnNoPhiVals = value
        if not self.widgetsRefreshing:
            self.parent.setModified()

    def handleMinWavelengthMonNormChanged(self, value):
        """
        Slot for handling change to the minimum wavelength for
        monitor normalisation.
        Called when a valueChanged signal is emitted,
        from the minWavelengthMonNormSpinBox.
        Alters the instrument's minimum wavelength
        for monitor normalisation as such.
        Parameters
        ----------
        value : float
            The new value of the minWavelengthMonNormSpinBox.
        """
        self.instrument.wavelengthRangeForMonitorNormalisation = (
            value,
            self.instrument.wavelengthRangeForMonitorNormalisation[1],
        )
        if not self.widgetsRefreshing:
            self.parent.setModified()

    def handleMaxWavelengthMonNormChanged(self, value):
        """
        Slot for handling change to the maximum wavelength for
        monitor normalisation.
        Called when a valueChanged signal is emitted,
        from the maxWavelengthMonNormSpinBox.
        Alters the instrument's maximum wavelength
        for monitor normalisation as such.
        Parameters
        ----------
        value : float
            The new value of the maxWavelengthMonNormSpinBox.
        """
        self.instrument.wavelengthRangeForMonitorNormalisation = (
            self.instrument.wavelengthRangeForMonitorNormalisation[1],
            value,
        )
        if not self.widgetsRefreshing:
            self.parent.setModified()

    def handleSpectrumNumbersIBChanged(self, text):
        """
        Slot for handling change to the spectrum numbers
        for the incident beam monitor.
        Called when the textChanged signal is emitted,
        from the spectrumNumbersIBLineEdit.
        Alters the instrument's spectrum numbers for the incident
        beam monitor as such.
        Parameters
        ----------
        text : str
            The new value of the spectrumNumbersIBLineEdit.
        """
        self.instrument.incidentMonitorQuietCountConst = [
            int(x) for x in text.split()
        ]
        if not self.widgetsRefreshing:
            self.parent.setModified()

    def handleSpectrumNumbersTChanged(self, text):
        """
        Slot for handling change to the spectrum numbers
        for the transmission monitor.
        Called when the textChanged signal is emitted,
        from the spectrumNumbersTLineEdit.
        Alters the instrument's spectrum numbers for the transmission
        monitor as such.
        Parameters
        ----------
        text : str
            The new value of the spectrumNumbersTLineEdit.
        """
        self.instrument.transmissionMonitorQuietCountConst = [
            int(x) for x in text.split()
        ]
        if not self.widgetsRefreshing:
            self.parent.setModified()

    def handleIncidentMonitorQuietCountConstChanged(self, value):
        """
        Slot for handling change to the incident monitor quiet count constant.
        Called when the valueChanged signal is emitted,
        form the incidentMonitorQuietCountConstSpinBox.
        Alters the instrument's quiet count constant for the
        incident beam monitor as such.
        Parameters
        ----------
        value : float
            The new value of the incidentMonitorQuietCountConstSpinBox.
        """
        self.instrument.incidentMonitorQuietCountConst = value
        if not self.widgetsRefreshing:
            self.parent.setModified()

    def handleTransmissionMonitorQuietCountConstChanged(self, value):
        """
        Slot for handling change to the incident monitor quiet count constant.
        Called when the valueChanged signal is emitted,
        form the transmissionMonitorQuietCountConstSpinBox.
        Alters the instrument's quiet count constant for the
        transmission monitor as such.
        Parameters
        ----------
        value : float
            The new value of the transmissionMonitorQuietCountConstSpinBox.
        """
        self.instrument.incidentMonitorQuietCountConst = value
        if not self.widgetsRefreshing:
            self.parent.setModified()

    def handleChannelNoAChanged(self, value):
        """
        Slot for handling change to the lower channel number.
        Called when the valueChanged signal is emitted,
        form the channelNoASpinBox.
        Alters the instrument's lower channel number as such.
        Parameters
        ----------
        value : int
            The new value of the channelNoASpinBox.
        """
        self.instrument.channelNosSpikeAnalysis = (
            value,
            self.instrument.channelNosSpikeAnalysis[1],
        )
        if not self.widgetsRefreshing:
            self.parent.setModified()

    def handleChannelNoBChanged(self, value):
        """
        Slot for handling change to the upper channel number.
        Called when the valueChanged signal is emitted,
        form the channelNoBSpinBox.
        Alters the instrument's upper channel number as such.
        Parameters
        ----------
        value : int
            The new value of the channelNoBSpinBox.
        """
        self.instrument.channelNosSpikeAnalysis = (
            self.instrument.channelNosSpikeAnalysis[0],
            value,
        )
        if not self.widgetsRefreshing:
            self.parent.setModified()

    def handleSpikeAnalysisAcceptanceFactorChanged(self, value):
        """
        Slot for handling change to the spike analysis acceptance factor.
        Called when the valueChanged signal is emitted,
        from the acceptanceFactorSpinBox.
        Alters the instrument's spike analysis acceptane factor
        as such.
        Parameters
        ----------
        value : float
            The new value of the acceptanceFactorSpinBox.
        """
        self.instrument.spikeAnalysisAcceptanceFactor = value
        if not self.widgetsRefreshing:
            self.parent.setModified()

    def handleMinWavelengthChanged(self, value):
        """
        Slot for handling change to the minimum wavelength.
        Called when the valueChanged signal is emitted,
        from the minWavelengthSpinBox.
        Alters the instrument's minimum wavelength as such.
        Parameters
        ----------
        value : float
            The new value of the minWavelengthSpinBox.
        """
        self.instrument.wavelengthMin = value
        if not self.widgetsRefreshing:
            self.parent.setModified()

    def handleMaxWavelengthChanged(self, value):
        """
        Slot for handling change to the maximum wavelength.
        Called when the valueChanged signal is emitted,
        from the minWavelengthSpinBox.
        Alters the instrument's maximum wavelength as such.
        Parameters
        ----------
        value : float
            The new value of the maxWavelengthSpinBox.
        """
        self.instrument.wavelengthMax = value
        if not self.widgetsRefreshing:
            self.parent.setModified()

    def handleStepWavelengthChanged(self, value):
        """
        Slot for handling change to the step size in  wavelength.
        Called when the valueChanged signal is emitted,
        from the stepWavelengthSpinBox.
        Alters the instrument's wavelength step size as such.
        Parameters
        ----------
        value : float
            The new value of the stepWavelengthSpinBox.
        """
        self.instrument.wavelengthStep = value
        if not self.widgetsRefreshing:
            self.parent.setModified()

    def handleNoSmoothsOnMonitorChanged(self, value):
        """
        Slot for handling change to the number of smooths on the monitor.
        Called when the valueChanged signal is emitted,
        from the noSmoothsOnMonitorSpinBox.
        Alters the instrument's number of smooths on the monitor as such.
        Parameters
        ----------
        value : int
            The new value of the noSmoothsOnMonitorSpinBox.
        """
        self.instrument.NoSmoothsOnMonitor = value
        if not self.widgetsRefreshing:
            self.parent.setModified()

    def handleScaleStateChanged(self):
        """
        Slot for handling change in the X-Scale for final DCS.
        Called when the stateChanged signal is emitted,
        from any of the scale radio buttons.
        Updates the interface, to reflect the change in scale selection.
        """
        for scale, widgets in self.scales.items():
            state = widgets[0].isChecked()
            if state:
                self.instrument.scaleSelection = scale
                self.instrument.XMin = widgets[1].value()
                self.instrument.XMax = widgets[2].value()
                self.instrument.XStep = widgets[3].value()
                if not self.widgetsRefreshing:
                    self.parent.setModified()
            for widget in widgets[1:]:
                widget.setEnabled(state)

    def handleXMinChanged(self, value):
        self.instrument.XMin = value
        if not self.widgetsRefreshing:
            self.parent.setModified()

    def handleXMaxChanged(self, value):
        if not self.widgetsRefreshing:
            self.parent.setModified()

    def handleXStepChanged(self, value):
        if not self.widgetsRefreshing:
            self.parent.setModified()

    def handleGroupsAcceptanceFactorChanged(self, value):
        """
        Slot for handling change to the groups acceptance factor.
        Called when the valueChanged signal is emitted,
        from the groupsAcceptanceFactorSpinBox.
        Alters the instrument's groups acceptane factor
        as such.
        Parameters
        ----------
        value : float
            The new value of the groupsAcceptanceFactorSpinBox.
        """
        self.instrument.groupsAcceptanceFactor = value
        if not self.widgetsRefreshing:
            self.parent.setModified()

    def handleMergePowerChanged(self, value):
        """
        Slot for handling change to the merge power.
        Called when the valueChanged signal is emitted,
        from the mergePowerSpinBox.
        Alters the instrument's merge power.
        as such.
        Parameters
        ----------
        value : float
            The new value of the mergePowerSpinBox.
        """
        self.instrument.mergePower = value
        if not self.widgetsRefreshing:
            self.parent.setModified()

    def handleIncidentFlightPathChanged(self, value):
        """
        Slot for handling change to the incident flight path.
        Called when the valueChanged signal is emitted,
        from the incidentFlightPathSpinBox.
        Alters the instrument's incident flight path.
        as such.
        Parameters
        ----------
        value : float
            The new value of the incidentFlightPathSpinBox.
        """
        self.instrument.incidentFlightPath = value
        if not self.widgetsRefreshing:
            self.parent.setModified()

    def handleSpectrumNumberForOutputDiagChanged(self, value):
        """
        Slot for handling change to the spectrum number for output diagnostics.
        Called when the valueChanged signal is emitted,
        from the outputDiagSpectrumSpinBox.
        Alters the instrument's incident flight path.
        as such.
        Parameters
        ----------
        value : int
            The new value of the outputDiagSpectrumSpinBox.
        """
        self.instrument.spectrumNumberForOutputDiagnosticFiles = value
        if not self.widgetsRefreshing:
            self.parent.setModified()

    def handleBrowse(self, target, title, dir=False):
        """
        Slot for handling browsing files.
        Parameters
        ----------
        target : QWidget
            Target widget.
        title : str
            Title for QFileDialog to use.
        dir : bool, optional
            Defaults to false. True means accept a directory.
        """
        filename = self.browseFile(title, dir=dir)
        if filename:
            target.setText(filename)

    def browseFile(self, title, dir=False):
        """
        Helper function for browsing files.
        Parameters
        ----------
        title : str
            Title for QFileDialog to use.
        dir : bool, optional
            Defaults to false. True means accept a directory.
        Returns
        -------
        str[]
        """
        if dir:
            filename = QFileDialog.getExistingDirectory(self, title, "")
        else:
            filename, _ = QFileDialog.getOpenFileName(self, title, "")
        return filename

    def updateGroupingParameterPanel(self):
        """
        Fills the GroupingParameterPanel table.
        """
        self.groupingParameterTable.makeModel(
            self.instrument.groupingParameterPanel
        )

    def handleAddGroupingParameter(self):
        """
        Slot for handling insertion to the grouping parameter panel.
        Called when a clicked signal is emitted, from the
        addGroupingParameterButton.
        """
        self.groupingParameterTable.insertRow()
        if not self.widgetsRefreshing:
            self.parent.setModified()

    def handleRemoveGroupingParameter(self):
        """
        Slot for removing files from grouping parameter panel.
        Called when a clicked signal is emitted,
        from the removeGroupingParameterButton.
        """
        self.groupingParameterTable.removeRow(
            self.groupingParameterTable.selectionModel().selectedRows()
        )
        if not self.widgetsRefreshing:
            self.parent.setModified()

    def handleGroupingParameterPanelToggled(self, on):
        """
        Slot for handling toggling the grouping parameter panel.
        Called when a toggled signal is emitted from the
        groupingParameterGroupBox.
        """
        self.groupingParameterWidget.setVisible(on)