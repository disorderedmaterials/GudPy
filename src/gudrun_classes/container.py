from copy import deepcopy
from src.gudrun_classes.data_files import DataFiles
from src.gudrun_classes.composition import Composition
from src.gudrun_classes.enums import FTModes, Geometry, UnitsOfDensity
from src.gudrun_classes import config
from src.gudrun_classes.enums import CrossSectionSource
from src.gudrun_classes.sample import Sample


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
        self.periodNumber = 1
        self.dataFiles = DataFiles([], "CONTAINER")
        self.composition = Composition("CONTAINER")
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

        self.runAsSample = False

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

        nameLine = (
            f"CONTAINER {self.name}{TAB}"
            if self.name != "CONTAINER"
            else
            f"CONTAINER{TAB}"
        )

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
            if self.totalCrossSectionSource != CrossSectionSource.FILE
            else
            f"{self.crossSectionFilename}{TAB}"
        )

        return (
            f'{nameLine}{{\n\n'
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

    def convertToSample(self):

        sample = Sample()
        sample.name = self.name
        sample.periodNumber = self.periodNumber
        sample.dataFiles = deepcopy(self.dataFiles)
        sample.forceCalculationOfCorrections = True
        sample.composition = deepcopy(self.composition)
        sample.geometry = self.geometry
        sample.upstreamThickness = self.upstreamThickness
        sample.downstreamThickness = self.downstreamThickness
        sample.angleOfRotation = self.angleOfRotation
        sample.sampleWidth = self.sampleWidth
        sample.innerRadius = self.innerRadius
        sample.outerRadius = self.outerRadius
        sample.sampleHeight = self.sampleHeight
        sample.density = self.density
        sample.densityUnits = self.densityUnits
        sample.totalCrossSectionSource = self.totalCrossSectionSource
        sample.sampleTweakFactor = self.tweakFactor
        sample.FTMode = FTModes.NO_FT
        sample.grBroadening = 0.1
        sample.exponentialValues = [(0.0, 1.0)]
        sample.normalisationCorrectionFactor = 1.0
        sample.fileSelfScattering = "*"
        sample.maxRadFT = 20.0
        sample.powerForBroadening = 0.2
        sample.stepSize = 0.03
        sample.scatteringFraction = 1.0

        return sample
