import os
from zipfile import ZipFile, ZIP_DEFLATED
from pathlib import Path

from core import utils
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

    def __init__(self, params):
        """
        Constructs the lists of directories and files which
        the file system consists of.

        Parameters
        ----------
        params: params
            Data to create file system from.
        """
        self.params = params
        self.dataFileDir = params.instrument.dataFileDir
        self.fileDir = params.instrument.GudrunStartFolder
        dataFileType = params.instrument.dataFileType

        # Collect directories
        self.dirs = {
            "Data file directory": params.instrument.dataFileDir,
            "Gudrun start folder": params.instrument.GudrunStartFolder,
            "Startup file folder": params.instrument.startupFileFolder,
        }

        # Collect files of static objects
        self.files = {
            "Detector Calibration File": (
                params.instrument.detectorCalibrationFileName
            ),
            "Groups File": params.instrument.groupFileName,
            "Deadtime Constants File": (
                params.instrument.deadtimeConstantsFileName
            ),
            "Scattering Lengths File": (
                params.instrument.neutronScatteringParametersFile
            ),
            "Incident Beam Spectrum Parameters": (
                params.beam.filenameIncidentBeamSpectrumParams
            ),
        }

        self.dataFiles = [
            *params.normalisation.dataFiles.dataFiles,
            *params.normalisation.dataFilesBg.dataFiles,
        ]

        # If NXS files are being used
        # then we also need the nexus definition file.
        if dataFileType.lower() == "nxs":
            self.files[
                "NeXus Definition File"
            ] = params.instrument.nxsDefinitionFile

        # If the Total Cross Section Source of any object uses a file,
        # then we need to include that file.
        if params.normalisation.totalCrossSectionSource == (
            CrossSectionSource.FILE
        ):
            self.files[
                "Total cross section source"
            ] = params.normalisation.crossSectionFilename

        # Iterate through SampleBackgrounds, Samples and Containers,
        # collecting their data files and if they are using
        # a file for the Total Cross Section Source, then collect
        # that file too.

        for sampleBackground in params.sampleBackgrounds:
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
                self.params.projectDir,
                Path(self.params.path()).stem + ".zip",
            )
        with ZipFile(exportTo, "w", ZIP_DEFLATED) as zipFile:
            for sample in samples:
                if len(sample.dataFiles.dataFiles):
                    path = os.path.join(
                        self.params.projectDir,
                        sample.dataFiles.dataFiles[0].replace(
                            self.params.instrument.dataFileType, "mint01"
                        ),
                    )
                safeSampleName = utils.replace_unwanted_chars(
                    sample.name).translate(
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
                            self.params.projectDir,
                            safeSampleName + ".sample",
                        )
                        if not os.path.exists(path):
                            sample.write_out(
                                self.params.projectDir
                            )
                        zipFile.write(path, arcname=os.path.basename(path))

            return zipFile.filename
