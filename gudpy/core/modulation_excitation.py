from PySide6.QtCore import QProcess
import os
import subprocess
import sys

from core.enums import ExtrapolationModes
from core.utils import resolve
from core import config
from copy import deepcopy
import tempfile
import shutil

SUFFIX = ".exe" if os.name == "nt" else ""


class RawPulse:
    """
    Class to represent a Raw Pulse.
    A Raw Pulse is one that is extracted directly from the event
    mode data.

    ...

    Attributes
    ----------
    start : float
        Start time of the pulse.
    end : float
        End time of the pulse.
    """
    def __init__(self, start, end):
        """
        Constructs all the necessary attributes for the RawPulse object.

        Parameters
        ----------
        start : float
            Start time.
        end : float
            End time.
        """
        self.start = start
        self.end = end

    def __str__(self):
        return f"{self.start} {self.end}"


class DefinedPulse:
    """
    Class to represent a Defined Pulse.
    These are user defined, and work using relative times.
    For instance, rather than the 'start time' of the pulse,
    the user would define the 'period offset', which indicates
    the time from the period start that the pulse starts.

    ...

    Attributes
    ----------
    label : str
        Label of the pulse.
    periodOffset : float
        Start offset of the pulse, relative to the period start.
    duration : float:
        Duration of the pulse.
    """
    def __init__(self, label="", periodOffset=0.0, duration=0.0):
        """
        Constructs all the necessary attributes for the RawPulse object.

        Parameters
        ----------
        label : str
            Pulse labl.
        periodOffset : float
            Start offset of pulse.
        duration : float
            Pulse duration.
        """
        self.label = label
        self.periodOffset = periodOffset
        self.duration = duration

    def __str__(self):
        return f"{self.label} {self.periodOffset} {self.duration}"


class Period:
    """
    Class to represent a Period.
    This Period can consist of RawPulses (i.e. the period might just
    reflect all pulses extracted from a spectra in the event mode data),
    or it can consist of DefinedPulses (in cases where data is incomplete etc).

    ...

    Attributes
    ----------
    duration : float
        Duration of the period.
    periodBegin : float
        Period start time relative to start of run.
    startPulse : float
        Start time of the first pulse in the period.
    definedPulses : DefinedPulse[]
        List of DefinedPulses in use (can be none).
    rawPulses : float[]
        List of RawPulses start times in use (can be none).
    useDefinedPulses : bool
        Should defined pulses be used (or raw pulses)?

    Methods
    -------
    determineStartTime(pulseLabel)
        Determines and assigns the 'periodBegin'.
    setRawPulses(pulses)
        Sets raw pulses.
    """
    def __init__(self):
        """
        Constructs all the necessary attributes for the Period object.
        """
        self.duration = 0.0
        self.periodBegin = 0.0
        self.startPulse = 0.0
        self.definedPulses = []
        self.rawPulses = []
        self.useDefinedPulses = True

    def determineStartTime(self, pulseLabel):
        """
        Determines and assigns the 'periodBegin',
        by matching the 'pulseLabel' to labels of defined pulses.
        In the case of using raw pulses, this is time time of the start pulse.

        Parameters
        ----------
        pulseLabel : str
            Target Pulse label.
        """
        if not self.definedPulses:
            self.periodBegin = self.startPulse
        for pulse in self.definedPulses:
            if pulse.label == pulseLabel:
                self.periodBegin = self.startPulse - pulse.periodOffset
                return

    def setRawPulses(self, pulses):
        """
        Setter method for 'rawPulses' attribute.s

        Parameters
        ----------
        pulses : float[]
            Raw pulse start times to assign.
        """
        self.rawPulses = pulses

    def __str__(self):
        # If using defined pulses, then we need to write
        # the period duration, start time and the defined pulses.
        if self.useDefinedPulses:
            pulseLines = "\n".join([str(p) for p in self.definedPulses])
            return (
                f"{self.duration}\n"
                f"{self.periodBegin}\n"
                f"{len(self.definedPulses)}\n"
                f"{pulseLines}"
            )
        # Otherwise, just the raw pulses.
        else:
            # Construct list of RawPulses, using period duration
            # to determine end time.
            rawPulses = [
                RawPulse(p, p + self.duration) for p in self.rawPulses
            ]
            pulseLines = "\n".join([str(p) for p in rawPulses])
            return f"{len(rawPulses)}\n" f"{pulseLines}"


class ModulationExcitation:
    """
    Class to represent the ModulationExcitation data processing pipeline.
    This class is used for interfacing with ModEx for data preparation,
    and then subsequently processing the extracted data using Gudrun.

    ...

    Attributes
    ----------
    ref : GudrunFile
        Reference to the initial GudrunFile object.
    gudrunFile : GudrunFile
        Copy of the initial GudrunFile object.
    period : Period
        Period definition to use.
    extrapolationMode : ExtrapolationModes
        Extrapolation mode to use (if any).
    startLabel : str
        Label of the first pulse.
    dataFileDir : str
        Data file directory.
    outputDir : str
        Output directory.
    sample : Sample
        Sample to be targeted.
    useTempDataFileDir : bool
        Should a temporary directory be used for data files?
    interpolate : bool
        Should final data be interpolated?
    tmp : tempfile.TemporaryDirectory
        Temporary directory.
    path : str
        Path to write configuration file.
    goodFrameThreshold : int
        Threshold for filtering pulses by good frames below.

    Methods
    -------
    write_out()
        Writes out the configuration file.
    isConfigurationValid()
        Checks if the current configuration is valid.
    preprocess(useTempDataFileDir=false, headless=True)
        Performs preprocessing.
    copyfile(src, dest)
        Helper for copying files.
    process(files, headless=True)
        Performs processing.
    interpolateData(files)
        Interpolates data.
    """
    def __init__(self, gudrunFile):
        """
        Constructs all the necessary attributes for the
        ModulationExcitation object.

        Parameters
        ----------
        gudrunFile: GudrunFile
            Parent GudrunFile.
        """
        self.ref = gudrunFile
        self.gudrunFile = deepcopy(gudrunFile)
        self.period = Period()
        self.extrapolationMode = ExtrapolationModes.FORWARDS
        self.startLabel = ""
        self.dataFileDir = self.gudrunFile.instrument.dataFileDir
        self.outputDir = ""
        self.sample = None
        self.useTempDataFileDir = False
        self.interpolate = False
        self.tmp = tempfile.TemporaryDirectory()
        self.path = "modex.cfg"
        self.goodFrameThreshold = 0

    def write_out(self):
        """
        Writes out the configuration file to the output path.
        """
        with open(self.path, "w") as fp:
            fp.write(str(self))

    def isConfigurationValid(self):
        """
        Checks if the current configuration is valid.
        """

        # Check for valid directories.
        if not self.outputDir:
            return False, "Output Directory not specified"
        if not os.path.exists(self.outputDir):
            return (
                False,
                f"Output Directory ({self.outputDir}) does not exist.",
            )
        if not self.dataFileDir:
            return False, "Data File Directory not specified"
        if not os.path.exists(self.dataFileDir):
            return (
                False,
                f"Output Directory ({self.dataFileDir}) does not exist.",
            )

        # Check that period is valid
        if self.period.useDefinedPulses:
            # Ensure we have some pulses.
            if len(self.period.definedPulses) == 0:
                return False, "No Pulses were defined."
            for p in self.period.definedPulses:
                # Ensure that pulses actually occur in the period.
                if p.periodOffset > self.period.duration:
                    return (
                        False,
                        f"Pulse {p.label} start {p.start}"
                        f" is beyond period duration {self.period.duration}.",
                    )
                if p.periodOffset + p.duration > self.period.duration:
                    return (
                        False,
                        f"Pulse {p.label} end {p.periodOffset + p.duration}"
                        f" is beyond period duration {self.period.duration}.",
                    )
        else:
            # Ensure we have some pulses.
            if len(self.period.rawPulses) == 0:
                return False, "No raw pulses were supplied."
        return True, ""

    def preprocess(self, useTempDataFileDir=False, headless=True):
        """
        Performs preprocessing.
        This includes, if necessary, moving data files into the temporary
        data file directory, and subsequently performing the relevant
        preprocessing using modulation_excitation (ModEx).

        Parameters
        ----------
        useTempDataFileDir : bool, optional
            Should a temporary data file directory be used?
        headless : bool, optional
            Should processing be headless?
        """

        # Cleanup temp directory.
        for f in os.listdir(self.tmp.name):
            fp = os.path.join(self.tmp.name, f)
            if os.path.isfile(fp):
                os.remove(fp)
            elif os.path.isdir(fp):
                shutil.rmtree(fp)

        self.useTempDataFileDir = useTempDataFileDir
        # List to hold tasks, in the case of headful preprocessing.
        tasks = []
        # Resolve path to modulation_excitation binary.
        if headless:
            modulation_excitation = resolve(
                "bin", f"modulation_excitation{SUFFIX}"
            )
        else:
            if hasattr(sys, "_MEIPASS"):
                modulation_excitation = os.path.join(
                    sys._MEIPASS, f"modulation_excitation{SUFFIX}"
                )
            else:
                modulation_excitation = resolve(
                    os.path.join(config.__rootdir__, "bin"),
                    f"modulation_excitation{SUFFIX}",
                )
        # Error if binary is missing.
        if not os.path.exists(modulation_excitation):
            return FileNotFoundError

        # Purge outputs.
        spec_bad = os.path.join(
            self.ref.instrument.GudrunInputFileDir, "spec.bad"
        )
        spike_dat = os.path.join(
            self.ref.instrument.GudrunInputFileDir, "spike.dat"
        )
        if headless:
            # If these files exist, copy them to the temporary directory.
            if os.path.exists(spec_bad):
                self.copyfile(
                    spec_bad, os.path.join(self.tmp.name, "spec.bad")
                )
            if os.path.exists(spike_dat):
                self.copyfile(
                    spike_dat, os.path.join(self.tmp.name, "spike.dat")
                )
        else:
            # If not headless, add them as tasks.
            if os.path.exists(spec_bad):
                tasks.append(
                    (
                        self.copyfile,
                        [spec_bad, os.path.join(self.tmp.name, "spec.bad")],
                    )
                )
            if os.path.exists(spike_dat):
                tasks.append(
                    (
                        self.copyfile,
                        [spec_bad, os.path.join(self.tmp.name, "spike.dat")],
                    )
                )
        if self.useTempDataFileDir:
            # Set the data file directory to be in the temporary directory.
            self.dataFileDir = os.path.join(self.tmp.name, "data")
            # If headless, copy all the data files into this new directory.
            if headless:
                if os.path.exists(self.dataFileDir):
                    shutil.rmtree(self.dataFileDir)
                os.makedirs(self.dataFileDir)
                for dataFile in self.ref.normalisation.dataFiles.dataFiles:
                    self.copyfile(
                        os.path.join(
                            self.ref.instrument.dataFileDir, dataFile
                        ),
                        os.path.join(self.dataFileDir, dataFile),
                    )
                for dataFile in self.ref.normalisation.dataFilesBg.dataFiles:
                    self.copyfile(
                        os.path.join(
                            self.ref.instrument.dataFileDir, dataFile
                        ),
                        os.path.join(self.dataFileDir, dataFile),
                    )
                for dataFile in self.ref.sampleBackgrounds[
                    0
                ].dataFiles.dataFiles:
                    self.copyfile(
                        os.path.join(
                            self.ref.instrument.dataFileDir, dataFile
                        ),
                        os.path.join(self.dataFileDir, dataFile),
                    )
                for dataFile in (
                    self.ref.sampleBackgrounds[0]
                    .samples[0]
                    .dataFiles.dataFiles
                ):
                    self.copyfile(
                        os.path.join(
                            self.ref.instrument.dataFileDir, dataFile
                        ),
                        os.path.join(self.dataFileDir, dataFile),
                    )
                for container in (
                    self.ref.sampleBackgrounds[0].samples[0].containers
                ):
                    for dataFile in container.dataFiles.dataFiles:
                        self.copyfile(
                            os.path.join(
                                self.ref.instrument.dataFileDir,
                                dataFile,
                            ),
                            os.path.join(
                                self.dataFileDir, dataFile
                            ),
                        )
            # Otherwise, append the copies as tasks.
            else:
                if os.path.exists(os.path.join(self.dataFileDir)):
                    tasks.append(
                        (shutil.rmtree, [os.path.join(self.dataFileDir)])
                    )
                tasks.append(
                    (
                        os.makedirs,
                        [
                            os.path.join(self.dataFileDir),
                        ],
                    )
                )
                for dataFile in self.ref.normalisation.dataFiles.dataFiles:
                    tasks.append(
                        (
                            self.copyfile,
                            [
                                os.path.join(
                                    self.ref.instrument.dataFileDir, dataFile
                                ),
                                os.path.join(self.dataFileDir, dataFile),
                            ],
                        )
                    )
                for dataFile in self.ref.normalisation.dataFilesBg.dataFiles:
                    tasks.append(
                        (
                            self.copyfile,
                            [
                                os.path.join(
                                    self.ref.instrument.dataFileDir, dataFile
                                ),
                                os.path.join(self.dataFileDir, dataFile),
                            ],
                        )
                    )
                for dataFile in self.ref.sampleBackgrounds[
                    0
                ].dataFiles.dataFiles:
                    tasks.append(
                        (
                            self.copyfile,
                            [
                                os.path.join(
                                    self.ref.instrument.dataFileDir, dataFile
                                ),
                                os.path.join(self.dataFileDir, dataFile),
                            ],
                        )
                    )
                for dataFile in (
                    self.ref.sampleBackgrounds[0]
                    .samples[0]
                    .dataFiles.dataFiles
                ):
                    tasks.append(
                        (
                            self.copyfile,
                            [
                                os.path.join(
                                    self.ref.instrument.dataFileDir, dataFile
                                ),
                                os.path.join(self.dataFileDir, dataFile),
                            ],
                        )
                    )
                for container in (
                    self.ref.sampleBackgrounds[0].samples[0].containers
                ):
                    for dataFile in container.dataFiles.dataFiles:
                        tasks.append(
                            (
                                self.copyfile,
                                [
                                    os.path.join(
                                        self.ref.instrument.dataFileDir,
                                        dataFile,
                                    ),
                                    os.path.join(
                                        self.dataFileDir, dataFile
                                    ),
                                ],
                            )
                        )
        if headless:
            # Write out the configuration file and
            # perform modulation_excitation.
            self.write_out()
            result = subprocess.run(
                [modulation_excitation, "modex.cfg"],
                capture_output=True,
                text=True,
            )
            return result
        else:
            # Append the write_out call, and a QProcess to run
            # modulation_excitation to the tasks.
            tasks.append((self.write_out, []))
            proc = QProcess()
            proc.setProgram(modulation_excitation)
            proc.setArguments([self.path])
            tasks.append(proc)
            return tasks

    def copyfile(self, src, dest):
        """
        Helper for copying files.
        Fails quietly if the files are the same.

        Parameters
        ----------
        src : str
            Source.
        dest : str
            Destination.
        """
        if os.path.exists(src):
            try:
                shutil.copyfile(src, dest)
            except shutil.SameFileError:
                pass

    def process(self, files, headless=True):
        """
        Performs processing.
        This includes running gudrun_dcs on each of the specified files.


        Parameters
        ----------
        files : str[]
            List of files to process.
        headless : bool
        """

        # List to hold tasks, in the case of headful processing.
        tasks = []
        for f in files:
            # Deepcopy the GudrunFile object.
            gf = deepcopy(self.gudrunFile)

            base = os.path.basename(f)
            # If temporary data file directory is being used,
            # then update the dataFileDir to reflect that.
            if self.useTempDataFileDir:
                gf.instrument.dataFileDir = self.dataFileDir + os.path.sep
            # gudrun_dcs will be run inside the temp directory.
            gf.instrument.GudrunInputFileDir = self.tmp.name
            # Ensure that only this file will be processed.
            gf.sampleBackgrounds[0].samples[0].dataFiles.dataFiles = [base]

            # This is the base name of the file, without extensions.
            base = os.path.splitext(base)[0]

            if headless:
                # If headless, then process the file, and copy the outputted
                # mint file directly to the output directoy.
                gf.process()
                self.copyfile(
                    os.path.join(
                        gf.instrument.GudrunInputFileDir, base + ".mint01"
                    ),
                    os.path.join(self.outputDir, base + ".mint01"),
                )
            else:
                # Otherwise, append the processing as tasks.
                dcs, func, args = gf.dcs(
                    path=os.path.join(
                        gf.instrument.GudrunInputFileDir, "gudpy.txt"
                    ),
                    headless=False,
                )
                task = (dcs, func, args, gf.instrument.GudrunInputFileDir)
                tasks.append(task)
                src = os.path.join(
                    gf.instrument.GudrunInputFileDir, base + ".mint01"
                )
                dest = os.path.join(self.outputDir, base + ".mint01")
                tasks.append((self.copyfile, [src, dest]))

        if headless and self.interpolate:
            # Call interpolation method on outputted files.
            self.interpolateData(files)
        elif not headless and self.interpolate:
            # Append interpolation as a task.
            tasks.append((self.interpolateData, [files]))

        if not headless:
            return tasks

    def interpolateData(self, files):
        """
        Interpolates specified files into a single output file.
        These files are expected to be mint01 files.
        The result is a file with len(files)+1 columns,
        where the first column represents the Q value,
        and the following len(files) columns represent the DCS values
        of each individual mint01 file (organise by start time).

        Parameters
        ----------
        files : str[]
            List of files to interpolate.
        """
        print("Using good frame threshold: ", str(self.goodFrameThreshold))
        # Sort the files beforehand,
        # so they should be in ascending order by start time.
        files = sorted(
            [
                os.path.join(
                    self.outputDir,
                    os.path.basename(f)
                    .replace(os.path.splitext(f)[-1], ".mint01")
                )
                for f in files
            ]
        )   

        with open("modex.diagnostics") as fp:
            diagnostics = fp.readlines()

        # Simple helper function.
        # Given a list of lines in column format, return the nth column.
        def parseColumn(n, lines):
            col = []
            for line in lines:
                if line.startswith('#'):
                    continue
                tokens = line.split()
                col.append(float(tokens[n]))
            return col

        # For storing final output.
        Q = []
        DCS = []

        # Flag for determining if the Q (x) column has been read yet.
        # We only need to read it once.
        readQ = False

        periods = []

        # If using all pulses, then step is 1.
        step = (
            len(self.period.definedPulses)
            if self.period.useDefinedPulses
            else 1
        )

        # Iterate files, stepping by step.
        for i in range(0, len(files), step):
            period = {}
            # Iterate files in period.
            for j in range(i, i+step):
                # If the file doesn't exist, then there are no DCS values.
                if not os.path.exists(files[j]):
                    period[files[j]] = []
                elif int(diagnostics[j].split()[1]) < self.goodFrameThreshold:
                    print(f"Ignoring {files[j]}, since {int(diagnostics[j].split()[1])} < {self.goodFrameThreshold}")
                else:
                    # Otherwise, read in the DCS values.
                    with open(files[j], "r", encoding='utf-8') as fp:
                        lines = fp.readlines()
                        # Read Q, if it has not been read.
                        if not readQ:
                            # Retrieve Q.
                            Q = parseColumn(0, lines)
                            readQ = True
                        # Retrieve DCS values.
                        period[files[j]] = parseColumn(1, lines)
            periods.append(period)
        # Write out the date in the interpolated format.
        with open(
            os.path.join(
                self.outputDir,
                "interpolated.dat"
            ),
            "w", encoding="utf-8"
        ) as fp:
            goodPeriods = []
            # Iterate through the periods, to determine which ones are good.
            for period in periods:
                # If the number of DCS values does not match
                # the number of Q values, then discard.
                # This also handles the files which don't exist.
                if any([len(p) != len(Q) for p in period.values()]):
                    continue
                # If the DCS values are all zero, then discard.
                elif any([list(set(p)) == [0.0] for p in period.values()]):
                    continue
                else:
                    goodPeriods.append(period)
            # Construct the final DCS data.
            DCS = [
                pulse for period in goodPeriods
                for pulse in period.values()
            ]
            for i in range(len(Q)):
                # Take i'th DCS level of each pulse.
                dcs = [x[i] for x in DCS]
                # Write the i'th Q value along with the relevant DCS levels.
                fp.write(f"  {Q[i]}  {'  '.join([str(x) for x in dcs])}\n")

    def __str__(self):
        dataFilesLines = "\n".join(
            [
                os.path.abspath(
                    os.path.join(self.ref.instrument.dataFileDir, df)
                )
                for df in self.ref.sampleBackgrounds[0]
                .samples[0]
                .dataFiles.dataFiles
            ]
        )
        # Determine the start time of the period.
        self.period.determineStartTime(self.startLabel)

        # If not using defined pulses, then no extrapolation
        # is necessary.
        if not self.period.useDefinedPulses:
            extrapolationMode = ExtrapolationModes.NONE.name
        else:
            extrapolationMode = ExtrapolationModes(
                self.extrapolationMode.value
            ).name
        nxsDefinitionsPath = os.path.join(
            self.ref.instrument.GudrunStartFolder,
            self.ref.instrument.nxsDefinitionFile,
        )
        numDataFiles = len(
            self.ref.sampleBackgrounds[0].samples[0].dataFiles.dataFiles
        )
        return (
            f"{self.dataFileDir}\n"
            f"{nxsDefinitionsPath}\n"
            f"{numDataFiles}\n"
            f"{dataFilesLines}\n"
            f"{extrapolationMode}\n"
            f"{str(self.period)}"
        )
