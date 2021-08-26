from src.scripts.utils import spacify
from src.gudrun_classes.enums import Geometry


class Beam:
    """
    Class to represent a Beam.

    ...

    Attributes
    ----------
    sampleGeometry : Geometry
        geometry of the beam (FLATPLATE / CYLINDRICAL).
    noBeamProfileValues : int
        number of beam profile values.
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
    Methods
    -------
    """
    def __init__(self):
        """
        Constructs all the necessary attributes for the Beam object.

        Parameters
        ----------
        None
        """
        self.sampleGeometry = Geometry.FLATPLATE
        self.noBeamProfileValues = 0
        self.beamProfileValues = []
        self.stepSizeAbsorption = 0.0
        self.stepSizeMS = 0.0
        self.noSlices = 0
        self.angularStepForCorrections = 0
        self.incidentBeamLeftEdge = 0.0
        self.incidentBeamRightEdge = 0.0
        self.incidentBeamTopEdge = 0.0
        self.incidentBeamBottomEdge = 0.0
        self.scatteredBeamLeftEdge = 0.0
        self.scatteredBeamRightEdge = 0.0
        self.scatteredBeamTopEdge = 0.0
        self.scatteredBeamBottomEdge = 0.0
        self.filenameIncidentBeamSpectrumParams = ""
        self.overallBackgroundFactor = 0.0
        self.sampleDependantBackgroundFactor = 0.0
        self.shieldingAttenuationCoefficient = 0.0

    def __str__(self):
        """
        Returns the string representation of the Beam object.

        Parameters
        ----------
        None

        Returns
        -------
        string : str
            String representation of Beam.
        """
        TAB = "          "

        incidentBeamLine = (
            f'{self.incidentBeamLeftEdge} '
            f'{self.incidentBeamRightEdge} '
            f'{self.incidentBeamTopEdge} '
            f'{self.incidentBeamBottomEdge}'
            f'{TAB}'
            f'Incident beam edges relative to centre of sample [cm]\n'
        )
        scatteredBeamLine = (
            f'{self.scatteredBeamLeftEdge} '
            f'{self.scatteredBeamRightEdge} '
            f'{self.scatteredBeamTopEdge} '
            f'{self.scatteredBeamBottomEdge}'
            f'{TAB}'
            f'Scattered beam edges relateive to centre of samples [cm]\n'
        )

        absorptionAndMSLine = (
            f'{self.stepSizeAbsorption} '
            f'{self.stepSizeMS} '
            f'{self.noSlices}'
            f'{TAB}'
            f'Step size for absorption and m.s. calculation of no. of slices\n'
        )

        return (

            f'{Geometry(self.sampleGeometry.value).name}{TAB}'
            f'Sample geometry\n'
            f'{self.noBeamProfileValues}{TAB}'
            f'Number of beam profile values\n'
            f'{spacify(self.beamProfileValues)}{TAB}'
            f'Beam profile values (Maximum of 50 allowed currently)\n'
            f'{absorptionAndMSLine}'
            f'{self.angularStepForCorrections}{TAB}'
            f'Angular step for corrections [deg.]\n'
            f'{incidentBeamLine}'
            f'{scatteredBeamLine}'
            f'{self.filenameIncidentBeamSpectrumParams}{TAB}'
            f'Filename containing incident beam spectrum parameters\n'
            f'{self.overallBackgroundFactor}{TAB}'
            f'Overall background factor\n'
            f'{self.sampleDependantBackgroundFactor}{TAB}'
            f'Sample dependent background factor\n'
            f'{self.shieldingAttenuationCoefficient}{TAB}'
            f'Shielding attenuation coefficient [per m per \u212b]'

        )
