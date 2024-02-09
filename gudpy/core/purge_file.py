import os

from core.enums import Instruments
from core.utils import spacify, numifyBool
from core import config

SUFFIX = ".exe" if os.name == "nt" else ""


class PurgeFile:
    """
    Class to represent a PurgeFile.

    ...

    Attributes
    ----------
    gudrunFile : GudrunFile
        Parent GudrunFile that we are creating the PurgeFile from.
    excludeSampleAndCan : bool
        Exclude sample and container data files?
    standardDeviation : tuple(int, int)
         Stores the number of std deviations allowed above and below
         the mean ratio and the range of std's allowed around the mean
         standard deviation.
    ignoreBad : bool
        Ignore any existing bad spectrum files (spec.bad, spec.dat)?
    Methods
    -------
    write_out()
        Writes out the string representation of the PurgeFile to purge_det.dat
    purge()
        Writes out the file, and then calls purge_det on that file.
    """

    def __init__(
            self,
            gudrunFile,
            standardDeviation=(10, 10),
            ignoreBad=True,
            excludeSampleAndCan=True,
    ):
        """
        Constructs all the necessary attributes for the PurgeFile object.

        Parameters
        ----------
        gudrunFile : GudrunFile
            Parent GudrunFile that we are creating the PurgeFile from.
        """
        self.gudrunFile = gudrunFile
        self.excludeSampleAndCan = excludeSampleAndCan
        self.standardDeviation = standardDeviation
        self.ignoreBad = ignoreBad

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

        instrumentLine = Instruments(
            self.gudrunFile.instrument.name.value
        ).name

        detCalibrationFileLine = os.path.join(
            baseDirectory,
            self.gudrunFile.instrument.detectorCalibrationFileName
        )

        groupFileLine = os.path.join(
            baseDirectory,
            self.gudrunFile.instrument.groupFileName
        )

        spectrumNumbersLine = spacify(
            self.gudrunFile.instrument.spectrumNumbersForIncidentBeamMonitor
        )

        channelNosLine = spacify(
            self.gudrunFile.instrument.channelNosSpikeAnalysis, num_spaces=2
        )

        groupsAcceptanceFactorLine = (
            self.gudrunFile.instrument.groupsAcceptanceFactor
        )

        nxsDefinitionFilePath = os.path.join(
            baseDirectory,
            self.gudrunFile.instrument.nxsDefinitionFile
        )

        nxsDefinitionFileLine = (
            f"{nxsDefinitionFilePath}{config.spc10}"
            f"NeXus definition file\n"
            if self.gudrunFile.instrument.dataFileType in ["nxs", "NXS"]
            else
            ""
        )

        normalisationDataFiles = [
            f"{df}{config.spc2}{self.gudrunFile.normalisation.periodNumber}"
            f"{config.spc10}"
            for df in self.gudrunFile.normalisation.dataFiles
        ]

        normalisationDataFilesBg = [
            f"{df}{config.spc2}{self.gudrunFile.normalisation.periodNumberBg}"
            f"{config.spc10}"
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
                f"{df}{config.spc2}{sample.periodNumber}"
                for sampleBackground in self.gudrunFile.sampleBackgrounds
                for sample in sampleBackground.samples
                for df in sample.dataFiles
                if sample.runThisSample
            ]

        if self.excludeSampleAndCan:
            containerDataFiles = []
        else:
            containerDataFiles = [
                f"{df}{config.spc2}{container.periodNumber}"
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
            f'{instrumentLine}{config.spc10}'
            f'Instrument name\n'
            f'{self.gudrunFile.instrument.GudrunInputFileDir}{config.spc10}'
            f'Gudrun input file directory:\n'
            f'{self.gudrunFile.instrument.dataFileDir}{config.spc10}'
            f'Data file directory\n'
            f'{detCalibrationFileLine}{config.spc10}'
            f'Detector calibration file name\n'
            f'{groupFileLine}{config.spc10}'
            f'Groups file name\n'
            f'{spectrumNumbersLine}{config.spc10}'
            f'Spectrum number(s) for incident beam monitor\n'
            f'{channelNosLine}{config.spc10}'
            f'Channel numbers for spike analysis\n'
            f'{groupsAcceptanceFactorLine}{config.spc10}'
            f'Spike analysis acceptance factor\n'
            f'{nxsDefinitionFileLine}'
            f'{spacify(self.standardDeviation, num_spaces=2)}{config.spc10}'
            f'Specify the number of standard deviations allowed'
            f' above and below the mean ratio.'
            f' Specify the range of std\'s allowed'
            f' around the mean standard deviation.\n'
            f'{numifyBool(self.ignoreBad)}{config.spc10}'
            f'Ignore any existing bad spectrum and spike files'
            f' (spec.bad, spike.dat)?\n'
            f'{dataFilesLines}'
        )
