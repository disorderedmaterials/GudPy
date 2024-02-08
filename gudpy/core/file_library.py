import os
from zipfile import ZipFile, ZIP_DEFLATED
from pathlib import Path

from core.enums import CrossSectionSource


class GudPyFileLibrary:
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
        self.gudrunFile = gudrunFile
        self.dataFileDir = gudrunFile.instrument.dataFileDir
        self.fileDir = gudrunFile.instrument.GudrunStartFolder
        dataFileType = gudrunFile.instrument.dataFileType

        # Collect directories
        self.dirs = {
            "Data file directory": gudrunFile.instrument.dataFileDir,
            "Gudrun start folder": gudrunFile.instrument.GudrunStartFolder,
            "Startup file folder": gudrunFile.instrument.startupFileFolder,
        }

        # Collect files of static objects
        self.files = {
            "Detector Calibration File": (
                gudrunFile.instrument.detectorCalibrationFileName
            ),
            "Groups File": gudrunFile.instrument.groupFileName,
            "Deadtime Constants File": (
                gudrunFile.instrument.deadtimeConstantsFileName
            ),
            "Scattering Lengths File": (
                gudrunFile.instrument.neutronScatteringParametersFile
            ),
            "Incident Beam Spectrum Parameters": (
                gudrunFile.beam.filenameIncidentBeamSpectrumParams
            ),
        }

        self.dataFiles = [
            *gudrunFile.normalisation.dataFiles.dataFiles,
            *gudrunFile.normalisation.dataFilesBg.dataFiles,
        ]

        # If NXS files are being used
        # then we also need the nexus definition file.
        if dataFileType.lower() == "nxs":
            self.files[
                "NeXus Definition File"
            ] = gudrunFile.instrument.nxsDefinitionFile

        # If the Total Cross Section Source of any object uses a file,
        # then we need to include that file.
        if gudrunFile.normalisation.totalCrossSectionSource == (
            CrossSectionSource.FILE
        ):
            self.files[
                "Total cross section source"
            ] = gudrunFile.normalisation.crossSectionFilename

        # Iterate through SampleBackgrounds, Samples and Containers,
        # collecting their data files and if they are using
        # a file for the Total Cross Section Source, then collect
        # that file too.

        for sampleBackground in gudrunFile.sampleBackgrounds:
            self.dataFiles.extend(sampleBackground.dataFiles.dataFiles)

            for sample in sampleBackground.samples:
                self.dataFiles.extend(sample.dataFiles.dataFiles)
                if sample.totalCrossSectionSource == CrossSectionSource.FILE:
                    self.files[sample.name] = sample.crossSectionFilename

                for container in sample.containers:
                    self.dataFiles.extend(container.dataFiles.dataFiles)
                    if container.totalCrossSectionSource == (
                        CrossSectionSource.FILE
                    ):
                        self.files[
                            container.name
                        ] = container.crossSectionFilename

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
            [
                *[
                    (
                        (
                            (
                                os.path.exists(dir_)
                                | os.path.exists(os.path.join(
                                    self.fileDir, dir_
                                ))
                                and dir_
                                and not os.path.isfile(dir_)
                                and dir_ != os.path.sep
                            )
                        ),
                        name,
                        dir_,
                    )
                    for name, dir_ in self.dirs.items()
                ],
                *[
                    (
                        (
                            os.path.isfile(file)
                            | os.path.isfile(os.path.join(self.fileDir, file))
                            | (file == "*")
                        ),
                        name,
                        file,
                    )
                    for name, file in self.files.items()
                ],
            ],
            [
                *[
                    (
                        os.path.isfile(os.path.join(
                            self.dataFileDir, dataFile)),
                        "Data files",
                        dataFile,
                    )
                    for dataFile in self.dataFiles
                ],
            ]
        ]

    def exportMintData(
        self,
        samples,
        renameDataFiles=False,
        exportTo=None,
        includeParams=False,
    ):
        if not exportTo:
            exportTo = os.path.join(
                self.gudrunFile.projectDir,
                Path(self.gudrunFile.path()).stem + ".zip",
            )
        with ZipFile(exportTo, "w", ZIP_DEFLATED) as zipFile:
            for sample in samples:
                if len(sample.dataFiles.dataFiles):
                    path = os.path.join(
                        self.gudrunFile.projectDir,
                        sample.dataFiles.dataFiles[0].replace(
                            self.gudrunFile.instrument.dataFileType, "mint01"
                        ),
                    )
                safeSampleName = sample.name.replace(" ", "_").translate(
                    {ord(x): "" for x in r"/\!*~,&|[]"}
                )
                if os.path.exists(path):
                    outpath = path
                    if renameDataFiles:
                        newName = safeSampleName + ".mint01"
                        outpath = newName
                    zipFile.write(path, arcname=os.path.basename(outpath))
                    if includeParams:
                        path = os.path.join(
                            self.gudrunFile.projectDir,
                            safeSampleName + ".sample",
                        )
                        if not os.path.exists(path):
                            sample.write_out(
                                self.gudrunFile.projectDir
                            )
                        zipFile.write(path, arcname=os.path.basename(path))

            return zipFile.filename
