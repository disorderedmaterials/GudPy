try:
    from utils import spacify, numifyBool
    from data_files import DataFiles
    from composition import Composition
except ModuleNotFoundError:
    from scripts.utils import spacify, numifyBool
    from gudrun_classes.data_files import DataFiles
    from gudrun_classes.composition import Composition


class Normalisation:
    def __init__(self):
        self.numberOfFilesPeriodNumber = (0, 0)
        self.dataFiles = DataFiles([], "NORMALISATION")
        self.numberOfFilesPeriodNumberBg = (0, 0)
        self.dataFilesBg = DataFiles([], "NORMALISATION BACKGROUND")
        self.forceCalculationOfCorrections = False
        self.composition = Composition([], "NORMALISATION")
        self.geometry = ""
        self.thickness = (0.0, 0.0)
        self.angleOfRotationSampleWidth = (0.0, 0.0)
        self.densityOfAtoms = 0.0
        self.tempForNormalisationPC = 0
        self.totalCrossSectionSource = ""
        self.normalisationDifferentialCrossSectionFilename = ""
        self.lowerLimitSmoothedNormalisation = 0.0
        self.normalisationDegreeSmoothing = 0.0
        self.minNormalisationSignalBR = 0.0

    def __str__(self):

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

        return (
            f'{spacify(self.numberOfFilesPeriodNumber)}{TAB}'
            f'Number of  files and period number\n'
            f'{dataFilesLineA}'
            f'{spacify(self.numberOfFilesPeriodNumberBg)}{TAB}'
            f'Number of  files and period number\n'
            f'{dataFilesLineB}'
            f'{numifyBool(self.forceCalculationOfCorrections)}{TAB}'
            f'Force calculation of corrections?\n'
            f'{str(self.composition)}\n'
            f'*  0  0{TAB}* 0 0 to specify end of composition input\n'
            f'{self.geometry}{TAB}'
            f'Geometry\n'
            f'{spacify(self.thickness)}{TAB}'
            f'Upstream and downstream thickness [cm]\n'
            f'{spacify(self.angleOfRotationSampleWidth)}{TAB}'
            f'Angle of rotation and sample width (cm)\n'
            f'{self.densityOfAtoms}{TAB}'
            f'Density atoms/\u212b^3?\n'
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
