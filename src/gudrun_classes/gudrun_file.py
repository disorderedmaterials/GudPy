import sys
import os
from os.path import isfile
import subprocess
import time
from copy import deepcopy

from src.scripts.utils import (
        extract_nums_from_string, iteristype, isin,
        firstword, boolifyNum,
        extract_ints_from_string,
        extract_floats_from_string,
        count_occurrences,
        firstNFloats,
        firstNInts,
        nthfloat,
        nthint
        )
from src.gudrun_classes.instrument import Instrument
from src.gudrun_classes.beam import Beam
from src.gudrun_classes.normalisation import Normalisation
from src.gudrun_classes.sample import Sample
from src.gudrun_classes.sample_background import SampleBackground
from src.gudrun_classes.container import Container
from src.gudrun_classes.composition import Composition
from src.gudrun_classes.element import Element
from src.gudrun_classes.data_files import DataFiles
from src.gudrun_classes.purge_file import PurgeFile
from src.gudrun_classes.enums import (
    Instruments, UnitsOfDensity, MergeWeights,
    Scales, NormalisationType, OutputUnits,
    Geometry
)


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

        self.instrument.name = Instruments[firstword(lines[0])]
        self.instrument.GudrunInputFileDir = firstword(lines[1])
        self.instrument.dataFileDir = firstword(lines[2])
        self.instrument.dataFileType = firstword(lines[3])
        self.instrument.detectorCalibrationFileName = firstword(lines[4])
        self.instrument.columnNoPhiVals = int(firstword(lines[5]))
        self.instrument.groupFileName = firstword(lines[6])
        self.instrument.deadtimeConstantsFileName = firstword(lines[7])
        self.instrument.spectrumNumbersForIncidentBeamMonitor = extract_ints_from_string(lines[8])
        self.instrument.wavelengthRangeForMonitorNormalisation = firstNInts(lines[9], 2)
        self.instrument.spectrumNumbersForTransmissionMonitor = extract_ints_from_string(lines[10])
        self.instrument.incidentMonitorQuietCountConst = nthfloat(lines[11], 0)
        self.instrument.transmissionMonitorQuietCountConst = nthfloat(lines[12], 0)
        self.instrument.channelNosSpikeAnalysis = firstNInts(lines[13], 2)
        self.instrument.spikeAnalysisAcceptanceFactor = nthint(lines[14], 0)

        wavelengthRange = firstNFloats(lines[15], 3)
        self.instrument.wavelengthMin = wavelengthRange[0]
        self.instrument.wavelengthMax = wavelengthRange[1]
        self.instrument.wavelengthStep = wavelengthRange[2]
        self.instrument.NoSmoothsOnMonitor = nthint(lines[16], 0)
        
        XRange = firstNFloats(lines[17], 3)
        self.instrument.XMin = XRange[0]
        self.instrument.XMax = XRange[1]
        self.instrument.XStep = XRange[2]
        self.instrument.useLogarithmicBinning = self.instrument.XStep == -0.01

        i = 18
        line = lines[i]
        while "end input of specified values" not in line:
            self.instrument.groupingParameterPanel.append(tuple(firstNInts(line, 4)))
            i += 1

        self.instrument.groupsAcceptanceFactor = nthfloat(lines[i+1], 0)        
        self.instrument.mergePower = nthint(lines[i+2], 0)
        self.instrument.subSingleAtomScattering = boolifyNum(nthint(lines[i+3], 0))
        self.instrument.mergeWeights = MergeWeights[MergeWeights(nthint(lines[i+4], 0)).name]
        self.instrument.incidentFlightPath = nthfloat(lines[i+5], 0)
        self.instrument.spectrumNumberForOutputDiagnosticFiles = nthint(lines[i+6], 0)
        self.instrument.neutronScatteringParametersFile = firstword(lines[i+7])
        self.instrument.scaleSelection = Scales[Scales(nthint(lines[i+8], 0)).name]
        self.instrument.subWavelengthBinnedData = boolifyNum(nthint(lines[i+9], 0))
        self.instrument.GudrunStartFolder = firstword(lines[i+10])
        self.instrument.startupFileFolder = firstword(lines[i+11])
        self.instrument.logarithmicStepSize = nthfloat(lines[i+12], 0)
        self.instrument.hardGroupEdges = boolifyNum(nthint(lines[i+13], 0))
        if self.instrument.dataFileType == "NXS" or self.instrument.dataFileType == "nxs":
            self.instrument.nxsDefinitionFile = firstword(lines[i+14])
            i+=1
        self.instrument.numberIterations = nthint(lines[i+14], 0)
        self.instrument.tweakTweakFactors = boolifyNum(nthint(lines[i+15], 0))

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

        self.beam.sampleGeometry = Geometry[firstword(lines[0])]
        self.beam.noBeamProfileValues = nthint(lines[1], 0)
        self.beam.beamProfileValues = extract_floats_from_string(lines[2])
        self.beam.stepSizeAbsorption = nthfloat(lines[3], 0)
        self.beam.stepSizeMS = nthfloat(lines[3], 1)
        self.beam.noSlices = nthint(lines[3], 2)
        self.beam.angularStepForCorrections = nthint(lines[4], 0)

        self.beam.incidentBeamLeftEdge = nthfloat(lines[5], 0)
        self.beam.incidentBeamRightEdge = nthfloat(lines[5], 1)
        self.beam.incidentBeamTopEdge = nthfloat(lines[5], 2)
        self.beam.incidentBeamBottomEdge = nthfloat(lines[5], 3)

        self.beam.scatteredBeamLeftEdge = nthfloat(lines[6], 0)
        self.beam.scatteredBeamRightEdge = nthfloat(lines[6], 1)
        self.beam.scatteredBeamTopEdge = nthfloat(lines[6], 2)
        self.beam.scatteredBeamBottomEdge = nthfloat(lines[6], 3)

        self.beam.filenameIncidentBeamSpectrumParams = firstword(lines[7])
        self.beam.overallBackgroundFactor = nthfloat(lines[8], 0)
        self.beam.sampleDependantBackgroundFactor = nthfloat(lines[9], 0)
        self.beam.shieldingAttenuationCoefficient = nthfloat(lines[10], 0)

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

        self.normalisation.numberOfFiles = nthint(lines[0], 0)
        self.normalisation.periodNumber = nthint(lines[0], 1)

        # Extract data files
        dataFiles = []
        for i in range(self.normalisation.numberOfFiles):
            dataFiles.append(firstword(lines[i+1]))
        self.normalisation.dataFiles = DataFiles(dataFiles, "NORMALISATION")    
        i+=2

        self.normalisation.numberOfFilesBg = nthint(lines[i], 0)
        self.normalisation.periodNumberBg = nthint(lines[i], 1)

        # Extract background data files
        dataFilesBg = []
        for j in range(self.normalisation.numberOfFilesBg):
            dataFilesBg.append(firstword(lines[i+j+1]))
        self.normalisation.dataFilesBg = DataFiles(dataFilesBg, "NORMALISATION BACKGROUND")
        j+=i+2

        self.normalisation.forceCalculationOfCorrections = boolifyNum(nthint(lines[j], 0))

        # Construct composition
        composition = []
        n = 1
        line = lines[j+n]
        while "end of composition input" not in line:
            atomicSymbol = firstword(line)
            massNo = nthint(line, 1)
            abundance = nthfloat(line, 2)
            composition.append(Element(atomicSymbol, massNo, abundance))
            n+=1
            line = lines[j+n]
        self.normalisation.composition = Composition(composition, "NORMALISATION")
        j+=n+1
        self.normalisation.geometry = Geometry[firstword(lines[j])]

        if (self.normalisation.geometry == Geometry.SameAsBeam and self.beam.sampleGeometry == Geometry.FLATPLATE) or self.normalisation.geometry == Geometry.FLATPLATE:
            self.normalisation.upstreamThickness = nthfloat(lines[j+1], 0)
            self.normalisation.downstreamThickness = nthfloat(lines[j+1], 1)
            self.normalisation.angleOfRotation = nthfloat(lines[j+2], 0)
            self.normalisation.sampleWidth = nthfloat(lines[j+2], 1)
        
        density = nthfloat(lines[j+3], 0)
        self.normalisation.density = abs(density)
        self.normalisation.densityUnits = UnitsOfDensity.ATOMIC if density < 0 else UnitsOfDensity.CHEMICAL

        self.normalisation.tempForNormalisationPC = nthint(lines[j+4], 0)
        self.normalisation.totalCrossSectionSource = firstword(lines[j+5])
        self.normalisation.normalisationDifferentialCrossSectionFilename = firstword(lines[j+6])
        self.normalisation.lowerLimitSmoothedNormalisation = nthfloat(lines[j+7], 0)
        self.normalisation.normalisationDegreeSmoothing = nthfloat(lines[j+8], 0)
        self.normalisation.minNormalisationSignalBR = nthfloat(lines[j+9], 0)

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

        sampleBackground.numberOfFiles = nthint(lines[0], 0)
        sampleBackground.periodNumber = nthint(lines[0], 1)
        
        dataFiles = []
        for i in range(sampleBackground.numberOfFiles):
            dataFiles.append(firstword(lines[i+1]))
        i+=2
        sampleBackground.dataFiles = DataFiles(dataFiles, "SAMPLE BACKGROUD")

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

        # Extract the sample name, and then discard whitespace lines.
        sample.name = str(lines[0][:-2]).strip()
        lines[:] = lines[2:]

        sample.numberOfFiles = nthint(lines[0], 0)
        sample.periodNumber = nthint(lines[0], 1)

        dataFiles = []
        for i in range(sample.numberOfFiles):
            dataFiles.append(firstword(lines[i+1]))
        sample.dataFiles = DataFiles(dataFiles, sample.name)
        i+=2

        sample.forceCalculationOfCorrections = boolifyNum(nthint(lines[i], 0))

        # Construct composition
        composition = []
        n = 1
        line = lines[i+n]
        while "end of composition input" not in line:
            atomicSymbol = firstword(line)
            massNo = nthint(line, 1)
            abundance = nthfloat(line, 2)
            composition.append(Element(atomicSymbol, massNo, abundance))
            n+=1
            line = lines[i+n]
        sample.composition = Composition(composition, sample.name)
        i+=n+1

        sample.geometry = Geometry[firstword(lines[i])]

        if (sample.geometry == Geometry.SameAsBeam and self.beam.sampleGeometry == Geometry.FLATPLATE) or sample.geometry == Geometry.FLATPLATE:
            sample.upstreamThickness = nthfloat(lines[i+1], 0)
            sample.downstreamThickness = nthfloat(lines[i+1], 1)
            sample.angleOfRotation = nthfloat(lines[i+2], 0)
            sample.sampleWidth = nthfloat(lines[i+2], 1)

        density = nthfloat(lines[i+3], 0)
        sample.density = abs(density)
        sample.densityUnits = UnitsOfDensity.ATOMIC if density < 0 else UnitsOfDensity.CHEMICAL

        sample.tempForNormalisationPC = nthint(lines[i+4], 0)
        sample.totalCrossSectionSource = firstword(lines[i+5])
        sample.sampleTweakFactor = nthfloat(lines[i+6], 0)
        sample.topHatW = nthfloat(lines[i+7], 0)
        sample.minRadFT = nthfloat(lines[i+8], 0)
        sample.grBroadening = nthfloat(lines[i+9], 0)

        # Extract resonance values
        n = 10
        line = lines[i+n]
        while "to finish specifying wavelength range of resonance" not in line:
            sample.resonanceValues.append(tuple(extract_floats_from_string(line)))
            n+=1
            line = lines[i+n]
        i+=n+1

        # Extract exponential values
        n = 0
        line = lines[i+n]
        while "to specify end of exponential parameter input" not in line:
            sample.exponentialValues.append(tuple(extract_nums_from_string(line)))
            n+=1
            line = lines[i+n]
        i+=n+1

        sample.normalisationCorrectionFactor = nthfloat(lines[i], 0)
        sample.fileSelfScattering = firstword(lines[i+1])
        sample.normaliseTo = NormalisationType[NormalisationType(nthint(lines[i+2], 0)).name]
        sample.maxRadFT = nthfloat(lines[i+3], 0)
        sample.outputUnits = OutputUnits[OutputUnits(nthint(lines[i+4], 0)).name]
        sample.powerForBroadening = nthfloat(lines[i+5], 0)
        sample.stepSize = nthfloat(lines[i+6], 0)
        sample.include = boolifyNum(nthint(lines[i+7], 0))
        sample.scatteringFraction = nthfloat(lines[i+8], 0)
        sample.attenuationCoefficient = nthfloat(lines[i+8], 1)
        print(str(sample))
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
                    container.densityUnits = UnitsOfDensity.ATOMIC
                else:
                    container.densityUnits = UnitsOfDensity.CHEMICAL
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
    # print(g.dcs())
