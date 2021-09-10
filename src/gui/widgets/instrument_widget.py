from PyQt5.QtWidgets import QDoubleSpinBox, QTableWidgetItem, QWidget, QFileDialog
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
        self.instrument.name = self.nameComboBox.itemData(index)

    def handleDataFileDirectoryChanged(self, text):
        self.instrument.dataFileDir = text

    def handleDataFileTypeChanged(self, index):
        self.instrument.dataFileType = self.dataFileTypeCombo.itemText(index)
        self.nexusDefintionFileLineEdit.setEnabled(self.instrument.dataFileType in ["nxs", "NXS"])
        self.browseNexusDefinitionButton.setEnabled(self.instrument.dataFileType in ["nxs", "NXS"])

    def handleDetectorCalibrationFileChanged(self, text):
        self.instrument.detectorCalibrationFileName = text

    def handleGroupsFileChanged(self, text):
        self.instrument.groupFileName = text

    def handleDeadtimeFileChanged(self, text):
        self.instrument.deadtimeConstantsFileName = text

    def handleUseLogarithmicBinningSwitched(self, state):
        self.instrument.useLogarithmicBinning = state

    def handleMergeWeightsChanged(self, index):
        self.instrument.mergeWeights = (
            self.mergeWeightsComboBox.itemData(index)
        )

    def handleNeutronScatteringParamsFileChanged(self, text):
        self.instrument.neutronScatteringParametersFile = text

    def handleNexusDefinitionFileChanged(self, text):
        self.instrument.nxsDefinitionFile = text

    def handleHardGroupEdgesSwitched(self, state):
        self.instrument.hardGroupEdges = state

    def handleColumnNoPhiValuesChanged(self, value):
        self.instrument.columnNoPhiVals = value

    def handleMinWavelengthMonNormChanged(self, value):
        self.instrument.wavelengthRangeForMonitorNormalisation = (
            value,
            self.instrument.wavelengthRangeForMonitorNormalisation[1],
        )

    def handleMaxWavelengthMonNormChanged(self, value):
        self.instrument.wavelengthRangeForMonitorNormalisation = (
            self.instrument.wavelengthRangeForMonitorNormalisation[1],
            value,
        )

    def handleSpectrumNumbersIBChanged(self, text):
        self.instrument.incidentMonitorQuietCountConst = [int(x) for x in text.split()]

    def handleSpectrumNumbersTChanged(self, text):
        self.instrument.transmissionMonitorQuietCountConst = [int(x) for x in text.split()]


    def handleIncidentMonitorQuietCountConstChanged(self, value):
        self.instrument.incidentMonitorQuietCountConst = value

    def handleTransmissionMonitorQuietCountConstChanged(self, value):
        self.instrument.incidentMonitorQuietCountConst = value

    def handleChannelNoAChanged(self, value):
        self.instrument.channelNosSpikeAnalysis = (
            value,
            self.instrument.channelNosSpikeAnalysis[1],
        )

    def handleChannelNoBChanged(self, value):
        self.instrument.channelNosSpikeAnalysis = (
            self.instrument.channelNosSpikeAnalysis[0],
            value,
        )

    def handleSpikeAnalysisAcceptanceFactorChanged(self, value):
        self.instrument.spikeAnalysisAcceptanceFactor = value

    def handleMinWavelengthChanged(self, value):
        self.instrument.wavelengthMin = value

    def handleMaxWavelengthChanged(self, value):
        self.instrument.wavelengthMax = value

    def handleStepWavelengthChanged(self, value):
        self.instrument.wavelengthStep = value

    def handleNoSmoothsOnMonitorChanged(self, value):
        self.instrument.NoSmoothsOnMonitor = value

    def handleQScaleStateChanged(self):
        button, min, max, step = self.scales[Scales.Q]
        state = button.isChecked()
        min.setEnabled(state)
        max.setEnabled(state)
        step.setEnabled(state)

    def handleDSpacingScaleStateChanged(self):
        button, min, max, step = self.scales[Scales.D_SPACING]
        state = button.isChecked()
        min.setEnabled(state)
        max.setEnabled(state)
        step.setEnabled(state)

    def handleWavelengthScaleStateChanged(self):
        button, min, max, step = self.scales[Scales.WAVELENGTH]
        state = button.isChecked()
        min.setEnabled(state)
        max.setEnabled(state)
        step.setEnabled(state)

    def handleEnergyScaleStateChanged(self):
        button, min, max, step = self.scales[Scales.ENERGY]
        state = button.isChecked()
        min.setEnabled(state)
        max.setEnabled(state)
        step.setEnabled(state)

    def handleTOFScaleStateChanged(self):
        button, min, max, step = self.scales[Scales.TOF]
        state = button.isChecked()
        min.setEnabled(state)
        max.setEnabled(state)
        step.setEnabled(state)

    def handleGroupsAcceptanceFactorChanged(self, value):
        self.instrument.groupsAcceptanceFactor = value

    def handleMergePowerChanged(self, value):
        self.instrument.mergePower = value

    def handleIncidentFlightPathChanged(self, value):
        self.instrument.incidentFlightPath = value

    def handleSpectrumNumberForOutputDiagChanged(self, value):
        self.instrument.spectrumNumberForOutputDiagnosticFiles = value
    
    def handleBrowse(self, target, title, dir=False):
        target.setText(self.browseFile(title, dir=dir)[0])

    def browseFile(self, title, dir=False):
        filename = QFileDialog.getOpenFileName(self, title, '') if not dir else QFileDialog.getExistingDirectory(self, title, '')
        return filename

    def updateGroupingParameterPanel(self):
        # Fill the GroupingParameterPanel table.
        self.instrument.groupingParameterPanel = [(1, 0.1, 0.2, 2.0)]
        self.groupingParameterTable.makeModel(self.instrument.groupingParameterPanel)
        return
        for i, row in enumerate(self.instrument.groupingParameterPanel):
            for j, col in enumerate(row):
                # print(self.groupingParameterTable.item(i,j))
                self.groupingParameterTable.setValue((i, j, col))

    def handleGroupingParameterPanelChanged(self, item):
        pass
        print("changfed")
        value = item.text()
        row = item.row()
        col = item.column()
        if row < len(self.instrument.groupingParameterPanel):
            immutableRow = self.instrument.groupingParameterPanel[row]
            mutableRow = list(immutableRow)
            mutableRow[col] = float(value)
            self.instrument.groupingParameterPanel[row] = mutableRow
        else:
            newRow = tuple(
                [
                    float(self.groupingParameterTable.item(row, j).value())
                    for j in range(3)
                    if self.groupingParameterTable.item(row, j)
                    # and
                    # len(self.groupingParameterTable.item(row, j).value())
                ]
            )
            print(newRow)


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

        self.browseDataFileDirectoryButton.clicked.connect(lambda : self.handleBrowse(self.dataFileDirectoryLineEdit, "Data file directory", dir=True))

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

        self.browseDetCalibrationButton.clicked.connect(lambda : self.handleBrowse(self.detCalibrationLineEdit, "Detector calibration file"))


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

        self.browseDeadtimeFileButton.clicked.connect(lambda : self.handleBrowse(self.deadtimeFileLineEdit, "Deadtime constants file"))

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

        self.spectrumNumbersIBLineEdit.textChanged.connect(self.handleSpectrumNumbersIBChanged)

        self.spectrumNumbersTLineEdit.setText(
            spacify(self.instrument.spectrumNumbersForTransmissionMonitor)
        )

        self.spectrumNumbersTLineEdit.textChanged.connect(self.handleSpectrumNumbersTChanged)

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

        selection, min, max, step = self.scales[
            self.instrument.scaleSelection
        ]
        selection.setChecked(True)
        min.setValue(self.instrument.XMin)
        max.setValue(self.instrument.XMax)
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

        self.browseNeutronScatteringParamsButton.clicked.connect(lambda : self.handleBrowse(self.neutronScatteringParamsFileLineEdit, "Neutron scattering parameters file"))

        self.nexusDefintionFileLineEdit.setText(
            self.instrument.nxsDefinitionFile
        )


        self.nexusDefintionFileLineEdit.textChanged.connect(
            self.handleNexusDefinitionFileChanged
        )

        self.nexusDefintionFileLineEdit.setEnabled(self.instrument.dataFileType in ["nxs", "NXS"])
        self.browseNexusDefinitionButton.setEnabled(self.instrument.dataFileType in ["nxs", "NXS"])

        self.browseNexusDefinitionButton.clicked.connect(lambda : self.handleBrowse(self.nexusDefinitionFileLineEdit, "NeXus defnition file"))

        self.hardGroupEdgesCheckBox.setChecked(self.instrument.hardGroupEdges)
        self.hardGroupEdgesCheckBox.stateChanged.connect(
            self.handleHardGroupEdgesSwitched
        )

        # self.groupingParameterTable.model = GroupingParameterModel(self, self.instrument.groupingParameterPanel, ["Group", "XMin", "XMax", "Background Factor"])
        self.updateGroupingParameterPanel()
        # self.groupingParameterTable.itemChanged.connect(self.handleGroupingParameterPanelChanged)