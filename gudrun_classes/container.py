try:
    from utils import spacify
    from data_files import DataFiles
    from composition import Composition
except ModuleNotFoundError:
    from scripts.utils import spacify
    from gudrun_classes.data_files import DataFiles
    from gudrun_classes.composition import Composition


class Container:
    def __init__(self):
        self.name = ""
        self.numberOfFilesPeriodNumber = (0, 0)
        self.dataFiles = DataFiles([], "CONTAINER")
        self.composition = Composition([], "CONTAINER")
        self.geometry = ""
        self.thickness = (0.0, 0.0)
        self.angleOfRotationSampleWidth = (0.0, 0.0)
        self.densityOfAtoms = 0.0
        self.totalCrossSectionSource = ""
        self.tweakFactor = 0.0
        self.scatteringFractionAttenuationCoefficient = (0.0, 0.0)

    def __str__(self):
        TAB = "          "
        dataFilesLines = (
            f'{str(self.dataFiles)}\n'
            if len(self.dataFiles.dataFiles) > 0
            else
            ''
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
            f'{self.densityOfAtoms}{TAB}'
            f'Density atoms/\u212b^3?\n'
            f'{self.totalCrossSectionSource}{TAB}'
            f'Total cross section source\n'
            f'{self.tweakFactor}{TAB}'
            f'Tweak factor\n'
            f'{spacify(self.scatteringFractionAttenuationCoefficient)}'
            f'{TAB}'
            f'Sample environment scattering fraction '
            f'and attenuation coefficient [per A]\n'
            f'\n}}\n'
        )
