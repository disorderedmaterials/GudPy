from PyQt5.QtWidgets import QWidget, QFileDialog
from PyQt5 import uic
from src.gudrun_classes.enums import Instruments, MergeWeights, Scales
from src.scripts.utils import spacify
import os


class InstrumentWidget(QWidget):
    """
    Class to represent a InstrumentWidget. Inherits QWidget.

    ...

    Attributes
    ----------
    instrument : Instrument
        Instrument object belonging to the GudrunFile.
    parent : QWidget
        Parent widget.
    Methods
    -------
    initComponents()
        Loads UI file, and then populates data from the Instrument.
    handleInstrumentNameChanged(index)
       Slot for handling change to the instrument name.
    handleDataFileDirectoryChanged(text)
        Slot for handling change to the data file directory.
    handleDataFileTypeChanged(index)
        Slot for handling hange to the data file type.
    handleDetectorCalibrationFileChanged(text)
        Slot for handling change to the detector calibration file name.
    handleGroupsFileChanged(text)
        Slot for handling change to the groups file name.
    handleDeadtimeFileChanged(text)
        Slot for handling change to the deadtime constants file name.
    handleUseLogarithmicBinningSwitched(state)
        Slot for handling switching logarithmic binning on/off.
    handleMergeWeightsChanged(index)
        Slot for handling change to what to merge weights by.
    handleNeutronScatteringParamsFileChanged(text)
        Slot for handling change to the neutron
        scattering parameters file name.
    handleNexusDefinitionFileChanged(text)
        Slot for handling change to the NeXus definition file name.
    handleHardGroupEdgesSwitched(state)
        Slot for handling switching hard group edges on/off.
    handleColumnNoPhiValuesChanged(value)
        Slot for handling change to the column numbers for phi values.
    handleMinWavelengthMonNormChanged(value)
        Slot for handling change to the minimum wavelength for
        monitor normalisation.
    handleMaxWavelengthMonNormChanged(value)
        Slot for handling change to the maximum wavelength for
        monitor normalisation.
    handleSpectrumNumbersIBChanged(text)
        Slot for handling change to the spectrum numbers
        for the incident beam monitor.
    handleSpectrumNumbersTChanged(text)
        Slot for handling change to the spectrum numbers
        for the transmission monitor
    handleIncidentMonitorQuietCountConstChanged(value)
        Slot for handling change to the incident monitor quiet count constant.
    handleTransmissionMonitorQuietCountConstChanged(value)
        Slot for handling change to the
        transmission monitor quiet count constant.
    handleChannelNoAChanged(value)
        Slot for handling change to the lower channel number.
    handleChannelNoBChanged(value)
        Slot for handling change to the upper channel number.
    handleSpikeAnalysisAcceptanceFactorChanged(value)
        Slot for handling change to the spike analysis acceptance factor.
    handleMinWavelengthChanged(value)
        Slot for handling change to the minimum wavelength.
    handleMaxWavelengthChanged(value)
        Slot for handling change to the maximum wavelength.
    handleStepWavelengthChanged(value)
        Slot for handling change to the wavelength step size.
    handleNoSmoothsOnMonitorChanged(value)
        Slot for handling change to the number of smooths on the monitor.
    handleQScaleStateChanged()
        Slot for handling switching to/from the Q-Scale for final DCS.
    handleDSpacingScaleStateChanged()
        Slot for handling switching to/from the D-Spacing scale for final DCS.
    handleWavelengthScaleStateChanged()
        Slot for handling switching to/from the wavelength scale for final DCS.
    handleEnergyScaleStateChanged()
        Slot for handling switching to/from the energy scale for final DCS.
    handleTOFScaleStateChanged()
        Slot for handling switching to/from the TOF scale for final DCS.
    handleGroupsAcceptanceFactorChanged(value)
        Slot for handling change to the groups acceptance factor.
    handleMergePowerChanged(value)
        Slot for handling change to the merge power.
    handleIncidentFlightPathChanged(value)
        Slot for handling change to the incident flight path.
    handleSpectrumNumberForOutputDiagChanged(value)
        Slot for handling change to the spectrum number for output diagnostics.
    handleBrowse(target, title, dir=False)
        Slot for handling browsing files.
    browseFile( title, dir=False)
        Helper method for browsing files.
    updateGroupingParameterPanel()
        Fill the grouping parameter panel.
    handleAddGroupingParameter()
        Slot for handling adding a row to the grouping parameter panel.
    handleRemoveGroupingParameter()
        Slot for removing a row from the grouping parameter panel.
    """

    def __init__(self, instrument, parent=None):
        """
        Constructs all the necessary attributes
        for the InstrumentWidget object.
        Calls the initComponents method,
        to load the UI file and populate data.
        Parameters
        ----------
        instrument : Instrument
            Instrument object belonging to the GudrunFile.
        parent : QWidget, optional
            Parent widget.
        """
        self.instrument = instrument
        self.parent = parent

        super(InstrumentWidget, self).__init__(parent=self.parent)

        self.initComponents()

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

    def handleQScaleStateChanged(self):
        """
        Slot for handling switching to/from the Q-Scale for final DCS.
        Called when the stateChanged signal is emitted,
        from the _QRadioButton.
        Updates the interface, to reflect the change in scale selection.
        Parameters
        ----------
        state : int
            The new state of the _QRadioButton (1: True, 0: False)
        """
        button, min_, max_, step = self.scales[Scales.Q]
        state = button.isChecked()
        min_.setEnabled(state)
        max_.setEnabled(state)
        step.setEnabled(state)

    def handleDSpacingScaleStateChanged(self):
        """
        Slot for handling switching to/from the D-Spacing scale for final DCS.
        Called when the stateChanged signal is emitted,
        from the DSpacingRadioButton.
        Updates the interface, to reflect the change in scale selection.
        Parameters
        ----------
        state : int
            The new state of the DSpacingRadioButton (1: True, 0: False)
        """
        button, min_, max_, step = self.scales[Scales.D_SPACING]
        state = button.isChecked()
        min_.setEnabled(state)
        max_.setEnabled(state)
        step.setEnabled(state)

    def handleWavelengthScaleStateChanged(self):
        """
        Slot for handling switching to/from the wavelength scale for final DCS.
        Called when the stateChanged signal is emitted,
        from the wavelengthRadioButton.
        Updates the interface, to reflect the change in scale selection.
        Parameters
        ----------
        state : int
            The new state of the wavelengthRadioButton (1: True, 0: False)
        """
        button, min_, max_, step = self.scales[Scales.WAVELENGTH]
        state = button.isChecked()
        min_.setEnabled(state)
        max_.setEnabled(state)
        step.setEnabled(state)

    def handleEnergyScaleStateChanged(self):
        """
        Slot for handling switching to/from the energy scale for final DCS.
        Called when the stateChanged signal is emitted,
        from the energyRadioButton.
        Updates the interface, to reflect the change in scale selection.
        Parameters
        ----------
        state : int
            The new state of the energyRadioButton (1: True, 0: False)
        """
        button, min_, max_, step = self.scales[Scales.ENERGY]
        state = button.isChecked()
        min_.setEnabled(state)
        max_.setEnabled(state)
        step.setEnabled(state)

    def handleTOFScaleStateChanged(self):
        """
        Slot for handling switching to/from the TOF scale for final DCS.
        Called when the stateChanged signal is emitted,
        from the TOFRadioButton.
        Updates the interface, to reflect the change in scale selection.
        Parameters
        ----------
        state : int
            The new state of the TOFRadioButton (1: True, 0: False)
        """
        button, min_, max_, step = self.scales[Scales.TOF]
        state = button.isChecked()
        min_.setEnabled(state)
        max_.setEnabled(state)
        step.setEnabled(state)

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
            target.setText(filename[0])

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
        filename = (
            QFileDialog.getOpenFileName(self, title, "")
            if not dir
            else QFileDialog.getExistingDirectory(self, title, "")
        )
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

    def handleRemoveGroupingParameter(self):
        """
        Slot for removing files from grouping parameter panel.
        Called when a clicked signal is emitted,
        from the removeGroupingParameterButton.
        """
        self.groupingParameterTable.removeRow(
            self.groupingParameterTable.selectionModel().selectedRows()
        )

    def initComponents(self):
        """
        Loads the UI file for the InstrumentWidget object,
        and then populates the child widgets with their
        corresponding data from the attributes of the Instrument object.
        """
        current_dir = os.path.dirname(os.path.realpath(__file__))
        uifile = os.path.join(current_dir, "ui_files/instrumentWidget.ui")
        uic.loadUi(uifile, self)

        for i in Instruments:
            self.nameComboBox.addItem(i.name, i)
        self.nameComboBox.setCurrentIndex(self.instrument.name.value)
        self.nameComboBox.currentIndexChanged.connect(
            self.handleInstrumentNameChanged
        )

        self.dataFileDirectoryLineEdit.setText(self.instrument.dataFileDir)
        self.dataFileDirectoryLineEdit.textChanged.connect(
            self.handleDataFileDirectoryChanged
        )

        self.browseDataFileDirectoryButton.clicked.connect(
            lambda: self.handleBrowse(
                self.dataFileDirectoryLineEdit, "Data file directory", dir=True
            )
        )

        dataFileTypes = ["raw", "sav", "txt", "nxs", "*"]
        self.dataFileTypeCombo.addItems(dataFileTypes)
        self.dataFileTypeCombo.setCurrentIndex(
            dataFileTypes.index(self.instrument.dataFileType)
        )
        self.dataFileTypeCombo.currentIndexChanged.connect(
            self.handleDataFileTypeChanged
        )

        self.detCalibrationLineEdit.setText(
            self.instrument.detectorCalibrationFileName
        )
        self.detCalibrationLineEdit.textChanged.connect(
            self.handleDetectorCalibrationFileChanged
        )

        self.browseDetCalibrationButton.clicked.connect(
            lambda: self.handleBrowse(
                self.detCalibrationLineEdit, "Detector calibration file"
            )
        )

        self.phiValuesColumnSpinBox.setValue(self.instrument.columnNoPhiVals)
        self.phiValuesColumnSpinBox.valueChanged.connect(
            self.handleColumnNoPhiValuesChanged
        )

        self.groupsFileLineEdit.setText(self.instrument.groupFileName)
        self.groupsFileLineEdit.textChanged.connect(
            self.handleGroupsFileChanged
        )

        self.deadtimeFileLineEdit.setText(
            self.instrument.deadtimeConstantsFileName
        )
        self.deadtimeFileLineEdit.textChanged.connect(
            self.handleDeadtimeFileChanged
        )

        self.browseDeadtimeFileButton.clicked.connect(
            lambda: self.handleBrowse(
                self.deadtimeFileLineEdit, "Deadtime constants file"
            )
        )

        self.minWavelengthMonNormSpinBox.setValue(
            self.instrument.wavelengthRangeForMonitorNormalisation[0]
        )
        self.maxWavelengthMonNormSpinBox.setValue(
            self.instrument.wavelengthRangeForMonitorNormalisation[1]
        )
        self.minWavelengthMonNormSpinBox.valueChanged.connect(
            self.handleMinWavelengthMonNormChanged
        )
        self.maxWavelengthMonNormSpinBox.valueChanged.connect(
            self.handleMaxWavelengthMonNormChanged
        )

        self.spectrumNumbersIBLineEdit.setText(
            spacify(self.instrument.spectrumNumbersForIncidentBeamMonitor)
        )

        self.spectrumNumbersIBLineEdit.textChanged.connect(
            self.handleSpectrumNumbersIBChanged
        )

        self.spectrumNumbersTLineEdit.setText(
            spacify(self.instrument.spectrumNumbersForTransmissionMonitor)
        )

        self.spectrumNumbersTLineEdit.textChanged.connect(
            self.handleSpectrumNumbersTChanged
        )

        self.incidentMonitorQuietCountConstSpinBox.setValue(
            self.instrument.incidentMonitorQuietCountConst
        )
        self.incidentMonitorQuietCountConstSpinBox.valueChanged.connect(
            self.handleIncidentMonitorQuietCountConstChanged
        )
        self.transmissionMonitorQuietCountConstSpinBox.setValue(
            self.instrument.transmissionMonitorQuietCountConst
        )
        self.transmissionMonitorQuietCountConstSpinBox.valueChanged.connect(
            self.handleTransmissionMonitorQuietCountConstChanged
        )

        self.channelNoASpinBox.setValue(
            self.instrument.channelNosSpikeAnalysis[0]
        )
        self.channelNoASpinBox.valueChanged.connect(
            self.handleChannelNoAChanged
        )
        self.channelNoBSpinBox.setValue(
            self.instrument.channelNosSpikeAnalysis[1]
        )
        self.channelNoBSpinBox.valueChanged.connect(
            self.handleChannelNoBChanged
        )

        self.acceptanceFactorSpinBox.setValue(
            self.instrument.spikeAnalysisAcceptanceFactor
        )
        self.acceptanceFactorSpinBox.valueChanged.connect(
            self.handleSpikeAnalysisAcceptanceFactorChanged
        )

        self.minWavelengthSpinBox.setValue(self.instrument.wavelengthMin)
        self.minWavelengthSpinBox.valueChanged.connect(
            self.handleMinWavelengthChanged
        )
        self.maxWavelengthSpinBox.setValue(self.instrument.wavelengthMax)
        self.maxWavelengthSpinBox.valueChanged.connect(
            self.handleMaxWavelengthChanged
        )
        self.stepWavelengthSpinBox.setValue(self.instrument.wavelengthStep)
        self.stepWavelengthSpinBox.valueChanged.connect(
            self.handleStepWavelengthChanged
        )

        self.noSmoothsOnMonitorSpinBox.setValue(
            self.instrument.NoSmoothsOnMonitor
        )
        self.noSmoothsOnMonitorSpinBox.valueChanged.connect(
            self.handleNoSmoothsOnMonitorChanged
        )

        self.scales = {
            Scales.Q: (
                self._QRadioButton,
                self.minQSpinBox,
                self.maxQSpinBox,
                self.stepQSpinBox,
            ),
            Scales.D_SPACING: (
                self.DSpacingRadioButton,
                self.minDSpacingSpinBox,
                self.maxDSpacingSpinBox,
                self.stepDSpacingSpinBox,
            ),
            Scales.WAVELENGTH: (
                self.wavelengthRadioButton,
                self.minWavelength_SpinBox,
                self.maxWavelength_SpinBox,
                self.stepWavelength_SpinBox,
            ),
            Scales.ENERGY: (
                self.energyRadioButton,
                self.minEnergySpinBox,
                self.maxEnergySpinBox,
                self.stepEnergySpinBox,
            ),
            Scales.TOF: (
                self.TOFRadioButton,
                self.minTOFSpinBox,
                self.maxTOFSpinBox,
                self.stepTOFSpinBox,
            ),
        }
        self._QRadioButton.toggled.connect(self.handleQScaleStateChanged)
        self.DSpacingRadioButton.toggled.connect(
            self.handleDSpacingScaleStateChanged
        )
        self.wavelengthRadioButton.toggled.connect(
            self.handleWavelengthScaleStateChanged
        )
        self.energyRadioButton.toggled.connect(
            self.handleEnergyScaleStateChanged
        )
        self.TOFRadioButton.toggled.connect(self.handleTOFScaleStateChanged)

        selection, min_, max_, step = (
            self.scales[self.instrument.scaleSelection]
        )
        selection.setChecked(True)
        min_.setValue(self.instrument.XMin)
        max_.setValue(self.instrument.XMax)
        step.setValue(self.instrument.XStep)

        self.logarithmicBinningCheckBox.setChecked(
            self.instrument.useLogarithmicBinning
        )
        self.logarithmicBinningCheckBox.stateChanged.connect(
            self.handleUseLogarithmicBinningSwitched
        )

        self.groupsAcceptanceFactorSpinBox.setValue(
            self.instrument.groupsAcceptanceFactor
        )
        self.groupsAcceptanceFactorSpinBox.valueChanged.connect(
            self.handleGroupsAcceptanceFactorChanged
        )
        self.mergePowerSpinBox.setValue(self.instrument.mergePower)
        self.mergePowerSpinBox.valueChanged.connect(
            self.handleMergePowerChanged
        )

        for m in MergeWeights:
            self.mergeWeightsComboBox.addItem(m.name, m)
        self.mergeWeightsComboBox.setCurrentIndex(
            self.instrument.mergeWeights.value
        )
        self.mergeWeightsComboBox.currentIndexChanged.connect(
            self.handleMergeWeightsChanged
        )
        self.incidentFlightPathSpinBox.setValue(
            self.instrument.incidentFlightPath
        )
        self.incidentFlightPathSpinBox.valueChanged.connect(
            self.handleIncidentFlightPathChanged
        )

        self.outputDiagSpectrumSpinBox.setValue(
            self.instrument.spectrumNumberForOutputDiagnosticFiles
        )
        self.neutronScatteringParamsFileLineEdit.setText(
            self.instrument.neutronScatteringParametersFile
        )
        self.neutronScatteringParamsFileLineEdit.textChanged.connect(
            self.handleNeutronScatteringParamsFileChanged
        )

        self.browseNeutronScatteringParamsButton.clicked.connect(
            lambda: self.handleBrowse(
                self.neutronScatteringParamsFileLineEdit,
                "Neutron scattering parameters file",
            )
        )

        self.nexusDefintionFileLineEdit.setText(
            self.instrument.nxsDefinitionFile
        )

        self.nexusDefintionFileLineEdit.textChanged.connect(
            self.handleNexusDefinitionFileChanged
        )

        self.nexusDefintionFileLineEdit.setEnabled(
            self.instrument.dataFileType in ["nxs", "NXS"]
        )
        self.browseNexusDefinitionButton.setEnabled(
            self.instrument.dataFileType in ["nxs", "NXS"]
        )

        self.browseNexusDefinitionButton.clicked.connect(
            lambda: self.handleBrowse(
                self.nexusDefintionFileLineEdit, "NeXus defnition file"
            )
        )

        self.hardGroupEdgesCheckBox.setChecked(self.instrument.hardGroupEdges)
        self.hardGroupEdgesCheckBox.stateChanged.connect(
            self.handleHardGroupEdgesSwitched
        )

        self.updateGroupingParameterPanel()
        self.addGroupingParameterButton.clicked.connect(
            self.handleAddGroupingParameter
        )
        self.removeGroupingParameterButton.clicked.connect(
            self.handleRemoveGroupingParameter
        )
