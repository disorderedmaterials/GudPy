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

        super(InstrumentWidget, self).__init__(object=self.instrument, parent=self.parent)
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

        self.phiValuesColumnLineEdit.setText(str(self.instrument.columnNoPhiVals))
        self.phiValuesColumnLineEdit.textChanged.connect()

        self.groupsFileLineEdit.setText(self.instrument.groupFileName)
        self.groupsFileLineEdit.textChanged.connect(self.handleGroupsFileChanged)

        self.deadtimeFileLineEdit.setText(self.instrument.deadtimeConstantsFileName)
        self.deadtimeFileLineEdit.textChanged.connect(self.handleDeadtimeFileChanged)

        self.minWavelengthMonNormLineEdit.setText(str(self.instrument.wavelengthRangeForMonitorNormalisation[0]))
        self.maxWavelengthMonNormLineEdit.setText(str(self.instrument.wavelengthRangeForMonitorNormalisation[1]))
        self.minWavelengthMonNormLineEdit.textChanged.connect()
        self.maxWavelengthMonNormLineEdit.textChanged.connect()

        self.spectrumNumbersIBLineEdit.setText(spacify(self.instrument.spectrumNumbersForIncidentBeamMonitor))

        self.spectrumNumbersTLineEdit.setText(spacify(self.instrument.spectrumNumbersForTransmissionMonitor))

        self.quietCountConstIMLineEdit.setText(str(self.instrument.incidentMonitorQuietCountConst))

        self.quietCountConstTMLineEdit.setText(str(self.instrument.transmissionMonitorQuietCountConst))

        self.channelNoALineEdit.setText(str(self.instrument.channelNosSpikeAnalysis[0]))

        self.channelNoBLineEdit.setText(str(self.instrument.channelNosSpikeAnalysis[1]))

        self.acceptanceFactorLineEdit.setText(str(self.instrument.spikeAnalysisAcceptanceFactor))

        self.minWavelengthLineEdit.setText(str(self.instrument.wavelengthMin))

        self.maxWavelengthLineEdit.setText(str(self.instrument.wavelengthMax))

        self.stepWavelengthLineEdit.setText(str(self.instrument.wavelengthStep))

        self.noSmoothsOnMonitorLineEdit.setText(str(self.instrument.NoSmoothsOnMonitor))

        self.scales = {
            Scales.Q: (self._QRadioButton, self.minQLineEdit, self.maxQLineEdit, self.stepQLineEdit),
            Scales.D_SPACING: (self.DSpacingRadioButton, self.minDSpacingLineEdit, self.maxDSpacingLineEdit, self.stepDSpacingLineEdit),
            Scales.WAVELENGTH: (self.wavelengthRadioButton, self.minWavelength_LineEdit, self.maxWavelength_LineEdit, self.stepWavelength_LineEdit),
            Scales.ENERGY: (self.energyRadioButton, self.minEnergyLineEdit, self.maxEnergyLineEdit, self.stepEnergyLineEdit),
            Scales.TOF: (self.TOFRadioButton, self.minTOFLineEdit, self.maxTOFLineEdit, self.stepTOFLineEdit)
        }

        selection, min, max, step = self.scales[self.instrument.scaleSelection]
        selection.setChecked(True)
        min.setText(str(self.instrument.XMin))
        max.setText(str(self.instrument.XMax))
        step.setText(str(self.instrument.XStep))

        self.logarithmicBinningCheckBox.setChecked(self.instrument.useLogarithmicBinning)
        self.logarithmicBinningCheckBox.stateChanged.connect(self.handleUseLogarithmicBinningSwitched)

        self.groupsAcceptanceFactorLineEdit.setText(str(self.instrument.groupsAcceptanceFactor))

        self.mergePowerLineEdit.setText(str(self.instrument.mergePower))

        for m in MergeWeights:
            self.mergeWeightsComboBox.addItem(m.name, m)
        self.mergeWeightsComboBox.setCurrentIndex(self.instrument.mergeWeights.value)
        self.mergeWeightsComboBox.currentIndexChanged.connect(self.handleMergeWeightsChanged)
        self.incidentFlightPathLineEdit.setText(str(self.instrument.incidentFlightPath))

        self.outputDiagSpectrumLineEdit.setText(str(self.instrument.spectrumNumberForOutputDiagnosticFiles))
        self.neutronScatteringParamsFileLineEdit.setText(self.instrument.neutronScatteringParametersFile)
        self.neutronScatteringParamsFileLineEdit.textChanged.connect(self.handleNeutronScatteringParamsFileChanged)
        self.hardGroupEdgesCheckBox.setChecked(self.instrument.hardGroupEdges)
        self.hardGroupEdgesCheckBox.stateChanged.connect(self.handleHardGroupEdgesSwitched)
