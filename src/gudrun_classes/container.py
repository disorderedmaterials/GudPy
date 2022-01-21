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
        self.topHatW = 0.0
        self.FTMode = FTModes.SUB_AVERAGE
        self.minRadFT = 0.0
        self.maxRadFT = 0.0
        self.grBroadening = 0.
        self.powerForBroadening = 0.0
        self.stepSize = 0.0

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

        nameLine = (
            f"CONTAINER {self.name}{config.spc5}"
            if self.name != "CONTAINER"
            else
            f"CONTAINER{config.spc5}"
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
            f'{self.upstreamThickness}{config.spc2}{self.downstreamThickness}{config.spc5}'
            f'Upstream and downstream thicknesses [cm]\n'
            f'{self.angleOfRotation}{config.spc2}{self.sampleWidth}{config.spc5}'
            f'Angle of rotation and sample width (cm)\n'
            if (
                self.geometry == Geometry.SameAsBeam
                and config.geometry == Geometry.FLATPLATE
            )
            or self.geometry == Geometry.FLATPLATE
            else
            f'{self.innerRadius}{config.spc2}{self.outerRadius}{config.spc5}'
            f'Inner and outer radii [cm]\n'
            f'{self.sampleHeight}{config.spc5}'
            f'Sample height (cm)\n'
        )

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

        return (
            f'{nameLine}{{\n\n'
            f'{len(self.dataFiles)}{config.spc2}{self.periodNumber}{config.spc5}'
            f'Number of files and period number\n'
            f'{dataFilesLines}'
            f'{str(self.composition)}{compositionSuffix}'
            f'*{config.spc2}0{config.spc2}0{config.spc5}* 0 0 to specify end of composition input\n'
            f'SameAsBeam{config.spc5}'
            f'Geometry\n'
            f'{geometryLines}'
            f'{densityLine}'
            f'{crossSectionLine}'
            f'Total cross section source\n'
            f'{self.tweakFactor}{config.spc5}'
            f'Tweak factor\n'
            f'{self.scatteringFraction}{config.spc2}{self.attenuationCoefficient}'
            f'{config.spc5}'
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
        sample.FTMode = self.FTMode
        sample.grBroadening = self.grBroadening
        sample.exponentialValues = [(0.0, 1.0)]
        sample.normalisationCorrectionFactor = 1.0
        sample.fileSelfScattering = "*"
        sample.maxRadFT = self.maxRadFT
        sample.minRadFT = self.minRadFT
        sample.powerForBroadening = self.powerForBroadening
        sample.stepSize = self.stepSize
        sample.scatteringFraction = 1.0

        return sample
