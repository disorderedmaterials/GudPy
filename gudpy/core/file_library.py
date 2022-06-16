import os
from zipfile import ZipFile, ZIP_DEFLATED
from pathlib import Path

from core.enums import CrossSectionSource


class GudPyFileLibrary():
    """
    Class to represent a GudPyFileLibrary,
    (all files related to the input file).
    ...

    Attributes
    ----------
    gudrunFile : GudrunFile
        Reference GudrunFile object.
    dataFileDir : str
        Data file directory.
    fileDir : str
        Gudrun input filele directory.
    dirs : str[]
        List of directories.
    files: str[]
        List of files
    dataFiles : str[]
        List of data files.

    Methods
    -------
    checkFilesExist()
        Checks if the files and directories exist, in the current file system.
    exportMintData(samples, renameDataFiles=False, exportTo=None, includeParams=False)
        Exports mint data.
    """

    def __init__(self, gudrunFile):
        """
        Constructs the lists of directories and files which
        the file system consists of.

        Parameters
        ----------
        gudrunFile: GudrunFile
            Input file to create file system from.
        """
        self.gudrunFile = gudrunFile
        self.dataFileDir = gudrunFile.instrument.dataFileDir
        self.fileDir = gudrunFile.instrument.GudrunStartFolder
        dataFileType = gudrunFile.instrument.dataFileType

        # Collect directories
        self.dirs = [
            gudrunFile.instrument.GudrunInputFileDir,
            gudrunFile.instrument.dataFileDir,
            gudrunFile.instrument.GudrunStartFolder,
            gudrunFile.instrument.startupFileFolder
        ]

        # Collect files of static objects
        self.files = [
            gudrunFile.instrument.groupFileName,
            gudrunFile.instrument.deadtimeConstantsFileName,
            gudrunFile.instrument.neutronScatteringParametersFile,
            gudrunFile.beam.filenameIncidentBeamSpectrumParams,
        ]

        self.dataFiles = [
            *gudrunFile.normalisation.dataFiles.dataFiles,
            *gudrunFile.normalisation.dataFilesBg.dataFiles
        ]

        # If NXS files are being used
        # then we also need the nexus definition file.
        if dataFileType.lower() == "nxs":
            self.files.append(gudrunFile.instrument.nxsDefinitionFile)

        # If the Total Cross Section Source of any object uses a file,
        # then we need to incldue that file.
        if gudrunFile.normalisation.totalCrossSectionSource == (
            CrossSectionSource.FILE
        ):
            self.files.append(gudrunFile.normalisation.crossSectionFilename)

        # Iterate through SampleBackgrounds, Samples and Containers,
        # collecting their data files and if they are using
        # a file for the Total Cross Section Source, then collect
        # that file too.

        for sampleBackground in gudrunFile.sampleBackgrounds:
            self.dataFiles.extend(sampleBackground.dataFiles.dataFiles)

            for sample in sampleBackground.samples:
                self.dataFiles.extend(sample.dataFiles.dataFiles)
                if sample.totalCrossSectionSource == CrossSectionSource.FILE:
                    self.files.append(sample.crossSectionFilename)

                for container in sample.containers:
                    self.dataFiles.extend(container.dataFiles.dataFiles)
                    if container.totalCrossSectionSource == (
                        CrossSectionSource.FILE
                    ):
                        self.files.append(container.crossSectionFilename)

    def checkFilesExist(self):
        """
        Checks that the files and directories in the file system exist.

        Returns
        -------
        (bool, str)[] : 
            List of tuples of boolean values and paths,
            indicating if the given path exists.
        """
        return [
            *[
                (
                    (
                        os.path.isdir(dir_)
                        | os.path.isdir(os.path.join(self.fileDir, dir_)),
                    ),
                    dir_
                )
                for dir_ in self.dirs
            ],
            *[
                (
                    (
                        os.path.isfile(file)
                        | os.path.isfile(os.path.join(self.fileDir, file))
                        | (file == "*")
                    ),
                    file
                )
                for file in self.files
            ],
            *[
                (
                    os.path.isfile(os.path.join(self.dataFileDir, dataFile)),
                    dataFile
                )
                for dataFile in self.dataFiles
            ]
        ]

    def exportMintData(
        self, samples, renameDataFiles=False,
        exportTo=None, includeParams=False
    ):
        """
        Exports mint01 files outputted from given `samples`.

        Parameters
        ----------
        samples : Sample[]
            List of Sample objects to export.
        renameDataFiles : bool, optional
            Should mint01 files be renamed to sample?
        exportTo : NoneType | str, optional
            Export target.
        includeParams : bool, optional
            Should a sample parameters file be produced for each sample?
        

        Returns
        -------
        str : path to produced zip file.
        """
        if not exportTo:
            exportTo = (
                os.path.join(
                    self.gudrunFile.instrument.GudrunInputFileDir,
                    Path(self.gudrunFile.path).stem + ".zip"
                )
            )
        with ZipFile(exportTo, "w", ZIP_DEFLATED) as zipFile:
            for sample in samples:
                if len(sample.dataFiles.dataFiles):
                    path = os.path.join(
                        self.gudrunFile.instrument.GudrunInputFileDir,
                        sample.dataFiles.dataFiles[0].replace(
                            self.gudrunFile.instrument.dataFileType,
                            "mint01"
                        )
                    )
                safeSampleName = sample.name.replace(" ", "_").translate(
                    {ord(x): '' for x in r'/\!*~,&|[]'}
                )
                if os.path.exists(path):
                    outpath = path
                    if renameDataFiles:
                        newName = safeSampleName + ".mint01"
                        outpath = newName
                    zipFile.write(path, arcname=os.path.basename(outpath))
                    if includeParams:
                        path = os.path.join(
                            self.gudrunFile.instrument.GudrunInputFileDir,
                            safeSampleName + ".sample"
                        )
                        if not os.path.exists(path):
                            sample.write_out(
                                self.gudrunFile.instrument.GudrunInputFileDir
                            )
                        zipFile.write(path, arcname=os.path.basename(path))

            return zipFile.filename
