from src.scripts.utils import bjoin, numifyBool
from src.gudrun_classes.data_files import DataFiles
from src.gudrun_classes.composition import Composition
from src.gudrun_classes.enums import (
    CrossSectionSource, FTModes, UnitsOfDensity,
    NormalisationType, OutputUnits, Geometry
)
from src.gudrun_classes import config


class Sample:
    """
    Class to represent a Sample.

    ...

    Attributes
    ----------
    name : str
        Name of the sample.
    periodNumber : int
        Period number of data files.
    dataFiles : DataFiles
        DataFiles object storing data files belonging to the container.
    forceCalculationOfCorrections : bool
        Decide whether to force calculations of corrections or read them
        from the file, if it exists.
    composition : Composition
        Composition object storing the atomic composition of the sample.
    geometry : Geometry
        Geometry of the sample (FLATPLATE / CYLINDRICAL / SameAsBeam).
    upstreamThickness : float
        Upstream thickness of the sample - if its geometry is FLATPLATE.
    downstreamThickness : float
        Downstream thickness of the sample - if its geometry is FLATPLATE.
    angleOfRotation : float
        Angle of rotation of the sample - if its geometry is FLATPLATE.
    sampleWidth : float
        Width of the sample - if its geometry is FLATPLATE.
    innerRadius : float
        Inner radius of the sample - if its geometry is CYLINDRICAL.
    outerRadius : float
        Outer radius of the sample - if its geometry is CYLINDRICAL.
    sampleHeight : float
        Height of the sample - if its geometry is CYLINDRICAL.
    density : str
        Density of the sample
    densityUnits : int
        0 = atoms/Angstrom^3, 1 = gm/cm^3
    tempForNormalisationPC : float
        Temperature for Placzek Correction.
    overallBackgroundFactor : float
        Background factor.
    totalCrossSectionSource : CrossSectionSource
        TABLES / TRANSMISSION monitor / filename
    crossSectionFilename : str
        Filename for the total cross section source if applicable.
    sampleTweakFactor : float
        Tweak factor for the sample.
    topHatW : float
        Width of top hat function for Fourier transform.
    minRadFT : float
        Minimum radius for Fourier transform.
    grBroadening : float
        Broadening of g(r) at r = 1 Angstrom
    resonanceValues : tuple[]
        List of tuples storing wavelength ranges for resonance values.
    exponentialValues : tuple[]
        List of tuples storing exponential amplitude and decay values.
    normalisationCorrectionFactor : float
        Factor to multiply normalisation by prior to dividing into sample.
    fileSelfScattering : str
        Name of file containing scattering as a function of wavelength.
    normaliseTo : int
        Normalisation type required on the final merged DCS data.
        0 = nothing, 1 = <f>^2, 2 = <f^2>
    maxRadFT : float
        Maximum radiues for Fourier transform.
    outputUnits : int
        Output units for final merged DCS, barns/atom/sr or cm^-1/sr
    powerForBroadening : float
        Broadening power
        0 = constant, 0.5 = sqrt(r), 1 = r
    stepSize : float
        Step size in radius for final g(r).
    runThisSample : bool
        Should the sample be included in analysis?
    scatteringFraction : float
        Sample environment scattering fraction to compensate
        for different scattering in different containers.
    attenuationCoefficient : float
        Sample environment attenuation coefficient to
        compensate for different attenuation in different containers.
    containers : Container[]
        List of Container objects attached to this sample.
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
        self.periodNumber = 1
        self.dataFiles = DataFiles([], "SAMPLE")
        self.forceCalculationOfCorrections = False
        self.composition = Composition("SAMPLE")
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
        self.totalCrossSectionSource = CrossSectionSource.TRANSMISSION
        self.crossSectionFilename = ""
        self.sampleTweakFactor = 0.0
        self.topHatW = 0.0
        self.FTMode = FTModes.SUB_AVERAGE
        self.minRadFT = 0.0
        self.grBroadening = 0.0
        self.resonanceValues = []
        self.exponentialValues = []
        self.normalisationCorrectionFactor = 0.0
        self.fileSelfScattering = ""
        self.normaliseTo = NormalisationType.NOTHING
        self.maxRadFT = 0.0
        self.outputUnits = OutputUnits.BARNS_ATOM_SR
        self.powerForBroadening = 0.0
        self.stepSize = 0.0
        self.runThisSample = True
        self.scatteringFraction = 0.0
        self.attenuationCoefficient = 0.0

        self.containers = []

    def pathName(self):
        return self.name.replace(" ", "_").translate(
            {ord(x): '' for x in r'/\!*~,&|[]'}
        ) + ".sample"

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

        nameLine = (
            f"SAMPLE {self.name}{TAB}"
            if self.name != "SAMPLE"
            else
            f"SAMPLE{TAB}"
        )

        dataFilesLine = (
            f'{str(self.dataFiles)}\n'
            if len(self.dataFiles.dataFiles) > 0
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

        if self.densityUnits == UnitsOfDensity.ATOMIC:
            density = self.density*-1
        elif self.densityUnits == UnitsOfDensity.CHEMICAL:
            density = self.density

        densityLine = (
            f'{density}{TAB}'
            f'Density {self.densityUnits.name}?\n'
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

        if self.FTMode == FTModes.NO_FT:
            topHatWidthLine = f"0{TAB}"
        elif self.FTMode == FTModes.SUB_AVERAGE:
            topHatWidthLine = f"{-self.topHatW}{TAB}"
        else:
            topHatWidthLine = f"{self.topHatW}{TAB}"

        resonanceLines = (
            bjoin(
                self.resonanceValues,
                " Min. and max resonance wavelength [\u212b]. 0  0 to end.\n",
                sameseps=True
            )
        )
        exponentialLines = (
            bjoin(
                self.exponentialValues,
                " Exponential amplitude and decay [1/\u212b]\n",
                sameseps=True,
                suffix="0"
            )
        )

        selfScatteringLine = (
            f'{self.fileSelfScattering}{TAB}'
            f'Name of file containing self scattering'
            f' as a function of wavelength [\u212b]\n'
        )

        normaliseLine = (
            f'{self.normaliseTo.value}{TAB}'
            f'Normalise to:{self.normaliseTo.name}\n'
        )

        unitsLine = (
            f'{self.outputUnits.value}{TAB}'
            f'Output units: {self.outputUnits.name}\n'
        )

        sampleEnvironmentLine = (
            f'{self.scatteringFraction}  {self.attenuationCoefficient}'
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
            f'\n{nameLine}{{\n\n'
            f'{len(self.dataFiles)}  {self.periodNumber}{TAB}'
            f'Number of  files and period number\n'
            f'{dataFilesLine}'
            f'{numifyBool(self.forceCalculationOfCorrections)}{TAB}'
            f'Force calculation of sample corrections?\n'
            f'{str(self.composition)}{compositionSuffix}'
            f'*  0  0{TAB}* 0 0 to specify end of composition input\n'
            f'{Geometry(self.geometry.value).name}{TAB}'
            f'Geometry\n'
            f'{geometryLines}'
            f'{densityLine}'
            f'{self.tempForNormalisationPC}{TAB}'
            f'Temperature for sample Placzek correction\n'
            f'{crossSectionLine}'
            f'Total cross section source\n'
            f'{self.sampleTweakFactor}{TAB}'
            f'Sample tweak factor\n'
            f'{topHatWidthLine}'
            f'Top hat width (1/\u212b) for cleaning up Fourier Transform\n'
            f'{self.minRadFT}{TAB}'
            f'Minimum radius for FT  [\u212b]\n'
            f'{self.grBroadening}{TAB}'
            f'g(r) broadening at r = 1\u212b [\u212b]\n'
            f'{resonanceLines}'
            f'0  0{TAB}0  0{TAB}'
            f' to finish specifying wavelength range of resonance\n'
            f'{exponentialLines}'
            f'*  0  0{TAB}* 0 0 to specify end of exponential parameter input'
            f'\n'
            f'{self.normalisationCorrectionFactor}{TAB}'
            f'Normalisation correction factor\n'
            f'{selfScatteringLine}'
            f'{normaliseLine}'
            f'{self.maxRadFT}{TAB}'
            f'Maximum radius for FT [\u212b]\n'
            f'{unitsLine}'
            f'{self.powerForBroadening}{TAB}'
            f'Power for broadening function e.g. 0.5\n'
            f'{self.stepSize}{TAB}'
            f'Step size [\u212b]\n'
            f'{numifyBool(self.runThisSample)}{TAB}'
            f'Analyse this sample?\n'
            f'{sampleEnvironmentLine}'
            f'\n}}\n\n'
            f'{SAMPLE_CONTAINERS}'
            f'\nGO\n'
        )
