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
        """
        Creates directories for normalisation background
        and normalisation outputs.

        Parameters
        ----------
        outputDir : str
            Path to target output directory
        """
        # Create normalisation folders and move datafiles
        for normFile in self.gudrunFile.normalisation.dataFiles:
            self.copyOutputs(normFile, os.path.join(outputDir, self.NORM))
        for normBgFile in self.gudrunFile.normalisation.dataFilesBg:
            self.copyOutputs(normBgFile,
                             os.path.join(outputDir, self.NORM_BG))

    def createSampleBgDir(self, outputDir):
        """
        Creates output directory for sample backgrounds

        Parameters
        ----------
        outputDir : str
            Path to target output directory
        """
        # Iterate through all sample backgrounds
        for count, sampleBackground in enumerate(
                self.gudrunFile.sampleBackgrounds):
            # Move all datafiles into their sample background folder
            # Creates the folder if there is none
            for dataFile in sampleBackground.dataFiles:
                self.copyOutputs(
                    dataFile,
                    os.path.join(
                        outputDir, self.SAMPLE_BGS,
                        f"{self.SAMPLE_BG}{count + 1}")
                )

    def createSampleDir(self, outputDir, samples, tree=""):
        """
        Creates output directory for each sample

        Parameters
        ----------
        outputDir : str
            Path to target output directory
        samples : Sample[]
            List of samples in a sample background
        tree : str, optional
            Target basename if running iteratively,
            is the root folder of the sample folders
            by default ""

        """
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
            # Move datafiles to sample folder
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

    def naiveOrganise(self):
        """Organises Gudrun outputs
        """
        # Create normalisation and sample background folders
        self.createNormDir(self.outputDir)
        self.createSampleBgDir(self.outputDir)
        # Create sample folders
        for sampleBackground in self.gudrunFile.sampleBackgrounds:
            self.createSampleDir(
                self.outputDir,
                sampleBackground.samples)

    def iterativeOrganise(self, nTotal, nCurrent, head):
        """
        Organises Gudrun outputs when it is run
        iteratively

        Parameters
        ----------
        nTotal : int
            Total number of iterations
        nCurrent : int
            Current iteration
        head : str
            Intended basename for folders
            which gets incremented per iteration
        """
        if nCurrent == 0:
            # Create the normalisation and sample background directories
            # if this is the first iteration
            self.createNormDir(self.outputDir)
            self.createSampleBgDir(
                self.outputDir)
        # Create the sample output folders
        for sampleBackground in self.gudrunFile.sampleBackgrounds:
            self.createSampleDir(
                self.gudrunDir,
                sampleBackground.samples,
                f"{head}_{nCurrent + 1}")
            if nCurrent == nTotal:
                # If this is the final iteration, move root folder
                # to output folder
                for sample in [
                    s for s in sampleBackground.samples
                    if s.runThisSample and len(s.dataFiles)
                ]:
                    shutil.move(
                        os.path.join(self.gudrunDir, sample.name),
                        uniquify(
                            os.path.join(
                                self.outputDir,
                                sample.name))
                    )

    def copyOutputs(self, fpath, targetDir):
        """
        Copy all files with the same basename
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
        Copy all files with the same basename
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
        # Data filename
        fname = os.path.splitext(fname)[0]
        # Path to folder which will hold all outputs from the run
        runDir = os.path.join(targetDir, fname)
        # Path to folder which will hold Gudrun outputs
        outDir = os.path.join(runDir, self.OUTPUTS)
        # Path to folder which will hold Gudrun diagnostic outputs
        diagDir = os.path.join(runDir, self.DIAGNOSTICS)
        for f in os.listdir(self.gudrunDir):
            # Moving all files with output file extensions
            for suffix in self.Outputs["sampleOutputs"]:
                if f == f"{fname}.{suffix}":
                    if not os.path.isdir(outDir):
                        makeDir(outDir)
                    shutil.copyfile(
                        os.path.join(self.gudrunDir, f),
                        os.path.join(outDir, f)
                    )
            # Moving all files with diagnostic file extensions
            for suffix in self.Outputs["sampleDiagnostics"]:
                if f == f"{fname}.{suffix}":
                    if not os.path.isdir(diagDir):
                        makeDir(diagDir)
                    shutil.copyfile(
                        os.path.join(self.gudrunDir, f),
                        os.path.join(diagDir, f)
                    )
