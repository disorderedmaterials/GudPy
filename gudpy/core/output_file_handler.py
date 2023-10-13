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
        self.tempOutDir = {
            "root": os.path.join(self.gudrunDir, "out"),
            "samps": [],
            "add": ""
        }
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
                # Generate unique paths for sample output directories
                self.tempOutDir["samps"].append(
                    os.path.join(
                        self.tempOutDir["root"],
                        uniquify(os.path.join(
                            self.outputDir,
                            sample.name
                        )).partition(self.outputDir + "/")[-1]
                    )
                )
        # Generate unique path for Additional Outputs folder
        self.tempOutDir["add"] = os.path.join(
            self.tempOutDir["root"],
            uniquify(os.path.join(
                self.outputDir,
                "AdditionalOutputs"
            )).partition(self.outputDir + "/")[-1]
        )

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
            self.copyOutputs(
                normFile, os.path.join(
                    outputDir, "Normalisation"))
        for normBgFile in self.gudrunFile.normalisation.dataFilesBg:
            self.copyOutputs(normBgFile,
                             os.path.join(outputDir,
                                          "NormalisationBackground"))

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
                        outputDir, "SampleBackgrounds",
                        f"SampleBackground{count + 1}")
                )

    def createSampleDir(self, outputDir, tree=""):
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
        for sample in self.samples:
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
                self.copyOutputsByExt(
                    dataFile,
                    samplePath
                )
            # Copy over .sample file
            if os.path.exists(os.path.join(
                    self.gudrunDir, sample.pathName())):
                makeDir(samplePath)
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

    def naiveOrganise(self):
        """Organises Gudrun outputs
        """
        # Create normalisation and sample background folders
        self.createNormDir(self.outputDir)
        self.createSampleBgDir(self.outputDir)
        # Create sample folders
        self.createSampleDir(
            self.tempOutDir["root"])
        # Copy remaining outputs
        self.copyRemaining(self.tempOutDir["add"])
        # Move over sample & additional outputs to output directory
        for folder in os.listdir(self.tempOutDir["root"]):
            shutil.move(
                os.path.join(self.tempOutDir["root"], folder),
                uniquify(os.path.join(self.outputDir, folder))
            )

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
        iterName = f"{head}_{nCurrent + 1}"

        if nCurrent == 0:
            # Create the normalisation and sample background directories
            # if this is the first iteration
            self.createNormDir(self.outputDir)
            self.createSampleBgDir(
                self.outputDir)
            for sampleDir in self.tempOutDir["samps"]:
                makeDir(sampleDir)

        # Create the sample output folders
        self.createSampleDir(
            self.gudrunDir,
            iterName)

        self.copyRemaining(os.path.join(
            self.tempOutDir["add"],
            iterName))

        # Copy organised folder to temporary sample output dir
        for sample, sampleOutDir in zip(
                self.samples, self.tempOutDir["samps"]):
            shutil.move(
                os.path.join(
                    self.gudrunDir,
                    sample.name,
                    iterName),
                sampleOutDir
            )
        # Move over sample & additional outputs to output directory
        for folder in os.listdir(self.tempOutDir["root"]):
            shutil.move(
                os.path.join(self.tempOutDir["root"], folder, iterName),
                os.path.join(self.outputDir, folder, iterName)
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

    def copyRemaining(self, targetDir):
        """
        Copy over all files that haven't been copied over,
        as specified in `copiedFiles`

        Parameters
        ----------
        targetDir : str
            Directory for the files to be copied to
        """
        makeDir(targetDir)

        for f in os.listdir(self.gudrunDir):
            if f not in self.copiedFiles and os.path.isfile(
                    os.path.join(self.gudrunDir, f)):
                shutil.copyfile(
                    os.path.join(self.gudrunDir, f),
                    os.path.join(targetDir, f)
                )
