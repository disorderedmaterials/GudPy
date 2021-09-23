from src.scripts.utils import numifyBool
from src.gudrun_classes.data_files import DataFiles
from src.gudrun_classes.composition import Composition
from src.gudrun_classes.enums import (
    CrossSectionSource, Geometry, UnitsOfDensity
)
from src.gudrun_classes import config


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
        self.periodNumber = 0
        self.dataFiles = DataFiles([], "NORMALISATION")
        self.periodNumberBg = 0
        self.dataFilesBg = DataFiles([], "NORMALISATION BACKGROUND")
        self.forceCalculationOfCorrections = False
        self.composition = Composition([], "NORMALISATION")
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
        TAB = "          "

        dataFilesLineA = (
            f'{str(self.dataFiles)}\n'
            if len(self.dataFiles.dataFiles) > 0
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

        geometryLines = (
            f'{self.upstreamThickness}  {self.downstreamThickness}{TAB}'
            f'Upstream and downstream thickness [cm]\n'
            f'{self.angleOfRotation}  {self.sampleWidth}{TAB}'
            f'Angle of rotation and sample width (cm)\n'
            if (
                (
                    self.geometry == Geometry.SameAsBeam
                    and config.geometry == Geometry.FLATPLATE
                )
                or self.geometry == Geometry.FLATPLATE)
            else
            f'{self.innerRadius}  {self.outerRadius}{TAB}'
            f'Inner and outer radii [cm]\n'
            f'{self.sampleHeight}{TAB}'
            f'Sample height (cm)\n'
        )

        if self.densityUnits == UnitsOfDensity.ATOMIC:
            units = 'atoms/\u212b^3'
            density = -self.density
        elif self.densityUnits == UnitsOfDensity.CHEMICAL:
            units = 'gm/cm^3'
            density = self.density

        densityLine = (
            f'{density}{TAB}'
            f'Density {units}?\n'
        )

        crossSectionSource = (
            CrossSectionSource(self.totalCrossSectionSource.value).name
        )
        crossSectionLine = (
            f"{crossSectionSource}{TAB}"
            if self.totalCrossSectionSource != CrossSectionSource.FILE
            else
            f"{self.crossSectionFilename}{TAB}"
        )

        return (
            f'{len(self.dataFiles)}  {self.periodNumber}{TAB}'
            f'Number of  files and period number\n'
            f'{dataFilesLineA}'
            f'{len(self.dataFilesBg)}  {self.periodNumberBg}{TAB}'
            f'Number of  files and period number\n'
            f'{dataFilesLineB}'
            f'{numifyBool(self.forceCalculationOfCorrections)}{TAB}'
            f'Force calculation of corrections?\n'
            f'{str(self.composition)}{compositionSuffix}'
            f'*  0  0{TAB}* 0 0 to specify end of composition input\n'
            f'{Geometry(self.geometry.value).name}{TAB}'
            f'Geometry\n'
            f'{geometryLines}'
            f'{densityLine}'
            f'{self.tempForNormalisationPC}{TAB}'
            f'Temperature for normalisation Placzek correction\n'
            f'{crossSectionLine}'
            f'Total cross section source\n'
            f'{self.normalisationDifferentialCrossSectionFile}{TAB}'
            f'Normalisation differential cross section filename\n'
            f'{self.lowerLimitSmoothedNormalisation}{TAB}'
            f'Lower limit on smoothed normalisation\n'
            f'{self.normalisationDegreeSmoothing}{TAB}'
            f'Normalisation degree of smoothing\n'
            f'{self.minNormalisationSignalBR}{TAB}'
            f'Minimum normalisation signal to background ratio'
        )
