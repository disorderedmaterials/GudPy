from PyQt5.QtGui import QRegExpValidator
from PyQt5.QtWidgets import QWidget, QFileDialog
from PyQt5.QtCore import QRegExp
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
    handleScaleStateChanged()
        Slot for handling change in the X-Scale for final DCS.
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
    handleGroupingParameterPanelToggled()
        Slot for handling toggling the grouping parameter panel.
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

    def initComponents(self):
        """
        Loads the UI file for the InstrumentWidget object,
        and then populates the child widgets with their
        corresponding data from the attributes of the Instrument object.
        """
        # Acquire the lock
        self.widgetsRefreshing = True
        current_dir = os.path.dirname(os.path.realpath(__file__))
        uifile = os.path.join(current_dir, "ui_files/instrumentWidget.ui")
        uic.loadUi(uifile, self)

        # Setup the widget and slot for the instrument name.
        for i in Instruments:
            self.nameComboBox.addItem(i.name, i)
        self.nameComboBox.setCurrentIndex(self.instrument.name.value)
        self.nameComboBox.currentIndexChanged.connect(
            self.handleInstrumentNameChanged
        )

        # Setup the widgets and slots for configuration files.
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

        self.groupsFileLineEdit.setText(self.instrument.groupFileName)
        self.groupsFileLineEdit.textChanged.connect(
            self.handleGroupsFileChanged
        )
        self.browseGroupsFileButton.clicked.connect(
            lambda: self.handleBrowse(
                self.groupsFileLineEdit, "Groups file"
            )
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

        self.phiValuesColumnSpinBox.setValue(self.instrument.columnNoPhiVals)
        self.phiValuesColumnSpinBox.valueChanged.connect(
            self.handleColumnNoPhiValuesChanged
        )

        # Setup the widgets and slots for the wavelength range and step size
        # for monitor normalisation.
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

        # Setup the widgets and slots for the spectrum numbers
        # and quiet count const for the incident beam monitor.
        # Regular expression to accept space delimited integers.
        spectrumNumbersRegex = QRegExp(r"^\d+(?:\s+\d+)*$")
        spectrumNumbersValidator = QRegExpValidator(spectrumNumbersRegex)

        self.spectrumNumbersIBLineEdit.setText(
            spacify(self.instrument.spectrumNumbersForIncidentBeamMonitor)
        )

        self.spectrumNumbersIBLineEdit.textChanged.connect(
            self.handleSpectrumNumbersIBChanged
        )

        self.spectrumNumbersIBLineEdit.setValidator(spectrumNumbersValidator)

        self.incidentMonitorQuietCountConstSpinBox.setValue(
            self.instrument.incidentMonitorQuietCountConst
        )
        self.incidentMonitorQuietCountConstSpinBox.valueChanged.connect(
            self.handleIncidentMonitorQuietCountConstChanged
        )

        # Setup the widgets and slots for the spectrum numbers
        # and quiet count const for the transmission beam monitor.
        self.spectrumNumbersTLineEdit.setText(
            spacify(self.instrument.spectrumNumbersForTransmissionMonitor)
        )

        self.spectrumNumbersTLineEdit.textChanged.connect(
            self.handleSpectrumNumbersTChanged
        )

        self.spectrumNumbersTLineEdit.setValidator(spectrumNumbersValidator)

        self.transmissionMonitorQuietCountConstSpinBox.setValue(
            self.instrument.transmissionMonitorQuietCountConst
        )
        self.transmissionMonitorQuietCountConstSpinBox.valueChanged.connect(
            self.handleTransmissionMonitorQuietCountConstChanged
        )

        # Setup the widgets and slots for the channel numbers
        # to be used for spike analysis.
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

        # Setup the widget and slot for the
        # acceptance factor for spike analysis.
        self.acceptanceFactorSpinBox.setValue(
            self.instrument.spikeAnalysisAcceptanceFactor
        )
        self.acceptanceFactorSpinBox.valueChanged.connect(
            self.handleSpikeAnalysisAcceptanceFactorChanged
        )

        # Setup the widgets and slots for the wavelength range and step size.
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

        # Setup the widget and slot for the number of smoothings on monitor.
        self.noSmoothsOnMonitorSpinBox.setValue(
            self.instrument.NoSmoothsOnMonitor
        )
        self.noSmoothsOnMonitorSpinBox.valueChanged.connect(
            self.handleNoSmoothsOnMonitorChanged
        )

        # Dictionary, mapping enum members to tuples of widgets.
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

        # Setup the widgets and slots for the scales.
        selection, min_, max_, step = (
            self.scales[self.instrument.scaleSelection]
        )
        selection.setChecked(True)
        min_.setValue(self.instrument.XMin)
        max_.setValue(self.instrument.XMax)
        step.setValue(self.instrument.XStep)
        min_.setEnabled(True)
        max_.setEnabled(True)
        step.setEnabled(True)

        for scaleRadioButton, minSpinBox, maxSpinBox, stepSpinBox in (
            self.scales.values()
        ):
            scaleRadioButton.toggled.connect(self.handleScaleStateChanged)
            minSpinBox.valueChanged.connect(self.handleXMinChanged)
            maxSpinBox.valueChanged.connect(self.handleXMaxChanged)
            stepSpinBox.valueChanged.connect(self.handleXStepChanged)

        # Setup the widget and slot for enabling/disabling
        # logarithmic binning.
        self.logarithmicBinningCheckBox.setChecked(
            self.instrument.useLogarithmicBinning
        )
        self.logarithmicBinningCheckBox.stateChanged.connect(
            self.handleUseLogarithmicBinningSwitched
        )

        # Setup the widget and slot for the groups acceptance factor.
        self.groupsAcceptanceFactorSpinBox.setValue(
            self.instrument.groupsAcceptanceFactor
        )
        self.groupsAcceptanceFactorSpinBox.valueChanged.connect(
            self.handleGroupsAcceptanceFactorChanged
        )

        # Setup the widgets and slots for merging.
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

        # Setup the widget and slot for the incident flight path.
        self.incidentFlightPathSpinBox.setValue(
            self.instrument.incidentFlightPath
        )
        self.incidentFlightPathSpinBox.valueChanged.connect(
            self.handleIncidentFlightPathChanged
        )

        # Setup the widget and slot for the spectrum number
        # for output diagnostics.
        self.outputDiagSpectrumSpinBox.setValue(
            self.instrument.spectrumNumberForOutputDiagnosticFiles
        )

        # Setup the widgets and slots for the neutron
        # scattering parameters file and NeXus definition file.
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

        # Setup the widget and slot for enabling/disablign hard group edges.
        self.hardGroupEdgesCheckBox.setChecked(self.instrument.hardGroupEdges)
        self.hardGroupEdgesCheckBox.stateChanged.connect(
            self.handleHardGroupEdgesSwitched
        )

        # Setup the widgets and slots for the grouping parameter panel.

        self.groupingParameterWidget.setVisible(False)
        self.updateGroupingParameterPanel()
        self.addGroupingParameterButton.clicked.connect(
            self.handleAddGroupingParameter
        )
        self.removeGroupingParameterButton.clicked.connect(
            self.handleRemoveGroupingParameter
        )
        self.groupingParameterGroupBox.setChecked(False)
        self.groupingParameterGroupBox.toggled.connect(
            self.handleGroupingParameterPanelToggled
        )
        # Release the lock
        self.widgetsRefreshing = False
