

from inspect import cleandoc

from utils import *

class Sample:
    def __init__(self):
        
        self.name =''
        self.numberOfFilesPeriodNumber = (0,0)
        self.dataFiles = None
        self.forceCalculationOfCorrections = False
        self.composition = None
        self.geometry = ''
        self.thickness = (0.,0.)
        self.angleOfRotationSampleWidth = (0.,0.)
        self.densityOfAtoms = 0.
        self.tempForNormalisationPC = 0
        self.totalCrossSectionSource = ''
        self.sampleTweakFactor = 0.
        self.topHatW = 0.
        self.minRadFT = 0.
        self.gor = 0.
        self.expAandD = (0.,0.,0)
        self.normalisationCorrectionFactor = 0.
        self.fileSelfScattering = ''
        self.normaliseTo = 0
        self.maxRadFT = 0.
        self.outputUnits = 0
        self.powerForBroadening = 0.
        self.stepSize = 0.
        self.analyse = False
        self.sampleEnvironementScatteringFuncAttenuationCoeff = (0.,0.)
        
        self.sampleBackground = None
        self.containers = []

    def __str__(self):

        SAMPLE_BACKGROUND = SAMPLE_CONTAINERS = SAMPLE = ''

        if self.sampleBackground:
            SAMPLE_BACKGROUND = str(self.sampleBackground)
        if len(self.containers) > 0:
            SAMPLE_CONTAINERS = cleandoc("\n".join([str(x) for x in self.containers]))
        SAMPLE = cleandoc("""
{}        {{

{}        Number of  files and period number
{}
{}        Force calculation of sample corrections?
{}
*  0  0          * 0 0 to specify end of composition input
{}        Geometry
{}        Upstream and downstream thickness [cm]
{}        Angle of rotation and sample width (cm)
{}        Density atoms/Å^3?
{}        Temperature for sample Placzek correction
{}        Total cross section source
{}        Sample tweak factor
{}        Top hat width (1/Å) for cleaning up Fourier Transform
{}        Minimum radius for FT  [Å]
{}        g(r) broadening at r = 1A [A]
0  0          0   0          to finish specifying wavelength range of resonance
{}        Exponential amplitude and decay [1/A]
*  0  0          * 0 0 to specify end of exponential parameter input
{}        Normalisation correction factor
{}        Name of file containing self scattering as a function of wavelength [A]
{}        Normalise to:Nothing
{}        Maximum radius for FT [A]
{}        Output units: b/atom/sr
{}        Power for broadening function e.g. 0.5
{}        Step size [A]
{}        Analyse this sample?
{}        Sample environment scattering fraction and attenuation coefficient [per A]

}}



""".format(
                self.name,
                spacify(self.numberOfFilesPeriodNumber),
                str(self.dataFiles),
                numifyBool(self.forceCalculationOfCorrections),
                str(self.composition),
                self.geometry,
                spacify(self.thickness),
                spacify(self.angleOfRotationSampleWidth),
                self.densityOfAtoms,
                self.tempForNormalisationPC,
                self.totalCrossSectionSource,
                self.sampleTweakFactor,
                self.topHatW,
                self.minRadFT,
                self.gor,
                spacify(self.expAandD),
                self.normalisationCorrectionFactor,
                self.fileSelfScattering,
                self.normaliseTo,
                self.maxRadFT,
                self.outputUnits,
                self.powerForBroadening,
                self.stepSize,
                numifyBool(self.analyse),
                spacify(self.sampleEnvironementScatteringFuncAttenuationCoeff)
            ))


        if len(SAMPLE_BACKGROUND) > 0 and len(SAMPLE_CONTAINERS) > 0:

            return (cleandoc(
"""{}
{}

{}
GO
            """.format(
                SAMPLE_BACKGROUND,
                SAMPLE,
                SAMPLE_CONTAINERS
            )
            ))
        elif len(SAMPLE_BACKGROUND) == 0 and len(SAMPLE_CONTAINERS) > 0:
            return (cleandoc("""
{}

{}
GO

            """.format(
                SAMPLE,
                SAMPLE_CONTAINERS
            )
            ))
        elif len(SAMPLE_BACKGROUND) > 0 and len(SAMPLE_CONTAINERS) == 0:
            return (cleandoc("""
{}
{}
GO

            """.format(
                SAMPLE_BACKGROUND,
                SAMPLE
            )
            ))            
        else:
            return (cleandoc("""
{}

GO

""".format(
                SAMPLE
            )
            ))  





        # if SAMPLE_BACKGROUND and SAMPLE_CONTAINERS:
        #     return SAMPLE_BACKGROUND + SAMPLE + SAMPLE_CONTAINERS
        # elif SAMPLE_BACKGROUND and not SAMPLE_CONTAINERS:
        #     return SAMPLE_BACKGROUND + SAMPLE
        # elif not SAMPLE_BACKGROUND and SAMPLE_CONTAINERS:
        #     return SAMPLE + SAMPLE_CONTAINERS


#         else:
#                         return cleandoc("""
# {}

# SAMPLE {}        {{

# {}        Number of  files and period number
# {}
# {}        Force calculation of sample corrections?
# {}
# *  0  0          * 0 0 to specify end of composition input
# {}        Geometry
# {}        Upstream and downstream thickness [cm]
# {}        Angle of rotation and sample width (cm)
# {}        Density atoms/Å^3?
# {}        Temperature for sample Placzek correction
# {}        Total cross section source
# {}        Sample tweak factor
# {}        Top hat width (1/Å) for cleaning up Fourier Transform
# {}        Minimum radius for FT  [Å]
# {}        g(r) broadening at r = 1A [A]
# 0  0          0   0          to finish specifying wavelength range of resonance
# {}        Exponential amplitude and decay [1/A]
# *  0  0          * 0 0 to specify end of exponential parameter input
# {}        Normalisation correction factor
# {}        Name of file containing self scattering as a function of wavelength [A]
# {}        Normalise to:Nothing
# {}        Maximum radius for FT [A]
# {}        Output units: b/atom/sr
# {}        Power for broadening function e.g. 0.5
# {}        Step size [A]
# {}        Analyse this sample?
# {}        Sample environment scattering fraction and attenuation coefficient [per A]

# }}
#                 """.format(
#                     str(self.sampleBackground),
#                     self.name,
#                     spacify(self.numberOfFilesPeriodNumber),
#                     str(self.dataFiles),
#                     numifyBool(self.forceCalculationOfCorrections),
#                     str(self.composition),
#                     self.geometry,
#                     spacify(self.thickness),
#                     spacify(self.angleOfRotationSampleWidth),
#                     self.densityOfAtoms,
#                     self.tempForNormalisationPC,
#                     self.totalCrossSectionSource,
#                     self.sampleTweakFactor,
#                     self.topHatW,
#                     self.minRadFT,
#                     self.gor,
#                     spacify(self.expAandD),
#                     self.normalisationCorrectionFactor,
#                     self.fileSelfScattering,
#                     self.normaliseTo,
#                     self.maxRadFT,
#                     self.outputUnits,
#                     self.powerForBroadening,
#                     self.stepSize,
#                     numifyBool(self.analyse),
#                     spacify(self.sampleEnvironementScatteringFuncAttenuationCoeff)
#                 ))



            