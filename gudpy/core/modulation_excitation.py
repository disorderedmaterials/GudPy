from email.charset import QP
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

class RawPulse():

    def __init__(self, start, end):
        self.start = start
        self.end = end
    
    def __str__(self):
        return f"{self.start} {self.end}"

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
        self.periodBegin = 0.
        self.startPulse = 0.
        self.definedPulses = []
        self.rawPulses = []
        self.useDefinedPulses = True

    def determineStartTime(self, pulseLabel):
        print(pulseLabel, self.definedPulses)
        if not self.definedPulses:
            self.periodBegin = self.startPulse
        for pulse in self.definedPulses:
            if pulse.label == pulseLabel:
                self.periodBegin = self.startPulse - pulse.periodOffset
                return

    def setRawPulses(self, pulses):
        self.rawPulses = pulses
        print(self.rawPulses)

    def __str__(self):
        print(self.useDefinedPulses)
        if self.useDefinedPulses:
            pulseLines = "\n".join([str(p) for p in self.definedPulses])
            return (
                f"{self.duration}\n"
                f"{self.periodBegin}\n"
                f"{len(self.definedPulses)}\n"
                f"{pulseLines}"
            )
        else:
            rawPulses = [RawPulse(p, p+self.duration) for p in self.rawPulses]
            pulseLines = "\n".join([str(p) for p in rawPulses])
            return (
                f"{self.startPulse}\n"
                f"{len(rawPulses)}\n"
                f"{pulseLines}"
            )


class ModulationExcitation():

    def __init__(self, gudrunFile):
        self.ref = gudrunFile
        self.gudrunFile = deepcopy(gudrunFile)
        self.period = Period()
        self.extrapolationMode = ExtrapolationModes.NONE
        self.startLabel = ""
        self.dataFileDir = None
        self.outputDir = None
        self.sample = None
        self.useTempDataFileDir = False
        self.tmp = tempfile.TemporaryDirectory()
        self.path = "modex.cfg"

    def write_out(self):
        with open(self.path, 'w') as fp:
            fp.write(str(self))

    def preprocess(self, useTempDataFileDir=False, headless=True):
        self.useTempDataFileDir = useTempDataFileDir
        tasks = []
        if headless:
            modulation_excitation = resolve("bin", f"modulation_excitation{SUFFIX}")
        else:
            modulation_excitation = resolve(
                os.path.join(
                    config.__rootdir__, "bin"
                ), f"modulation_excitation{SUFFIX}"
            )
        spec_bad = os.path.join(
            self.ref.instrument.GudrunInputFileDir,
            "spec.bad"
        )
        spike_dat = os.path.join(
            self.ref.instrument.GudrunInputFileDir,
            "spike.dat"
        )
        if headless:
            if os.path.exists(spec_bad):
                self.copyfile(
                    spec_bad,
                    os.path.join(
                        self.tmp.name,
                        "spec.bad"
                    )
            )
            if os.path.exists(spike_dat):
                self.copyfile(
                    spike_dat,
                    os.path.join(
                        self.tmp.name,
                        "spike.dat"
                    )
                )
        else:
            if os.path.exists(spec_bad):
                tasks.append(
                    (
                        self.copyfile,
                        [spec_bad, os.path.join(self.tmp.name, "spec.bad")]
                    )
                )
            if os.path.exists(spike_dat):
                tasks.append(
                    (
                        self.copyfile,
                        [spec_bad, os.path.join(self.tmp.name, "spike.dat")]
                    )
                )
        if self.useTempDataFileDir:
            self.dataFileDir = os.path.join(self.tmp.name, "data")
            if headless:
                for dataFile in self.ref.sampleBackgrounds[0].samples[0].dataFiles.dataFiles:
                    self.copyfile(
                        os.path.join(
                            self.ref.instrument.dataFileDir,
                            dataFile
                        ),
                        os.path.join(
                            self.tmp.name,
                            dataFile
                        )
                    )
            else:
                tasks.append((os.makedirs, [os.path.join(self.tmp.name, "data"),]))
                for dataFile in self.ref.normalisation.dataFiles.dataFiles:
                    tasks.append((self.copyfile, [os.path.join(self.ref.instrument.dataFileDir, dataFile), os.path.join(self.tmp.name, "data", dataFile)]))
                for dataFile in self.ref.normalisation.dataFilesBg.dataFiles:
                    tasks.append((self.copyfile, [os.path.join(self.ref.instrument.dataFileDir, dataFile), os.path.join(self.tmp.name, "data", dataFile)]))
                for dataFile in self.ref.sampleBackgrounds[0].dataFiles.dataFiles:
                    tasks.append((self.copyfile, [os.path.join(self.ref.instrument.dataFileDir, dataFile), os.path.join(self.tmp.name, "data", dataFile)]))
                for dataFile in self.ref.sampleBackgrounds[0].samples[0].dataFiles.dataFiles:
                    tasks.append((self.copyfile, [os.path.join(self.ref.instrument.dataFileDir, dataFile), os.path.join(self.tmp.name, "data", dataFile)]))
                for container in self.ref.sampleBackgrounds[0].samples[0].containers:
                    for dataFile in container.dataFiles.dataFiles:
                        tasks.append((self.copyfile, [os.path.join(self.ref.instrument.dataFileDir, dataFile), os.path.join(self.tmp.name, "data", dataFile)]))
        if headless:
            self.write_out()
            result = subprocess.run(
                [modulation_excitation, "modex.cfg"], capture_output=True, text=True
            )
            return result
        else:
            tasks.append((self.write_out, []))
            proc = QProcess()
            proc.setProgram(modulation_excitation)
            proc.setArguments([self.path])
            tasks.append(proc)
            return tasks

    def copyfile(self, src, dest):
        print(f"Copying {src} to {dest}")
        if os.path.exists(src):
            try:
                shutil.copyfile(src, dest)
            except shutil.SameFileError:
                print(f"{src}=={dest}")
        else:
            print(f"{src} doesn't exist.")

    def process(self, files, headless=True):
        tasks = []
        for f in files:
            gf = deepcopy(self.gudrunFile)
            base = os.path.basename(f)
            if self.useTempDataFileDir:
                gf.instrument.dataFileDir = self.dataFileDir + os.path.sep
            gf.instrument.GudrunInputFileDir = self.tmp.name
            gf.sampleBackgrounds[0].samples[0].dataFiles.dataFiles = [base]
            base = os.path.splitext(base)[0]
            if headless:
                gf.process()
                self.copyfile(os.path.join(gf.instrument.GudrunInputFileDir, base+".mint01"), os.path.join(self.outputDir, base+".mint01"))
            else:
                dcs, func, args = gf.dcs(
                    path = os.path.join(
                        gf.instrument.GudrunInputFileDir,
                        "gudpy.txt"
                    ),
                    headless=False
                )
                task = (dcs, func, args, gf.instrument.GudrunInputFileDir)
                tasks.append(task)
                src = os.path.join(gf.instrument.GudrunInputFileDir, base+".mint01")
                dest = os.path.join(self.outputDir, base+".mint01")
                tasks.append((self.copyfile, [src, dest,]))
        if not headless:
            return tasks

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
            f"{self.dataFileDir}\n"
            f"{os.path.join(self.ref.instrument.GudrunStartFolder, self.ref.instrument.nxsDefinitionFile)}\n"
            f"{len(self.ref.sampleBackgrounds[0].samples[0].dataFiles.dataFiles)}\n"
            f"{dataFilesLines}\n"
            f"{ExtrapolationModes(self.extrapolationMode.value).name}\n"
            f"{str(self.period)}"
        )
