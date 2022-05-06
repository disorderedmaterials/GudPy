from core.utils import numifyBool
from core.data_files import DataFiles
from core.composition import Composition
from core.enums import (
    CrossSectionSource, Geometry, UnitsOfDensity
)
from core import config


class Normalisation:
    """
    Class to represent Normalisation.

    ...

    Attributes
    ----------
    periodNumber : int
        Period number for data files.
    dataFiles : DataFiles
        DataFiles object storing data files belonging to the normalisation.
    periodNumberBg : int
        Period number for background data files.
    dataFilesBg : DataFiles
        DataFiles object storing background data files.
    composition : Composition
        Composition object storing the atomic composition of the container.
    geometry : Geometry
        Geometry of the normalisation (FLATPLATE / CYLINDRICAL / SameAsBeam).
    upstreamThickness : float
        Upstream thickness of the normalisation - if its geometry is FLATPLATE.
    downstreamThickness : float
        Downstream thickness of the normalisation - if its geometry
        is FLATPLATE.
    angleOfRotation : float
        Angle of rotation of the normalisation - if its geometry is FLATPLATE.
    sampleWidth : float
        Width of the normalisation - if its geometry is FLATPLATE.
    innerRadius : float
        Inner radius of the normalisation - if its geometry is CYLINDRICAL.
    outerRadius : float
        Outer radius of the normalisation - if its geometry is CYLINDRICAL.
    sampleHeight : float
        Height of the normalisation - if its geometry is CYLINDRICAL.
    density : float
        Density of normalisation
    densityUnits : int
        0 = atoms/Angstrom^3, 1 = gm/cm^3
    tempForNormalisationPC : float
        Temperature for Placzek correction.
    totalCrossSectionSource : CrossSectionSource
        TABLES / TRANSMISSION monitor / filename
    crossSectionFilename : str
        Filename for the total cross section source if applicable.
    normalisationDifferentialCrossSectionFile : str
        Name of the normalisation differential cross section file.
    lowerLimitSmoothedNormalisation : float
        Lowest accepted value for smoothed Vanadium.
        Detectors are rejected below this value.
    normalisationDegreeSmoothing : float
        Degree of smoothing on Vanadium.
    minNormalisationSignalBR : float
        Vanadium signal to background acceptance ratio.
    Methods
    -------
    """
    def __init__(self):
        """
        Constructs all the necessary attributes for the Normalistion object.

        Parameters
        ----------
        None
        """
        self.periodNumber = 1
        self.dataFiles = DataFiles([], "NORMALISATION")
        self.periodNumberBg = 1
        self.dataFilesBg = DataFiles([], "NORMALISATION BACKGROUND")
        self.forceCalculationOfCorrections = False
        self.composition = Composition("NORMALISATION")
        self.geometry = Geometry.SameAsBeam
        self.upstreamThickness = 0.0
        self.downstreamThickness = 0.0
        self.angleOfRotation = 0.0
        self.sampleWidth = 0.0
        self.innerRadius = 0.0
        self.outerRadius = 0.0
        self.sampleHeight = 0.0
        self.density = 0.0
        self.densityUnits = UnitsOfDensity.ATOMIC
        self.tempForNormalisationPC = 0.0
        self.totalCrossSectionSource = CrossSectionSource.TABLES
        self.crossSectionFilename = ""
        self.normalisationDifferentialCrossSectionFile = ""
        self.lowerLimitSmoothedNormalisation = 0.0
        self.normalisationDegreeSmoothing = 0.0
        self.minNormalisationSignalBR = 0.0

        self.yamlignore = {
            "yamlignore"
        }

    def __str__(self):
        """
        Returns the string representation of the Normalisation object.

        Parameters
        ----------
        None

        Returns
        -------
        string : str
            String representation of Normalisation.
        """

        dataFilesLineA = (
            f'{str(self.dataFiles)}\n'
            if len(self.dataFiles) > 0
            else
            ''
        )

        dataFilesLineB = (
            f'{str(self.dataFilesBg)}\n'
            if len(self.dataFilesBg.dataFiles) > 0
            else
            ''
        )

        compositionSuffix = "" if str(self.composition) == "" else "\n"

        geometryLine = (
            f'SameAsBeam{config.spc5}Geometry\n'
            if self.geometry == Geometry.SameAsBeam
            else
            f'{Geometry(self.geometry.value).name}{config.spc5}Geometry\n'
        )
        geometryLines = (
            f'{self.upstreamThickness}{config.spc2}'
            f'{self.downstreamThickness}{config.spc5}'
            f'Upstream and downstream thickness [cm]\n'
            f'{self.angleOfRotation}{config.spc2}'
            f'{self.sampleWidth}{config.spc5}'
            f'Angle of rotation and sample width (cm)\n'
            if (
                (
                    self.geometry == Geometry.SameAsBeam
                    and config.geometry == Geometry.FLATPLATE
                )
                or self.geometry == Geometry.FLATPLATE)
            else
            f'{self.innerRadius}{config.spc2}{self.outerRadius}{config.spc5}'
            f'Inner and outer radii [cm]\n'
            f'{self.sampleHeight}{config.spc5}'
            f'Sample height (cm)\n'
        )

        if self.densityUnits == UnitsOfDensity.ATOMIC:
            units = 'atoms/\u212b^3'
            density = -self.density
        elif self.densityUnits == UnitsOfDensity.CHEMICAL:
            units = 'gm/cm^3'
            density = self.density

        densityLine = (
            f'{density}{config.spc5}'
            f'Density {units}?\n'
        )

        crossSectionSource = (
            CrossSectionSource(self.totalCrossSectionSource.value).name
        )
        crossSectionLine = (
            f"{crossSectionSource}{config.spc5}"
            if self.totalCrossSectionSource != CrossSectionSource.FILE
            else
            f"{self.crossSectionFilename}{config.spc5}"
        )

        if not self.normalisationDifferentialCrossSectionFile:
            self.normalisationDifferentialCrossSectionFile = "*"

        return (
            f'{len(self.dataFiles)}{config.spc2}'
            f'{self.periodNumber}{config.spc5}'
            f'Number of  files and period number\n'
            f'{dataFilesLineA}'
            f'{len(self.dataFilesBg)}{config.spc2}'
            f'{self.periodNumberBg}{config.spc5}'
            f'Number of  files and period number\n'
            f'{dataFilesLineB}'
            f'{numifyBool(self.forceCalculationOfCorrections)}{config.spc5}'
            f'Force calculation of corrections?\n'
            f'{str(self.composition)}{compositionSuffix}'
            f'*{config.spc2}0{config.spc2}0{config.spc5}'
            f'* 0 0 to specify end of composition input\n'
            f'{geometryLine}'
            f'{geometryLines}'
            f'{densityLine}'
            f'{self.tempForNormalisationPC}{config.spc5}'
            f'Temperature for normalisation Placzek correction\n'
            f'{crossSectionLine}'
            f'Total cross section source\n'
            f'{self.normalisationDifferentialCrossSectionFile}{config.spc5}'
            f'Normalisation differential cross section filename\n'
            f'{self.lowerLimitSmoothedNormalisation}{config.spc5}'
            f'Lower limit on smoothed normalisation\n'
            f'{self.normalisationDegreeSmoothing}{config.spc5}'
            f'Normalisation degree of smoothing\n'
            f'{self.minNormalisationSignalBR}{config.spc5}'
            f'Minimum normalisation signal to background ratio'
        )
