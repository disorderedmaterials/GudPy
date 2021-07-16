
from inspect import cleandoc

from utils import *

class Beam:
    def __init__(self):
        self.sampleGeometry = ''
        self.noBeamProfileValues = 0
        self.beamProfileValues = []
        self.stepSizeAbsorptionMSNoSlices = (0.,0.,0)
        self.angularStepForCorrections = 0
        self.incidentBeamEdgesRelCentroid = (0.,0.,0.,0.)
        self.scatteredBeamEdgesRelCentroid = (0.,0.,0.,0.)
        self.filenameIncidentBeamSpectrumParams = ''
        self.overallBackgroundFactor = 0.
        self.sampleDependantBackgroundFactor = 0.
        self.shieldingAttenuationCoefficient = 0.

    def __str__(self):

        return cleandoc("""
{}        Sample geometry
{}        Number of beam profile values
{}        Beam profile values (Maximum of 50 allowed currently)
{}        Step size for absorption and m.s. calculation of no. of slices
{}        Angular step for corrections [deg.]
{}        Incident beam edges relative to centre of sample [cm]
{}        Scattered beam edges relative to centre of sample [cm]
{}        Filename containing incident beam spectrum parameters
{}        Overall background factor
{}        Sample dependent background factor
{}        Shielding attenuation coefficient [per m per A]""".format(
                self.sampleGeometry,
                self.noBeamProfileValues,
                spacify(self.beamProfileValues),
                spacify(self.stepSizeAbsorptionMSNoSlices),
                self.angularStepForCorrections,
                spacify(self.incidentBeamEdgesRelCentroid),
                spacify(self.scatteredBeamEdgesRelCentroid),
                self.filenameIncidentBeamSpectrumParams,
                self.overallBackgroundFactor,
                self.sampleDependantBackgroundFactor,
                self.shieldingAttenuationCoefficient
            ))

