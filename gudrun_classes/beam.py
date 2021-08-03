try:
    from utils import spacify
except ModuleNotFoundError:
    from scripts.utils import spacify


class Beam:
    def __init__(self):
        self.sampleGeometry = ""
        self.noBeamProfileValues = 0
        self.beamProfileValues = []
        self.stepSizeAbsorptionMSNoSlices = (0.0, 0.0, 0)
        self.angularStepForCorrections = 0
        self.incidentBeamEdgesRelCentroid = (0.0, 0.0, 0.0, 0.0)
        self.scatteredBeamEdgesRelCentroid = (0.0, 0.0, 0.0, 0.0)
        self.filenameIncidentBeamSpectrumParams = ""
        self.overallBackgroundFactor = 0.0
        self.sampleDependantBackgroundFactor = 0.0
        self.shieldingAttenuationCoefficient = 0.0

    def __str__(self):
        TAB = "          "
        return (

            f'{self.sampleGeometry}{TAB}'
            f'Sample geometry\n'
            f'{self.noBeamProfileValues}{TAB}'
            f'Number of beam profile values\n'
            f'{spacify(self.beamProfileValues)}{TAB}'
            f'Beam profile values (Maximum of 50 allowed currently)\n'
            f'{spacify(self.stepSizeAbsorptionMSNoSlices)}{TAB}'
            f'Step size for absorption and m.s. calculation of no. of slices\n'
            f'{self.angularStepForCorrections}{TAB}'
            f'Angular step for corrections [deg.]\n'
            f'{spacify(self.incidentBeamEdgesRelCentroid)}{TAB}'
            f'Incident beam edges relative to centre of sample [cm]\n'
            f'{spacify(self.scatteredBeamEdgesRelCentroid)}{TAB}'
            f'Scattered beam edges relateive to centre of samples [cm]\n'
            f'{self.filenameIncidentBeamSpectrumParams}{TAB}'
            f'Filename containing incident beam spectrum parameters\n'
            f'{self.overallBackgroundFactor}{TAB}'
            f'Overall background factor\n'
            f'{self.sampleDependantBackgroundFactor}{TAB}'
            f'Sample dependent background factor\n'
            f'{self.shieldingAttenuationCoefficient}{TAB}'
            f'Shielding attenuation coefficient [per m per A]'

        )
