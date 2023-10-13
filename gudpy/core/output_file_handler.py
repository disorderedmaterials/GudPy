import os
import shutil
from core.utils import makeDir, uniquify


class OutputFileHandler():

    def __init__(self, gudrunFile):
        self.gudrunFile = gudrunFile
        # List of run samples
        self.samples = []
        # Directory where Gudrun files are outputted (temp)
        self.gudrunDir = self.gudrunFile.instrument.GudrunInputFileDir
        # Temporary output dir paths
        self.tempOutDir = os.path.join(self.gudrunDir, os.path.splitext(
            self.gudrunFile.filename)[0])
        self.samplePaths = []
        # Name the output directory as the input file
        self.outputDir = os.path.join(
            self.gudrunFile.inputFileDir,
            os.path.splitext(self.gudrunFile.filename)[0]
        )
        # Files that have been copied
        self.copiedFiles = []
        self.outputExts = [
            ".dcs01",
            ".dcsd01",
            ".dcse01",
            ".dcst01",
            ".dscw01",
            ".mdcs01",
            ".mdcsd01",
            ".mdcse01",
            ".mdcsw01",
            ".mint01",
            ".mgor01",
            ".mdor01",
            ".gud",
            ".sample"
        ]

        # Generating paths
        for sampleBackground in self.gudrunFile.sampleBackgrounds:
            for sample in [
                    s for s in sampleBackground.samples
                    if s.runThisSample and len(s.dataFiles)]:
                self.samples.append(sample)

    def naiveOrganise(self):
        """Organises Gudrun outputs
        """
        # Create normalisation and sample background folders
        self.createNormDir(self.tempOutDir)
        self.createSampleBgDir(self.tempOutDir)
        # Create sample folders
        self.createSampleDir(self.tempOutDir)
        # Create additonal output folders
        self.createAddOutDir(self.tempOutDir)
        # Move over samples to output directory
        self.exportTempDir()

    def iterativeOrganise(self, nCurrent, head):
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
        iterName = f"{head}_{nCurrent + 1}"
        iterDir = os.path.join(self.tempOutDir, iterName)

        # Create the normalisation and sample background directories
        # if this is the first iteration
        self.createNormDir(iterDir)
        self.createSampleBgDir(iterDir)

        # Create the sample output folders
        self.createSampleDir(iterDir)

        self.createAddOutDir(iterDir)

        self.exportTempDir()

    def createNormDir(self, targetDir):
        """
        Creates directories for normalisation background
        and normalisation outputs.

        Parameters
        ----------
        targetDir : str
            Path to target output directory
        """
        # Create normalisation folders and move datafiles
        for normFile in self.gudrunFile.normalisation.dataFiles:
            self.copyOutputs(
                normFile, os.path.join(
                    targetDir, "Normalisation"))
        for normBgFile in self.gudrunFile.normalisation.dataFilesBg:
            self.copyOutputs(normBgFile,
                             os.path.join(targetDir,
                                          "NormalisationBackground"))

    def createSampleBgDir(self, targetDir):
        """
        Creates output directory for sample backgrounds

        Parameters
        ----------
        targetDir : str
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
                        targetDir, "SampleBackgrounds",
                        f"SampleBackground{count + 1}")
                )

    def createSampleDir(self, targetDir):
        """
        Creates output directory for each sample

        Parameters
        ----------
        targetDir : str
            Path to target output directory
        samples : Sample[]
            List of samples in a sample background
        tree : str, optional
            Target basename if running iteratively,
            is the root folder of the sample folders
            by default ""

        """
        # Create sample folders within background folders
        for sample in self.samples:
            samplePath = uniquify(os.path.join(
                targetDir,
                sample.name
            ))
            # Move datafiles to sample folder
            for dataFile in sample.dataFiles:
                self.copyOutputsByExt(
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
                self.copiedFiles.append(sample.pathName())

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

    def createAddOutDir(self, targetDir):
        """
        Copy over all files that haven't been copied over,
        as specified in `copiedFiles`

        Parameters
        ----------
        targetDir : str
            Directory for the files to be copied to
        """
        addDir = makeDir(os.path.join(targetDir, "AdditionalOutputs"))

        for f in os.listdir(self.gudrunDir):
            if f == self.gudrunFile.outpath:
                shutil.copyfile(
                    os.path.join(self.gudrunDir, f),
                    os.path.join(targetDir, f)
                )
            elif f not in self.copiedFiles and os.path.isfile(
                    os.path.join(self.gudrunDir, f)):
                shutil.copyfile(
                    os.path.join(self.gudrunDir, f),
                    os.path.join(addDir, f)
                )

    def exportTempDir(self):
        """
        Copy temp dir into user's directory
        Overwrites if directory already exists
        """
        shutil.copytree(
            os.path.join(self.tempOutDir),
            os.path.join(self.outputDir),
            dirs_exist_ok=True
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
            if os.path.splitext(f)[0] == fname:
                if not dirCreated:
                    makeDir(runDir)
                    dirCreated = True
                shutil.copyfile(
                    os.path.join(self.gudrunDir, f),
                    os.path.join(runDir, f)
                )
                self.copiedFiles.append(f)

    def copyOutputsByExt(self, fname, targetDir):
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
        outDir = makeDir(os.path.join(runDir, "Outputs"))
        # Path to folder which will hold Gudrun diagnostic outputs
        diagDir = makeDir(os.path.join(runDir, "Diagnostics"))
        for f in os.listdir(self.gudrunDir):
            # If the file has the same name as requested filename
            fn, ext = os.path.splitext(f)
            if fn == fname:
                # Set dir depending on file extension
                dir = outDir if ext in self.outputExts else diagDir
                shutil.copyfile(
                    os.path.join(self.gudrunDir, f),
                    os.path.join(dir, f)
                )
                self.copiedFiles.append(f)
