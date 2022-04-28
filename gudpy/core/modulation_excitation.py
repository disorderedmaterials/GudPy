from asyncio import subprocess
import os

from core.enums import ExtrapolationModes
from core.utils import resolve
from copy import deepcopy
import tempfile


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
        self.outputDir = None
        self.sample = None
        self.useDefinedPulses = True

    def write_out(self):
        with open('modex.cfg', 'w') as fp:
            fp.write(str(self))

    def run(self, headless=True):

        if headless:
            self.write_out()
            modulation_excitation = resolve("bin", f"modulation_excitation{SUFFIX}")
            result = subprocess.run(
                [modulation_excitation, "modex.cfg"], capture_output=True, text=True
            )
            print(result)
            gf = deepcopy(self.gudrunFile)
            for df in os.listdir(self.outputDir):
                pass


    def __str__(self):

        dataFilesLines = '\n'.join(
            [
                os.path.abspath(
                    os.path.join(self.gudrunFile.instrument.dataFileDir, df)
                )
                for df in self.sample.dataFiles.dataFiles
            ]
        )

        return (
            f"{self.outputDir}\n"
            f"{len(self.sample.dataFiles.dataFiles)}\n"
            f"{dataFilesLines}\n"
            f"{ExtrapolationModes(self.extrapolationMode.value).name}\n"
            f"{str(self.period)}"
        )
