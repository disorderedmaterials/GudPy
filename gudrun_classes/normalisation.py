from inspect import cleandoc

try:
    from utils import *
    from data_files import DataFiles
    from composition import Composition
except ModuleNotFoundError:
    from scripts.utils import *
    from gudrun_classes.data_files import DataFiles
    from gudrun_classes.composition import Composition

class Normalisation:
    def __init__(self):
        self.numberOfFilesPeriodNumber = (0,0)
        self.dataFiles = DataFiles([], 'NORMALISATION')
        self.numberOfFilesPeriodNumberBg = (0,0)
        self.dataFilesBg = DataFiles([], 'NORMALISATION BACKGROUND')
        self.forceCalculationOfCorrections = False
        self.composition = Composition([], 'NORMALISATION')
        self.geometry = ''
        self.thickness = (0.,0.)
        self.angleOfRotationSampleWidth = (0.,0.)
        self.densityOfAtoms = 0.
        self.tempForNormalisationPC = 0
        self.totalCrossSectionSource = ''
        self.normalisationDifferentialCrossSectionFilename = ''
        self.lowerLimitSmoothedNormalisation = 0.
        self.normalisationDegreeSmoothing = 0.
        self.minNormalisationSignalBR = 0.
    
    def __str__(self):
        return cleandoc("""
{}        Number of  files and period number
{}
{}        Number of  files and period number
{}
{}        Force calculation of corrections?
{}
* 0 0        * 0 0 to specify end of compisition input
{}        Geometry
{}        Upstream and downstream thickness [cm]
{}        Angle of rotation and sample width (cm)
{}        Density atoms/\u212b^3?
{}        Temperature for normalisation Placzek correction
{}        Total cross section source
{}        Normalisation differential cross section filename
{}        Lower limit on smoothed normalisation
{}        Normalisation degree of smoothing
{}        Minimum normalisation signal to background ratio""".format(
                spacify(self.numberOfFilesPeriodNumber),
                str(self.dataFiles),
                spacify(self.numberOfFilesPeriodNumberBg),
                str(self.dataFilesBg),
                numifyBool(self.forceCalculationOfCorrections),
                str(self.composition),
                self.geometry,
                spacify(self.thickness),
                spacify(self.angleOfRotationSampleWidth),
                self.densityOfAtoms,
                self.tempForNormalisationPC,
                self.totalCrossSectionSource,
                self.normalisationDifferentialCrossSectionFilename,
                self.lowerLimitSmoothedNormalisation,
                self.normalisationDegreeSmoothing,
                self.minNormalisationSignalBR
        ))

