import os
import shutil
import typing
from dataclasses import dataclass
from core.utils import makeDir
import tempfile


@dataclass
class SampleOutput:
    sampleFile: str
    gudFile: str
    outputs: typing.Dict[str, str]


@dataclass
class GudrunOutput:
    path: str
    name: str
    inputFile: str
    sampleOutputs: typing.Dict[str, SampleOutput]

    def gudFiles(self) -> list[str]:
        return [so.gudFile for so in self.sampleOutputs.values()]

    def gudFile(self, idx: int = None, *, name: str = None) -> str:
        if idx is not None:
            asList = list(self.sampleOutputs.values())
            assert (idx < len(asList))
            return asList[idx].gudFile
        elif name is not None:
            assert (name in self.sampleOutputs)
            return self.sampleOutputs[name].gudFile


class OutputFileHandler():

    def __init__(self, gudrunFile, head="", overwrite=True):
        """
        Initialise `OutputFileHandler`

        Parameters
        ----------
        gudrunFile : GudrunFile
            Gudrun file object that defines run parameters
        head : str, optional
            Where to branch outputs, if desired, by default ""
        overwrite : bool, optional
            Whether or not to overwrite previous output directiory,
            by default True
        """

        self.gudrunFile = gudrunFile
        # List of run samples
        self.samples = []
        # Directory where Gudrun files are outputted (temp)
        self.gudrunDir = self.gudrunFile.instrument.GudrunInputFileDir
        # Make sure it is a temporary directory
        assert (self.gudrunDir.startswith(tempfile.gettempdir()))
        # Temporary output dir paths
        self.tempOutDir = os.path.join(self.gudrunDir, os.path.splitext(
            self.gudrunFile.filename)[0])
        if head:
            self.tempOutDir = os.path.join(
                self.tempOutDir, f"{head}")

        # Name the output directory as the input file
        self.outputDir = os.path.join(
            self.gudrunFile.inputFileDir,
            os.path.splitext(self.gudrunFile.filename)[0],
            f"{head}"
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

        # If output directory exists, move to a temp dir and clear it
        # Avoids shutil.rmtree
        if overwrite is True and os.path.exists(self.outputDir):
            with tempfile.TemporaryDirectory() as tmp:
                shutil.move(self.outputDir, os.path.join(tmp, "prev"))

    def organiseOutput(self):
        """Organises Gudrun outputs

        Returns
        -------
        GudrunOutput : GudrunOutput
            Dataclass containing information about important paths
        """
        # Create normalisation and sample background folders
        self._createNormDir(self.tempOutDir)
        self._createSampleBgDir(self.tempOutDir)
        # Create sample folders
        sampleOutputs = self._createSampleDir(self.tempOutDir)
        # Create additonal output folders
        inputFile = self._createAddOutDir(self.tempOutDir)
        # Move over folders to output directory
        makeDir(self.outputDir)
        for root, dirs, files in os.walk(self.tempOutDir):
            r = os.path.join(
                self.gudrunFile.inputFileDir,
                root.partition(self.gudrunDir + "/")[-1])
            for d in dirs:
                makeDir(os.path.join(r, d))
            for f in files:
                shutil.copyfile(
                    os.path.join(root, f),
                    os.path.join(r, f)
                )

        return GudrunOutput(path=self.outputDir,
                            name=os.path.splitext(self.gudrunFile.filename)[0],
                            inputFile=inputFile,
                            sampleOutputs=sampleOutputs
                            )

    def _createNormDir(self, dest):
        """
        Creates directories for normalisation background
        and normalisation outputs.

        Parameters
        ----------
        dest : str
            Path to target output directory
        """
        # Create normalisation folders and move datafiles
        for normFile in self.gudrunFile.normalisation.dataFiles:
            self._copyOutputs(
                normFile, os.path.join(
                    dest, "Normalisation"))
        for normBgFile in self.gudrunFile.normalisation.dataFilesBg:
            self._copyOutputs(normBgFile,
                              os.path.join(dest,
                                           "NormalisationBackground"))

    def _createSampleBgDir(self, dest):
        """
        Creates output directory for sample backgrounds

        Parameters
        ----------
        dest : str
            Path to target output directory
        """
        # Iterate through all sample backgrounds
        for count, sampleBackground in enumerate(
                self.gudrunFile.sampleBackgrounds):
            # Move all datafiles into their sample background folder
            # Creates the folder if there is none
            for dataFile in sampleBackground.dataFiles:
                self._copyOutputs(
                    dataFile,
                    os.path.join(
                        dest, "SampleBackgrounds",
                        f"SampleBackground{count + 1}")
                )

    def _createSampleDir(self, dest):
        """
        Creates output directory for each sample

        Parameters
        ----------
        dest : str
            Path to target output directory
        samples : Sample[]
            List of samples in a sample background
        tree : str, optional
            Target basename if running iteratively,
            is the root folder of the sample folders
            by default ""

        Returns
        --------
        sampleOutputs : Dict[str, SampleOutput]
            Dictionary mapping sample names to the paths
            of their useful outputs

        """
        sampleOutputs = {}
        # Create sample folders within background folders
        for sample in self.samples:
            sampleFile = ""
            gudFile = ""
            sampleOutput = {}

            samplePath = os.path.join(
                dest,
                sample.name.replace(" ", "_")
            )
            # Move datafiles to sample folder
            for idx, dataFile in enumerate(sample.dataFiles):
                out = self._copyOutputsByExt(
                    dataFile,
                    samplePath
                )
                if idx == 0 and out[dataFile]:
                    sampleOutput = out
                    gudFile = (out[dataFile][".gud"]
                               if ".gud" in out[dataFile] else "")
            # Copy over .sample file
            if os.path.exists(os.path.join(
                    self.gudrunDir, sample.pathName())):
                shutil.copyfile(
                    os.path.join(self.gudrunDir, sample.pathName()),
                    os.path.join(samplePath, sample.pathName())
                )
                self.copiedFiles.append(sample.pathName())

            # Path to sample file output
            sampleFile = os.path.join(
                self.outputDir,
                sample.name.replace(" ", "_"),
                sample.pathName())

            sampleOutputs[sample.name] = SampleOutput(
                sampleFile, gudFile, sampleOutput)

            # Create container folders within sample folder
            for container in sample.containers:
                containerPath = os.path.join(
                    samplePath,
                    (container.name.replace(" ", "_")
                     if container.name != "CONTAINER"
                     else "Container"))
                for dataFile in container.dataFiles:
                    self._copyOutputs(
                        dataFile,
                        containerPath
                    )
        return sampleOutputs

    def _createAddOutDir(self, dest):
        """
        Copy over all files that haven't been copied over,
        as specified in `copiedFiles`

        Parameters
        ----------
        dest : str
            Directory for the files to be copied to

        Returns
        -------
        inputFile : str
            Path to the input file
        """
        addDir = makeDir(os.path.join(dest, "AdditionalOutputs"))
        inputFile = ""

        for f in os.listdir(self.gudrunDir):
            if f == self.gudrunFile.outpath:
                inputFile = os.path.join(
                    self.outputDir, "AdditionalOutputs", f)
                shutil.copyfile(
                    os.path.join(self.gudrunDir, f),
                    os.path.join(addDir, f)
                )
            elif f not in self.copiedFiles and os.path.isfile(
                    os.path.join(self.gudrunDir, f)):
                shutil.copyfile(
                    os.path.join(self.gudrunDir, f),
                    os.path.join(addDir, f)
                )
            return inputFile

    def _copyOutputs(self, fpath, dest):
        """
        Copy all files with the same basename
        as the provided filepath, except the original file.
        Creates a folder in the target directory and all necessary
        directories.

        Parameters
        ----------
        fpath : str
            Full filename of target file
        dest : str
            Directory for the files to be copied to
        """
        fname = os.path.splitext(fpath)[0]
        runDir = os.path.join(dest, fname)
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

    def _copyOutputsByExt(self, fpath, dest):
        """
        Copy all files with the same basename
        as the provided filepath and splits them into outputs
        and diagnostics folders based on their extension.
        Creates a folder in the target directory and all necessary
        directories.

        Parameters
        ----------
        fpath : str
            Full filename of target file
        suffixes : str[]
            List of target file extenstions
        dest : str
            Directory for the files to be copied to

        Returns
        -------
        outputs : Dict[str, str]
            Dictionary mapping output extension to filepath
        """
        # Data filename
        fname = os.path.splitext(fpath)[0]
        # Path to folder which will hold all outputs from the run
        runDir = os.path.join(dest, fname)
        # Path to folder which will hold Gudrun outputs
        outDir = makeDir(os.path.join(runDir, "Outputs"))
        # Path to folder which will hold Gudrun diagnostic outputs
        diagDir = makeDir(os.path.join(runDir, "Diagnostics"))

        outputs = {}
        outputs[fpath] = {}
        for f in os.listdir(self.gudrunDir):
            # If the file has the same name as requested filename
            fn, ext = os.path.splitext(f)
            if fn == fname:
                # Set dir depending on file extension
                dir = outDir if ext in self.outputExts else diagDir
                if dir == outDir:
                    outputs[fpath][ext] = os.path.join(
                        self.outputDir, "Outputs", f)
                shutil.copyfile(
                    os.path.join(self.gudrunDir, f),
                    os.path.join(dir, f)
                )
                self.copiedFiles.append(f)
        return outputs
