try:
    from utils import spacify, numifyBool
except ModuleNotFoundError:
    from scripts.utils import spacify, numifyBool


class Instrument:
    def __init__(self):
        self.name = ""
        self.GudrunInputFileDir = ""
        self.dataFileDir = ""
        self.dataFileType = ""
        self.detectorCalibrationFileName = ""
        self.columnNoPhiVals = 0
        self.groupFileName = ""
        self.deadtimeConstantsFileName = ""
        self.spectrumNumbersForIncidentBeamMonitor = []
        self.wavelengthRangeForMonitorNormalisation = (0, 0)
        self.spectrumNumbersForTransmissionMonitor = []
        self.incidentMonitorQuietCountConst = 0.0
        self.transmissionMonitorQuietCountConst = 0.0
        self.channelNosSpikeAnalysis = (0, 0)
        self.spikeAnalysisAcceptanceFactor = 0
        self.wavelengthMin = 0.
        self.wavelengthMax = 0.
        self.wavelengthStep = 0.
        self.NoSmoothsOnMonitor = 0
        self.XMin = 0.
        self.XMax = 0.
        self.XStep = 0.
        self.useLogarithmicBinning = False
        self.groupingParameterPanel = (0, 0.0, 0.0, 0.0)
        self.groupsAcceptanceFactor = 0.0
        self.mergePower = 0
        self.subSingleAtomScattering = False
        self.byChannel = 0
        self.incidentFlightPath = 0.0
        self.spectrumNumberForOutputDiagnosticFiles = 0
        self.neutronScatteringParametersFile = ""
        self.scaleSelection = 0
        self.subWavelengthBinnedData = False
        self.GudrunStartFolder = ""
        self.startupFileFolder = ""
        self.logarithmicStepSize = 0.0
        self.hardGroupEdges = False
        self.numberIterations = 0
        self.tweakTweakFactors = False

    def __str__(self):
        TAB = "          "

        wavelengthLineA = spacify(
            self.wavelengthRangeForMonitorNormalisation,
            num_spaces=2
        )

        channelNosLine = spacify(
            self.channelNosSpikeAnalysis,
            num_spaces=2
        )

        wavelengthLineB = (
            f'{self.wavelengthMin}'
            f'  {self.wavelengthMax}'
            f'  {self.wavelengthStep}'
        )

        if self.useLogarithmicBinning:
            self.XStep = -0.01

        XScaleLine = (
            f'{self.XMin}  {self.XMax}  {self.XStep}'
        )

        groupingParameterPanelLine = (
            f'{spacify(self.groupingParameterPanel)}{TAB}'
            f'Group, Xmin, Xmax, Background factor\n'
            f'0  0  0  0{TAB}0 0 0 0 to end input of specified values\n'
            if all(self.groupingParameterPanel)
            else
            f'0  0  0  0{TAB}0 0 0 0 to end input of specified values\n'
        )

        scaleSelectionLine = (
            f'{self.scaleSelection}        '
            f'Scale selection: 1 = Q, 2 = d-space,'
            f' 3 = wavelength, 4 = energy, 5 = TOF\n'
        )

        return (
            f'{self.name}{TAB}'
            f'Instrument name\n'
            f'{self.GudrunInputFileDir}{TAB}'
            f'Gudrun input file directory:\n'
            f'{self.dataFileDir}{TAB}'
            f'Data file directory\n'
            f'{self.dataFileType}{TAB}'
            f'Data file type\n'
            f'{self.detectorCalibrationFileName}{TAB}'
            f'Detector calibration file name\n'
            f'{self.columnNoPhiVals}{TAB}'
            f'User table column number for phi values\n'
            f'{self.groupFileName}{TAB}'
            f'Groups file name\n'
            f'{self.deadtimeConstantsFileName}{TAB}'
            f'Deadtime constants file name\n'
            f'{spacify(self.spectrumNumbersForIncidentBeamMonitor)}{TAB}'
            f'Spectrum number(s) for incident beam monitor\n'
            f'{wavelengthLineA}{TAB}'
            f'Wavelength range [\u212b] for monitor normalisation\n'
            f'{spacify(self.spectrumNumbersForTransmissionMonitor)}{TAB}'
            f'Spectrum number(s) for transmission monitor\n'
            f'{self.incidentMonitorQuietCountConst}{TAB}'
            f'Incident monitor quiet count constant\n'
            f'{self.transmissionMonitorQuietCountConst}{TAB}'
            f'Transmission monitor quiet count constant\n'
            f'{channelNosLine}{TAB}'
            f'Channel numbers for spike analysis\n'
            f'{self.spikeAnalysisAcceptanceFactor}{TAB}'
            f'Spike analysis acceptance factor\n'
            f'{wavelengthLineB}{TAB}'
            f'Wavelength range to use [\u212b] and step size\n'
            f'{self.NoSmoothsOnMonitor}{TAB}'
            f'No. of smooths on monitor\n'
            f'{XScaleLine}{TAB}'
            f'Min, Max and step in x-scale (-ve for logarithmic binning)\n'
            f'{groupingParameterPanelLine}'
            f'{self.groupsAcceptanceFactor}{TAB}'
            f'Groups acceptance factor\n'
            f'{self.mergePower}{TAB}'
            f'Merge power\n'
            f'{numifyBool(self.subSingleAtomScattering)}{TAB}'
            f'Substract single atom scattering?\n'
            f'{self.byChannel}{TAB}'
            f'By channel?\n'
            f'{self.incidentFlightPath}{TAB}'
            f'Incident flight path [m]\n'
            f'{self.spectrumNumberForOutputDiagnosticFiles}{TAB}'
            f'Spectrum number to output diagnostic files\n'
            f'{self.neutronScatteringParametersFile}{TAB}'
            f'Neutron scattering parameters file\n'
            f'{scaleSelectionLine}'
            f'{numifyBool(self.subWavelengthBinnedData)}{TAB}'
            f'Subtract wavelength-binned data?\n'
            f'{self.GudrunStartFolder}{TAB}'
            f'Folder where Gudrun started\n'
            f'{self.startupFileFolder}{TAB}'
            f'Folder containing the startup file\n'
            f'{self.logarithmicStepSize}{TAB}'
            f'Logarithmic step size\n'
            f'{numifyBool(self.hardGroupEdges)}{TAB}'
            f'Hard group edges?\n'
            f'{self.numberIterations}{TAB}'
            f'Number of iterations\n'
            f'{numifyBool(self.tweakTweakFactors)}{TAB}'
            f'Tweak the tweak factor(s)?'
        )
