from inspect import cleandoc

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
        scaleSelectionLine = (
            f'{self.scaleSelection}        '
            f'Scale selection: 1 = Q, 2 = d-space,'
            f' 3 = wavelength, 4 = energy, 5 = TOF'
        )

        wavelengthLine = (
            f'{self.wavelengthMin}'
            f'  {self.wavelengthMax}'
            f'  {self.wavelengthStep}'
        )

        if self.useLogarithmicBinning:
            self.XStep = -0.01

        XScaleLine = (
            f'{self.XMin}  {self.XMax}  {self.XStep}'
        )

        if not all(self.groupingParameterPanel):
            return cleandoc(
                str(
                    """
{}        Instrument name
{}        Gudrun input file directory:
{}        Data file directory
{}        Data file type
{}        Detector calibration file name
{}        User table column number for phi values
{}        Groups file name
{}        Deadtime constants file name
{}        Spectrum number(s) for incident beam monitor
{}        Wavelength range [\u212b] for monitor normalisation
{}        Spectrum number(s) for transmission monitor
{}        Incident monitor quiet count constant
{}        Transmission monitor quiet count constant
{}        Channel numbers for spike analysis
{}        Spike analysis acceptance factor
{}        Wavelength range to use [\u212b] and step size
{}        No. of smooths on monitor
{}        Min, Max and step in x-scale (-ve for logarithmic binning)
0  0  0  0          0 0 0 0 to end input of specified values
{}        Groups acceptance factor
{}        Merge power
{}        Substract single atom scattering?
{}        By channel?
{}        Incident flight path [m]
{}        Spectrum number to output diagnostic files
{}        Neutron scattering parameters file
{}
{}        Subtract wavelength-binned data?
{}        Folder where Gudrun started
{}        Folder containing the startup file
{}        Logarithmic step size
{}        Hard group edges?
{}        Number of iterations
{}        Tweak the tweak factor(s)?""".format(
                        self.name,
                        self.GudrunInputFileDir,
                        self.dataFileDir,
                        self.dataFileType,
                        self.detectorCalibrationFileName,
                        self.columnNoPhiVals,
                        self.groupFileName,
                        self.deadtimeConstantsFileName,
                        spacify(self.spectrumNumbersForIncidentBeamMonitor),
                        spacify(
                            self.wavelengthRangeForMonitorNormalisation,
                            num_spaces=2,
                        ),
                        spacify(self.spectrumNumbersForTransmissionMonitor),
                        self.incidentMonitorQuietCountConst,
                        self.transmissionMonitorQuietCountConst,
                        spacify(self.channelNosSpikeAnalysis, num_spaces=2),
                        self.spikeAnalysisAcceptanceFactor,
                        wavelengthLine,
                        self.NoSmoothsOnMonitor,
                        XScaleLine,
                        self.groupsAcceptanceFactor,
                        self.mergePower,
                        numifyBool(self.subSingleAtomScattering),
                        self.byChannel,
                        self.incidentFlightPath,
                        self.spectrumNumberForOutputDiagnosticFiles,
                        self.neutronScatteringParametersFile,
                        scaleSelectionLine,
                        numifyBool(self.subWavelengthBinnedData),
                        self.GudrunStartFolder,
                        self.startupFileFolder,
                        self.logarithmicStepSize,
                        numifyBool(self.hardGroupEdges),
                        self.numberIterations,
                        numifyBool(self.tweakTweakFactors),
                    )
                )
            )
        else:

            return cleandoc(
                str(
                    """
{}        Instrument name
{}        Gudrun input file directory:
{}        Data file directory
{}        Data file type
{}        Detector calibration file name
{}        User table column number for phi values
{}        Groups file name
{}        Deadtime constants file name
{}        Spectrum number(s) for incident beam monitor
{}        Wavelength range [\u212b] for monitor normalisation
{}        Spectrum number(s) for transmission monitor
{}        Incident monitor quiet count constant
{}        Transmission monitor quiet count constant
{}        Channel numbers for spike analysis
{}        Spike analysis acceptance factor
{}        Wavelength range to use [\u212b] and step size
{}        No. of smooths on monitor
{}        Min, Max and step in x-scale (-ve for logarithmic binning)
{}
0  0  0  0          0 0 0 0 to end input of specified values
{}        Groups acceptance factor
{}        Merge power
{}        Substract single atom scattering?
{}        By channel?
{}        Incident flight path [m]
{}        Spectrum number to output diagnostic files
{}        Neutron scattering parameters file
{}
{}        Subtract wavelength-binned data?
{}        Folder where Gudrun started
{}        Folder containing the startup file
{}        Logarithmic step size
{}        Hard group edges?
{}        Number of iterations
{}        Tweak the tweak factor(s)?""".format(
                        self.name,
                        self.GudrunInputFileDir,
                        self.dataFileDir,
                        self.dataFileType,
                        self.detectorCalibrationFileName,
                        self.columnNoPhiVals,
                        self.groupFileName,
                        self.deadtimeConstantsFileName,
                        spacify(self.spectrumNumbersForIncidentBeamMonitor),
                        spacify(
                            self.wavelengthRangeForMonitorNormalisation,
                            num_spaces=2,
                        ),
                        spacify(self.spectrumNumbersForTransmissionMonitor),
                        self.incidentMonitorQuietCountConst,
                        self.transmissionMonitorQuietCountConst,
                        spacify(self.channelNosSpikeAnalysis, num_spaces=2),
                        self.spikeAnalysisAcceptanceFactor,
                        wavelengthLine,
                        self.NoSmoothsOnMonitor,
                        XScaleLine,
                        ""
                        if not all(self.groupingParameterPanel)
                        else cleandoc((
                            spacify(self.groupingParameterPanel),
                            """        Group, Xmin, Xmax, Background factor"""
                        )),
                        self.groupsAcceptanceFactor,
                        self.mergePower,
                        numifyBool(self.subSingleAtomScattering),
                        self.byChannel,
                        self.incidentFlightPath,
                        self.spectrumNumberForOutputDiagnosticFiles,
                        self.neutronScatteringParametersFile,
                        scaleSelectionLine,
                        numifyBool(self.subWavelengthBinnedData),
                        self.GudrunStartFolder,
                        self.startupFileFolder,
                        self.logarithmicStepSize,
                        numifyBool(self.hardGroupEdges),
                        self.numberIterations,
                        numifyBool(self.tweakTweakFactors),
                    )
                )
            )
