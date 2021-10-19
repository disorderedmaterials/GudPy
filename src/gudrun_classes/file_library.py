import os
import sys
from src.gudrun_classes.enums import CrossSectionSource


class GudPyFileLibrary():
    """
    Class to represent a GudPyFileLibrary,
    (all files related to the input file).
    ...

    Attributes
    ----------
    dirs : str[]
        List of directories.
    files: str[]
        List of files
    Methods
    -------
    checkFilesExist()
        Checks if the files and directories exist, in the current file system.
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
        dataFileType = gudrunFile.instrument.dataFileType
        dataFileDir = gudrunFile.instrument.dataFileDir

        # Collect directories.
        self.dirs = [
            gudrunFile.instrument.GudrunInputFileDir,
            gudrunFile.instrument.dataFileDir,
            gudrunFile.instrument.GudrunStartFolder,
            gudrunFile.instrument.startupFileFolder,
        ]

        suffix = gudrunFile.instrument.GudrunStartFolder

        # Collect files of static objects.
        self.files = [
            os.path.join(suffix, gudrunFile.instrument.groupFileName),
            os.path.join(
                suffix, gudrunFile.instrument.deadtimeConstantsFileName
            ),
            os.path.join(
                suffix, gudrunFile.instrument.neutronScatteringParametersFile
            ),
            os.path.join(
                suffix, gudrunFile.beam.filenameIncidentBeamSpectrumParams
            ),
            *[
                os.path.join(dataFileDir, df)
                for df in gudrunFile.normalisation.dataFiles.dataFiles
            ],
            *[
                os.path.join(dataFileDir, df)
                for df in gudrunFile.normalisation.dataFilesBg.dataFiles
            ]
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
            self.files = [
                *self.files,
                *[
                    os.path.join(dataFileDir, df)
                    for df in sampleBackground.dataFiles.dataFiles
                ]
            ]

            for sample in sampleBackground.samples:
                self.files = [
                    *self.files,
                    *[
                        os.path.join(dataFileDir, df)
                        for df in sample.dataFiles.dataFiles
                    ]
                ]
                if sample.totalCrossSectionSource == CrossSectionSource.FILE:
                    self.files.append(sample.crossSectionFilename)

                for container in sample.containers:
                    self.files = [
                        *self.files,
                        *[
                            os.path.join(dataFileDir, df)
                            for df in container.dataFiles.dataFiles
                        ]
                    ]
                    if container.totalCrossSectionSource == (
                        CrossSectionSource.FILE
                    ):
                        self.files.append(container.crossSectionFilename)

    def checkFilesExist(self):
        """
        Checks that the files and directories in the file system exist.

        Returns
        -------
        (bool, str)[]
            List of tuples of boolean values and paths,
            indicating if the given path exists.
        """
        return [
            (os.path.isfile(path) | os.path.isdir(path), path)
            for path in self.files
        ]
