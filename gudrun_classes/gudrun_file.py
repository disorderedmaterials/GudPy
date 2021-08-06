import sys
import os
from os.path import isfile
import subprocess
import time
from copy import deepcopy

try:
    sys.path.insert(1, os.path.join(sys.path[0], "../scripts"))
    from utils import (
            iteristype, isin,
            firstword, boolifyNum,
            extract_ints_from_string,
            extract_floats_from_string,
            count_occurrences)
    from instrument import Instrument
    from beam import Beam
    from normalisation import Normalisation
    from sample import Sample
    from sample_background import SampleBackground
    from container import Container
    from composition import Composition
    from element import Element
    from data_files import DataFiles
    from purge_file import PurgeFile
    from enums import UnitsOfDensity
except ModuleNotFoundError:
    sys.path.insert(1, os.path.join(sys.path[0], "scripts"))
    from scripts.utils import (
            iteristype, isin,
            firstword, boolifyNum,
            extract_ints_from_string,
            extract_floats_from_string,
            count_occurrences)
    from gudrun_classes.beam import Beam
    from gudrun_classes.composition import Composition
    from gudrun_classes.container import Container
    from gudrun_classes.data_files import DataFiles
    from gudrun_classes.element import Element
    from gudrun_classes.instrument import Instrument
    from gudrun_classes.normalisation import Normalisation
    from gudrun_classes.sample_background import SampleBackground
    from gudrun_classes.sample import Sample
    from gudrun_classes.purge_file import PurgeFile
    from gudrun_classes.enums import UnitsOfDensity


class GudrunFile:
    """
    Class to represent a GudFile (files with .gud extension).
    .gud files are outputted by gudrun_dcs, via merge_routines
    each .gud file belongs to an individual sample.

    ...

    Attributes
    ----------
    path : str
        Path to the file.
    outpath : str
        Path to write to, when not overwriting the initial file.
    instrument : Instrument
        Instrument object extracted from the input file.
    beam : Beam
        Beam object extracted from the input file.
    normalisation : Normalisation
        Normalisation object extracted from the input file.
    sampleBackgrounds : SampleBackground[]
        List of SampleBackgrounds extracted from the input file.
    Methods
    -------
    parseInstrument(lines):
        Initialises an Intrument object and assigns it
        to the instrument attribute.
        Parses the attributes of the Instrument from the input lines.
    parseBeam(lines):
        Initialises a Beam object and assigns it to the beam attribute.
        Parses the attributes of the Beam from the input lines.
    parseNormalisation(lines):
        Initialises a Normalisation object and assigns it
        to the normalisation attribute.
        Parses the attributes of the Normalisation from the input lines.
    parseSampleBackground(lines):
        Initialises a SampleBackground object.
        Parses the attributes of the SampleBackground from the input lines.
        Returns the SampleBackground object.
    parseSample(lines):
        Initialises a Sample object.
        Parses the attributes of the Sample from the input lines.
        Returns the Sample object.
    parseContainer(lines):
        Initialises a Container object.
        Parses the attributes of the Container from the input lines.
        Returns the Container object.
    makeParse(lines, key):
        Uses the key to call a parsing function from a dictionary
        of parsing functions. The lines are passed as an argument.
        Returns the result of the called parsing function.
    sampleBackgroundHelper(lines):
        Parses the SampleBackground, its Samples and their Containers.
        Returns the SampleBackground object.
    parse():
        Parse the GudrunFile from its path.
        Assign objects from the file to the attributes of the class.
    write_out(overwrite=False)
        Writes out the string representation of the GudrunFile to a file.
    dcs(path=''):
        Call gudrun_dcs on the path supplied. If the path is its
        default value, then use the path attribute as the path.
    process():
        Write out the GudrunFile, and call gudrun_dcs on the outputted file.
    purge():
        Create a PurgeFile from the GudrunFile, and run purge_det on it.
    """

    def __init__(self, path=None):
        """
        Constructs all the necessary attributes for the GudrunFile object.
        Calls the GudrunFile's parse method,
        to parse the GudrunFile from its path.

        Parameters
        ----------
        path : str
            Path to the file.
        """

        self.path = path

        # Construct the outpath.
        fname = os.path.basename(self.path)
        ref_fname = "gudpy_{}".format(fname)
        dir = os.path.dirname(os.path.dirname(os.path.abspath(self.path)))
        self.outpath = "{}/{}".format(dir, ref_fname)

        self.instrument = None
        self.beam = None
        self.normalisation = None
        self.sampleBackgrounds = []

        # Parse the GudrunFile.
        self.parse()

    def parseInstrument(self, lines):
        """
        Intialises an Instrument object and assigns it to the
        instrument attribute.
        Parses the attributes of the Instrument from the input lines.
        Raises a ValueError if any mandatory attributes are missing.


        Parameters
        ----------
        lines : str
            Input lines to parse the Instrument from.
        Returns
        -------
        None
        """

        self.instrument = Instrument()

        # Dictionary of key phrases for ensuring expected data is on
        # the expected lines.
        KEYPHRASES = {
            "name": "Instrument name",
            "GudrunInputFileDir": "Gudrun input file dir",
            "dataFileDir": "Data file dir",
            "dataFileType": "Data file type",
            "detectorCalibrationFileName": "Detector calibration",
            "columnNoPhiVals": "phi values",
            "groupFileName": "Groups file name",
            "deadtimeConstantsFileName": "Deadtime constants",
            "spectrumNumbersForIncidentBeamMonitor": [
                "Spectrum",
                "number",
                "incident",
            ],
            "wavelengthRangeForMonitorNormalisation": [
                "Wavelength",
                "range",
                "normalisation",
            ],
            "spectrumNumbersForTransmissionMonitor": [
                "Spectrum",
                "number",
                "transmission",
            ],
            "incidentMonitorQuietCountConst": ["Incident", "quiet", "count"],
            "transmissionMonitorQuietCountConst": [
                "Transmission",
                "quiet",
                "count",
            ],
            "channelNosSpikeAnalysis": "Channel numbers",
            "spikeAnalysisAcceptanceFactor": "Spike analysis acceptance",
            "wavelengthMin": ["Wavelength", "range", "step", "size"],
            "NoSmoothsOnMonitor": "smooths on monitor",
            "XMin": "x-scale",
            "groupsAcceptanceFactor": "Groups acceptance",
            "mergePower": "Merge power",
            "subSingleAtomScattering": ["single", "atom", "scattering?"],
            "mergeWeights": ["By", "?"],
            "incidentFlightPath": "Incident flight path",
            "spectrumNumberForOutputDiagnosticFiles": [
                "Spectrum",
                "number",
                "diagnostic",
            ],
            "neutronScatteringParametersFile": "Neutron scattering parameters",
            "scaleSelection": "Scale selection",
            "subWavelengthBinnedData": ["Subtract", "wavelength-binned"],
            "GudrunStartFolder": "Folder where Gudrun started",
            "startupFileFolder": "Folder containing the startup file",
            "logarithmicStepSize": "Logarithmic step size",
            "hardGroupEdges": "edges?",
            "numberIterations": "iterations",
            "tweakTweakFactors": "tweak",
        }

        # Extract marker line
        lines = [
            line
            for line in lines
            if "end input of specified values" not in line
        ]

        # Check if the grouping parameter panel
        # attribute is present in the file
        isGroupingParameterPanelUsed = [
            line
            for line in lines
            if "Group, Xmin, Xmax, Background factor" in line
        ]

        # If grouping parameter panel is not being used,
        # remove its key from the dict
        auxVars = deepcopy(self.instrument.__dict__)
        if not len(isGroupingParameterPanelUsed):
            auxVars.pop("groupingParameterPanel", None)

        # Pop these attributes, we will deal with them separately.
        auxVars.pop("wavelengthMax", None)
        auxVars.pop("wavelengthStep", None)
        auxVars.pop("XMax", None)
        auxVars.pop("XStep", None)
        auxVars.pop("useLogarithmicBinning", None)

        # Map the attributes of the Instrument class to line numbers.

        FORMAT_MAP = dict.fromkeys(auxVars.keys())
        FORMAT_MAP.update((k, i) for i, k in enumerate(FORMAT_MAP))
        # Categorise attributes by variables, for easier handling.

        STRINGS = [
            x
            for x in self.instrument.__dict__.keys()
            if isinstance(self.instrument.__dict__[x], str)
        ]
        LISTS = [
            x
            for x in self.instrument.__dict__.keys()
            if isinstance(self.instrument.__dict__[x], list)
        ]
        INTS = [
            x
            for x in self.instrument.__dict__.keys()
            if isinstance(self.instrument.__dict__[x], int)
            and not isinstance(self.instrument.__dict__[x], bool)
        ]
        FLOATS = [
            x
            for x in self.instrument.__dict__.keys()
            if isinstance(self.instrument.__dict__[x], float)
        ]
        BOOLS = [
            x
            for x in self.instrument.__dict__.keys()
            if isinstance(self.instrument.__dict__[x], bool)
        ]
        TUPLES = [
            x
            for x in self.instrument.__dict__.keys()
            if isinstance(self.instrument.__dict__[x], tuple)
        ]
        TUPLE_INTS = [
            x for x in TUPLES if iteristype(self.instrument.__dict__[x], int)
        ]
        TUPLE_FLOATS = [
            x for x in TUPLES if iteristype(self.instrument.__dict__[x], float)
        ]

        """
        Get all attributes that are strings:
            - Instrument name
            - Gudrun input file directory
            - Data file directory
            - Data file type
            - Detector calibration file name
            - Group file name
            - Deadtime constants file name
            - Neutron scattering parameters file
            - Gudrun start folder
            - Startup file folder
        """

        for key in STRINGS:
            try:
                isin_, i = isin(KEYPHRASES[key], lines)
                if not isin_:
                    raise ValueError(
                        "Whilst parsing INSTRUMENT, {} was not found".format(
                            key
                        )
                    )
                if i != FORMAT_MAP[key]:
                    FORMAT_MAP[key] = i
                self.instrument.__dict__[key] = firstword(
                    lines[FORMAT_MAP[key]]
                )
            except IndexError:
                continue
        """
        Get all attributes that are integers:
            - User table column number for phi values
            - Spike analysis acceptance factor
            - Number of smooths on monitor
            - Merge power
            - Channel for subtracting single atom scattering
            - Spectrum number for output diagnostic files
            - Scale selection
            - Number of iterations
        """

        for key in INTS:
            isin_, i = isin(KEYPHRASES[key], lines)
            if not isin_:
                raise ValueError(
                    "Whilst parsing INSTRUMENT, {} was not found".format(key)
                )
            if i != FORMAT_MAP[key]:
                FORMAT_MAP[key] = i
            self.instrument.__dict__[key] = int(
                firstword(lines[FORMAT_MAP[key]])
            )

        """
        Get all attributes that are floats (doubles):
            - Incident monitor quiet count constant
            - Transmission monitor quiet count constant
            - Groups acceptance factor
            - Incident flight path
            - Logarithmic step size
        """

        for key in FLOATS:
            if key in ["XMax", "XStep", "wavelengthMax", "wavelengthStep"]:
                continue
            isin_, i = isin(KEYPHRASES[key], lines)
            if not isin_:
                if key == "XMin":
                    raise ValueError(
                        'Whilst parsing INSTRUMENT'
                        ', Xmin, Xmax, XStep was not found'
                    )
                elif key == "wavelengthMin":
                    raise ValueError(
                        'Whilst parsing INSTRUMENT'
                        ', wavelengthMin, wavelengthMax,'
                        ' wavelengthStep was not found'
                    )
                else:
                    raise ValueError(
                        f'Whilst parsing INSTRUMENT, {key} was not found'
                    )
            if i != FORMAT_MAP[key]:
                FORMAT_MAP[key] = i
            if key == "XMin":
                XScale = extract_floats_from_string(
                    lines[FORMAT_MAP[key]]
                )
                self.instrument.__dict__["XMin"] = XScale[0]
                self.instrument.__dict__["XMax"] = XScale[1]
                self.instrument.__dict__["XStep"] = XScale[2]
                if len(XScale) > 3:
                    if XScale[3] == -0.01:
                        self.instrument.__dict__["useLogarithmicBinning"] = (
                            True
                        )
            elif key == "wavelengthMin":
                wScale = extract_floats_from_string(
                    lines[FORMAT_MAP[key]]
                )
                self.instrument.__dict__["wavelengthMin"] = wScale[0]
                self.instrument.__dict__["wavelengthMax"] = wScale[1]
                self.instrument.__dict__["wavelengthStep"] = wScale[2]
            else:
                self.instrument.__dict__[key] = float(
                    firstword(lines[FORMAT_MAP[key]])
                )

        """
        Get all attributes that are boolean values:
            - Subtract single atom scattering?
            - Subtract wavelength-binned data?
            - Hard group edges?
            - Tweak the tweak factor(s)?
        """

        for key in BOOLS:
            if key == "useLogarithmicBinning":
                continue
            isin_, i = isin(KEYPHRASES[key], lines)
            if not isin_:
                raise ValueError(
                    "Whilst parsing INSTRUMENT, {} was not found".format(key)
                )
            if i != FORMAT_MAP[key]:
                FORMAT_MAP[key] = i
            self.instrument.__dict__[key] = boolifyNum(
                int(firstword(lines[FORMAT_MAP[key]]))
            )

        """
        Get all attributes that need to be stored in arbitrary sized lists:
            - Spectrum numbers for incident beam monitor
            - Spectrum numbers for transmission monitor
        """

        for key in LISTS:
            isin_, i = isin(KEYPHRASES[key], lines)
            if not isin_:
                raise ValueError(
                    "Whilst parsing INSTRUMENT, {} was not found".format(key)
                )
            if i != FORMAT_MAP[key]:
                FORMAT_MAP[key] = i
            self.instrument.__dict__[key] = extract_ints_from_string(
                lines[FORMAT_MAP[key]]
            )

        """
        Get all attributes that need to be stored as a tuple of ints:
            - Wavelength range for monitor normalisation
            - Channel numbers for spike analysis
        """

        for key in TUPLE_INTS:
            isin_, i = isin(KEYPHRASES[key], lines)
            if not isin_:
                raise ValueError(
                    "Whilst parsing INSTRUMENT, {} was not found".format(key)
                )
            if i != FORMAT_MAP[key]:
                FORMAT_MAP[key] = i
            self.instrument.__dict__[key] = tuple(
                extract_ints_from_string(lines[FORMAT_MAP[key]])
            )

        """
        Get all attributes that need to be stored as a tuple of floats:
            - Wavelength range to use and step size.
        """

        for key in TUPLE_FLOATS:
            isin_, i = isin(KEYPHRASES[key], lines)
            if not isin_:
                raise ValueError(
                    "Whilst parsing INSTRUMENT, {} was not found".format(key)
                )
            if i != FORMAT_MAP[key]:
                FORMAT_MAP[key] = i
            self.instrument.__dict__[key] = tuple(
                extract_floats_from_string(lines[FORMAT_MAP[key]])
            )

        """
        Get the attributes for the grouping parameter panel:
            - Group
            - Xmin
            - Xmax
            - Background factor
        """
        if isGroupingParameterPanelUsed:
            key = "groupingParameterPanel"
            group = int(firstword(lines[FORMAT_MAP[key]]))
            maxMinBf = extract_floats_from_string(lines[FORMAT_MAP[key]])[1:]
            groupingParameterPanel = tuple([group] + maxMinBf)
            self.instrument.__dict__[key] = groupingParameterPanel

    def parseBeam(self, lines):
        """
        Intialises a Beam object and assigns it to the
        beam attribute.
        Parses the attributes of the Beam from the input lines.
        Raises a ValueError if any mandatory attributes are missing.


        Parameters
        ----------
        lines : str
            Input lines to parse the Beam from.
        Returns
        -------
        None
        """

        self.beam = Beam()

        # Dictionary of key phrases for ensuring expected data is on
        # the expected lines.
        KEYPHRASES = {
            "sampleGeometry": "Sample geometry",
            "noBeamProfileValues": ["number", "beam", "profile", "values"],
            "beamProfileValues": ["Beam", "profile", "values", "("],
            "stepSizeAbsorption": ["Step", "size", "m.s"],
            "angularStepForCorrections": "Angular step",
            "incidentBeamLeftEdge": "Incident beam edges",
            "scatteredBeamLeftEdge": "Scattered beam edges",
            "filenameIncidentBeamSpectrumParams": [
                "Filename",
                "incident",
                "spectrum",
                "parameters",
            ],
            "overallBackgroundFactor": "Overall background factor",
            "sampleDependantBackgroundFactor": "Sample dependent background",
            "shieldingAttenuationCoefficient": [
                "Shielding",
                "attenuation",
                "coefficient",
            ],
        }

        # Map the attributes of the Beam class to line numbers.

        FORMAT_MAP = dict.fromkeys(self.beam.__dict__.keys())
        FORMAT_MAP.pop("incidentBeamRightEdge", None)
        FORMAT_MAP.pop("incidentBeamTopEdge", None)
        FORMAT_MAP.pop("incidentBeamBottomEdge", None)
        FORMAT_MAP.pop("scatteredBeamRightEdge", None)
        FORMAT_MAP.pop("scatteredBeamTopEdge", None)
        FORMAT_MAP.pop("scatteredBeamBottomEdge", None)
        FORMAT_MAP.update((k, i) for i, k in enumerate(FORMAT_MAP))

        # Categorise attributes by variables, for easier handling.

        STRINGS = [
            x
            for x in self.beam.__dict__.keys()
            if isinstance(self.beam.__dict__[x], str)
        ]
        LISTS = [
            x
            for x in self.beam.__dict__.keys()
            if isinstance(self.beam.__dict__[x], list)
        ]
        INTS = [
            x
            for x in self.beam.__dict__.keys()
            if isinstance(self.beam.__dict__[x], int)
            and not isinstance(self.beam.__dict__[x], bool)
        ]
        FLOATS = [
            x
            for x in self.beam.__dict__.keys()
            if isinstance(self.beam.__dict__[x], float)
        ]
        TUPLES = [
            x
            for x in self.beam.__dict__.keys()
            if isinstance(self.beam.__dict__[x], tuple)
        ]
        TUPLE_FLOATS = [
            x for x in TUPLES if iteristype(self.beam.__dict__[x], float)
        ]

        """
        Get all attributes that are strings:
            - Sample geometry
            - Filename for incident beam spectrum parameters
        """

        for key in STRINGS:
            isin_, i = isin(KEYPHRASES[key], lines)
            if not isin_:
                raise ValueError(
                    "Whilst parsing BEAM, {} was not found".format(key)
                )
            if i != FORMAT_MAP[key]:
                FORMAT_MAP[key] = i
            self.beam.__dict__[key] = firstword(lines[FORMAT_MAP[key]])

        """
        Get all attributes that are integers:
            - Number of beam profile values
            - Angular step for corrections
        """

        for key in INTS:
            if key == "noSlices":
                continue
            isin_, i = isin(KEYPHRASES[key], lines)
            if not isin_:
                raise ValueError(
                    "Whilst parsing BEAM, {} was not found".format(key)
                )
            if i != FORMAT_MAP[key]:
                FORMAT_MAP[key] = i
            self.beam.__dict__[key] = int(firstword(lines[FORMAT_MAP[key]]))

        """
        Get all attributes that are floats (doubles):
            - Overall background factor
            - Sample dependant background factor
            - Shielding attenuation coefficient
        """

        for key in FLOATS:
            if key in [
                    "incidentBeamRightEdge", "incidentBeamTopEdge",
                    "incidentBeamBottomEdge", "scatteredBeamRightEdge",
                    "scatteredBeamTopEdge", "scatteredBeamBottomEdge",
                    "stepSizeAbsorption", "stepSizeMS"
                    ]:
                continue
            isin_, i = isin(KEYPHRASES[key], lines)
            if not isin_:
                raise ValueError(
                    "Whilst parsing BEAM, {} was not found".format(key)
                )
            if i != FORMAT_MAP[key]:
                FORMAT_MAP[key] = i

            if key == "incidentBeamLeftEdge":
                edges = extract_floats_from_string(lines[FORMAT_MAP[key]])
                (
                    self.beam.incidentBeamLeftEdge,
                    self.beam.incidentBeamRightEdge,
                    self.beam.incidentBeamTopEdge,
                    self.beam.incidentBeamBottomEdge,
                    *rest
                ) = edges
            elif key == "scatteredBeamLeftEdge":
                edges = extract_floats_from_string(lines[FORMAT_MAP[key]])
                (
                    self.beam.scatteredBeamLeftEdge,
                    self.beam.scatteredBeamRightEdge,
                    self.beam.scatteredBeamTopEdge,
                    self.beam.scatteredBeamBottomEdge,
                    *rest
                ) = edges
            else:
                self.beam.__dict__[key] = float(
                    firstword(lines[FORMAT_MAP[key]])
                )

        """
        Get all attributes that need to be stored in arbitrary sized lists:
            - Beam profile values
        """

        for key in LISTS:
            isin_, i = isin(KEYPHRASES[key], lines)
            if not isin_:
                raise ValueError(
                    "Whilst parsing BEAM, {} was not found".format(key)
                )
            if i != FORMAT_MAP[key]:
                FORMAT_MAP[key] = i
            self.beam.__dict__[key] = extract_floats_from_string(
                lines[FORMAT_MAP[key]]
            )

        """
        Get all attributes that need to be stored as a tuple of floats:
            - Incident beam edges relative to centre of sample
            - Scattered beam edges relative to centre of sample
        """

        for key in TUPLE_FLOATS:
            isin_, i = isin(KEYPHRASES[key], lines)
            if not isin_:
                raise ValueError(
                    "Whilst parsing BEAM, {} was not found".format(key)
                )
            if i != FORMAT_MAP[key]:
                FORMAT_MAP[key] = i
            self.beam.__dict__[key] = tuple(
                extract_floats_from_string(lines[FORMAT_MAP[key]])
            )

        """
        Get the step size for absorption
        and m.s. calculation and number of slices
        """

        key = "stepSizeAbsorption"
        isin_, i = isin(KEYPHRASES[key], lines)
        if not isin_:
            raise ValueError(
                "Whilst parsing BEAM, {} was not found".format(key)
            )
        if i != FORMAT_MAP[key]:
            FORMAT_MAP[key] = i
        stepSizeAbsorptionMS = extract_floats_from_string(
            lines[FORMAT_MAP[key]]
        )
        (
            self.beam.stepSizeAbsorption,
            self.beam.stepSizeMS,
            self.beam.noSlices,
            *rest
        ) = stepSizeAbsorptionMS
        self.beam.noSlices = int(self.beam.noSlices)

    def parseNormalisation(self, lines):
        """
        Intialises a Normalisation object and assigns it to the
        normalisation attribute.
        Parses the attributes of the Normalisation from the input lines.
        Raises a ValueError if any mandatory attributes are missing.


        Parameters
        ----------
        lines : str
            Input lines to parse the Normalisation from.
        Returns
        -------
        None
        """

        self.normalisation = Normalisation()

        # Dictionary of key phrases for ensuring expected data is on
        # the expected lines.
        KEYPHRASES = {
            "forceCalculationOfCorrections": ["Force", "corrections?"],
            "geometry": "Geometry",
            "thickness": ["Upstream", "downstream", "thickness"],
            "angleOfRotationSampleWidth": "Angle of rotation",
            "density": "Density",
            "tempForNormalisationPC": "Placzek correction",
            "totalCrossSectionSource": "Total cross",
            "normalisationDifferentialCrossSectionFilename": [
                "Normalisation",
                "cross section",
                "filename",
            ],
            "lowerLimitSmoothedNormalisation": "Lower limit",
            "normalisationDegreeSmoothing": "Normalisation degree",
            "minNormalisationSignalBR": "background ratio",
        }

        # Count the number of data files and background data files.

        if not isin(["number", "files", "period"], lines) == (True, 0):
            raise ValueError((
                'Whilst parsing NORMALISATION, '
                'numberOfFilesPeriodNumber was not found'
            ))

        if not isin(["number", "files", "period"], deepcopy(lines[2:]))[0]:
            raise ValueError((
                'Whilst parsing NORMALISATION, '
                'numberOfFilesPeriodNumberBg was not found'
            ))

        numberFiles = extract_ints_from_string(lines[0])[0]
        numberFilesBG = extract_ints_from_string(lines[numberFiles + 1])[0]

        # Count the number of elements
        numberElements = count_occurrences(
            "Normalisation atomic composition", lines
        ) + count_occurrences("Composition", lines)

        # Map the attributes of the Beam class to line numbers.

        FORMAT_MAP = dict.fromkeys(self.normalisation.__dict__.keys())
        FORMAT_MAP.pop("dataFiles", None)
        FORMAT_MAP.pop("dataFilesBg", None)
        FORMAT_MAP.pop("composition", None)
        FORMAT_MAP.pop("densityUnits", None)
        FORMAT_MAP.update((k, i) for i, k in enumerate(FORMAT_MAP))

        # Index arithmetic to fix indexes,
        # which get skewed by data files and elements

        for key in FORMAT_MAP.keys():
            if FORMAT_MAP[key] > 0:
                FORMAT_MAP[key] += numberFiles

        marker = 0
        for key in FORMAT_MAP.keys():
            if FORMAT_MAP[key] - numberFiles == 1:
                marker = FORMAT_MAP[key]
                continue
            if marker:
                if FORMAT_MAP[key] > marker:
                    FORMAT_MAP[key] += numberFilesBG

        marker = 0
        for key in FORMAT_MAP.keys():
            if FORMAT_MAP[key] - numberFilesBG - numberFiles == 2:
                marker = FORMAT_MAP[key]
                continue
            if marker:
                if FORMAT_MAP[key] > marker:
                    FORMAT_MAP[key] += numberElements + 1

        # Categorise attributes by variables, for easier handling.
        STRINGS = [
            x
            for x in self.normalisation.__dict__.keys()
            if isinstance(self.normalisation.__dict__[x], str)
        ]
        INTS = [
            x
            for x in self.normalisation.__dict__.keys()
            if isinstance(self.normalisation.__dict__[x], int)
            and not isinstance(self.normalisation.__dict__[x], bool)
        ]
        FLOATS = [
            x
            for x in self.normalisation.__dict__.keys()
            if isinstance(self.normalisation.__dict__[x], float)
        ]
        BOOLS = [
            x
            for x in self.normalisation.__dict__.keys()
            if isinstance(self.normalisation.__dict__[x], bool)
        ]
        TUPLES = [
            x
            for x in self.normalisation.__dict__.keys()
            if isinstance(self.normalisation.__dict__[x], tuple)
        ]
        TUPLE_FLOATS = [
            x
            for x in TUPLES
            if iteristype(self.normalisation.__dict__[x], float)
        ]
        TUPLE_INTS = [
            x
            for x in TUPLES
            if iteristype(self.normalisation.__dict__[x], int)
        ]

        """
        Get all attributes that are strings:
            - Geometry
            - Total cross section source
            - Normalisation differential cross section filename
        """

        for key in STRINGS:
            isin_, i = isin(KEYPHRASES[key], lines)
            if not isin_:
                raise ValueError(
                    "Whilst parsing NORMALISATION, {} was not found".format(
                        key
                    )
                )
            if i != FORMAT_MAP[key]:
                FORMAT_MAP[key] = i
            self.normalisation.__dict__[key] = firstword(
                lines[FORMAT_MAP[key]]
            )

        """
        Get all attributes that are integers:
            - Temperature for normalisation Placzek correction
        """

        for key in INTS:
            if key == "densityUnits":
                continue
            isin_, i = isin(KEYPHRASES[key], lines)
            if not isin_:
                raise ValueError(
                    "Whilst parsing NORMALISATION, {} was not found".format(
                        key
                    )
                )
            if i != FORMAT_MAP[key]:
                FORMAT_MAP[key] = i
            self.normalisation.__dict__[key] = int(
                firstword(lines[FORMAT_MAP[key]])
            )

        """
        Get all attributes that are floats (doubles):
            - Density of atoms
            - Lower limit on smoothed normalisation
            - Normalisation degree smoothing
            - Minimum normalisation signal to background ratio
        """

        for key in FLOATS:
            isin_, i = isin(KEYPHRASES[key], lines)
            if not isin_:
                raise ValueError(
                    "Whilst parsing NORMALISATION, {} was not found".format(
                        key
                    )
                )
            if i != FORMAT_MAP[key]:
                FORMAT_MAP[key] = i
            if key == "density":
                density = float(firstword(lines[FORMAT_MAP[key]]))
                if density < 0:
                    density = abs(density)
                    self.normalisation.densityUnits = (
                        UnitsOfDensity.ATOMIC.value
                    )
                else:
                    self.normalisation.densityUnits = (
                        UnitsOfDensity.CHEMICAL.value
                    )
                self.normalisation.__dict__[key] = density
            else:
                self.normalisation.__dict__[key] = (
                    float(firstword(lines[FORMAT_MAP[key]]))
                )

        """
        Get all attributes that are boolean values:
            - Subtract single atom scattering?
            - Subtract wavelength-binned data?
            - Hard group edges?
            - Tweak the tweak factor(s)?
        """

        for key in BOOLS:
            isin_, i = isin(KEYPHRASES[key], lines)
            if not isin_:
                raise ValueError(
                    "Whilst parsing NORMALISATION, {} was not found".format(
                        key
                    )
                )
            if i != FORMAT_MAP[key]:
                FORMAT_MAP[key] = i
            self.normalisation.__dict__[key] = boolifyNum(
                int(firstword(lines[FORMAT_MAP[key]]))
            )

        """
        Get all attributes that need to be stored as a tuple of floats:
            - Upstream and downstream thickness
            - Angle of rotation and sample width
        """

        for key in TUPLE_FLOATS:
            isin_, i = isin(KEYPHRASES[key], lines)
            if not isin_:
                raise ValueError(
                    "Whilst parsing NORMALISATION, {} was not found".format(
                        key
                    )
                )
            if i != FORMAT_MAP[key]:
                FORMAT_MAP[key] = i
            self.normalisation.__dict__[key] = tuple(
                extract_floats_from_string(lines[FORMAT_MAP[key]])
            )
            if key == "angleOfRotationSampleWidth":
                self.normalisation.__dict__[key] = (
                    self.normalisation.__dict__[key][0],
                    int(self.normalisation.__dict__[key][1]),
                )

        """
        Get all attributes that need to be stored as a tuple of ints:
            - Number of files and period number
            - Number of background files and period number
        """

        for key in TUPLE_INTS:
            self.normalisation.__dict__[key] = tuple(
                extract_ints_from_string(lines[FORMAT_MAP[key]])
            )

        # Get all of the normalisation datafiles and their information.

        dataFiles = []
        for j in range(self.normalisation.numberOfFilesPeriodNumber[0]):
            curr = lines[FORMAT_MAP["numberOfFilesPeriodNumber"] + j + 1]
            if "data files" in curr or "Data files" in curr:
                dataFiles.append(firstword(curr))
            else:
                raise ValueError(
                    "Number of data files does not \
                    match number of data files specified"
                )
        self.normalisation.dataFiles = DataFiles(
            deepcopy(dataFiles), "NORMALISATION"
        )

        # Get all of the normalisation
        # background datafiles and their information.

        dataFiles = []
        for j in range(self.normalisation.numberOfFilesPeriodNumberBg[0]):
            curr = lines[FORMAT_MAP["numberOfFilesPeriodNumberBg"] + j + 1]
            if "data files" in curr or "Data files" in curr:
                dataFiles.append(firstword(curr))
            else:
                raise ValueError(
                    "Number of data files does not \
                    match number of data files specified"
                )
        self.normalisation.dataFilesBg = DataFiles(
            deepcopy(dataFiles), "NORMALISATION BACKGROUND"
        )

        # Get all of the elements and their information,
        # and then build the composition

        elements = []
        for j in range(numberElements):
            curr = lines[FORMAT_MAP["forceCalculationOfCorrections"] + j + 1]
            if (
                "Normalisation atomic composition" in curr
                or "Composition" in curr
            ):
                elementInfo = [x for x in curr.split(" ") if x][:3]
                element = Element(
                    elementInfo[0], int(elementInfo[1]), float(elementInfo[2])
                )
                elements.append(element)

        self.normalisation.composition = Composition(elements, "Normalisation")

    def parseSampleBackground(self, lines):
        """
        Intialises a SampleBackground object.
        Parses the attributes of the SampleBackground from the input lines.
        Raises a ValueError if any mandatory attributes are missing.
        Returns the parsed object.

        Parameters
        ----------
        lines : str
            Input lines to parse the Instrument from.
        Returns
        -------
        sampleBackground : SampleBackground
            The SampleBackground that was parsed from the input lines.
        """

        sampleBackground = SampleBackground()

        # Get the number of files and period number.
        if not isin(["files", "period"], lines)[0]:
            raise ValueError((
                'Whilst parsing SAMPLE BACKGROUND 1, '
                'numberOfFilesPeriodNumber was not found'
            ))
        sampleBackground.numberOfFilesPeriodNumber = tuple(
            extract_ints_from_string(str(lines[0]))
        )

        # Get the associated data files.
        dataFiles = []
        for i in range(sampleBackground.numberOfFilesPeriodNumber[0]):
            if "data files" in lines[i + 1]:
                dataFiles.append(firstword(lines[i + 1]))
            else:
                raise ValueError(
                    "Number of data files does not\
                     match number of data files specified"
                )
        sampleBackground.dataFiles = DataFiles(dataFiles, "SAMPLE BACKGROUND")

        return sampleBackground

    def parseSample(self, lines):
        """
        Intialises a Sample object.
        Parses the attributes of the Sample from the input lines.
        Raises a ValueError if any mandatory attributes are missing.
        Returns the parsed object.

        Parameters
        ----------
        lines : str
            Input lines to parse the Instrument from.
        Returns
        -------
        sample : Sample
            The Sample that was parsed from the input lines.
        """

        sample = Sample()

        # Extract the name from the lines,
        # and then discard the unnecessary lines.
        sample.name = str(lines[0][:-2]).strip()
        lines[:] = lines[2:]

        # Dictionary of key phrases for ensuring expected data is on
        # the expected lines.
        KEYPHRASES = {
            "numberOfFilesPeriodNumber": ["files", "period"],
            "forceCalculationOfCorrections": ["Force", "corrections?"],
            "geometry": "Geometry",
            "thickness": ["Upstream", "downstream", "thickness"],
            "angleOfRotationSampleWidth": "Angle of rotation",
            "density": "Density",
            "tempForNormalisationPC": "Placzek correction",
            "totalCrossSectionSource": "Total cross",
            "sampleTweakFactor": "tweak factor",
            "topHatW": "Top hat width",
            "minRadFT": "Minimum radius for FT",
            "grBroadening": ["g(r)", "broadening"],
            "expAandD": ["Exponential", "amplitude", "decay"],
            "normalisationCorrectionFactor": "Normalisation correction factor",
            "fileSelfScattering": ["file", "self scattering", "function"],
            "normaliseTo": "Normalise",
            "maxRadFT": "Maximum radius for FT",
            "outputUnits": "Output units",
            "powerForBroadening": "Power for broadening",
            "stepSize": "Step size",
            "include": ["Analyse", "sample?"],
            "environementScatteringFuncAttenuationCoeff": [
                "environment",
                "scattering fraction",
                "attenuation coefficient",
            ],
        }

        # Discard lines which don't contain information.
        lines = [
            line
            for line in lines
            if "end of" not in line and "to finish" not in line
        ]

        # Count the number of files and the number of elements.
        numberFiles = count_occurrences("data files", lines)
        numberElements = count_occurrences(
            "Sample atomic composition", lines
        ) + count_occurrences("Composition", lines)

        # Map the attributes of the Sample class to line numbers.

        FORMAT_MAP = dict.fromkeys(sample.__dict__.keys())
        FORMAT_MAP.pop("name", None)
        FORMAT_MAP.pop("dataFiles", None)
        FORMAT_MAP.pop("composition", None)
        FORMAT_MAP.pop("sampleBackground", None)
        FORMAT_MAP.pop("containers", None)
        FORMAT_MAP.pop("runThisSample", None)
        FORMAT_MAP.pop("densityUnits", None)
        FORMAT_MAP.update((k, i) for i, k in enumerate(FORMAT_MAP))

        # Index arithmetic to fix indexes,
        # which get skewed by data files and elements

        for key in FORMAT_MAP.keys():
            if FORMAT_MAP[key] > 0:
                FORMAT_MAP[key] += numberFiles

        marker = 0
        for key in FORMAT_MAP.keys():
            if FORMAT_MAP[key] - numberFiles == 1:
                marker = FORMAT_MAP[key]
                # print(key)
                continue
            if marker:
                if FORMAT_MAP[key] > marker:
                    FORMAT_MAP[key] += numberElements

        # Categorise attributes by variables, for easier handling.
        STRINGS = [
            x
            for x in sample.__dict__.keys()
            if isinstance(sample.__dict__[x], str)
        ]
        INTS = [
            x
            for x in sample.__dict__.keys()
            if isinstance(sample.__dict__[x], int)
            and not isinstance(sample.__dict__[x], bool)
        ]
        FLOATS = [
            x
            for x in sample.__dict__.keys()
            if isinstance(sample.__dict__[x], float)
        ]
        BOOLS = [
            x
            for x in sample.__dict__.keys()
            if isinstance(sample.__dict__[x], bool)
            and not x == "runThisSample"
        ]
        TUPLES = [
            x
            for x in sample.__dict__.keys()
            if isinstance(sample.__dict__[x], tuple)
        ]
        TUPLE_FLOATS = [
            x for x in TUPLES if iteristype(sample.__dict__[x], float)
        ]
        TUPLE_INTS = [x for x in TUPLES if iteristype(sample.__dict__[x], int)]

        """
        Get all attributes that are strings:
            - Geometry
            - Total cross section source
            - File containing self scattering as a function of wavelength [A]
        """

        for key in STRINGS:
            try:
                isin_, i = isin(KEYPHRASES[key], lines)
                if not isin_:
                    raise ValueError(
                        "Whilst parsing {}, {} was not found".format(
                            sample.name, key
                        )
                    )
                if i != FORMAT_MAP[key]:
                    FORMAT_MAP[key] = i
                sample.__dict__[key] = firstword(lines[FORMAT_MAP[key]])
            except KeyError:
                continue
            # print(firstword(lines(FORMAT_MAP[key])))

        """
        Get all attributes that are integers:
            - Temperature for normalisation Placzek correction
            - Top hat width (1/\u212b) for cleaning up Fourier Transform
            - Normalise to
            - Output units
        """

        for key in INTS:
            if key == "densityUnits":
                continue
            isin_, i = isin(KEYPHRASES[key], lines)
            if not isin_:
                raise ValueError(
                    "Whilst parsing {}, {} was not found".format(
                        sample.name, key
                    )
                )
            if i != FORMAT_MAP[key]:
                FORMAT_MAP[key] = i
            sample.__dict__[key] = int(firstword(lines[FORMAT_MAP[key]]))

        """
        Get all attributes that are floats (doubles):
            - Density of atoms
            - Sample tweak factor
            - Minimum radius for Fourier Transform
            - g(r) broadening at r= 1A
            - Maximum radius for Fourier Transform
            - Power for broadening function
            - Step size
        """

        for key in FLOATS:
            isin_, i = isin(KEYPHRASES[key], lines)
            if not isin_:
                raise ValueError(
                    "Whilst parsing {}, {} was not found".format(
                        sample.name, key
                    )
                )
            if i != FORMAT_MAP[key]:
                FORMAT_MAP[key] = i
            if key == "density":
                density = float(firstword(lines[FORMAT_MAP[key]]))
                if density < 0:
                    density = abs(density)
                    sample.densityUnits = UnitsOfDensity.ATOMIC.value
                else:
                    sample.densityUnits = UnitsOfDensity.CHEMICAL.value
                sample.__dict__[key] = density
            else:
                sample.__dict__[key] = float(firstword(lines[FORMAT_MAP[key]]))

        """
        Get all attributes that are boolean values:
            - Force calculation of corrections?
            - Analyse this sample?
        """

        for key in BOOLS:
            isin_, i = isin(KEYPHRASES[key], lines)
            if not isin_:
                raise ValueError(
                    "Whilst parsing {}, {} was not found".format(
                        sample.name, key
                    )
                )
            if i != FORMAT_MAP[key]:
                FORMAT_MAP[key] = i
            sample.__dict__[key] = boolifyNum(
                int(firstword(lines[FORMAT_MAP[key]]))
            )

        """
        Get all attributes that need to be stored as a tuple of floats:
            - Upstream and downstream thickness
            - Angle of rotation and sample width
            - Sample environment scattering fraction
                and attenuation coefficient
        """

        for key in TUPLE_FLOATS:
            isin_, i = isin(KEYPHRASES[key], lines)
            if not isin_:
                raise ValueError(
                    "Whilst parsing {}, {} was not found".format(
                        sample.name, key
                    )
                )
            if i != FORMAT_MAP[key]:
                FORMAT_MAP[key] = i
            sample.__dict__[key] = tuple(
                extract_floats_from_string(lines[FORMAT_MAP[key]])
            )
            if key == "angleOfRotationSampleWidth":
                sample.__dict__[key] = (
                    sample.__dict__[key][0],
                    int(sample.__dict__[key][1]),
                )

        """
        Get all attributes that need to be stored as a tuple of ints:
            - Number of files and period number
        """

        for key in TUPLE_INTS:
            isin_, i = isin(KEYPHRASES[key], lines)
            if not isin_:
                raise ValueError(
                    "Whilst parsing {}, {} was not found".format(
                        sample.name, key
                    )
                )
            if i != FORMAT_MAP[key]:
                FORMAT_MAP[key] = i
            sample.__dict__[key] = tuple(
                extract_ints_from_string(lines[FORMAT_MAP[key]])
            )

        """
        Get the exponential amplitude and decay
        """

        key = "expAandD"
        isin_, i = isin(KEYPHRASES[key], lines)
        if not isin_:
            raise ValueError(
                "Whilst parsing {}, {} was not found".format(sample.name, key)
            )
        if i != FORMAT_MAP[key]:
            FORMAT_MAP[key] = i
        expAmp = extract_floats_from_string(lines[FORMAT_MAP[key]])[:2]
        decay = int(extract_floats_from_string(lines[FORMAT_MAP[key]])[2])
        expAandD = tuple(expAmp + [decay])
        sample.__dict__[key] = expAandD

        # Get all of the sample datafiles and their information.

        dataFiles = []
        for j in range(sample.numberOfFilesPeriodNumber[0]):
            curr = lines[FORMAT_MAP["numberOfFilesPeriodNumber"] + j + 1]
            if "data files" in curr:
                dataFiles.append(firstword(curr))
            else:
                raise ValueError(
                    "Number of data files does not\
                     match number of data files specified"
                )
        sample.dataFiles = DataFiles(
            deepcopy(dataFiles), "{}".format(sample.name)
        )

        # Get all of the elements and their information,
        # and then build the composition

        elements = []
        for j in range(numberElements):
            curr = lines[FORMAT_MAP["forceCalculationOfCorrections"] + j + 1]
            if "Sample atomic composition" in curr or "Composition" in curr:
                elementInfo = [x for x in curr.split(" ") if x][:3]
                element = Element(
                    elementInfo[0], int(elementInfo[1]), float(elementInfo[2])
                )
                elements.append(element)

        sample.composition = Composition(elements, "Sample")

        return sample

    def parseContainer(self, lines):
        """
        Intialises a Container object.
        Parses the attributes of the Container from the input lines.
        Raises a ValueError if any mandatory attributes are missing.
        Returns the parsed object.

        Parameters
        ----------
        lines : str
            Input lines to parse the Instrument from.
        Returns
        -------
        container : Container
            The Container that was parsed from the input lines.
        """

        container = Container()
        # Extract the name from the lines,
        # and then discard the unnecessary lines.
        container.name = str(lines[0][:-2]).strip()
        lines[:] = lines[2:]

        # Dictionary of key phrases for ensuring expected data is on
        # the expected lines.
        KEYPHRASES = {
            "numberOfFilesPeriodNumber": ["files", "period"],
            "geometry": "Geometry",
            "thickness": ["Upstream", "downstream", "thickness"],
            "angleOfRotationSampleWidth": "Angle of rotation",
            "density": "Density",
            "totalCrossSectionSource": "Total cross",
            "tweakFactor": "tweak factor",
            "scatteringFractionAttenuationCoefficient": [
                "environment",
                "scattering fraction",
                "attenuation coefficient",
            ],
        }

        lines = [line for line in lines if "end of" not in line]

        # Count the number of files and number of elements.
        numberFiles = count_occurrences("data files", lines)
        numberElements = count_occurrences(
            "Container atomic composition", lines
        ) + count_occurrences("Composition", lines)

        # Map the attributes of the Beam class to line numbers.

        FORMAT_MAP = dict.fromkeys(container.__dict__.keys())
        FORMAT_MAP.pop("name", None)
        FORMAT_MAP.pop("dataFiles", None)
        FORMAT_MAP.pop("composition", None)
        FORMAT_MAP.pop("densityUnits", None)
        FORMAT_MAP.update((k, i) for i, k in enumerate(FORMAT_MAP))

        for key in FORMAT_MAP.keys():
            if FORMAT_MAP[key] > 0:
                FORMAT_MAP[key] += numberFiles + numberElements

        # Categorise attributes by variables, for easier handling.
        STRINGS = [
            x
            for x in container.__dict__.keys()
            if isinstance(container.__dict__[x], str)
        ]
        FLOATS = [
            x
            for x in container.__dict__.keys()
            if isinstance(container.__dict__[x], float)
        ]
        TUPLES = [
            x
            for x in container.__dict__.keys()
            if isinstance(container.__dict__[x], tuple)
        ]
        TUPLE_FLOATS = [
            x for x in TUPLES if iteristype(container.__dict__[x], float)
        ]
        TUPLE_INTS = [
            x for x in TUPLES if iteristype(container.__dict__[x], int)
        ]

        """
        Get all attributes that are strings:
            - Geometry
            - Total cross section source
        """

        for key in STRINGS:
            try:
                isin_, i = isin(KEYPHRASES[key], lines)
                if not isin_:
                    raise ValueError(
                        "Whilst parsing {}, {} was not found".format(
                            container.name, key
                        )
                    )
                if i != FORMAT_MAP[key]:
                    FORMAT_MAP[key] = i
                container.__dict__[key] = firstword(lines[FORMAT_MAP[key]])
            except KeyError:
                continue

        """
        Get all attributes that are floats (doubles):
            - Density of atoms
            - Tweak factor
        """

        for key in FLOATS:
            isin_, i = isin(KEYPHRASES[key], lines)
            if not isin_:
                raise ValueError(
                    "Whilst parsing {}, {} was not found".format(
                        container.name, key
                    )
                )
            if i != FORMAT_MAP[key]:
                FORMAT_MAP[key] = i
            if key == "density":
                density = float(firstword(lines[FORMAT_MAP[key]]))
                if density < 0:
                    density = abs(density)
                    container.densityUnits = UnitsOfDensity.ATOMIC.value
                else:
                    container.densityUnits = UnitsOfDensity.CHEMICAL.value
                container.__dict__[key] = density
            else:
                container.__dict__[key] = (
                    float(firstword(lines[FORMAT_MAP[key]]))
                )

        """
        Get all attributes that need to be stored as a tuple of floats:
            - Upstream and downstream thickness
            - Angle of rotation and sample width
            - Sample environment scattering fraction
                and attenuation coefficient
        """

        for key in TUPLE_FLOATS:
            isin_, i = isin(KEYPHRASES[key], lines)
            if not isin_:
                raise ValueError(
                    "Whilst parsing {}, {} was not found".format(
                        container.name, key
                    )
                )
            if i != FORMAT_MAP[key]:
                FORMAT_MAP[key] = i
            container.__dict__[key] = tuple(
                extract_floats_from_string(lines[FORMAT_MAP[key]])
            )

        """
        Get all attributes that need to be stored as a tuple of ints:
            - Number of files and period number
        """

        for key in TUPLE_INTS:
            isin_, i = isin(KEYPHRASES[key], lines)
            if not isin_:
                raise ValueError(
                    "Whilst parsing {}, {} was not found".format(
                        container.name, key
                    )
                )
            if i != FORMAT_MAP[key]:
                FORMAT_MAP[key] = i
            container.__dict__[key] = tuple(
                extract_ints_from_string(lines[FORMAT_MAP[key]])
            )

        # Get all of the container datafiles and their information.

        dataFiles = []
        for j in range(numberFiles):
            curr = lines[FORMAT_MAP["numberOfFilesPeriodNumber"] + j + 1]
            if "data files" in curr:
                dataFiles.append(firstword(curr))
            else:
                raise ValueError(
                    "Number of data files does not \
                    match number of data files specified"
                )
        container.dataFiles = DataFiles(
            deepcopy(dataFiles), "{}".format(container.name)
        )

        # Get all elements in the composition and their details.

        elements = []
        for j in range(numberElements):
            curr = lines[
                FORMAT_MAP["numberOfFilesPeriodNumber"] + j + numberFiles + 1
            ]
            if "atomic composition" in curr or "Composition" in curr:
                elementInfo = [x for x in curr.split(" ") if x][:3]
                element = Element(
                    elementInfo[0], int(elementInfo[1]), float(elementInfo[2])
                )
                elements.append(element)
            else:
                print("ERROR " + str(curr))

        container.composition = Composition(elements, "Container")

        return container

    def makeParse(self, lines, key):
        """
        Calls a parsing function from a dictionary of parsing functions
        by the input key. The input lines are passed as an argument.
        Returns the result of the called parsing function.
        Only use case is as a helper function during parsing.

        Parameters
        ----------
        lines : list
            List of strings. Each element of the list is a line from the
            input file.
        key : str
            Parsing function to call
            (INSTRUMENT/BEAM/NORMALISATION/SAMPLE BACKGROUND/SAMPLE/CONTAINER)
        Returns
        -------
        NoneType
            if parsing INSTRUMENT/BEAM/NORMALISATION
        SampleBackground
            if parsing SAMPLE BACKGROUND
        Sample
            if parsing Sample
        Container
            if parsing Container
        """

        parsingFunctions = {
            "INSTRUMENT": self.parseInstrument,
            "BEAM": self.parseBeam,
            "NORMALISATION": self.parseNormalisation,
            "SAMPLE BACKGROUND": self.parseSampleBackground,
            "SAMPLE": self.parseSample,
            "CONTAINER": self.parseContainer,
        }
        # Return the result of the parsing function that was called.
        return parsingFunctions[key](lines)

    def sampleBackgroundHelper(self, lines):
        """
        Helper method for parsing Sample Background and its
        Samples and their Containers.
        Returns the SampleBackground object.
        Parameters
        ----------
        lines : list
            List of strings. Each element of the list is a line from the
            input file.
        Returns
        -------
        SampleBackground
            The SampleBackground parsed from the lines.
        """

        KEYWORDS = {
            "SAMPLE BACKGROUND": None,
            "SAMPLE": [],
            "CONTAINER": Container,
        }

        # Iterate through the lines, parsing any Samples,
        #  backgrounds and containers found
        parsing = ""
        start = end = 0
        for i, line in enumerate(lines):
            for key in KEYWORDS.keys():
                if key in line and firstword(line) in KEYWORDS.keys():
                    parsing = key
                    start = i
                    break
            if line[0] == "}":
                end = i
                if parsing == "SAMPLE BACKGROUND":
                    start += 2
                slice = deepcopy(lines[start: end - 1])
                if parsing == "SAMPLE":
                    KEYWORDS[parsing].append(self.makeParse(slice, parsing))
                elif parsing == "CONTAINER":
                    KEYWORDS["SAMPLE"][-1].containers.append(
                        deepcopy(self.makeParse(slice, parsing))
                    )
                else:
                    KEYWORDS[parsing] = self.makeParse(slice, parsing)
                start = end = 0
        KEYWORDS["SAMPLE BACKGROUND"].samples = KEYWORDS["SAMPLE"]

        return KEYWORDS["SAMPLE BACKGROUND"]

    def parse(self):
        """
        Parse the GudrunFile from its path.
        Assign objects from the file to the attributes of the class.
        Raises ValueError if Instrument, Beam or Normalisation are missing.

        Parameters
        ----------
        None
        Returns
        -------
        None
        """

        # Ensure only valid files are given.
        if not self.path:
            raise ValueError(
                "Path not supplied. Cannot parse from an empty path!"
            )
        if not isfile(self.path):
            raise ValueError(
                "The path supplied is invalid.\
                 Cannot parse from an invalid path"
            )
        parsing = ""

        start = end = 0
        KEYWORDS = {"INSTRUMENT": False, "BEAM": False, "NORMALISATION": False}

        # Iterate through the file,
        # parsing the Instrument, Beam and Normalisation.
        with open(self.path, encoding="utf-8") as fp:
            lines = fp.readlines()
            split = 0
            for i, line in enumerate(lines):
                if (
                    firstword(line) in KEYWORDS.keys()
                    and not KEYWORDS[firstword(line)]
                ):
                    parsing = firstword(line)
                    start = i
                elif line[0] == "}":
                    end = i
                    slice = deepcopy(lines[start + 2: end - 1])
                    self.makeParse(slice, parsing)
                    KEYWORDS[parsing] = True
                    if parsing == "NORMALISATION":
                        split = end
                        break
                    start = end = 0

            # If we didn't parse each one of the keywords, then panic
            if not all(KEYWORDS.values()):
                raise ValueError((
                    'INSTRUMENT, BEAM and NORMALISATION'
                    ' were not parsed. It\'s possible the file'
                    ' supplied is of an incorrect format!'
                ))
            # Get everything after the final item parsed
            lines_split = deepcopy(lines[split + 1:])
            start = end = 0
            found = False

            # Parse sample backgrounds and
            # corresponding samples and containers.
            for i, line in enumerate(lines_split):
                if ("SAMPLE BACKGROUND" in line and "{" in line) and not found:
                    start = i
                    found = True
                    continue
                elif (
                    ("SAMPLE BACKGROUND" in line and "{" in line)
                    or ("END" in line)
                ) and found:
                    end = i
                    found = False
                    slice = deepcopy(lines_split[start:end])
                    self.sampleBackgrounds.append(
                        self.sampleBackgroundHelper(slice)
                    )
                    start = end + 1
                else:
                    continue

    def __str__(self):
        """
        Returns the string representation of the GudrunFile object.

        Parameters
        ----------
        None

        Returns
        -------
        string : str
            String representation of GudrunFile.
        """

        LINEBREAK = "\n\n"
        header = "'  '  '        '  '/'" + LINEBREAK
        instrument = (
            "INSTRUMENT          {\n\n"
            + str(self.instrument)
            + LINEBREAK
            + "}"
        )
        beam = "BEAM          {\n\n" + str(self.beam) + LINEBREAK + "}"
        normalisation = (
            "NORMALISATION          {\n\n"
            + str(self.normalisation)
            + LINEBREAK
            + "}"
        )
        sampleBackgrounds = "\n".join(
            [str(x) for x in self.sampleBackgrounds]
        ).rstrip()
        footer = "\n\n\nEND\n1\nDate and Time last written:  {}\nN".format(
            time.strftime("%Y%m%d %H:%M:%S")
        )
        return (
            header
            + instrument
            + LINEBREAK
            + beam
            + LINEBREAK
            + normalisation
            + LINEBREAK
            + sampleBackgrounds
            + footer
        )

    def write_out(self, overwrite=False):
        """
        Writes out the string representation of the GudrunFile.
        If 'overwrite' is True, then the initial file is overwritten.
        Otherwise, it is written to 'gudpy_{initial filename}.txt'.

        Parameters
        ----------
        overwrite : bool, optional
            Overwrite the initial file? (default is False).

        Returns
        -------
        None
        """
        if not overwrite:
            f = open(self.outpath, "w", encoding="utf-8")
        else:
            f = open(self.path, "w", encoding="utf-8")
        f.write(str(self))
        f.close()

    def dcs(self, path=''):
        """
        Purge detectors and then call gudrun_dcs on the path supplied.
        If the path is its default value,
        then use the path attribute as the path.

        Parameters
        ----------
        overwrite : bool, optional
            Overwrite the initial file? (default is False).
        path : str, optional
            Path to parse from (default is empty, which indicates self.path).
        Returns
        -------
        subprocess.CompletedProcess
            The result of calling gudrun_dcs using subprocess.run.
            Can access stdout/stderr from this.
        """
        if not path:
            path = self.path
        self.purge()
        try:
            result = subprocess.run(
                ["bin/gudrun_dcs", path], capture_output=True, text=True
            )
        except FileNotFoundError:
            gudrun_dcs = sys._MEIPASS + os.sep + "gudrun_dcs"
            result = subprocess.run(
                [gudrun_dcs, path], capture_output=True, text=True
            )
        return result

    def process(self):
        """
        Write out the current state of the file, then
        purge detectors and then call gudrun_dcs on the file that
        was written out.

        Parameters
        ----------
        None
        Returns
        -------
        subprocess.CompletedProcess
            The result of calling gudrun_dcs using subprocess.run.
            Can access stdout/stderr from this.
        """
        self.write_out()
        return self.dcs(path=self.outpath)

    def purge(self):
        """
        Create a PurgeFile from the GudrunFile,
        and then call Purge.purge() to purge the detectors.

        Parameters
        ----------
        None
        Returns
        -------
        subprocess.CompletedProcess
            The result of calling purge_det using subprocess.run.
            Can access stdout/stderr from this.
        """
        purge = PurgeFile(self)
        return purge.purge()


if __name__ == "__main__":
    g = GudrunFile(
        path="/home/jared/GudPy/GudPy/tests/TestData/NIMROD-water/water.txt"
        )
    print(g.dcs())
