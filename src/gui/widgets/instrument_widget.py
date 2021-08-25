from PyQt5.QtWidgets import QWidget
from PyQt5 import uic
from src.gui.widgets.gudpy_widget import GudPyWidget
from src.gudrun_classes.enums import Instruments, MergeWeights, Scales
from src.scripts.utils import spacify
import os

class InstrumentWidget(GudPyWidget):
    def __init__(self, instrument, parent=None):
        self.instrument = instrument
        self.parent = parent

        super(InstrumentWidget, self).__init__(object=self.instrument, parent=self.parent)
        self.initComponents()
    
    def initComponents(self):
        current_dir = os.path.dirname(os.path.realpath(__file__))
        uifile = os.path.join(current_dir, "ui_files/instrumentWidget.ui")
        uic.loadUi(uifile, self)

        for i in Instruments:
            self.nameComboBox.addItem(i.name, i)
        self.nameComboBox.setCurrentIndex(self.instrument.name.value)
        self.widgetMap[self.nameComboBox] = "name"
        
        self.dataFileDirectoryLineEdit.setText(self.instrument.dataFileDir)
        self.widgetMap[self.dataFileDirectoryLineEdit] = "dataFileDir"

        dataFileTypes = ["raw", "sav", "txt", "nxs", "*"]
        self.dataFileTypeCombo.addItems(dataFileTypes)
        self.dataFileTypeCombo.setCurrentIndex(dataFileTypes.index(self.instrument.dataFileType))
        self.widgetMap[self.dataFileTypeCombo] = "dataFileType"

        self.detCalibrationLineEdit.setText(self.instrument.detectorCalibrationFileName)
        self.widgetMap[self.detCalibrationLineEdit] = "detectorCalibrationFileName"

        self.phiValuesColumnLineEdit.setText(str(self.instrument.columnNoPhiVals))
        self.widgetMap[self.phiValuesColumnLineEdit] = "columnNoPhiVals"

        self.groupsFileLineEdit.setText(self.instrument.groupFileName)
        self.widgetMap[self.groupsFileLineEdit] = "groupFileName"

        self.deadtimeFileLineEdit.setText(self.instrument.deadtimeConstantsFileName)
        self.widgetMap[self.deadtimeFileLineEdit] = "deadtimeConstantsFileName"

        self.minWavelengthMonNormLineEdit.setText(str(self.instrument.wavelengthRangeForMonitorNormalisation[0]))
        self.maxWavelengthMonNormLineEdit.setText(str(self.instrument.wavelengthRangeForMonitorNormalisation[1]))
        self.widgetMap[self.minWavelengthMonNormLineEdit] = ("wavelengthRangeForMonitorNormalisation", 0)
        self.widgetMap[self.maxWavelengthMonNormLineEdit] = ("wavelengthRangeForMonitorNormalisation", 1)

        self.spectrumNumbersIBLineEdit.setText(spacify(self.instrument.spectrumNumbersForIncidentBeamMonitor))
        self.widgetMap[self.spectrumNumbersIBLineEdit] = "spectrumNumbersForIncidentBeamMonitor"

        self.spectrumNumbersTLineEdit.setText(spacify(self.instrument.spectrumNumbersForTransmissionMonitor))
        self.widgetMap[self.spectrumNumbersTLineEdit] = "spectrumNumbersForTransmissionMonitor"

        self.quietCountConstIMLineEdit.setText(str(self.instrument.incidentMonitorQuietCountConst))
        self.widgetMap[self.quietCountConstIMLineEdit] = "incidentMonitorQuietCountConst"

        self.quietCountConstTMLineEdit.setText(str(self.instrument.transmissionMonitorQuietCountConst))
        self.widgetMap[self.quietCountConstTMLineEdit] = "transmissionMonitorQuietCountConst"

        self.channelNoALineEdit.setText(str(self.instrument.channelNosSpikeAnalysis[0]))
        self.widgetMap[self.channelNoALineEdit] = ("channelNosSpikeAnalysis", 0)

        self.channelNoBLineEdit.setText(str(self.instrument.channelNosSpikeAnalysis[1]))
        self.widgetMap[self.channelNoBLineEdit] = ("channelNosSpikeAnalysis", 1)

        self.acceptanceFactorLineEdit.setText(str(self.instrument.spikeAnalysisAcceptanceFactor))
        self.widgetMap[self.acceptanceFactorLineEdit] = "spikeAnalysisAcceptanceFactor"

        self.minWavelengthLineEdit.setText(str(self.instrument.wavelengthMin))
        self.widgetMap[self.minWavelengthLineEdit] = "wavelengthMin"

        self.maxWavelengthLineEdit.setText(str(self.instrument.wavelengthMax))
        self.widgetMap[self.maxWavelengthLineEdit] = "wavelengthMax"

        self.stepWavelengthLineEdit.setText(str(self.instrument.wavelengthStep))
        self.widgetMap[self.stepWavelengthLineEdit] = "wavelengthStep"

        self.noSmoothsOnMonitorLineEdit.setText(str(self.instrument.NoSmoothsOnMonitor))
        self.widgetMap[self.noSmoothsOnMonitorLineEdit] = "NoSmoothsOnMonitor"

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
        self.widgetMap[min] = "XMin"
        self.widgetMap[max] = "XMax"
        self.widgetMap[step] = "XStep"

        self.logarithmicBinningCheckBox.setChecked(self.instrument.useLogarithmicBinning)
        self.widgetMap[self.logarithmicBinningCheckBox] = "useLogarithmicBinning"

        self.groupsAcceptanceFactorLineEdit.setText(str(self.instrument.groupsAcceptanceFactor))
        self.widgetMap[self.groupsAcceptanceFactorLineEdit] = "groupsAcceptanceFactor"

        self.mergePowerLineEdit.setText(str(self.instrument.mergePower))
        self.widgetMap[ self.mergePowerLineEdit] = "mergePower"

        for m in MergeWeights:
            self.mergeWeightsComboBox.addItem(m.name, m)
        self.mergeWeightsComboBox.setCurrentIndex(self.instrument.mergeWeights.value)
        self.widgetMap[self.mergeWeightsComboBox] = "mergeWeights"

        self.incidentFlightPathLineEdit.setText(str(self.instrument.incidentFlightPath))
        self.widgetMap[self.incidentFlightPathLineEdit] = "incidentFlightPath"

        self.outputDiagSpectrumLineEdit.setText(str(self.instrument.spectrumNumberForOutputDiagnosticFiles))
        self.widgetMap[self.outputDiagSpectrumLineEdit] = "spectrumNumberForOutputDiagnosticFiles"
        self.neutronScatteringParamsFileLineEdit.setText(self.instrument.neutronScatteringParametersFile)
        self.widgetMap[self.neutronScatteringParamsFileLineEdit] = "neutronScatteringParametersFile"

        self.hardGroupEdgesCheckBox.setChecked(self.instrument.hardGroupEdges)
        self.widgetMap[self.hardGroupEdgesCheckBox] = "hardGroupEdges"
