import os
import sys
import subprocess

from PySide6.QtCore import QProcess
from core.enums import Instruments
from core.utils import resolve, spacify, numifyBool
from core import config

SUFFIX = ".exe" if os.name == "nt" else ""


class PurgeFile():
    """
    Class to represent a PurgeFile.

    ...

    Attributes
    ----------
    gudrunFile : GudrunFile
        Parent GudrunFile that we are creating the PurgeFile from.
    excludeSampleAndCan : bool
        Exclude sample and container data files?
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
    collectGudrunFileAttributes()
        Collects the attributes needed for the purge file.
    write_out()
        Writes out the string representation of the PurgeFile to purge_det.dat
    purge()
        Writes out the file, and then calls purge_det on that file.
    """
    def __init__(
            self,
            gudrunFile
    ):
        """
        Constructs all the necessary attributes for the PurgeFile object.

        Parameters
        ----------
        gudrunFile : GudrunFile
            Parent GudrunFile that we are creating the PurgeFile from.
        """
        self.gudrunFile = gudrunFile
        self.excludeSampleAndCan = True
        self.standardDeviation = (10, 10)
        self.ignoreBad = True

    def write_out(self, path=""):
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
        if not path:
            f = open("purge_det.dat", "w", encoding="utf-8")
            f.write(str(self))
        else:
            f = open(path, "w", encoding="utf-8")
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
        HEADER = f"'  '  '          '  '{os.path.sep}'\n\n"

        baseDirectory = self.gudrunFile.instrument.GudrunStartFolder

        nxsDefinitionFilePath = os.path.join(baseDirectory, self.gudrunFile.instrument.nxsDefinitionFile)
        nxsDefinitionFileLine = (
            f"{nxsDefinitionFilePath}{config.spc5}"
            f"NeXus definition file\n"
            if self.gudrunFile.instrument.dataFileType in ["nxs", "NXS"]
            else
            ""
        )

        normalisationDataFiles = [
            f"{df}{config.spc2}{self.gudrunFile.normalisation.periodNumber}{config.spc5}"
            for df in self.gudrunFile.normalisation.dataFiles
        ]

        normalisationDataFilesBg = [
            f"{df}{config.spc2}{self.gudrunFile.normalisation.periodNumberBg}{config.spc5}"
            for df in self.gudrunFile.normalisation.dataFilesBg
        ]

        sampleBackgroundDataFiles = [
            f"{df}{config.spc2}{sampleBackground.periodNumber}"
            for sampleBackground in self.gudrunFile.sampleBackgrounds
            for df in sampleBackground.dataFiles
        ]

        if self.excludeSampleAndCan:
            sampleDataFiles = []
        else:
            sampleDataFiles = [
                f"{df}{config.spc2}{sample.periodNo}"
                for sampleBackground in self.gudrunFile.sampleBackgrounds
                for sample in sampleBackground.samples
                for df in sample.dataFiles
                if sample.runThisSample
            ]

        if self.excludeSampleAndCan:
            containerDataFiles = []
        else:
            containerDataFiles = [
                f"{df}{config.spc2}{container.periodNo}"
                for sampleBackground in self.gudrunFile.sampleBackgrounds
                for sample in sampleBackground.samples
                for container in sample.containers
                for df in container.dataFiles
                if sample.runThisSample
            ]

        dataFilesLines = (
            f"{chr(10).join(normalisationDataFiles)}"
            f"{chr(10) if len(normalisationDataFiles) else ''}"
            f"{chr(10).join(normalisationDataFilesBg)}"
            f"{chr(10) if len(normalisationDataFilesBg) else ''}"  
            f"{chr(10).join(sampleBackgroundDataFiles)}"
            f"{chr(10) if len(sampleBackgroundDataFiles) else ''}"
            f"{chr(10).join(sampleDataFiles)}"
            f"{chr(10) if len(sampleDataFiles) else ''}"
            f"{chr(10).join(containerDataFiles)}"
        )

        return (
            f'{HEADER}'
            f'{Instruments(self.gudrunFile.instrument.name.value).name}{config.spc5}'
            f'Instrument name\n'
            f'{self.gudrunFile.instrument.GudrunInputFileDir}{config.spc5}'
            f'Gudrun input file directory:\n'
            f'{self.gudrunFile.instrument.dataFileDir}{config.spc5}'
            f'Data file directory\n'
            f'{os.path.join(baseDirectory, self.gudrunFile.instrument.detectorCalibrationFileName)}{config.spc5}'
            f'Detector calibration file name\n'
            f'{os.path.join(baseDirectory, self.gudrunFile.instrument.groupFileName)}{config.spc5}'
            f'Groups file name\n'
            f'{spacify(self.gudrunFile.instrument.spectrumNumbersForIncidentBeamMonitor)}{config.spc5}'
            f'Spectrum number(s) for incident beam monitor\n'
            f'{spacify(self.gudrunFile.instrument.channelNosSpikeAnalysis, num_spaces=2)}{config.spc5}'
            f'Channel numbers for spike analysis\n'
            f'{self.gudrunFile.instrument.groupsAcceptanceFactor}{config.spc5}'
            f'Spike analysis acceptance factor\n'
            f'{nxsDefinitionFileLine}'
            f'{spacify(self.standardDeviation, num_spaces=2)}{config.spc5}'
            f'Specify the number of standard deviations allowed'
            f' above and below the mean ratio.'
            f' Specify the range of std\'s allowed'
            f' around the mean standard deviation.\n'
            f'{numifyBool(self.ignoreBad)}{config.spc5}'
            f'Ignore any existing bad spectrum and spike files'
            f' (spec.bad, spike.dat)?\n'
            f'{dataFilesLines}'
        )

    def purge(
        self,
        standardDeviation=(10, 10),
        ignoreBad=True,
        excludeSampleAndCan=True,
        headless=True
    ):
        """
        Write out the current state of the PurgeFile, then
        purge detectors by calling purge_det on that file.

        Parameters
        ----------
        standardDeviation: tuple(int, int), optional
            Number of std deviations allowed above and below
            the mean ratio and the range of std's allowed around the mean
            standard deviation. Default is (10, 10)
        ignoreBad : bool, optional
            Ignore any existing bad spectrum files (spec.bad, spec.dat)?
            Default is True.
        excludeSampleAndCan : bool, optional
            Exclude sample and container data files?
        headless : bool
            Should headless mode be used?
        Returns
        -------
        subprocess.CompletedProcess
            The result of calling purge_det using subprocess.run.
            Can access stdout/stderr from this.
        """
        self.standardDeviation = standardDeviation
        self.ignoreBad = ignoreBad
        self.excludeSampleAndCan = excludeSampleAndCan
        if headless:
            try:
                cwd = os.getcwd()
                purge_det = resolve("bin", f"purge_det{SUFFIX}")
                os.chdir(self.gudrunFile.instrument.GudrunInputFileDir)
                self.write_out()
                result = subprocess.run(
                    [purge_det, "purge_det.dat"],
                    capture_output=True,
                    text=True
                )
                os.chdir(cwd)
            except FileNotFoundError:
                return False
            return result
        else:
            if hasattr(sys, '_MEIPASS'):
                purge_det = os.path.join(sys._MEIPASS, f"purge_det{SUFFIX}")
            else:
                purge_det = resolve(
                    os.path.join(
                        config.__rootdir__, "bin"
                    ), f"purge_det{SUFFIX}"
                )
            if not os.path.exists(purge_det):
                return FileNotFoundError()
            proc = QProcess()
            proc.setProgram(purge_det)
            proc.setArguments([])
            return (
                proc,
                self.write_out,
                [
                    os.path.join(
                        self.gudrunFile.instrument.GudrunInputFileDir,
                        "purge_det.dat"
                    )
                ]
            )
