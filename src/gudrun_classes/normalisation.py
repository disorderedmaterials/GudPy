from src.scripts.utils import spacify, numifyBool
from src.gudrun_classes.data_files import DataFiles
from src.gudrun_classes.composition import Composition
from src.gudrun_classes.enums import Geometry, UnitsOfDensity


class Normalisation:
    """
    Class to represent Normalisation.

    ...

    Attributes
    ----------
    numberOfFilesPeriodNumber : tuple(int, int)
        Number of data files and their period number.
    dataFiles : DataFiles
        DataFiles object storing data files belonging to the container.
    numberOfFilesPeriodNumberBg : tuple(int, int)
        Number of background data files and their period number.
    dataFilesBg : DataFiles
        DataFiles object storing background data files.
    composition : Composition
        Composition object storing the atomic composition of the container.
    geometry : Geometry
        Geometry of the container.
    thickness : tuple(float, float)
        Upstream and downstream thickness.
    angleOfRotationSampleWidth : tuple(float, float)
        Angle of rotation of the container and its width.
    density : float
        Density of normalisation
    densityUnits : int
        0 = atoms/Angstrom^3, 1 = gm/cm^3
    tempForNormalisationPC : int
        Temperature for Placzek correction.
    totalCrossSectionSource : str
        TABLES / TRANSMISSION monitor / filename
    normalisationDifferentialCrossSectionFilename : str
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
        self.numberOfFiles = 0
        self.periodNumber = 0
        self.dataFiles = DataFiles([], "NORMALISATION")
        self.numberOfFilesBg = 0
        self.periodNumberBg = 0
        self.dataFilesBg = DataFiles([], "NORMALISATION BACKGROUND")
        self.forceCalculationOfCorrections = False
        self.composition = Composition([], "NORMALISATION")
        self.geometry = Geometry.FLATPLATE
        self.upstreamThickness = 0.0
        self.downstreamThickness = 0.0
        self.angleOfRotation = 0.0
        self.sampleWidth = 0.0
        self.density = 0.0
        self.densityUnits = UnitsOfDensity.ATOMIC
        self.tempForNormalisationPC = 0
        self.totalCrossSectionSource = ""
        self.normalisationDifferentialCrossSectionFilename = ""
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
            f'{self.numberOfFiles}  {self.periodNumber}{TAB}'
            f'Number of  files and period number\n'
            f'{dataFilesLineA}'
            f'{self.numberOfFilesBg}  {self.periodNumberBg}{TAB}'
            f'Number of  files and period number\n'
            f'{dataFilesLineB}'
            f'{numifyBool(self.forceCalculationOfCorrections)}{TAB}'
            f'Force calculation of corrections?\n'
            f'{str(self.composition)}\n'
            f'*  0  0{TAB}* 0 0 to specify end of composition input\n'
            f'{Geometry(self.geometry.value).name}{TAB}'
            f'Geometry\n'
            f'{self.upstreamThickness}  {self.downstreamThickness}{TAB}'
            f'Upstream and downstream thickness [cm]\n'
            f'{self.angleOfRotation}  {self.sampleWidth}{TAB}'
            f'Angle of rotation and sample width (cm)\n'
            f'{densityLine}'
            f'{self.tempForNormalisationPC}{TAB}'
            f'Temperature for normalisation Placzek correction\n'
            f'{self.totalCrossSectionSource}{TAB}'
            f'Total cross section source\n'
            f'{self.normalisationDifferentialCrossSectionFilename}{TAB}'
            f'Normalisation differential cross section filename\n'
            f'{self.lowerLimitSmoothedNormalisation}{TAB}'
            f'Lower limit on smoothed normalisation\n'
            f'{self.normalisationDegreeSmoothing}{TAB}'
            f'Normalisation degree of smoothing\n'
            f'{self.minNormalisationSignalBR}{TAB}'
            f'Minimum normalisation signal to background ratio'
        )
