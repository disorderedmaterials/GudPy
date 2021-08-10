from PyQt5.QtWidgets import QComboBox, QLabel, QLineEdit, QPushButton, QTextEdit, QWidget

from scripts.utils import spacify, numifyBool
from gudrun_classes.enums import MergeWeights, Scales

class InstrumentPane(QWidget):

    def __init__(self, instrument, parent, x, y, relHeight, relWidth):
        self.instrument = instrument
        self.parent = parent
        self.x = x
        self.y = y
        self.relHeight = relHeight
        self.relWidth = relWidth
        super(InstrumentPane, self).__init__(parent)
        self.setGeometry(
            y,
            0,
            int(self.parent.size().width() * self.relWidth),
            int(self.parent.size().height() * self.relHeight),
        )
        self.childWidth = (self.parent.size().width()*self.relWidth) // 5
        self.childHeight =  (self.parent.size().height() * self.relHeight) // 20
        self.initComponents()

    def initComponents(self):
        instruments = {"SANDALS": 0, "GEM": 1, "NIMROD": 2,
                        "D4C": 3, "POLARIS": 4, "HIPD": 5,
                        "NPDF": 6
                        }

        self.instrumentLabel, self.instrumentCombo = (
            self.makeLabelComboBoxPair(
                "Instrument name",
                instruments[self.instrument.name],
                list(instruments.keys()),
                0,
                0
            )
        )

        self.gudrunInputFileLabel, self.gudrunInputFileText = (
            self.makeLabelTextPair(
                "Gudrun input file directory",
                self.instrument.GudrunInputFileDir,
                self.childHeight,
                0
                
            )
        )

        self.dataFileDirLabel, self.dataFileDirText = (
            self.makeLabelTextPair(
                "Data file directory",
                self.instrument.dataFileDir,
                self.childHeight*2,
                0
            )
        )

        dfTypes = { "raw": 0, "sav": 1, "txt": 2, "nxs": 3, "*": 4}

        self.dataFileTypeLabel, self.dataFileTypeText = (
            self.makeLabelComboBoxPair(
                "Data file type",
                dfTypes[self.instrument.dataFileType],
                list(dfTypes.keys()),
                self.childHeight*3,
                0
            )
        )

        self.detFileNameLabel, self.detFileNameText = (
            self.makeLabelTextPair(
                "Detector calibration file name",
                self.instrument.detectorCalibrationFileName,
                self.childHeight*4,
                0
            )
        )

        self.phiValuesLabel, self.phiValuesText = (
            self.makeLabelTextPair(
                "Column no. for phi values",
                self.instrument.columnNoPhiVals,
                self.childHeight*5,
                0
            )
        )

        self.groupsFileNameLabel, self.groupsFileNameText = (
            self.makeLabelTextPair(
                "Groups file name",
                self.instrument.groupFileName,
                self.childHeight*6,
                0
            )
        )

        self.deadtimeFileNameLabel, self.deadtimeFileNameText = (
            self.makeLabelTextPair(
                "Deadtime constants file name",
                self.instrument.deadtimeConstantsFileName,
                self.childHeight*7,
                0
            )
        )

        self.spectrumNumbersIBLabel, self.spectrumNumbersIBText = (
            self.makeLabelTextPair(
                "Spectrum no.s for incident beam monitor",
                spacify(self.instrument.spectrumNumbersForIncidentBeamMonitor),
                self.childHeight*8,
                0
            )
        )

        self.wavelengthRangeMonNormLabel, self.wavelengthRangeMonNormText = (
            self.makeLabelTextPair(
                "Wavelength range for monitor normalisation",
                self.instrument.wavelengthRangeForMonitorNormalisation,
                self.childHeight*9,
                0,
                isIterable=True
            )
        )

        self.spectrumNumbersTMLabel, self.spectrumNumbersTMText = (
            self.makeLabelTextPair(
                "Spectrum no.s for incident beam monitor",
                spacify(self.instrument.spectrumNumbersForTransmissionMonitor),
                self.childHeight*10,
                0
            )
        )

        self.iMonitorQuietCountConstLabel, self.iMonitorQuietCountConstText = (
            self.makeLabelTextPair(
                "Incident monitor quiet count constant",
                self.instrument.incidentMonitorQuietCountConst,
                self.childHeight*11,
                0            
            )
        )

        self.tMonitorQuietCountConstLabel, self.tMonitorQuietCountConstText = (
            self.makeLabelTextPair(
                "Transmission monitor quiet count constant",
                self.instrument.transmissionMonitorQuietCountConst,
                self.childHeight*12,
                0            
            )
        )

        self.channelNosLabel, self.channelNosText = (
            self.makeLabelTextPair(
                "Channel no.s for spike analysis",
                self.instrument.channelNosSpikeAnalysis,
                self.childHeight*13,
                0,
                isIterable=True
            )
        )
        self.spikeAcceptanceFactorLabel, self.spikeAcceptanceFactorText = (
            self.makeLabelTextPair(
                "Spike analysis acceptance factor",
                self.instrument.spikeAnalysisAcceptanceFactor,
                self.childHeight*14,
                0            
            )
        )

        self.wavelengthRangeLabel, self.wavelengthRangeText = (
            self.makeLabelTextPair(
                "Wavelength range and step size",
                [self.instrument.wavelengthMin, self.instrument.wavelengthMax, self.instrument.wavelengthStep],
                self.childHeight*15,
                0,
                isIterable=True
            )
        )

        self.noSmoothsLabel, self.noSmoothsText = (
            self.makeLabelTextPair(
                "No. of smooths on monitor",
                self.instrument.NoSmoothsOnMonitor,
                self.childHeight*16,
                0
            )
        )

        self.XRangeLabel, self.XRangeText = (
            self.makeLabelTextPair(
                "X range and step size",
                [self.instrument.XMin, self.instrument.XMax, self.instrument.XStep],
                self.childHeight*17,
                0,
                isIterable=True
            )
        )

        self.logarithmicBinningLabel, self.logarithmicBinningCombo = (
            self.makeLabelComboBoxPair(
                "Use logarithmic binning?",
                numifyBool(self.instrument.useLogarithmicBinning),
                ["False", "True"],
                self.childHeight*18,
                0
            )
        )

        self.groupsAcceptanceFactorLabel, self.groupsAcceptanceFactorText = (
            self.makeLabelTextPair(
                "Groups acceptance factor",
                self.instrument.groupsAcceptanceFactor,
                self.childHeight*19,
                0
            )
        )

        self.mergePowerLabel, self.mergePowerText = (
            self.makeLabelTextPair(
                "Merge power",
                self.instrument.mergePower,
                self.childHeight*20,
                0
            )
        )

        self.subAtomScatteringLabel, self.subAtomScatteringCombo = (
            self.makeLabelComboBoxPair(
                "Subtract single atom scattering?",
                numifyBool(self.instrument.subSingleAtomScattering),
                ["False", "True"],
                self.childHeight*21,
                0
            )
        )

        

        self.mergeWeightsLabel, self.mergeWeightsCombo = (
            self.makeLabelComboBoxPair(
                "Merge weights by?",
                self.instrument.mergeWeights.value,
                [m.name for m in MergeWeights],
                self.childHeight*22,
                0
            )
        )

        self.incidentFlightPathLabel, self.incidentFlightPathText = (
            self.makeLabelTextPair(
                "Incident flight path",
                self.instrument.incidentFlightPath,
                self.childHeight*23,
                0
            )
        )

        self.diagnosticSpectrumLabel, self.diagnosticSpectrumText = (
            self.makeLabelTextPair(
                "Spectrum number for output diagnostic files",
                self.instrument.spectrumNumberForOutputDiagnosticFiles,
                self.childHeight*24,
                0
            )
        )

        self.neutronParamsFileNameText, self.neutronParamsFileNameLabel = (
            self.makeLabelTextPair(
                "Neutron scattering params file",
                self.instrument.neutronScatteringParametersFile,
                self.childHeight*25,
                0
            )
        )

        self.scaleSelectionText, self.scaleSelectionCombo = (
            self.makeLabelComboBoxPair(
                "Scale selection",
                self.instrument.scaleSelection.value,
                [s.name for s in Scales],
                self.childHeight*26,
                0
            )
        )

        self.subWavelengthBinnedLabel, self.subWavelengthBinnedCombo = (
            self.makeLabelComboBoxPair(
                "Subtract single atom scattering?",
                numifyBool(self.instrument.subWavelengthBinnedData),
                ["False", "True"],
                self.childHeight*27,
                0
            )
        )

        self.GudrunStartFolderText, self.GudrunStartFolderLabel = (
            self.makeLabelTextPair(
                "Gudrun start folder",
                self.instrument.GudrunStartFolder,
                self.childHeight*28,
                0
            )
        )

        self.startupFileLabel, self.startupFileText = (
            self.makeLabelTextPair(
                "Gudrun start folder",
                self.instrument.startupFileFolder,
                self.childHeight*29,
                0
            )
        )

        self.logarithmicStepSizeLabel, self.logarithmicStepSizeText = (
            self.makeLabelTextPair(
                "Logarithmic step size",
                self.instrument.logarithmicStepSize,
                self.childHeight*30,
                0
            )
        )

        self.hardGroupEdgesLabel, self.hardGroupEdgesText = (
            self.makeLabelComboBoxPair(
                "Hard group edges?",
                numifyBool(self.instrument.hardGroupEdges),
                ["False", "True"],
                self.childHeight*31,
                0
            )
        )




        

    def makeLabelComboBoxPair(self, text, value, values, y, x):
        label = QLabel(self)
        label.setText(text)
        label.setGeometry(x, y, self.childWidth, self.childHeight)
        label.adjustSize()
        combo = QComboBox(self)
        combo.addItems(values)
        combo.setCurrentIndex(value)
        combo.setGeometry(x + label.size().width()+5, y, self.childWidth, self.childHeight//2)
        combo.adjustSize()
        return label, combo
    
    def makeLabelTextPair(self, text, value, y, x, isIterable=False):
        label = QLabel(self)
        label.setText(text)
        label.setGeometry(x, y, self.childWidth, self.childHeight)
        label.adjustSize()
        if not isIterable:
            text = QLineEdit(self)
            text.setText(str(value))
            text.setGeometry(x + label.size().width()+5, y, self.childWidth, self.childHeight//2)
            text.adjustSize()
            return label, text
        else:
            prev_size = label.size()
            texts = []
            for val in value:
                text = QLineEdit(self)
                text.setText(str(val))
                text.setGeometry(x + prev_size.width()+5, y, self.childWidth, self.childHeight//2)
                text.adjustSize()
                prev_size+=text.size()
                texts.append(text)
            return label, texts

    def updateArea(self):

        self.setGeometry(
            self.y,
            0,
            int(self.parent.size().width() * self.relWidth),
            int(self.parent.size().height() * self.relHeight),
        )