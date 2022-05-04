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
from watchpoints import watch

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
        self.definedPulses = True

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
        self.ref = gudrunFile
        self.gudrunFile = deepcopy(gudrunFile)
        self.period = Period()
        self.extrapolationMode = ExtrapolationModes.NONE
        self.startPulse = None
        self.auxDir = None
        self.outputDir = None
        watch(self.outputDir)
        self.sample = None
        self.useDefinedPulses = True
        self.tmp = tempfile.TemporaryDirectory()
        self.path = "modex.cfg"

    def write_out(self):
        with open(self.path, 'w') as fp:
            fp.write(str(self))

    def preprocess(self, useTempDir=False, headless=True):
        tasks = []
        if headless:
            modulation_excitation = resolve("bin", f"modulation_excitation{SUFFIX}")
        else:
            modulation_excitation = resolve(
                os.path.join(
                    config.__rootdir__, "bin"
                ), f"modulation_excitation{SUFFIX}"
            )
        if useTempDir:
            spec_bad = os.path.join(
                self.ref.instrument.GudrunInputFileDir,
                "spec.bad"
            )
            if headless:
                for dataFile in self.ref.sampleBackgrounds[0].samples[0].dataFiles.dataFiles:
                    shutil.copyfile(
                        os.path.join(
                            self.ref.instrument.dataFileDir,
                            dataFile
                        ),
                        os.path.join(
                            self.tmp.name,
                            dataFile
                        )
                    )
                    shutil.copyfile(
                        spec_bad,
                        os.path.join(
                            self.tmp.name,
                            "spec.bad"
                        )
                    )
            else:
                for dataFile in self.ref.normalisation.dataFiles.dataFiles:
                    tasks.append((shutil.copyfile, [os.path.join(self.ref.instrument.dataFileDir, dataFile), os.path.join(self.tmp.name, dataFile)]))
                for dataFile in self.ref.sampleBackgrounds[0].samples[0].dataFiles.dataFiles:
                    tasks.append((shutil.copyfile, [os.path.join(self.ref.instrument.dataFileDir, dataFile), os.path.join(self.tmp.name, dataFile)]))
                for container in self.ref.sampleBackgrounds[0].samples[0].containers:
                    for dataFile in container.dataFiles.dataFiles:
                        tasks.append((shutil.copyfile, [os.path.join(self.ref.instrument.dataFileDir, dataFile), os.path.join(self.tmp.name, dataFile)]))
                tasks.append((shutil.copyfile, [spec_bad, os.path.join(self.tmp.name, "spec.bad")]))
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
            shutil.copyfile(src, dest)
        else:
            print(f"{src} doesn't exist.")

    def process(self, files, headless=True):
        tasks = []
        for f in files:
            gf = deepcopy(self.gudrunFile)
            base = os.path.basename(f)
            gf.instrument.dataFileDir = self.tmp.name + "/"
            gf.sampleBackgrounds[0].samples[0].dataFiles.dataFiles = [base]
            gf.instrument.GudrunInputFileDir = self.tmp.name
            base = os.path.splitext(f)[0]
            print("BASE: " + base)
            if headless:
                gf.process()
                self.copyfile(os.path.join(self.tmp.name, base+".mint01"), os.path.join(self.outputDir, base+".mint01"))
            else:
                dcs, func, args = gf.dcs(
                    path = os.path.join(
                        self.tmp.name,
                        "gudpy.txt"
                    ),
                    headless=False
                )
                task = (dcs, func, args, self.tmp.name)
                tasks.append(task)
                # tasks.append(gf.dcs(path=os.path.join(self.tmp.name, "gudpy.txt"), headless=False),  + (self.tmp.name))
                src = os.path.join(self.tmp.name, base+".mint01")
                dest = os.path.join(self.outputDir, base+".mint01")
                tasks.append((self.copyfile, [src, dest,]))
        if not headless:
            return tasks
        # for f in files:
        #     gf = deepcopy(self.gudrunFile)
        #     base = os.path.basename(f)
        #     print(base)
        #     gf.sampleBackgrounds[0].samples[0].dataFiles.dataFiles = [base]
        #     # gf.instrument.GudrunInputFileDir = self.tmp.name
        #     gf.instrument.dataFileDir = self.tmp.name
        #     # gf.path = os.path.join(self.tmp.name, os.path.basename(gf.path))
        #     base = os.path.splitext(f)[0]
        #     if headless:
        #         gf.process()
        #         shutil.copyfile(os.path.join(self.tmp.name, base+".mint01"), os.path.join(self.outputDir, base+".mint01"))
        #     else:
        #         tasks.append(gf.dcs(path=os.path.join(self.gudrunFile.instrument.GudrunInputFileDir, "gudpy.txt"),headless=False))
        #         src = os.path.join(self.gudrunFile.instrument.GudrunInputFileDir, base+".mint01")
        #         dest = os.path.join(self.outputDir, base+".mint01")
        #         tasks.append((self.copyfile, [src, dest]))
        # if not headless:
        #     return tasks

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
            f"{self.tmp.name}\n"
            f"{os.path.join(self.ref.instrument.GudrunStartFolder, self.ref.instrument.nxsDefinitionFile)}\n"
            f"{len(self.ref.sampleBackgrounds[0].samples[0].dataFiles.dataFiles)}\n"
            f"{dataFilesLines}\n"
            f"{ExtrapolationModes(self.extrapolationMode.value).name}\n"
            f"{str(self.period)}"
        )
