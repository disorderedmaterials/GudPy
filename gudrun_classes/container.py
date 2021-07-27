
from inspect import cleandoc

try:
    from utils import *
    from data_files import DataFiles
    from composition import Composition
except ModuleNotFoundError:
    from scripts.utils import *
    from gudrun_classes.data_files import DataFiles
    from gudrun_classes.composition import Composition


class Container:
    def __init__(self):
        self.name = ''
        self.numberOfFilesPeriodNumber = (0, 0)
        self.dataFiles = DataFiles([], 'CONTAINER')
        self.composition = Composition([], 'CONTAINER')
        self.geometry = ''
        self.thickness = (0., 0.)
        self.angleOfRotationSampleWidth = (0., 0.)
        self.densityOfAtoms = 0.
        self.totalCrossSectionSource = ''
        self.tweakFactor = 0.
        self.scatteringFractionAttenuationCoefficient = (0., 0.)

    def __str__(self):
        if len(self.dataFiles.dataFiles) > 0:

            return cleandoc("""
{}        {{
    
{}        Number of files and period number
{}
{}
* 0 0        * 0 0 to specify end of composition input
{}        Geometry
{}        Upstream and downstream thickness [cm]
{}        Angle of rotation and sample width (cm)
{}        Density atoms/\u212b^3?
{}        Total cross section source
{}        Tweak factor
{}        Sample environment scattering fraction and attenuation coefficient [per A]

}}
            """.format(
                self.name,
                spacify(self.numberOfFilesPeriodNumber),
                str(self.dataFiles),
                str(self.composition),
                self.geometry,
                spacify(self.thickness),
                spacify(self.angleOfRotationSampleWidth),
                self.densityOfAtoms,
                self.totalCrossSectionSource,
                self.tweakFactor,
                spacify(self.scatteringFractionAttenuationCoefficient)
            ))
        else:
            return cleandoc("""
{}        {{

{}        Number of files and period number
{}
* 0 0        * 0 0 to specify end of composition input
{}        Geometry
{}        Upstream and downstream thickness [cm]
{}        Angle of rotation and sample width (cm)
{}        Density atoms/\u212b^3?
{}        Total cross section source
{}        Tweak factor
{}        Sample environment scattering fraction and attenuation coefficient [per A]

}}
            """.format(
                self.name,
                spacify(self.numberOfFilesPeriodNumber),
                str(self.composition),
                self.geometry,
                spacify(self.thickness),
                spacify(self.angleOfRotationSampleWidth),
                self.densityOfAtoms,
                self.totalCrossSectionSource,
                self.tweakFactor,
                spacify(self.scatteringFractionAttenuationCoefficient)
            ))
