import os
import sys
import subprocess
try:
    sys.path.insert(1, os.path.join(sys.path[0], "../scripts"))
    from utils import spacify, numifyBool
except ModuleNotFoundError:
    sys.path.insert(1, os.path.join(sys.path[0], "scripts"))
    from scripts.utils import spacify, numifyBool


class PurgeFile():
    """
    Class to represent a PurgeFile.

    ...

    Attributes
    ----------
    gudrunFile : GudrunFile
        Parent GudrunFile that we are creating the PurgeFile from.
    instrumentName : str
        Name of the instrument.
    inputFileDir : str
        Input file directory for Gudrun.
    dataFileDir : str
        Data file directory.
    dataFileType : str
        Type of files stored in dataFileDir.
    detCalibFile : str
        Filename used for detector calibration.
    groupsFile : str
        Name of detector groups file to read from.
    spectrumNumbers : int[]
        Number of spectra of incident beam monitor.
    channelNumbers : tuple(int, int)
        First and last channel numbers to check for spikes.
        0 0 signals to use all channels.
    acceptanceFactor : int
        Acceptance factor for spike analysis.
    standardDeviation : tuple(int, int)
         Stores the number of std deviations allowed above and below
         the mean ratio and the range of std's allowed around the mean
         standard deviation.
    ignoreBad : bool
        Ignore any existing bad spectrum files (spec.bad, spec.dat)?
    normalisationPeriodNo : int
        Period number for normalisation data files.
    normalisationPeriodNoBg : int
        Period number for normalisation background data files.
    normalisationDataFiles : str
        String representation of all normalisation data files,
        and their period numbers.
    normalisationBackgroundDataFiles : str
        String representation of all background normalisation data files,
        and their period numbers.
    sampleBackgroundDataFiles : str
        String representation of all sample background data files,
        and their period numbers.
    sampleDataFiles : str
        String representation of all sample data files,
        and their period numbers.
    containerDataFiles : str
        String representation of all containers data files,
        and their period numbers.
    Methods
    -------
    write_out()
        Writes out the string representation of the PurgeFile to purge_det.dat
    purge()
        Writes out the file, and then calls purge_det on that file.
    """
    def __init__(
            self, gudrunFile, standardDeviation=(10, 10), ignoreBad=True):
        """
        Constructs all the necessary attributes for the PurgeFile object.

        Parameters
        ----------
        gudrunFile : GudrunFile
            Parent GudrunFile that we are creating the PurgeFile from.
        standardDeviation: tuple(int, int), optional
            Number of std deviations allowed above and below
            the mean ratio and the range of std's allowed around the mean
            standard deviation. Default is (10, 10)
        ignoreBad : bool
            Ignore any existing bad spectrum files (spec.bad, spec.dat)?
            Default is True.
        """
        self.gudrunFile = gudrunFile

        # Extract relevant attributes from the GudrunFile object.
        self.instrumentName = gudrunFile.instrument.name
        self.inputFileDir = gudrunFile.instrument.GudrunInputFileDir
        self.dataFileDir = gudrunFile.instrument.dataFileDir
        self.detCalibFile = gudrunFile.instrument.detectorCalibrationFileName
        self.groupsFile = gudrunFile.instrument.groupFileName
        self.spectrumNumbers = (
            gudrunFile.instrument.spectrumNumbersForIncidentBeamMonitor
        )
        self.channelNumbers = (
            gudrunFile.instrument.channelNosSpikeAnalysis
        )
        self.acceptanceFactor = (
            gudrunFile.instrument.spikeAnalysisAcceptanceFactor
        )
        self.standardDeviation = standardDeviation
        self.ignoreBad = ignoreBad
        self.normalisationPeriodNo = (
            self.gudrunFile.normalisation.numberOfFilesPeriodNumber[1]
        )
        self.normalisationPeriodNoBg = (
            self.gudrunFile.normalisation.numberOfFilesPeriodNumberBg[1]
        )

        # Collect data files as strings of the format:
        # {name} {period number}
        # do this for normalisation, normalisation background,
        # sample background, sample and container data files.
        # insert eight space 'tab' after each period number,
        # for consistency with original Gudrun code.

        TAB = "          "
        self.normalisationDataFiles = ""
        self.normalisationBackgroundDataFiles = ""

        # Iterate through normalisation and normalisation background
        # data files, appending their string representation with
        # period number to the relevant string.
        for dataFile in self.gudrunFile.normalisation.dataFiles.dataFiles:
            self.normalisationDataFiles += (
                dataFile + "  " + str(self.normalisationPeriodNo) + TAB + "\n"
            )
        for dataFile in self.gudrunFile.normalisation.dataFilesBg.dataFiles:
            self.normalisationBackgroundDataFiles += (
                dataFile + "  " + str(self.normalisationPeriodNoBg)
                + TAB + "\n"
            )
        self.sampleBackgroundDataFiles = ""
        self.sampleDataFiles = ""
        self.containerDataFiles = ""

        # Iterate through sample backgrounds, samples and containers
        # data files, appending their string representation with
        # period number to the relevant string
        # only append samples and their containers, if
        # the sample is set to run.
        for sampleBackground in self.gudrunFile.sampleBackgrounds:
            periodNumber = sampleBackground.numberOfFilesPeriodNumber[1]
            for dataFile in sampleBackground.dataFiles.dataFiles:
                self.sampleBackgroundDataFiles += (
                    dataFile + "  " + str(periodNumber) + TAB + "\n"
                )
            for sample in [
                x
                for x in sampleBackground.samples
                if x.runThisSample
                    ]:
                periodNumber = sample.numberOfFilesPeriodNumber[1]
                for dataFile in sample.dataFiles.dataFiles:
                    self.sampleDataFiles += (
                        dataFile + "  " + str(periodNumber) + TAB + "\n"
                    )
                for container in sample.containers:
                    periodNumber = container.numberOfFilesPeriodNumber[1]
                    for dataFile in container.dataFiles.dataFiles:
                        self.containerDataFiles += (
                            dataFile + "  " + str(periodNumber) + TAB + "\n"
                        )

    def write_out(self):
        """
        Writes out the string representation of the PurgeFile to
        purge_det.dat.

        Parameters
        ----------
        None
        Returns
        -------
        None
        """
        # Write out the string representation of the PurgeFile
        # To purge_det.dat.
        f = open("purge_det.dat", "w", encoding="utf-8")
        f.write(str(self))
        f.close()

    def __str__(self):
        """
        Returns the string representation of the PurgeFile object.

        Parameters
        ----------
        None

        Returns
        -------
        string : str
            String representation of PurgeFile.
        """
        HEADER = "'  '  '          '  '/'\n\n"
        TAB = "          "
        return (
            f'{HEADER}'
            f'{self.instrumentName}{TAB}'
            f'Instrument name\n'
            f'{self.inputFileDir}{TAB}'
            f'Gudrun input file directory:\n'
            f'{self.dataFileDir}{TAB}'
            f'Data file directory\n'
            f'{self.detCalibFile}{TAB}'
            f'Detector calibration file name\n'
            f'{self.groupsFile}{TAB}'
            f'Groups file name\n'
            f'{spacify(self.spectrumNumbers)}{TAB}'
            f'Spectrum number(s) for incident beam monitor\n'
            f'{spacify(self.channelNumbers, num_spaces=2)}{TAB}'
            f'Channel numbers for spike analysis\n'
            f'{self.acceptanceFactor}{TAB}'
            f'Spike analysis acceptance factor\n'
            f'{spacify(self.standardDeviation, num_spaces=2)}{TAB}'
            f'Specify the number of standard deviations allowed'
            f' above and below the mean ratio.'
            f' Specify the range of std\'s allowed'
            f' around the mean standard deviation.\n'
            f'{numifyBool(self.ignoreBad)}{TAB}'
            f'Ignore any existing bad spectrum and spike files'
            f' (spec.bad, spike.dat)?\n'
            f'{self.normalisationDataFiles}'
            f'{self.normalisationBackgroundDataFiles}'
            f'{self.sampleBackgroundDataFiles}'
            f'{self.sampleDataFiles}'
            f'{self.containerDataFiles}'
        )

    def purge(self):
        """
        Write out the current state of the PurgeFile, then
        purge detectors by calling purge_det on that file.

        Parameters
        ----------
        None
        Returns
        -------
        subprocess.CompletedProcess
            The result of calling purge_det using subprocess.run.
            Can access stdout/stderr from this.
        """
        self.write_out()
        try:
            result = subprocess.run(
                ["bin/purge_det", "purge_det.dat"],
                capture_output=True,
                text=True
            )
        except FileNotFoundError:
            # FileNotFoundError probably means that GudPy is being
            # run as an executable.
            # So prepend sys._MEIPASS to the path to purge_det.
            purge_det = sys._MEIPASS + os.sep + "purge_det"
            result = subprocess.run(
                [purge_det, "purge_det.dat"], capture_output=True, text=True
            )
        return result
