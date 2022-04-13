import os
import shutil

class OutputFileHandler():

    def __init__(self, gudrunFile):
        self.gudrunFile = gudrunFile
        self.getRunFiles()
        self.outputs = {
            "sampleOutputs": [
                "dcs01",
                "dcsd01",
                "dcse01",
                "dcst01",
                "dscw01",
                "mdcs01",
                "mdcsd01",
                "mdcse01",
                "mdcsw01",
                "mint01",
                "mgor01",
                "mdor01",
                "gud",
                "sample"
            ],
            "sampleDiagnostics": [
                "abs01",
                "bak",
                "gr1",
                "gr2",
                "mul01",
                "mut01",
                "pla01",
                "rawmon",
                "smomon",
                "trans01"
            ],
            "containerOutputs": [

            ]
        }

    def getRunFiles(self):
        self.runFiles = [
            *[
                os.path.splitext(s.dataFiles.dataFiles[0])[0]
                for sampleBackground in self.gudrunFile.sampleBackgrounds
                for s in sampleBackground.samples if s.runThisSample
                and len(s.dataFiles.dataFiles)
            ],
            *[
                os.path.splitext(s.pathName())[0] for sampleBackground in self.gudrunFile.sampleBackgrounds
                for s in sampleBackground.samples if s.runThisSample
            ]
        ]

    def organiseSampleFiles(self, run, tree=""):
        dir = self.gudrunFile.instrument.GudrunInputFileDir
        if tree:
            outputDir = os.path.join(dir, tree, run)
            if os.path.exists(os.path.join(dir, tree)):
                    shutil.rmtree(os.path.join(dir, tree))
        else:
            if os.path.exists(outputDir):
                shutil.rmtree(outputDir)
            outputDir = os.path.join(dir, run)
        os.makedirs(os.path.join(outputDir, "outputs"))
        os.makedirs(os.path.join(outputDir, "diagnostics"))
        for f in os.listdir(dir):
            for suffix in self.outputs["sampleOutputs"]:
                if f == f"{run}.{suffix}":
                    shutil.copyfile(
                        os.path.join(dir, f),
                        os.path.join(outputDir, "outputs", f)
                    )
            for suffix in self.outputs["sampleDiagnostics"]:
                if f == f"{run}.{suffix}":
                    shutil.copyfile(
                        os.path.join(dir, f),
                        os.path.join(outputDir, "diagnostics", f)
                    )

    def naiveOrganise(self):
        for run in self.runFiles:
            self.organiseSampleFiles(run)
    
    def iterativeOrganise(self, head):
        for run in self.runFiles:
            self.organiseSampleFiles(run, tree=head)

