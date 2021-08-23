from PyQt5.QtWidgets import QWidget
from PyQt5 import uic
from src.gudrun_classes.enums import Instruments, MergeWeights, Scales
from src.scripts.utils import spacify
import os

class InstrumentWidget(QWidget):
    def __init__(self, instrument, parent=None):
        self.instrument = instrument
        self.parent = parent

        super(InstrumentWidget, self).__init__(self.parent)
        self.attributeMap = {}
        self.initComponents()
    
    def initComponents(self):
        current_dir = os.path.dirname(os.path.realpath(__file__))
        uifile = os.path.join(current_dir, "ui_files/instrumentWidget.ui")
        uic.loadUi(uifile, self)

        self.nameComboBox.addItems([i.name for i in Instruments])
        self.nameComboBox.setCurrentIndex(self.instrument.name.value)
        self.attributeMap[self.nameComboBox] = "name"
        
        self.dataFileDirectoryLineEdit.setText(self.instrument.dataFileDir)
        self.attributeMap[self.dataFileDirectoryLineEdit] = "dataFileDir"

        dataFileTypes = ["raw", "sav", "txt", "nxs", "*"]
        self.dataFileTypeCombo.addItems(dataFileTypes)
        self.dataFileTypeCombo.setCurrentIndex(dataFileTypes.index(self.instrument.dataFileType))
        self.attributeMap[self.dataFileTypeCombo] = "dataFileType"

        self.detCalibrationLineEdit.setText(self.instrument.detectorCalibrationFileName)
        self.attributeMap[self.detCalibrationLineEdit] = "detectorCalibrationFileName"

        self.phiValuesColumnLineEdit.setText(str(self.instrument.columnNoPhiVals))
        self.attributeMap[self.phiValuesColumnLineEdit] = "columnNoPhiVals"

        self.groupsFileLineEdit.setText(self.instrument.groupFileName)
        self.attributeMap[self.groupsFileLineEdit] = "groupFileName"

        self.deadtimeFileLineEdit.setText(self.instrument.deadtimeConstantsFileName)
        self.attributeMap[self.deadtimeFileLineEdit] = "deadtimeConstantsFileName"

        self.minWavelengthMonNormLineEdit.setText(str(self.instrument.wavelengthRangeForMonitorNormalisation[0]))
        self.maxWavelengthMonNormLineEdit.setText(str(self.instrument.wavelengthRangeForMonitorNormalisation[1]))
        self.attributeMap[self.minWavelengthMonNormLineEdit] = ("wavelengthRangeForMonitorNormalisation", 0)
        self.attributeMap[self.maxWavelengthMonNormLineEdit] = ("wavelengthRangeForMonitorNormalisation", 1)

        self.spectrumNumbersIBLineEdit.setText(spacify(self.instrument.spectrumNumbersForIncidentBeamMonitor))
        self.attributeMap[self.spectrumNumbersIBLineEdit] = "spectrumNumbersForIncidentBeamMonitor"

        self.spectrumNumbersTLineEdit.setText(spacify(self.instrument.spectrumNumbersForTransmissionMonitor))
        self.attributeMap[self.spectrumNumbersTLineEdit] = "spectrumNumbersForTransmissionMonitor"

        self.quietCountConstIMLineEdit.setText(str(self.instrument.incidentMonitorQuietCountConst))
        self.attributeMap[self.quietCountConstIMLineEdit] = "incidentMonitorQuietCountConst"

        self.quietCountConstTMLineEdit.setText(str(self.instrument.transmissionMonitorQuietCountConst))
        self.attributeMap[self.quietCountConstTMLineEdit] = "transmissionMonitorQuietCountConst"

        self.channelNoALineEdit.setText(str(self.instrument.channelNosSpikeAnalysis[0]))
        self.attributeMap[self.channelNoALineEdit] = ("channelNosSpikeAnalysis", 0)

        self.channelNoBLineEdit.setText(str(self.instrument.channelNosSpikeAnalysis[1]))
        self.attributeMap[self.channelNoBLineEdit] = ("channelNosSpikeAnalysis", 1)

        self.acceptanceFactorLineEdit.setText(str(self.instrument.spikeAnalysisAcceptanceFactor))
        self.attributeMap[self.acceptanceFactorLineEdit] = "spikeAnalysisAcceptanceFactor"

        self.minWavelengthLineEdit.setText(str(self.instrument.wavelengthMin))
        self.attributeMap[self.minWavelengthLineEdit] = "wavelengthMin"

        self.maxWavelengthLineEdit.setText(str(self.instrument.wavelengthMax))
        self.attributeMap[self.maxWavelengthLineEdit] = "wavelengthMax"

        self.stepWavelengthLineEdit.setText(str(self.instrument.wavelengthStep))
        self.attributeMap[self.stepWavelengthLineEdit] = "wavelengthStep"

        self.noSmoothsOnMonitorLineEdit.setText(str(self.instrument.NoSmoothsOnMonitor))
        self.attributeMap[self.noSmoothsOnMonitorLineEdit] = "NoSmoothsOnMonitor"

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
        self.attributeMap[min] = "XMin"
        self.attributeMap[max] = "XMax"
        self.attributeMap[step] = "XStep"

        self.logarithmicBinningCheckBox.setChecked(self.instrument.useLogarithmicBinning)
        self.attributeMap[self.logarithmicBinningCheckBox] = "useLogarithmicBinning"

        self.groupsAcceptanceFactorLineEdit.setText(str(self.instrument.groupsAcceptanceFactor))
        self.attributeMap[self.groupsAcceptanceFactorLineEdit] = "groupsAcceptanceFactor"

        self.mergePowerLineEdit.setText(str(self.instrument.mergePower))
        self.attributeMap[ self.mergePowerLineEdit] = "mergePower"

        self.mergeWeightsComboBox.addItems([m.name for m in MergeWeights])
        self.mergeWeightsComboBox.setCurrentIndex(self.instrument.mergeWeights.value)
        self.attributeMap[self.mergeWeightsComboBox] = "mergeWeights"

        self.incidentFlightPathLineEdit.setText(str(self.instrument.incidentFlightPath))
        self.attributeMap[self.incidentFlightPathLineEdit] = "incidentFlightPath"

        self.outputDiagSpectrumLineEdit.setText(str(self.instrument.spectrumNumberForOutputDiagnosticFiles))
        self.attributeMap[self.outputDiagSpectrumLineEdit] = "spectrumNumberForOutputDiagnosticFiles"
        self.neutronScatteringParamsFileLineEdit.setText(self.instrument.neutronScatteringParametersFile)
        self.attributeMap[self.neutronScatteringParamsFileLineEdit] = "neutronScatteringParametersFile"

        self.hardGroupEdgesCheckBox.setChecked(self.instrument.hardGroupEdges)
        self.attributeMap[self.hardGroupEdgesCheckBox] = "hardGroupEdges"

        print(self.attributeMap)