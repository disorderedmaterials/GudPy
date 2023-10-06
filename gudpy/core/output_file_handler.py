import os
import shutil
from core.utils import makeDir, uniquify


class OutputFileHandler():

    def __init__(self, gudrunFile):
        self.gudrunFile = gudrunFile
        # Directory where Gudrun files are outputted
        self.gudrunDir = self.gudrunFile.instrument.GudrunInputFileDir
        # Name the output directory as the input file
        self.outputDir = os.path.join(
            self.gudrunDir,
            os.path.splitext(self.gudrunFile.filename)[0]
        )
        # String constants
        self.NORM = "Normalisation"
        self.NORM_BG = "NormalisationBackground"
        self.SAMPLE = "Sample"
        self.SAMPLE_BG = "SampleBackground"
        self.SAMPLE_BGS = "SampleBackgrounds"
        self.CONTAINERS = "Containers"
        self.OUTPUTS = "Outputs"
        self.DIAGNOSTICS = "Diagnostics"
        self.Outputs = {
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

    def createNormDir(self, outputDir):
        # Create normalisation folders
        for normFile in self.gudrunFile.normalisation.dataFiles:
            self.copyOutputs(normFile, os.path.join(outputDir, self.NORM))
        for normBgFile in self.gudrunFile.normalisation.dataFilesBg:
            self.copyOutputs(normBgFile,
                             os.path.join(outputDir, self.NORM_BG))

    def createSampleBgDir(self, outputDir, sampleBackground):
        for dataFile in sampleBackground.dataFiles:
            self.copyOutputs(
                dataFile,
                os.path.join(
                    outputDir, self.SAMPLE_BGS, self.SAMPLE_BG),
                sep="",
                incFirst=True
            )

    def createSampleDir(self, outputDir, samples, tree=""):
        # Create sample folders within background folders
        for sample in [
            s for s in samples
            if s.runThisSample and len(s.dataFiles)
        ]:
            if tree:
                samplePath = os.path.join(
                    outputDir,
                    sample.name,
                    tree)
            else:
                samplePath = uniquify(os.path.join(
                    outputDir,
                    sample.name
                ))
            for dataFile in sample.dataFiles:
                self.copySuffixedOutputs(
                    dataFile,
                    samplePath
                )
            # Copy over .sample file
            if os.path.exists(os.path.join(
                    self.gudrunDir, sample.pathName())):
                shutil.copyfile(
                    os.path.join(self.gudrunDir, sample.pathName()),
                    os.path.join(samplePath, sample.pathName())
                )
            # Create container folders within sample folder
            for container in sample.containers:
                containerPath = uniquify(os.path.join(
                    samplePath,
                    (container.name.replace(" ", "_")
                     if container.name != "CONTAINER"
                     else "Container")))
                for dataFile in container.dataFiles:
                    self.copyOutputs(
                        dataFile,
                        containerPath
                    )
        return samplePath

    def naiveOrganise(self):
        # Create normalisation and sample background folders
        self.createNormDir(self.outputDir)
        # Create sample folders
        for sampleBackground in self.gudrunFile.sampleBackgrounds:
            self.createSampleBgDir(self.outputDir, sampleBackground)
            self.createSampleDir(
                self.outputDir,
                sampleBackground.samples)

    def iterativeOrganise(self, nTotal, nCurrent, head):
        for sampleBackground in self.gudrunFile.sampleBackgrounds:
            if nCurrent == 0:
                self.createNormDir(self.outputDir)
                self.createSampleBgDir(self.outputDir, sampleBackground)
            self.createSampleDir(
                self.gudrunDir,
                sampleBackground.samples,
                f"{head}_{nCurrent + 1}")
            if nCurrent == nTotal:
                for sample in [
                    s for s in sampleBackground.samples
                    if s.runThisSample and len(s.dataFiles)
                ]:
                    shutil.move(
                        os.path.join(self.gudrunDir, sample.name),
                        uniquify(
                            os.path.join(
                                self.outputDir,
                                f"{sample.name}_{head}"))
                    )

    def copyOutputs(self, fpath, targetDir):
        """
        Function to copy all files with the same basename
        as the provided filepath, except the original file.
        Creates a folder in the target directory and all necessary
        directories.

        Parameters
        ----------
        fpath : str
            Full filename of target file
        targetDir : str
            Directory for the files to be copied to
        """
        fname = os.path.splitext(fpath)[0]
        runDir = os.path.join(targetDir, fname)
        dirCreated = False
        for f in os.listdir(self.gudrunDir):
            # Get files with the same filename but not the same
            # extension
            if os.path.splitext(f)[0] == fname and f != fpath:
                if not dirCreated:
                    makeDir(runDir)
                    dirCreated = True
                shutil.copyfile(
                    os.path.join(self.gudrunDir, f),
                    os.path.join(runDir, f)
                )

    def copySuffixedOutputs(self, fname, targetDir):
        """
        Function to copy all files with the same basename
        as the provided filepath and splits them into outputs
        and diagnostics folders based on their extension.
        Creates a folder in the target directory and all necessary
        directories.

        Parameters
        ----------
        fname : str
            Full filename of target file
        suffixes : str[]
            List of target file extenstions
        targetDir : str
            Directory for the files to be copied to
        """
        fname = os.path.splitext(fname)[0]
        runDir = os.path.join(targetDir, fname)
        outDir = os.path.join(runDir, self.OUTPUTS)
        diagDir = os.path.join(runDir, self.DIAGNOSTICS)
        for f in os.listdir(self.gudrunDir):
            for suffix in self.Outputs["sampleOutputs"]:
                if f == f"{fname}.{suffix}":
                    if not os.path.isdir(outDir):
                        makeDir(outDir)
                    shutil.copyfile(
                        os.path.join(self.gudrunDir, f),
                        os.path.join(outDir, f)
                    )
            for suffix in self.Outputs["sampleDiagnostics"]:
                if f == f"{fname}.{suffix}":
                    if not os.path.isdir(diagDir):
                        makeDir(diagDir)
                    shutil.copyfile(
                        os.path.join(self.gudrunDir, f),
                        os.path.join(diagDir, f)
                    )
