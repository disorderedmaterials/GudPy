import os
import shutil


class OutputFileHandler():
    """
    Class to handle organising the output files of Gudrun.

    ...

    Parameters
    ----------
    gudrunFile : GudrunFile
        Reference GudrunFile object.
    outputs : str[]{}
        Dictionary of output files.
    runFiles : str[]

    Methods
    -------
    getRunFiles()
        Sets the run files.
    organiseSampleFiles(run, sampleRunFile, tree="")
        Organises sample output files.
    naiveOrganise()
        Performs a naive organise.
    iterativeOrganise(head)
        Performs an iterative organise using `head`.
    """
    def __init__(self, gudrunFile):
        """
        Sets up all the attributes for the OutputFileHandler class.
        Collects the run files.

        Parameters
        ----------
        gudrunFile : GudrunFile
            Reference GudrunFile object.
        """
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
        """
        Collects and assigns the run files.
        Each run file is prefixed with the name of the first
        data file belonging to the Sample.
        """
        self.runFiles = [
            [os.path.splitext(s.dataFiles[0])[0], s.pathName()]
            for sampleBackground in self.gudrunFile.sampleBackgrounds
            for s in sampleBackground.samples if s.runThisSample
            and len(s.dataFiles)
        ]

    def organiseSampleFiles(self, run, sampleRunFile, tree=""):
        """
        Organises the Sample outputs according to `tree`.

        Parameters
        ----------
        run : str
            Run file name, without extension.
        sampleRunFile : str
            Run file name, with extension.
        tree : str, optional
            Structure to use.
        """
        dir = self.gudrunFile.instrument.GudrunInputFileDir

        # If tree is present, construct the paths
        # otherwise, just use the current directory as the root.
        if tree:
            outputDir = os.path.join(dir, tree, run)
        else:
            outputDir = os.path.join(dir, run)
            # Remove tree if it exists.
            if os.path.exists(outputDir):
                shutil.rmtree(outputDir)
        
        # Set up necessary directories.
        if not os.path.exists(outputDir):
            os.makedirs(outputDir)
        os.makedirs(os.path.join(outputDir, "outputs"))
        os.makedirs(os.path.join(outputDir, "diagnostics"))

        # Copy relevant files into newly created directories.``
        if os.path.exists(os.path.join(dir, sampleRunFile)):
            shutil.copyfile(
                os.path.join(dir, sampleRunFile),
                os.path.join(outputDir, "outputs", sampleRunFile)
            )
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
        """
        Performs a naive organise of output files.
        This simply creates a directory named after the first data file
        (i.e. what the results are merged to), and creates the
        diagnostic / output directories there.
        """
        for run, runFile in self.runFiles:
            self.organiseSampleFiles(run, runFile)

    def iterativeOrganise(self, head):
        """
        Performs an 'iterative' organise of output files.
        This simply creates a directory named `head`, and
        naively organises output files into there.
        
        Parameters
        ----------
        head : str
            Root directory name.
        """
        path = os.path.join(
            self.gudrunFile.instrument.GudrunInputFileDir,
            head
        )
        if os.path.exists(path):
            shutil.rmtree(path)
        for run, runFile in self.runFiles:
            self.organiseSampleFiles(run, runFile, tree=head)
