from PyQt5.QtWidgets import QLineEdit, QWidget
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
        Constructs all the necessary attributes for the InstrumentWidget object.
        Calls the initComponents method, to load the UI file and populate data.
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
        self.instrument.dataFileType = self.dataFileTypeCombo.itemData(index)

    def handleDetectorCalibrationFileChanged(self, text):
        self.instrument.detectorCalibrationFileName = text
    
    def handleGroupsFileChanged(self, text):
        self.instrument.groupFileName = text
    
    def handleDeadtimeFileChanged(self, text):
        self.instrument.deadtimeConstantsFileName = text

    def handleUseLogarithmicBinningSwitched(self, state):
        self.instrument.useLogarithmicBinning = state    

    def handleMergeWeightsChanged(self, index):
        self.instrument.mergeWeights = self.mergeWeightsComboBox.itemData(index)

    def handleNeutronScatteringParamsFileChanged(self, text):
        self.instrument.neutronScatteringParametersFile = text
    
    def handleHardGroupEdgesSwitched(self, state):
        self.instrument.hardGroupEdges = state

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
        self.nameComboBox.currentIndexChanged.connect(self.handleInstrumentNameChanged)

        self.dataFileDirectoryLineEdit.setText(self.instrument.dataFileDir)
        self.dataFileDirectoryLineEdit.textChanged.connect(self.handleDataFileDirectoryChanged)

        dataFileTypes = ["raw", "sav", "txt", "nxs", "*"]
        self.dataFileTypeCombo.addItems(dataFileTypes)
        self.dataFileTypeCombo.setCurrentIndex(dataFileTypes.index(self.instrument.dataFileType))
        self.dataFileTypeCombo.currentIndexChanged.connect(self.handleDataFileTypeChanged)

        self.detCalibrationLineEdit.setText(self.instrument.detectorCalibrationFileName)
        self.detCalibrationLineEdit.textChanged.connect(self.handleDetectorCalibrationFileChanged)

        self.phiValuesColumnSpinBox.setValue(self.instrument.columnNoPhiVals)
        # self.phiValuesColumnSpinBox.valueChanged.connect()

        self.groupsFileLineEdit.setText(self.instrument.groupFileName)
        self.groupsFileLineEdit.textChanged.connect(self.handleGroupsFileChanged)

        self.deadtimeFileLineEdit.setText(self.instrument.deadtimeConstantsFileName)
        self.deadtimeFileLineEdit.textChanged.connect(self.handleDeadtimeFileChanged)

        self.minWavelengthMonNormSpinBox.setValue(self.instrument.wavelengthRangeForMonitorNormalisation[0])
        self.maxWavelengthMonNormSpinBox.setValue(self.instrument.wavelengthRangeForMonitorNormalisation[1])
        # self.minWavelengthMonNormLineEdit.valueChanged.connect()
        # self.maxWavelengthMonNormLineEdit.valueChanged.connect()

        self.spectrumNumbersIBLineEdit.setText(spacify(self.instrument.spectrumNumbersForIncidentBeamMonitor))

        self.spectrumNumbersTLineEdit.setText(spacify(self.instrument.spectrumNumbersForTransmissionMonitor))

        self.incidentMonitorQuietCountConstSpinBox.setValue(self.instrument.incidentMonitorQuietCountConst)
        # self.incidentMonitorQuietCountConstSpinBox.valueChanged.connect()
        self.transmissionMonitorQuietCountConstSpinBox.setValue(self.instrument.transmissionMonitorQuietCountConst)
        # self.transmissionMonitorQuietCountConstSpinBox.valueChanged.connect()

        self.channelNoASpinBox.setValue(self.instrument.channelNosSpikeAnalysis[0])
        # self.channelNoASpinBox.valueChanged.connect()
        self.channelNoBSpinBox.setValue(self.instrument.channelNosSpikeAnalysis[1])
        # self.channelNoBSpinBox.valueChanged.connect()

        self.acceptanceFactorSpinBox.setValue(self.instrument.spikeAnalysisAcceptanceFactor)
        # self.acceptanceFactorSpinBox.valueChanged.connect()

        self.minWavelengthSpinBox.setValue(self.instrument.wavelengthMin)
        # self.minWavelengthSpinBox.valueChanged.connect()
        self.maxWavelengthSpinBox.setValue(self.instrument.wavelengthMax)
        # self.maxWavelengthSpinBox.valueChanged.connect()
        # self.stepWavelengthSpinBox.valueChanged.connect()
        self.stepWavelengthSpinBox.setValue(self.instrument.wavelengthStep)

        self.noSmoothsOnMonitorSpinBox.setValue(self.instrument.NoSmoothsOnMonitor)

        self.scales = {
            Scales.Q: (self._QRadioButton, self.minQSpinBox, self.maxQSpinBox, self.stepQSpinBox),
            Scales.D_SPACING: (self.DSpacingRadioButton, self.minDSpacingSpinBox, self.maxDSpacingSpinBox, self.stepDSpacingSpinBox),
            Scales.WAVELENGTH: (self.wavelengthRadioButton, self.minWavelength_SpinBox, self.maxWavelength_SpinBox, self.stepWavelength_SpinBox),
            Scales.ENERGY: (self.energyRadioButton, self.minEnergySpinBox, self.maxEnergySpinBox, self.stepEnergySpinBox),
            Scales.TOF: (self.TOFRadioButton, self.minTOFSpinBox, self.maxTOFSpinBox, self.stepTOFSpinBox)
        }

        selection, min, max, step = self.scales[self.instrument.scaleSelection]
        selection.setChecked(True)
        min.setValue(self.instrument.XMin)
        max.setValue(self.instrument.XMax)
        step.setValue(self.instrument.XStep)

        self.logarithmicBinningCheckBox.setChecked(self.instrument.useLogarithmicBinning)
        self.logarithmicBinningCheckBox.stateChanged.connect(self.handleUseLogarithmicBinningSwitched)

        self.groupsAcceptanceFactorSpinBox.setValue(self.instrument.groupsAcceptanceFactor)

        self.mergePowerSpinBox.setValue(self.instrument.mergePower)

        for m in MergeWeights:
            self.mergeWeightsComboBox.addItem(m.name, m)
        self.mergeWeightsComboBox.setCurrentIndex(self.instrument.mergeWeights.value)
        self.mergeWeightsComboBox.currentIndexChanged.connect(self.handleMergeWeightsChanged)
        self.incidentFlightPathSpinBox.setValue(self.instrument.incidentFlightPath)

        self.outputDiagSpectrumSpinBox.setValue(self.instrument.spectrumNumberForOutputDiagnosticFiles)
        self.neutronScatteringParamsFileLineEdit.setText(self.instrument.neutronScatteringParametersFile)
        self.neutronScatteringParamsFileLineEdit.textChanged.connect(self.handleNeutronScatteringParamsFileChanged)
        self.hardGroupEdgesCheckBox.setChecked(self.instrument.hardGroupEdges)
        self.hardGroupEdgesCheckBox.stateChanged.connect(self.handleHardGroupEdgesSwitched)
