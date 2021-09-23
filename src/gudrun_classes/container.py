from src.gudrun_classes.data_files import DataFiles
from src.gudrun_classes.composition import Composition
from src.gudrun_classes.enums import Geometry, UnitsOfDensity
from src.gudrun_classes import config
from src.gudrun_classes.enums import CrossSectionSource


class Container:
    """
    Class to represent a Container.

    ...

    Attributes
    ----------
    name : str
        Name of the container.
    periodNumber : int
        Period number for the data files.
    dataFiles : DataFiles
        DataFiles object storing data files belonging to the container.
    composition : Composition
        Composition object storing the atomic composition of the container.
    geometry : Geometry
        Geometry of the container (FLATPLATE / CYLINDRICAL / SameAsBeam).
    upstreamThickness : float
        Upstream thickness of the container - if its geometry is FLATPLATE.
    downstreamThickness : float
        Downstream thickness of the container - if its geometry is FLATPLATE.
    angleOfRotation : float
        Angle of rotation of the container - if its geometry is FLATPLATE.
    sampleWidth : float
        Width of the container - if its geometry is FLATPLATE.
    innerRadius : float
        Inner radius of the container - if its geometry is CYLINDRICAL.
    outerRadius : float
        Outer radius of the container - if its geometry is CYLINDRICAL.
    sampleHeight : float
        Height of the container - if its geometry is CYLINDRICAL.
    density : float
        Density of the container.
    densityUnits : int
        0 = atoms/Angstrom^3, 1 = gm/cm^3
    overallBackgroundFactor : float
        Background factor.
    totalCrossSectionSource : CrossSectionSource
        TABLES / TRANSMISSION monitor / filename
    crossSectionFilename : str
        Filename for total cross section source if applicable.
    scatteringFractionAttenuationCoefficient : tuple(float, float)
        Sample environment scattering fraction and attenuation coefficient,
        per Angstrom
    Methods
    -------
    """
    def __init__(self):
        """
        Constructs all the necessary attributes for the Container object.

        Parameters
        ----------
        None
        """
        self.name = ""
        self.periodNumber = 0
        self.dataFiles = DataFiles([], "CONTAINER")
        self.composition = Composition([], "CONTAINER")
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
        self.totalCrossSectionSource = CrossSectionSource.TABLES
        self.crossSectionFilename = ""
        self.tweakFactor = 0.0
        self.scatteringFraction = 0.0
        self.attenuationCoefficient = 0.0

    def __str__(self):
        """
        Returns the string representation of the Container object.

        Parameters
        ----------
        None

        Returns
        -------
        string : str
            String representation of Container.
        """

        TAB = "          "
        dataFilesLines = (
            f'{str(self.dataFiles)}\n'
            if len(self.dataFiles.dataFiles) > 0
            else
            ''
            )

        if self.densityUnits == UnitsOfDensity.ATOMIC:
            units = 'atoms/\u212b^3'
            density = -self.density
        elif self.densityUnits == UnitsOfDensity.CHEMICAL:
            units = 'gm/cm^3'
            density = self.density

        compositionSuffix = "" if str(self.composition) == "" else "\n"

        geometryLines = (
            f'{self.upstreamThickness}  {self.downstreamThickness}{TAB}'
            f'Upstream and downstream thickness [cm]\n'
            f'{self.angleOfRotation}  {self.sampleWidth}{TAB}'
            f'Angle of rotation and sample width (cm)\n'
            if
            (
                self.geometry == Geometry.SameAsBeam
                and config.geometry == Geometry.FLATPLATE
            )
            or self.geometry == Geometry.FLATPLATE
            else
            f'{self.innerRadius}  {self.outerRadius}{TAB}'
            f'Inner and outer radii [cm]\n'
            f'{self.sampleHeight}{TAB}'
            f'Sample height (cm)\n'
        )

        densityLine = (
            f'{density}{TAB}'
            f'Density {units}?\n'
        )

        crossSectionSource = (
            CrossSectionSource(self.totalCrossSectionSource.value).name
        )
        crossSectionLine = (
            f"{crossSectionSource}{TAB}"
            if self.totalCrossSectionSource != CrossSectionSource.FILENAME
            else
            f"{self.crossSectionFilename}{TAB}"
        )

        return (
            f'{self.name}{TAB}{{\n\n'
            f'{len(self.dataFiles)}  {self.periodNumber}{TAB}'
            f'Number of files and period number\n'
            f'{dataFilesLines}'
            f'{str(self.composition)}{compositionSuffix}'
            f'*  0  0{TAB}'
            f'* 0 0 to specify end of composition input\n'
            f'{Geometry(self.geometry.value).name}{TAB}'
            f'Geometry\n'
            f'{geometryLines}'
            f'{densityLine}'
            f'{crossSectionLine}'
            f'Total cross section source\n'
            f'{self.tweakFactor}{TAB}'
            f'Tweak factor\n'
            f'{self.scatteringFraction}  {self.attenuationCoefficient}'
            f'{TAB}'
            f'Sample environment scattering fraction '
            f'and attenuation coefficient [per \u212b]\n'
            f'\n}}\n'
        )
