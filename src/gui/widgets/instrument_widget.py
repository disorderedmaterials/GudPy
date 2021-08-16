from PyQt5.QtWidgets import QWidget
from PyQt5 import uic
from gudrun_classes.enums import Instruments, MergeWeights, Scales
from scripts.utils import spacify
import os

class InstrumentWidget(QWidget):
    def __init__(self, instrument, parent=None):
        self.instrument = instrument
        self.parent = parent

        super(InstrumentWidget, self).__init__(self.parent)
        self.initComponents()
    
    def initComponents(self):
        current_dir = os.path.dirname(os.path.realpath(__file__))
        uifile = os.path.join(current_dir, "ui_files/instrumentWidget.ui")
        uic.loadUi(uifile, self)

        self.nameComboBox.addItems([i.name for i in Instruments])
        self.nameComboBox.setCurrentIndex(self.instrument.name.value)
        
        self.dataFileDirectoryLineEdit.setText(self.instrument.dataFileDir)

        dataFileTypes = ["raw", "sav", "txt", "nxs", "*"]
        self.dataFileTypeCombo.addItems(dataFileTypes)
        self.dataFileTypeCombo.setCurrentIndex(dataFileTypes.index(self.instrument.dataFileType))

        self.detCalibrationLineEdit.setText(self.instrument.detectorCalibrationFileName)
        self.phiValuesColumnLineEdit.setText(str(self.instrument.columnNoPhiVals))
        self.groupsFileLineEdit.setText(self.instrument.groupFileName)
        self.deadtimeFileLineEdit.setText(self.instrument.deadtimeConstantsFileName)

        # wavelengthRangeForMonitorNormalisation
        self.minWavelengthMonNormLineEdit.setText(str(self.instrument.wavelengthRangeForMonitorNormalisation[0]))
        self.maxWavelengthMonNormLineEdit.setText(str(self.instrument.wavelengthRangeForMonitorNormalisation[1]))


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


        scales = {
            Scales.Q: (self._QRadioButton, self.minQLineEdit, self.maxQLineEdit, self.stepQLineEdit),
            Scales.D_SPACING: (self.DSpacingRadioButton, self.minDSpacingLineEdit, self.maxDSpacingLineEdit, self.stepDSpacingLineEdit),
            Scales.WAVELENGTH: (self.wavelengthRadioButton, self.minWavelength_LineEdit, self.maxWavelength_LineEdit, self.stepWavelength_LineEdit),
            Scales.ENERGY: (self.energyRadioButton, self.minEnergyLineEdit, self.maxEnergyLineEdit, self.stepEnergyLineEdit),
            Scales.TOF: (self.TOFRadioButton, self.minTOFLineEdit, self.maxTOFLineEdit, self.stepTOFLineEdit)
        }

        selection, min, max, step = scales[self.instrument.scaleSelection]
        selection.setChecked(True)
        min.setText(str(self.instrument.XMin))
        max.setText(str(self.instrument.XMax))
        step.setText(str(self.instrument.XStep))
        self.logarithmicBinningCheckBox.setChecked(self.instrument.useLogarithmicBinning)
        
        self.groupsAcceptanceFactorLineEdit.setText(str(self.instrument.groupsAcceptanceFactor))
        self.mergePowerLineEdit.setText(str(self.instrument.mergePower))

        self.mergeWeightsComboBox.addItems([m.name for m in MergeWeights])
        self.mergeWeightsComboBox.setCurrentIndex(self.instrument.mergeWeights.value)

        self.incidentFlightPathLineEdit.setText(str(self.instrument.incidentFlightPath))
        self.outputDiagSpectrumLineEdit.setText(str(self.instrument.spectrumNumberForOutputDiagnosticFiles))
        self.neutronScatteringParamsFileLineEdit.setText(self.instrument.neutronScatteringParametersFile)

        self.hardGroupEdgesCheckBox.setChecked(self.instrument.hardGroupEdges)
