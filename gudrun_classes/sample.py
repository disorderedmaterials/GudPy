try:
    from utils import spacify, numifyBool
    from data_files import DataFiles
    from composition import Composition
    from enums import UnitsOfDensity
except ModuleNotFoundError:
    from scripts.utils import spacify, numifyBool
    from gudrun_classes.data_files import DataFiles
    from gudrun_classes.composition import Composition
    from gudrun_classes.enums import UnitsOfDensity


class Sample:
    """
    Class to represent a Sample.

    ...

    Attributes
    ----------
    name : str
        Name of the sample.
    numberOfFilesPeriodNumber : tuple(int, int)
        Number of data files and their period number.
    dataFiles : DataFiles
        DataFiles object storing data files belonging to the container.
    forceCalculationOfCorrections : bool
        Decide whether to force calculations of corrections or read them
        from the file, if it exists.
    composition : Composition
        Composition object storing the atomic composition of the sample.
    geometry : str
        Geometry of the sample (FLATPLATE / CYLINDRICAL).
    thickness : tuple(float, float)
        Upstream and downstream thickness.
    angleOfRotationSampleWidth : tuple(float, float)
        Angle of rotation of the sample and its width.
    density : str
        Density of the sample
    densityUnits : int
        0 = atoms/Angstrom^3, 1 = gm/cm^3
    overallBackgroundFactor : float
        Background factor.
    totalCrossSectionSource : str
        TABLES / TRANSMISSION monitor / filename
    sampleTweakFactor : float
        Tweak factor for the sample.
    topHatW : float
        Width of top hat function for Fourier transform.
    minRadFT : float
        Minimum radius for Fourier transform.
    grBroadening : float
        Broadening of g(r) at r = 1 Angstrom
    expAandD : tuple(float, float, int)
        Sample exponential paramaters.
    normalisationCorrectionFactor : float
        Factor to multiply normalisation by prior to dividing into sample.
    fileSelfScattering : str
        Name of file containing scattering as a function of wavelength.
    normaliseTo : int
        Normalisationt type required on the final merged DCS data.
        0 = nothing, 1 = <f>^2, 2 = <f^2>
    maxRadFT : float
        Maximum radiues for Fourier transform.
    outputUnits : int
        Output units for final merged DCS, barns/atom/sr or cm^-1/sr
    powerForBroadening : float
        Broadening power
        0 = constant, 0.5 = sqrt(r), 1 = r
    stepSize : int
        Step size in radius for final g(r).
    include : bool
        Should the sample be included in analysis?
    environementScatteringFuncAttenuationCoeff : tuple(float, float)
        Sample environment factors used to compensate
        for different attenuation and scattering in different containers.
    containers : Container[]
        List of Container objects attached to this sample.
    runThisSample : bool
        Should this sample be ran?
    Methods
    -------
    """
    def __init__(self):
        """
        Constructs all the necessary attributes for the Sample object.

        Parameters
        ----------
        None
        """
        self.name = ""
        self.numberOfFilesPeriodNumber = (0, 0)
        self.dataFiles = DataFiles([], "SAMPLE")
        self.forceCalculationOfCorrections = False
        self.composition = Composition([], "SAMPLE")
        self.geometry = ""
        self.thickness = (0.0, 0.0)
        self.angleOfRotationSampleWidth = (0.0, 0.0)
        self.density = 0.0
        self.densityUnits = UnitsOfDensity.ATOMIC
        self.tempForNormalisationPC = 0
        self.totalCrossSectionSource = ""
        self.sampleTweakFactor = 0.0
        self.topHatW = 0.0
        self.minRadFT = 0.0
        self.grBroadening = 0.0
        self.expAandD = (0.0, 0.0, 0)
        self.normalisationCorrectionFactor = 0.0
        self.fileSelfScattering = ""
        self.normaliseTo = 0
        self.maxRadFT = 0.0
        self.outputUnits = 0
        self.powerForBroadening = 0.0
        self.stepSize = 0.0
        self.include = False
        self.environementScatteringFuncAttenuationCoeff = (0.0, 0.0)

        self.containers = []
        self.runThisSample = True

    def __str__(self):
        """
        Returns the string representation of the Sample object.

        Parameters
        ----------
        None

        Returns
        -------
        string : str
            String representation of Sample.
        """

        TAB = "          "

        dataFilesLine = (
            f'{str(self.dataFiles)}\n'
            if len(self.dataFiles.dataFiles) > 0
            else
            ''
        )
        if self.densityUnits == UnitsOfDensity.ATOMIC:
            units = 'atoms/\u212b^3'
            density = self.density*-1
        elif self.densityUnits == UnitsOfDensity.CHEMICAL:
            units = 'gm/cm^3'
            density = self.density

        densityLine = (
            f'{density}{TAB}'
            f'Density {units}?\n'
        )

        selfScatteringLine = (
            f'{self.fileSelfScattering}{TAB}'
            f'Name of file containing self scattering'
            f' as a function of wavelength [\u212b]\n'
        )

        sampleEnvironmentLine = (
            f'{spacify(self.environementScatteringFuncAttenuationCoeff)}'
            f'{TAB}'
            f'Sample environment scattering fraction'
            f' and attenuation coefficient [per \u212b]\n'
        )

        SAMPLE_CONTAINERS = (
            "\n".join([str(x) for x in self.containers])
            if len(self.containers) > 0
            else
            ''
        )

        return (
            f'\n{self.name}{TAB}{{\n\n'
            f'{spacify(self.numberOfFilesPeriodNumber)}{TAB}'
            f'Number of  files and period number\n'
            f'{dataFilesLine}'
            f'{numifyBool(self.forceCalculationOfCorrections)}{TAB}'
            f'Force calculation of sample corrections?\n'
            f'{str(self.composition)}\n'
            f'*  0  0{TAB}* 0 0 to specify end of composition input\n'
            f'{self.geometry}{TAB}'
            f'Geometry\n'
            f'{spacify(self.thickness)}{TAB}'
            f'Upstream and downstream thickness [cm]\n'
            f'{spacify(self.angleOfRotationSampleWidth)}{TAB}'
            f'Angle of rotation and sample width (cm)\n'
            f'{densityLine}'
            f'{self.tempForNormalisationPC}{TAB}'
            f'Temperature for sample Placzek correction\n'
            f'{self.totalCrossSectionSource}{TAB}'
            f'Total cross section source\n'
            f'{self.sampleTweakFactor}{TAB}'
            f'Sample tweak factor\n'
            f'{self.topHatW}{TAB}'
            f'Top hat width (1/\u212b) for cleaning up Fourier Transform\n'
            f'{self.minRadFT}{TAB}'
            f'Minimum radius for FT  [\u212b]\n'
            f'{self.grBroadening}{TAB}'
            f'g(r) broadening at r = 1\u212b [\u212b]\n'
            f'0  0{TAB}0  0{TAB} to finish specifying wavelength'
            ' range of resonance\n'
            f'{spacify(self.expAandD)}{TAB}'
            f'Exponential amplitude and decay [1/\u212b]\n'
            f'*  0  0{TAB}* 0 0 to specify end of exponential parameter input'
            f'\n'
            f'{self.normalisationCorrectionFactor}{TAB}'
            f'Normalisation correction factor\n'
            f'{selfScatteringLine}'
            f'{self.normaliseTo}{TAB}'
            f'Normalise to:Nothing\n'
            f'{self.maxRadFT}{TAB}'
            f'Maximum radius for FT [\u212b]\n'
            f'{self.outputUnits}{TAB}'
            f'Output units: b/atom/sr\n'
            f'{self.powerForBroadening}{TAB}'
            f'Power for broadening function e.g. 0.5\n'
            f'{self.stepSize}{TAB}'
            f'Step size [\u212b]\n'
            f'{numifyBool(self.include)}{TAB}'
            f'Analyse this sample?\n'
            f'{sampleEnvironmentLine}'
            f'\n}}\n\n'
            f'{SAMPLE_CONTAINERS}'
            f'\nGO\n'
        )
