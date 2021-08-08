try:
    from utils import spacify
    from data_files import DataFiles
    from composition import Composition
    from enums import UnitsOfDensity
except ModuleNotFoundError:
    from scripts.utils import spacify
    from gudrun_classes.data_files import DataFiles
    from gudrun_classes.composition import Composition
    from gudrun_classes.enums import UnitsOfDensity


class Container:
    """
    Class to represent a Container.

    ...

    Attributes
    ----------
    name : str
        Name of the container.
    numberOfFilesPeriodNumber : tuple(int, int)
        Number of data files and their period number.
    dataFiles : DataFiles
        DataFiles object storing data files belonging to the container.
    composition : Composition
        Composition object storing the atomic composition of the container.
    geometry : str
        Geometry of the container.
    thickness : tuple(float, float)
        Upstream and downstream thickness.
    angleOfRotationSampleWidth : tuple(float, float)
        Angle of rotation of the container and its width.
    density : str
        Density of the container.
    densityUnits : int
        0 = atoms/Angstrom^3, 1 = gm/cm^3
    overallBackgroundFactor : float
        Background factor.
    totalCrossSectionSource : str
        TABLES / TRANSMISSION monitor / filename
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
        self.numberOfFilesPeriodNumber = (0, 0)
        self.dataFiles = DataFiles([], "CONTAINER")
        self.composition = Composition([], "CONTAINER")
        self.geometry = ""
        self.thickness = (0.0, 0.0)
        self.angleOfRotationSampleWidth = (0.0, 0.0)
        self.density = 0.0
        self.densityUnits = UnitsOfDensity.ATOMIC
        self.totalCrossSectionSource = ""
        self.tweakFactor = 0.0
        self.scatteringFractionAttenuationCoefficient = (0.0, 0.0)

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

        densityLine = (
            f'{density}{TAB}'
            f'Density {units}?\n'
        )

        return (
            f'{self.name}{TAB}{{\n\n'
            f'{spacify(self.numberOfFilesPeriodNumber)}{TAB}'
            f'Number of files and period number\n'
            f'{dataFilesLines}'
            f'{str(self.composition)}\n'
            f'*  0  0{TAB}'
            f'* 0 0 to specify end of composition input\n'
            f'{self.geometry}{TAB}'
            f'Geometry\n'
            f'{spacify(self.thickness)}{TAB}'
            f'Upstream and downstream thickness [cm]\n'
            f'{spacify(self.angleOfRotationSampleWidth)}{TAB}'
            f'Angle of rotation and sample width (cm)\n'
            f'{densityLine}'
            f'{self.totalCrossSectionSource}{TAB}'
            f'Total cross section source\n'
            f'{self.tweakFactor}{TAB}'
            f'Tweak factor\n'
            f'{spacify(self.scatteringFractionAttenuationCoefficient)}'
            f'{TAB}'
            f'Sample environment scattering fraction '
            f'and attenuation coefficient [per \u212b]\n'
            f'\n}}\n'
        )
