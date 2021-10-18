from src.scripts.utils import spacify, numifyBool, bjoin
from src.gudrun_classes.enums import MergeWeights, Scales, Instruments
import os
import sys


class Instrument:
    """
    Class to represent an Instrument.

    ...

    Attributes
    ----------
    name : Instrument
        Name of the instrument.
    GudrunInputFileDir : str
        Input file directory for Gudrun.
    dataFileDir : str
        Data file directory.
    dataFileType : str
        Type of files stored in dataFileDir.
    detectorCalibrationFileName : str
        Filename used for detector calibration.
    columnNoPhiVals : int
        User table column number for phi values
    groupFileName : str
        Name of detector groups file to read from.
    deadtimeConstantsFileName : str
        Name of file containing detector,
        module and data acquisition dead times.
    spectrumNumbersForIncidentBeamMonitor : int[]
        Number of spectra of incident beam monitor.
    wavelengthRangeForMonitorNormalisation : tuple(float, float)
        Input wavelength range for monitor normalisation.
        0 0 signals to divide channel by channel.
    spectrumNumbersForTransmissionMonitor : int[]
        Transmission monitor spectrum numbers
    incidentMonitorQuietCountConst : float
        Quiet count constant for incident beam monitor.
    transmissionMonitorQuietCountConst : float
        Quiet count constant for transmission beam monitor.
    channelNosSpikeAnalysis : tuple(int, int)
        First and last channel numbers to check for spikes.
        0 0 signals to use all channels.
    spikeAnalysisAcceptanceFactor : float
        Acceptance factor for spike analysis.
    wavelengthMin : float
        Minimum incident wavelength.
    wavelengthMax : float
        Maximum incident wavelength.
    wavelengthStep : float
        Wavelength step size for corrections.
    NoSmoothsOnMonitor : int
        Number of smoothings for monitor and Vanadium.
    XMin : float
        Minimum X for final merged data.
    XMax : float
        Maxmimum X for final merged data.
    XStep : float
        Step size for corrections.
        Negative means logarithmic binning above XMin.
    useLogarithmicBinning : bool
        Should logarithmic binning be used?
    groupingParameterPanel : tuples[]
        List of tuples which indicate that groups have special X-ranges.
    groupsAcceptanceFactor : float
        Acceptance factor for final merge.
        1.0 indicates all groups are accepted.
    mergePower : int
        Power used to set X-weighting for merge.
    subSingleAtomScattering : bool
        Should we subtract a background from each group prior to merge?
    mergeWeights : int
        0 = None
        1 = By detector
        2 = By channel
    incidentFlightPath : float
        Incident flight path.
    spectrumNumberForOutputDiagnosticFiles : int
        Spectrum number for diagnostic files.
        <=0 means no diagnostic files are written.
    neutronScatteringParametersFile : str
        Name of file which contains neutron scattering lengths.
    scaleSelection : int
        Indicates the units/scale for final outputs.
        1 = Q [1/Angstrom], 2 = d-space [Angstrom],
        3 = wavelength [Angstrom], 4 = energy [meV],
        5 = TOF [musec]
    subWavelengthBinnedData : bool
        Should we subtract wavelength data prior to merge?
    GudrunStartFolder : str
        Default folder for calibration, groups and other files,
        to be used if they have not been specified.
    startupFileFolder : str
        Location of instrument specific files.
    logarithmicStepSize : float
        Power to be used to increment the step size.
        Will be set to 0.0, if XStep > 0.
    hardGroupEdges : bool
        Should hard group edges be used?
    nxsDefinitionFile : str
        NeXus definition file to be used, if NeXus files are being used.
    numberIterations : int
        Number of iterations (may be obsolete).
    tweakTweakFactors : bool
        Should the tweak factors be tweaked? (may be obsolete).
    Methods
    -------
    """

    def __init__(self):
        """
        Constructs all the necessary attributes for the Instrument object.

        Parameters
        ----------
        None
        """
        self.name = Instruments.NIMROD
        self.GudrunInputFileDir = ""
        self.dataFileDir = ""
        self.dataFileType = ""
        self.detectorCalibrationFileName = ""
        self.columnNoPhiVals = 0
        self.groupFileName = ""
        self.deadtimeConstantsFileName = ""
        self.spectrumNumbersForIncidentBeamMonitor = []
        self.wavelengthRangeForMonitorNormalisation = (0., 0.)
        self.spectrumNumbersForTransmissionMonitor = []
        self.incidentMonitorQuietCountConst = 0.0
        self.transmissionMonitorQuietCountConst = 0.0
        self.channelNosSpikeAnalysis = (0, 0)
        self.spikeAnalysisAcceptanceFactor = 0.0
        self.wavelengthMin = 0.
        self.wavelengthMax = 0.
        self.wavelengthStep = 0.
        self.NoSmoothsOnMonitor = 0
        self.XMin = 0.
        self.XMax = 0.
        self.XStep = 0.
        self.useLogarithmicBinning = False
        self.groupingParameterPanel = []
        self.groupsAcceptanceFactor = 1.0
        self.mergePower = 0
        self.subSingleAtomScattering = False
        self.mergeWeights = MergeWeights.CHANNEL
        self.incidentFlightPath = 0.0
        self.spectrumNumberForOutputDiagnosticFiles = 0
        self.neutronScatteringParametersFile = ""
        self.scaleSelection = Scales.Q
        self.subWavelengthBinnedData = False
        self.GudrunStartFolder = (
            "bin" if not hasattr(sys, "_MEIPASS")
            else os.path.join(sys._MEIPASS, "bin")
        )
        self.startupFileFolder = "StartupFiles"
        self.logarithmicStepSize = 0.0
        self.hardGroupEdges = False
        self.nxsDefinitionFile = ""
        self.numberIterations = 0
        self.tweakTweakFactors = False

    def __str__(self):
        """
        Returns the string representation of the Instrument object.

        Parameters
        ----------
        None

        Returns
        -------
        string : str
            String representation of Instrument.
        """
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

        XScaleLine = (
            f'{self.XMin}  {self.XMax}  -0.01'
            if self.useLogarithmicBinning
            else
            f'{self.XMin}  {self.XMax}  {self.XStep}'
        )

        joined = bjoin(
            self.groupingParameterPanel,
            " Group, Xmin, Xmax, Background factor\n",
            sameseps=True
        )
        groupingParameterPanelLine = (
            f'{joined}'
            f'0  0  0  0{TAB}0 0 0 0 to end input of specified values\n'
        )

        if self.mergeWeights == MergeWeights.NONE:
            mergeBy = "Merge weights: None?"
        elif self.mergeWeights == MergeWeights.DETECTOR:
            mergeBy = "By detector?"
        elif self.mergeWeights == MergeWeights.CHANNEL:
            mergeBy = "By channel?"

        mergeWeightsLine = (
            f'{self.mergeWeights.value}{TAB}'
            f'{mergeBy}\n'
        )

        scaleSelectionLine = (
            f'{self.scaleSelection.value}        '
            f'Scale selection: 1 = Q, 2 = d-space,'
            f' 3 = wavelength, 4 = energy, 5 = TOF\n'
        )

        nexusDefinitionLine = (
            f'{self.nxsDefinitionFile}{TAB}'
            f'NeXus definition file\n'
            if self.nxsDefinitionFile
            else
            ""
        )

        return (
            f'{Instruments(self.name.value).name}{TAB}'
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
            f'{mergeWeightsLine}'
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
            f'{nexusDefinitionLine}'
            f'{self.numberIterations}{TAB}'
            f'Number of iterations\n'
            f'{numifyBool(self.tweakTweakFactors)}{TAB}'
            f'Tweak the tweak factor(s)?'
        )
