import os
from src.gudrun_classes.enums import CrossSectionSource


class GudPyFileSystem():

    def __init__(self, gudrunFile):
        dataFileType = gudrunFile.instrument.dataFileType
        dataFileDir = gudrunFile.instrument.dataFileDir
        self.dirs = [
            gudrunFile.instrument.GudrunInputFileDir,
            gudrunFile.instrument.dataFileDir,
            gudrunFile.instrument.GudrunStartFolder,
            gudrunFile.instrument.startupFileFolder,
        ]
        self.files = [
            os.path.join("bin", gudrunFile.instrument.groupFileName),
            os.path.join(
                "bin", gudrunFile.instrument.deadtimeConstantsFileName
            ),
            os.path.join(
                "bin", gudrunFile.instrument.neutronScatteringParametersFile
            ),
            os.path.join(
                "bin", gudrunFile.beam.filenameIncidentBeamSpectrumParams
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

        if dataFileType.lower() == "nxs":
            self.files.append(gudrunFile.instrument.nxsDefinitionFile)

        if gudrunFile.normalisation.totalCrossSectionSource == (
            CrossSectionSource.FILE
        ):
            self.files.append(gudrunFile.normalisation.crossSectionFilename)

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
        return [
            (os.path.isfile(path) | os.path.isdir(path), path)
            for path in self.files
        ]
