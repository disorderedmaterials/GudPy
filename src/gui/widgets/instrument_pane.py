from PyQt5.QtWidgets import QWidget


from scripts.utils import spacify, numifyBool
from gudrun_classes.enums import MergeWeights, Scales

from widgets.make_pairs import makeLabelComboBoxPair, makeLabelTextPair


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
        self.childHeight = (
            (self.parent.size().height() * self.relHeight) // 20
        )
        self.initComponents()

    def initComponents(self):
        instruments = {
            "SANDALS": 0, "GEM": 1, "NIMROD": 2,
            "D4C": 3, "POLARIS": 4, "HIPD": 5,
            "NPDF": 6
        }

        self.instrumentLabel, self.instrumentCombo = (
            makeLabelComboBoxPair(
                self,
                "Instrument name",
                instruments[self.instrument.name.name],
                list(instruments.keys()),
                0,
                0
            )
        )

        self.gudrunInputFileLabel, self.gudrunInputFileText = (
            makeLabelTextPair(
                self,
                "Gudrun input file directory",
                self.instrument.GudrunInputFileDir,
                self.childHeight,
                0
            )
        )

        self.dataFileDirLabel, self.dataFileDirText = (
            makeLabelTextPair(
                self,
                "Data file directory",
                self.instrument.dataFileDir,
                self.childHeight*2,
                0
            )
        )

        dfTypes = {"raw": 0, "sav": 1, "txt": 2, "nxs": 3, "*": 4}

        self.dataFileTypeLabel, self.dataFileTypeText = (
            makeLabelComboBoxPair(
                self,
                "Data file type",
                dfTypes[self.instrument.dataFileType],
                list(dfTypes.keys()),
                self.childHeight*3,
                0
            )
        )

        self.detFileNameLabel, self.detFileNameText = (
            makeLabelTextPair(
                self,
                "Detector calibration file name",
                self.instrument.detectorCalibrationFileName,
                self.childHeight*4,
                0
            )
        )

        self.phiValuesLabel, self.phiValuesText = (
            makeLabelTextPair(
                self,
                "Column no. for phi values",
                self.instrument.columnNoPhiVals,
                self.childHeight*5,
                0
            )
        )

        self.groupsFileNameLabel, self.groupsFileNameText = (
            makeLabelTextPair(
                self,
                "Groups file name",
                self.instrument.groupFileName,
                self.childHeight*6,
                0
            )
        )

        self.deadtimeFileNameLabel, self.deadtimeFileNameText = (
            makeLabelTextPair(
                self,
                "Deadtime constants file name",
                self.instrument.deadtimeConstantsFileName,
                self.childHeight*7,
                0
            )
        )

        self.spectrumNumbersIBLabel, self.spectrumNumbersIBText = (
            makeLabelTextPair(
                self,
                "Spectrum no.s for incident beam monitor",
                spacify(self.instrument.spectrumNumbersForIncidentBeamMonitor),
                self.childHeight*8,
                0
            )
        )

        self.wavelengthRangeMonNormLabel, self.wavelengthRangeMonNormText = (
            makeLabelTextPair(
                self,
                "Wavelength range for monitor normalisation",
                self.instrument.wavelengthRangeForMonitorNormalisation,
                self.childHeight*9,
                0,
                isIterable=True
            )
        )

        self.spectrumNumbersTMLabel, self.spectrumNumbersTMText = (
            makeLabelTextPair(
                self,
                "Spectrum no.s for incident beam monitor",
                spacify(self.instrument.spectrumNumbersForTransmissionMonitor),
                self.childHeight*10,
                0
            )
        )

        self.iMonitorQuietCountConstLabel, self.iMonitorQuietCountConstText = (
            makeLabelTextPair(
                self,
                "Incident monitor quiet count constant",
                self.instrument.incidentMonitorQuietCountConst,
                self.childHeight*11,
                0
            )
        )

        self.tMonitorQuietCountConstLabel, self.tMonitorQuietCountConstText = (
            makeLabelTextPair(
                self,
                "Transmission monitor quiet count constant",
                self.instrument.transmissionMonitorQuietCountConst,
                self.childHeight*12,
                0
            )
        )

        self.channelNosLabel, self.channelNosText = (
            makeLabelTextPair(
                self,
                "Channel no.s for spike analysis",
                self.instrument.channelNosSpikeAnalysis,
                self.childHeight*13,
                0,
                isIterable=True
            )
        )
        self.spikeAcceptanceFactorLabel, self.spikeAcceptanceFactorText = (
            makeLabelTextPair(
                self,
                "Spike analysis acceptance factor",
                self.instrument.spikeAnalysisAcceptanceFactor,
                self.childHeight*14,
                0
            )
        )

        self.wavelengthRangeLabel, self.wavelengthRangeText = (
            makeLabelTextPair(
                self,
                "Wavelength range and step size",
                [
                    self.instrument.wavelengthMin,
                    self.instrument.wavelengthMax,
                    self.instrument.wavelengthStep
                ],
                self.childHeight*15,
                0,
                isIterable=True
            )
        )

        self.noSmoothsLabel, self.noSmoothsText = (
            makeLabelTextPair(
                self,
                "No. of smooths on monitor",
                self.instrument.NoSmoothsOnMonitor,
                self.childHeight*16,
                0
            )
        )

        self.XRangeLabel, self.XRangeText = (
            makeLabelTextPair(
                self,
                "X range and step size",
                [
                    self.instrument.XMin,
                    self.instrument.XMax,
                    self.instrument.XStep
                ],
                self.childHeight*17,
                0,
                isIterable=True
            )
        )

        self.logarithmicBinningLabel, self.logarithmicBinningCombo = (
            makeLabelComboBoxPair(
                self,
                "Use logarithmic binning?",
                numifyBool(self.instrument.useLogarithmicBinning),
                ["False", "True"],
                self.childHeight*18,
                0
            )
        )

        self.groupsAcceptanceFactorLabel, self.groupsAcceptanceFactorText = (
            makeLabelTextPair(
                self,
                "Groups acceptance factor",
                self.instrument.groupsAcceptanceFactor,
                self.childHeight*19,
                0
            )
        )

        self.mergePowerLabel, self.mergePowerText = (
            makeLabelTextPair(
                self,
                "Merge power",
                self.instrument.mergePower,
                self.childHeight*20,
                0
            )
        )

        self.subAtomScatteringLabel, self.subAtomScatteringCombo = (
            makeLabelComboBoxPair(
                self,
                "Subtract single atom scattering?",
                numifyBool(self.instrument.subSingleAtomScattering),
                ["False", "True"],
                self.childHeight*21,
                0
            )
        )

        self.mergeWeightsLabel, self.mergeWeightsCombo = (
            makeLabelComboBoxPair(
                self,
                "Merge weights by?",
                self.instrument.mergeWeights.value,
                [m.name for m in MergeWeights],
                self.childHeight*22,
                0
            )
        )

        self.incidentFlightPathLabel, self.incidentFlightPathText = (
            makeLabelTextPair(
                self,
                "Incident flight path",
                self.instrument.incidentFlightPath,
                self.childHeight*23,
                0
            )
        )

        self.diagnosticSpectrumLabel, self.diagnosticSpectrumText = (
            makeLabelTextPair(
                self,
                "Spectrum number for output diagnostic files",
                self.instrument.spectrumNumberForOutputDiagnosticFiles,
                self.childHeight*24,
                0
            )
        )

        self.neutronParamsFileNameText, self.neutronParamsFileNameLabel = (
            makeLabelTextPair(
                self,
                "Neutron scattering params file",
                self.instrument.neutronScatteringParametersFile,
                self.childHeight*25,
                0
            )
        )

        self.scaleSelectionText, self.scaleSelectionCombo = (
            makeLabelComboBoxPair(
                self,
                "Scale selection",
                self.instrument.scaleSelection.value,
                [s.name for s in Scales],
                self.childHeight*26,
                0
            )
        )

        self.subWavelengthBinnedLabel, self.subWavelengthBinnedCombo = (
            makeLabelComboBoxPair(
                self,
                "Subtract single atom scattering?",
                numifyBool(self.instrument.subWavelengthBinnedData),
                ["False", "True"],
                self.childHeight*27,
                0
            )
        )

        self.GudrunStartFolderText, self.GudrunStartFolderLabel = (
            makeLabelTextPair(
                self,
                "Gudrun start folder",
                self.instrument.GudrunStartFolder,
                self.childHeight*28,
                0
            )
        )

        self.startupFileLabel, self.startupFileText = (
            makeLabelTextPair(
                self,
                "Gudrun start folder",
                self.instrument.startupFileFolder,
                self.childHeight*29,
                0
            )
        )

        self.logarithmicStepSizeLabel, self.logarithmicStepSizeText = (
            makeLabelTextPair(
                self,
                "Logarithmic step size",
                self.instrument.logarithmicStepSize,
                self.childHeight*30,
                0
            )
        )

        self.hardGroupEdgesLabel, self.hardGroupEdgesText = (
            makeLabelComboBoxPair(
                self,
                "Hard group edges?",
                numifyBool(self.instrument.hardGroupEdges),
                ["False", "True"],
                self.childHeight*31,
                0
            )
        )

    def updateArea(self):

        self.setGeometry(
            self.y,
            0,
            int(self.parent.size().width() * self.relWidth),
            int(self.parent.size().height() * self.relHeight),
        )
