import os
import subprocess

from core.enums import ExtrapolationModes
from core.utils import resolve
from copy import deepcopy
import tempfile
import shutil

from core.file_library import GudPyFileLibrary


SUFFIX = ".exe" if os.name == "nt" else ""


class Pulse():

    def __init__(self, label="", start=0.0, end=0.0):
        self.label = label
        self.start = start
        self.end = end

    def __str__(self):
        return f"{self.label} {self.start} {self.end}"


class DefinedPulse():

    def __init__(self, label="", periodOffset=0.0, duration=0.0):
        self.label = label
        self.periodOffset = periodOffset
        self.duration = duration

    def __str__(self):
        return f"{self.label} {self.periodOffset} {self.duration}"


class Period():

    def __init__(self):
        self.duration = 0.
        self.startPulse = 0.
        self.pulses = []
        self.definedPulses = False

    def __str__(self):

        pulseLines = "\n".join([str(p) for p in self.pulses])

        if self.definedPulses:
            return (
                f"{self.duration}\n"
                f"{self.startPulse}\n"
                f"{len(self.pulses)}\n"
                f"{pulseLines}"
            )
        else:
            return (
                f"{len(self.pulses)}\n"
                f"{pulseLines}"
            )


class ModulationExcitation():

    def __init__(self, gudrunFile):
        self.gudrunFile = gudrunFile
        self.period = Period()
        self.extrapolationMode = ExtrapolationModes.NONE
        self.startPulse = None
        self.auxDir = None
        self.outputDir = None
        self.sample = None
        self.useDefinedPulses = True

    def write_out(self):
        with open('modex.cfg', 'w') as fp:
            fp.write(str(self))

    def run(self, useTempDir=False, headless=True):

        if headless:
            gf = deepcopy(self.gudrunFile)
            modulation_excitation = resolve("bin", f"modulation_excitation{SUFFIX}")
            if useTempDir:
                self.auxDir = tempfile.TemporaryDirectory().name
                for dataFile in self.gudrunFile.sampleBackgrounds[0].samples[0].dataFiles.dataFiles:
                    shutil.copyfile(
                        os.path.join(
                            self.gudrunFile.instrument.dataFileDir,
                            dataFile
                        ),
                        os.path.join(
                            self.auxDir,
                            dataFile
                        )
                    )
                    self.gudrunFile.instrument.dataFileDir = self.auxDir
            else:
                self.auxDir = self.gudrunFile.instrument.dataFileDir
            self.write_out()
            files = os.listdir(self.auxDir)
            result = subprocess.run(
                [modulation_excitation, "modex.cfg"], capture_output=True, text=True
            )
            files = [f for f in os.listdir(self.auxDir) if not f in files]
            print(result.stdout)
            print (GudPyFileLibrary(self.gudrunFile).files)
            with tempfile.TemporaryDirectory() as t:
                for f in files:
                    gf.sampleBackgrounds[0].samples[0].dataFiles.dataFiles = [f]                    
                    gf.instrument.GudrunInputFileDir = t
                    gf.path = os.path.join(gf.instrument.GudrunInputFileDir, os.path.basename(gf.path))
                    gf.path
                    gf.process()
                    base = os.path.splitext(f)[0]
                    shutil.copyfile(os.path.join(t, base+".mint01"), os.path.join(self.outputDir, base+".mint01"))
                        # for f in os.listdir(t):
                        #     if f.endswith("mint01"):
                        #         print(os.path.join(t,f))
                        #         shutil.copyfile(os.path.join(t, f), os.path.join(self.outputDir, f))

    def __str__(self):

        dataFilesLines = '\n'.join(
            [
                os.path.abspath(
                    os.path.join(self.gudrunFile.instrument.dataFileDir, df)
                )
                for df in self.gudrunFile.sampleBackgrounds[0].samples[0].dataFiles.dataFiles
            ]
        )

        return (
            f"{self.auxDir}\n"
            f"{os.path.join(self.gudrunFile.instrument.GudrunStartFolder, self.gudrunFile.instrument.nxsDefinitionFile)}\n"
            f"{len(self.gudrunFile.sampleBackgrounds[0].samples[0].dataFiles.dataFiles)}\n"
            f"{dataFilesLines}\n"
            f"{ExtrapolationModes(self.extrapolationMode.value).name}\n"
            f"{str(self.period)}"
        )
