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

    def __init__(self, gudrunFile, standardDeviation=(10.0, 10.0), ignoreBad=True):
        
        self.gudrunFile = gudrunFile
        self.instrumentName = gudrunFile.instrument.name
        self.inputFileDir = gudrunFile.instrument.GudrunInputFileDir
        self.dataFileDir = gudrunFile.instrument.dataFileDir
        self.detCalibFile = os.path.abspath(gudrunFile.instrument.detectorCalibrationFileName)
        self.groupsFile = os.path.abspath(gudrunFile.instrument.groupFileName)
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
        self.ignoreBad  = ignoreBad
        self.normalisationPeriodNo = (
            self.gudrunFile.normalisation.numberOfFilesPeriodNumber[1]
        )
        self.sampleBackgroundDataFiles = ""
        self.sampleDataFiles = ""
        self.containerDataFiles = ""
        for sampleBackground in self.gudrunFile.sampleBackgrounds:
            periodNumber = sampleBackground.numberOfFilesPeriodNumber[1]
            for dataFile in sampleBackground.dataFiles.dataFiles:
                self.sampleBackgroundDataFiles+= (
                    dataFile + "  " + str(periodNumber) + "\n"
                )
            for sample in sampleBackground.samples:
                periodNumber = sample.numberOfFilesPeriodNumber[1]
                for dataFile in sample.dataFiles.dataFiles:
                    self.sampleDataFiles+= (
                        dataFile + "  " + str(periodNumber) + "\n"
                    )
                for container in sample.containers:
                    periodNumber = container.numberOfFilesPeriodNumber[1]
                    for dataFile in container.dataFiles.dataFiles:
                        self.containerDataFiles+= (
                            dataFile + "  " + str(periodNumber) + "\n"
                        )

    def write_out(self):

        f = open("purge_det.dat", "w", encoding="utf-8")
        f.write(str(self))
        f.close()
    
    def __str__(self):

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
            f' above and below the mean ratio.\n'
            f'{numifyBool(self.ignoreBad)}{TAB}'
            f'Ignore any existing bad spectrum and spike files'
            f' (spec.bad, spike.dat)?\n'
            f'{self.sampleBackgroundDataFiles}'
            f'{self.sampleDataFiles}'
            f'{self.containerDataFiles}'
        )
        
    def purge(self):
        self.write_out()
        try:
            result = subprocess.run(
                ["bin/purge_det", "purge_det.dat"], capture_output=True, text=True
            )
        except FileNotFoundError:
            purge_det = sys._MEIPASS + os.sep + "purge_det.dat"
            result = subprocess.run(
                [purge_det, "purge_det.dat"], capture_output=True, text=True
            )
        return result
