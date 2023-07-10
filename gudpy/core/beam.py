from core.utils import spacify
from core.enums import Geometry
from core import config


class Beam:
    """
    Class to represent a Beam.

    ...

    Attributes
    ----------
    sampleGeometry : Geometry
        geometry of the beam (FLATPLATE / CYLINDRICAL).
    beamProfileValues : float[]
        list of beam profile values.
    stepSizeAbsorption : float
        Step size for absorption calculations.
    stepSizeMS : float
        Step size for m.s calculation.
    noSlices : int
        Number of slices for m.s calculation.
    angularStepForCorrections : int
        Angular step size to be used in corrections [deg.].
    incidentBeamLeftEdge : float
        Left edge of incident beam relative to centre of sample.
    incidentBeamRightEdge : float
        Right edge of incident beam relative to centre of sample.
    incidentBeamTopEdge : float
        Top edge of incident beam relative to centre of sample.
    incidentBeamBottomEdge : float
        Bottom edge of incident beam relative to centre of sample.
    scatteredBeamLeftEdge : float
        Left edge of scattered beam relative to centre of sample.
    scatteredBeamRightEdge : float
        Right edge of scattered beam relative to centre of sample.
    scatteredBeamTopEdge : float
        Top edge of scattered beam relative to centre of sample.
    scatteredBeamBottomEdge : float
        Bottom edge of scattered beam relative to centre of sample.
    filenameIncidentBeamSpectrumParams : str
        Name of file containing the incident beam spectrum parameters.
    overallBackgroundFactor : float
        Overall ackground factor.
    sampleDependantBackgroundFactor : float
        Sample dependant background factor.
    shieldingAttenuationCoefficient : float
        Absorption coefficient for the shielding.
    yamlignore : str{}
        Class attributes to ignore during yaml serialisation.
    """
    def __init__(self):
        """
        Constructs all the necessary attributes for the Beam object.
        """
        self.sampleGeometry = Geometry.FLATPLATE
        self.beamProfileValues = [1., 1.]
        self.stepSizeAbsorption = 0.0
        self.stepSizeMS = 0.0
        self.noSlices = 0
        self.angularStepForCorrections = 0
        self.incidentBeamLeftEdge = -1.5
        self.incidentBeamRightEdge = 1.5
        self.incidentBeamTopEdge = 1.5
        self.incidentBeamBottomEdge = -1.5
        self.scatteredBeamLeftEdge = -2.0
        self.scatteredBeamRightEdge = 2.0
        self.scatteredBeamTopEdge = 2.0
        self.scatteredBeamBottomEdge = -2.0
        self.filenameIncidentBeamSpectrumParams = ""
        self.overallBackgroundFactor = 0.0
        self.sampleDependantBackgroundFactor = 0.0
        self.shieldingAttenuationCoefficient = 0.0

        self.yamlignore = {
            "yamlignore"
        }

    def __str__(self):
        """
        Returns the string representation of the Beam object.

        Returns
        -------
        str : String representation of Beam.
        """

        absorptionAndMSLine = (
            f'{self.stepSizeAbsorption}{config.spc2}'
            f'{self.stepSizeMS}{config.spc2}'
            f'{self.noSlices}'
            f'{config.spc5}'
            f'Step size for absorption and m.s. calculation'
            f' and no. of slices\n'
        )

        incidentBeamLine = (
            f'{self.incidentBeamLeftEdge}{config.spc2}'
            f'{self.incidentBeamRightEdge}{config.spc2}'
            f'{self.incidentBeamBottomEdge}{config.spc2}'
            f'{self.incidentBeamTopEdge}'
            f'{config.spc5}'
            f'Incident beam edges relative to centre of sample [cm]\n'
        )
        scatteredBeamLine = (
            f'{self.scatteredBeamLeftEdge}{config.spc2}'
            f'{self.scatteredBeamRightEdge}{config.spc2}'
            f'{self.scatteredBeamBottomEdge}{config.spc2}'
            f'{self.scatteredBeamTopEdge}'
            f'{config.spc5}'
            f'Scattered beam edges relative to centre of sample [cm]\n'
        )

        return (

            f'{Geometry(self.sampleGeometry.value).name}{config.spc5}'
            f'Sample geometry\n'
            f'{len(self.beamProfileValues)}{config.spc5}'
            f'Number of beam profile values\n'
            f'{spacify(self.beamProfileValues, num_spaces=2)}'
            f'{config.spc2}{config.spc5}'
            f'Beam profile values (Maximum of 50 allowed currently)\n'
            f'{absorptionAndMSLine}'
            f'{self.angularStepForCorrections}{config.spc5}'
            f'Angular step for corrections [deg.]\n'
            f'{incidentBeamLine}'
            f'{scatteredBeamLine}'
            f'{self.filenameIncidentBeamSpectrumParams}{config.spc5}'
            f'Filename containing incident beam spectrum parameters\n'
            f'{self.overallBackgroundFactor}{config.spc5}'
            f'Overall background factor\n'
            f'{self.sampleDependantBackgroundFactor}{config.spc5}'
            f'Sample dependent background factor\n'
            f'{self.shieldingAttenuationCoefficient}{config.spc5}'
            f'Shielding attenuation coefficient [per m per \u212b]'

        )
