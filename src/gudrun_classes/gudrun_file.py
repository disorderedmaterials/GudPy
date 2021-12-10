from PySide6.QtCore import QProcess
from src.gudrun_classes.exception import ParserException
import sys
import os
from os.path import isfile
import subprocess
import time
from src.scripts.utils import (
        extract_nums_from_string,
        firstword, boolifyNum,
        extract_ints_from_string,
        extract_floats_from_string,
        firstNFloats,
        firstNInts,
        nthfloat,
        nthint,
        resolve
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
    CrossSectionSource, Instruments, FTModes, UnitsOfDensity, MergeWeights,
    Scales, NormalisationType, OutputUnits,
    Geometry
)
from src.gudrun_classes import config
import re

SUFFIX = ".exe" if os.name == "nt" else ""


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
    purged : bool
        Have the detectors been purged?
    stream : str[]
        List of strings, where each item represents a line
        in the input stream.
    Methods
    -------
    getNextToken():
        Returns the next token in the input stream, whilst
        removing it from said input stream.
    peekNextToken():
        Returns the next token in the input stream without
        removing it.
    consumeTokens(n):
        Removes n tokens from the input stream.
    consumeUpToDelim(delim):
        Removes tokens until the delimiter is reached.
    consumeWhitespace():
        Removes tokens from the stream, until a non-whitespace
        token is reached.
    parseInstrument():
        Initialises an Intrument object and assigns it
        to the instrument attribute.
        Parses the attributes of the Instrument from the input stream.
    parseBeam():
        Initialises a Beam object and assigns it to the beam attribute.
        Parses the attributes of the Beam from the input stream.
    parseNormalisation():
        Initialises a Normalisation object and assigns it
        to the normalisation attribute.
        Parses the attributes of the Normalisation from the input stream.
    parseSampleBackground():
        Initialises a SampleBackground object.
        Parses the attributes of the SampleBackground from the input stream.
        Returns the SampleBackground object.
    parseSample():
        Initialises a Sample object.
        Parses the attributes of the Sample from the input stream.
        Returns the Sample object.
    parseContainer():
        Initialises a Container object.
        Parses the attributes of the Container from the input stream.
        Returns the Container object.
    makeParse(key):
        Uses the key to call a parsing function from a dictionary
        of parsing functions.
        Returns the result of the called parsing function.
    sampleBackgroundHelper():
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

    def __init__(self, path=None, config=False):
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
        self.outpath = "gudpy.txt"

        if isinstance(path, type(None)):
            self.instrument = Instrument()
            self.beam = Beam()
            self.normalisation = Normalisation()
            self.sampleBackgrounds = []
        else:
            self.instrument = None
            self.beam = None
            self.normalisation = None
            self.sampleBackgrounds = []
            self.parse(config=config)
        self.purged = False
        # Parse the GudrunFile.
        self.stream = None
        self.purgeFile = PurgeFile(self)

    def getNextToken(self):
        """
        Pops the 'next token' from the stream and returns it.
        Essentially removes the first line in the stream and returns it.

        Parameters
        ----------
        None
        Returns
        -------
        str | None
        """
        return self.stream.pop(0) if self.stream else None

    def peekNextToken(self):
        """
        Returns the next token in the input stream, without removing it.

        Parameters
        ----------
        None
        Returns
        -------
        str | None
        """
        return self.stream[0] if self.stream else None

    def consumeTokens(self, n):
        """
        Consume n tokens from the input stream.

        Parameters
        ----------
        None
        Returns
        -------
        None
        """
        for _ in range(n):
            self.getNextToken()

    def consumeUpToDelim(self, delim):
        """
        Consume tokens iteratively, until a delimiter is reached.

        Parameters
        ----------
        None
        Returns
        -------
        None
        """
        line = self.getNextToken()
        while line[0] != delim:
            line = self.getNextToken()

    def consumeWhitespace(self):
        """
        Consume tokens iteratively, while they are whitespace.

        Parameters
        ----------
        None
        Returns
        -------
        None
        """
        line = self.peekNextToken()
        if line and line.isspace():
            self.getNextToken()
            line = self.peekNextToken()

    def parseInstrument(self):
        """
        Intialises an Instrument object and assigns it to the
        instrument attribute.
        Parses the attributes of the Instrument from the input stream.
        Raises a ParserException if any mandatory attributes are missing.


        Parameters
        ----------
        None
        Returns
        -------
        None
        """
        try:
            # Initialise instrument attribute to a new instance of Instrument.
            self.instrument = Instrument()
            self.consumeWhitespace()

            # For string attributes,
            # we simply extract the firstword in the line.
            self.instrument.name = Instruments[firstword(self.getNextToken())]
            self.instrument.GudrunInputFileDir = (
                os.path.dirname(os.path.abspath(self.path))
            )
            self.consumeTokens(1)
            self.instrument.dataFileDir = firstword(self.getNextToken())
            self.instrument.dataFileType = firstword(self.getNextToken())
            self.instrument.detectorCalibrationFileName = (
                firstword(self.getNextToken())
            )

            # For single integer attributes,
            # we extract the zeroth int from the line.
            self.instrument.columnNoPhiVals = nthint(self.getNextToken(), 0)
            self.instrument.groupFileName = firstword(self.getNextToken())
            self.instrument.deadtimeConstantsFileName = (
                firstword(self.getNextToken())
            )

            # For N integer attributes,
            # we extract the first N integers from the line.
            self.instrument.spectrumNumbersForIncidentBeamMonitor = (
                extract_ints_from_string(self.getNextToken())
            )

            # For integer pair attributes,
            # we extract the first 2 integers from the line.
            self.instrument.wavelengthRangeForMonitorNormalisation = (
                tuple(firstNFloats(self.getNextToken(), 2))
            )

            if all(
                self.instrument.wavelengthRangeForMonitorNormalisation
            ) == 0.0:
                self.instrument.wavelengthRangeForMonitorNormalisation = (
                    0, 0
                )

            self.instrument.spectrumNumbersForTransmissionMonitor = (
                extract_ints_from_string(self.getNextToken())
            )

            # For single float attributes,
            # we extract the zeroth float from the line.
            self.instrument.incidentMonitorQuietCountConst = (
                nthfloat(self.getNextToken(), 0)
            )
            self.instrument.transmissionMonitorQuietCountConst = (
                nthfloat(self.getNextToken(), 0)
            )

            self.instrument.channelNosSpikeAnalysis = (
                tuple(firstNInts(self.getNextToken(), 2))
            )
            self.instrument.spikeAnalysisAcceptanceFactor = (
                nthfloat(self.getNextToken(), 0)
            )

            # Extract wavelength range
            # Which consists of the first 3 floats
            # (min, max, step) in the line.
            wavelengthRange = firstNFloats(self.getNextToken(), 3)
            self.instrument.wavelengthMin = wavelengthRange[0]
            self.instrument.wavelengthMax = wavelengthRange[1]
            self.instrument.wavelengthStep = wavelengthRange[2]

            self.instrument.NoSmoothsOnMonitor = nthint(self.getNextToken(), 0)

            # Extract X range
            # Which consists of the first 3 floats
            # (min, max, step) in the line.
            XRange = firstNFloats(self.getNextToken(), 3)

            self.instrument.XMin = XRange[0]
            self.instrument.XMax = XRange[1]
            self.instrument.XStep = XRange[2]

            # Extract the grouping parameter panel.
            # Each row in the panel consists of the first 4 ints
            # (Group, XMin, XMax, Background Factor) in the line.
            # If the marker line is encountered,
            # then the panel has been parsed.

            line = self.getNextToken()
            while "to end input of specified values" not in line:
                self.instrument.groupingParameterPanel.append(
                    tuple(firstNInts(line, 4))
                )
                line = self.getNextToken()

            self.instrument.groupsAcceptanceFactor = (
                nthfloat(self.getNextToken(), 0)
            )
            self.instrument.mergePower = nthint(self.getNextToken(), 0)

            # For boolean attributes, we convert the first
            # integer in the line to its boolean value.
            self.instrument.subSingleAtomScattering = (
                boolifyNum(nthint(self.getNextToken(), 0))
            )

            # For enumerated attributes, where the value  of the attribute is
            # the first integer in the line, and we must get the member,
            # we do this: Enum[Enum(value).name]
            self.instrument.mergeWeights = (
                MergeWeights[MergeWeights(nthint(self.getNextToken(), 0)).name]
            )
            self.instrument.incidentFlightPath = (
                nthfloat(self.getNextToken(), 0)
            )
            self.instrument.spectrumNumberForOutputDiagnosticFiles = (
                nthint(self.getNextToken(), 0)
            )

            self.instrument.neutronScatteringParametersFile = (
                firstword(self.getNextToken())

            )
            self.instrument.scaleSelection = (
                Scales[Scales(nthint(self.getNextToken(), 0)).name]
            )
            self.instrument.subWavelengthBinnedData = (
                boolifyNum(nthint(self.getNextToken(), 0))
            )
            self.consumeTokens(2)
            self.instrument.logarithmicStepSize = (
                nthfloat(self.getNextToken(), 0)
            )
            self.instrument.hardGroupEdges = (
                boolifyNum(nthint(self.getNextToken(), 0))
            )

            # If NeXus files are being used, then we expect a NeXus definition
            # file to be present, and extract it.
            if (
                self.instrument.dataFileType == "NXS"
                or self.instrument.dataFileType == "nxs"
            ):
                self.instrument.nxsDefinitionFile = (
                    firstword(self.getNextToken())
                )

            # Consume whitespace and the closing brace.
            self.consumeUpToDelim("}")

            # Resolve the paths, to make them relative.
            # First construct the regular expression to match against.
            pattern = re.compile(r"StartupFiles\S*")

            self.instrument.detectorCalibrationFileName = (
                re.search(
                    pattern,
                    self.instrument.detectorCalibrationFileName
                ).group()
            )

            self.instrument.groupFileName = (
                re.search(
                    pattern,
                    self.instrument.groupFileName
                ).group()
            )

            self.instrument.deadtimeConstantsFileName = (
                re.search(
                    pattern,
                    self.instrument.deadtimeConstantsFileName
                ).group()
            )

            self.instrument.neutronScatteringParametersFile = (
                re.search(
                    pattern,
                    self.instrument.neutronScatteringParametersFile
                ).group()
            )

        except Exception as e:
            raise ParserException(
                    "Whilst parsing Instrument, an exception occured."
                    " The input file is most likely of an incorrect format, "
                    "and some attributes were missing."
                    f"{str(e)}"
            ) from e

    def parseBeam(self):
        """
        Intialises a Beam object and assigns it to the
        beam attribute.
        Parses the attributes of the Beam from the input stream.
        Raises a ParserException if any mandatory attributes are missing.


        Parameters
        ----------
        None
        Returns
        -------
        None
        """

        try:
            # Initialise beam attribute to a new instance of Beam.
            self.beam = Beam()

            self.consumeWhitespace()

            # For enumerated attributes,
            # where the member name of the attribute is
            # the first 'word' in the line, and we must get the member,
            # we do this: Enum[memberName].
            self.beam.sampleGeometry = Geometry[firstword(self.getNextToken())]

            # Set the global geometry.
            config.geometry = self.beam.sampleGeometry

            # Ignore the number of beam values.
            self.consumeTokens(1)

            # For N float attributes,
            # we extract the first N floats from the line.
            self.beam.beamProfileValues = (
                extract_floats_from_string(self.getNextToken())
            )

            # For single float attributes,
            # we extract the zeroth float from the line.
            range = self.getNextToken()
            self.beam.stepSizeAbsorption = nthfloat(range, 0)
            self.beam.stepSizeMS = nthfloat(range, 1)
            self.beam.noSlices = nthint(range, 2)
            self.beam.angularStepForCorrections = (
                nthint(self.getNextToken(), 0)
            )

            # Extract the incident beam edges
            # relative to the centroid of the sample.
            incidentBeamEdges = self.getNextToken()
            self.beam.incidentBeamLeftEdge = nthfloat(incidentBeamEdges, 0)
            self.beam.incidentBeamRightEdge = nthfloat(incidentBeamEdges, 1)
            self.beam.incidentBeamTopEdge = nthfloat(incidentBeamEdges, 2)
            self.beam.incidentBeamBottomEdge = nthfloat(incidentBeamEdges, 3)

            # Extract the scattered beam edges
            # relative to the centroid of the sample.
            scatteredBeamEdges = self.getNextToken()
            self.beam.scatteredBeamLeftEdge = nthfloat(scatteredBeamEdges, 0)
            self.beam.scatteredBeamRightEdge = nthfloat(scatteredBeamEdges, 1)
            self.beam.scatteredBeamTopEdge = nthfloat(scatteredBeamEdges, 2)
            self.beam.scatteredBeamBottomEdge = nthfloat(scatteredBeamEdges, 3)

            # For string attributes,
            # we simply extract the firstword in the line.
            self.beam.filenameIncidentBeamSpectrumParams = (
                firstword(self.getNextToken())
            )

            # Now match it against a pattern,
            # to resolve the path to be relative.
            pattern = re.compile(r"StartupFiles\S*")

            self.beam.filenameIncidentBeamSpectrumParams = (
                re.search(
                    pattern,
                    self.beam.filenameIncidentBeamSpectrumParams
                ).group()
            )

            self.beam.overallBackgroundFactor = (
                nthfloat(self.getNextToken(), 0)
            )
            self.beam.sampleDependantBackgroundFactor = (
                nthfloat(self.getNextToken(), 0)
            )
            self.beam.shieldingAttenuationCoefficient = (
                nthfloat(self.getNextToken(), 0)
            )

            # Consume whitespace and the closing brace.
            self.consumeUpToDelim("}")

        except Exception as e:
            raise ParserException(
                    "Whilst parsing Beam, an exception occured."
                    " The input file is most likely of an incorrect format, "
                    "and some attributes were missing."
            ) from e

    def parseNormalisation(self):
        """
        Intialises a Normalisation object and assigns it to the
        normalisation attribute.
        Parses the attributes of the Normalisation from the input stream.
        Raises a ParserException if any mandatory attributes are missing.


        Parameters
        ----------
        None
        Returns
        -------
        None
        """

        try:
            # Initialise normalisation attribute
            # to a new instance of Normalisation.
            self.normalisation = Normalisation()

            self.consumeWhitespace()

            # The number of files and period number are both stored
            # on the same line.
            # So we extract the 0th integer for the number of files,
            # and the 1st integer for the period number.
            dataFileInfo = self.getNextToken()
            numberOfFiles = nthint(dataFileInfo, 0)
            self.normalisation.periodNumber = nthint(dataFileInfo, 1)

            # Extract data files
            dataFiles = []
            for _ in range(numberOfFiles):
                dataFiles.append(firstword(self.getNextToken()))

            # Create a DataFiles object from the dataFiles list constructed.
            self.normalisation.dataFiles = (
                DataFiles(dataFiles, "NORMALISATION")
            )

            # The number of background files and
            # background period number are both stored
            # on the same line.
            # So we extract the 0th integer for the number of background files,
            # and the 1st integer for the background riod number.
            dataFileInfoBg = self.getNextToken()
            numberOfFilesBg = nthint(dataFileInfoBg, 0)
            self.normalisation.periodNumberBg = nthint(dataFileInfoBg, 1)

            # Extract background data files
            dataFilesBg = []
            for j in range(numberOfFilesBg):
                dataFilesBg.append(firstword(self.getNextToken()))

            # Create a DataFiles object from the dataFiles list constructed.
            self.normalisation.dataFilesBg = (
                DataFiles(dataFilesBg, "NORMALISATION BACKGROUND")
            )

            # For boolean attributes, we convert the first
            # integer in the line to its boolean value.
            self.normalisation.forceCalculationOfCorrections = (
                boolifyNum(nthint(self.getNextToken(), 0))
            )

            # Construct composition
            composition = []
            line = self.getNextToken()
            # Extract the composition.
            # Each element in the composition consists of the first 'word',
            # integer at the second position, and float at the third position,
            # (Atomic Symbol, MassNo, Abundance) in the line.
            # If the marker line is encountered,
            # then the panel has been parsed.
            while "end of composition input" not in line:
                atomicSymbol = firstword(line)
                massNo = nthint(line, 1)
                abundance = nthfloat(line, 2)

                # Create an Element object and append to the composition list.
                composition.append(
                    Element(atomicSymbol, massNo, abundance)
                )
                line = self.getNextToken()

            # Create a Composition object from the dataFiles list constructed.
            self.normalisation.composition = (
                Composition("Normalisation", elements=composition)
            )

            # For enumerated attributes,
            # where the member name of the attribute is
            # the first 'word' in the line, and we must get the member,
            # we do this: Enum[memberName].
            self.normalisation.geometry = (
                Geometry[firstword(self.getNextToken())]
            )

            # Is the geometry FLATPLATE?
            if (
                (
                    self.normalisation.geometry == Geometry.SameAsBeam
                    and config.geometry == Geometry.FLATPLATE
                )
                    or self.normalisation.geometry == Geometry.FLATPLATE):
                # If is is FLATPLATE, then extract the upstream and downstream
                # thickness, the angle of rotation and sample width.
                thickness = self.getNextToken()
                self.normalisation.upstreamThickness = nthfloat(thickness, 0)
                self.normalisation.downstreamThickness = (
                    nthfloat(thickness, 1)
                )
                geometryInfo = self.getNextToken()
                self.normalisation.angleOfRotation = nthfloat(geometryInfo, 0)
                self.normalisation.sampleWidth = nthfloat(geometryInfo, 1)
            else:

                # Otherwise, it is CYLINDRICAL,
                # then extract the inner and outer
                # radii and the sample height.
                radii = self.getNextToken()
                self.normalisation.innerRadius = nthfloat(radii, 0)
                self.normalisation.outerRadius = nthfloat(radii, 1)
                self.normalisation.sampleHeight = (
                    nthfloat(self.getNextToken(), 0)
                )

            # Extract the density.
            density = nthfloat(self.getNextToken(), 0)

            # Take the absolute value of the density - since it could be -ve.
            self.normalisation.density = abs(density)

            # Decide on the units of density.
            # -ve density means it is atomic (atoms/A^3)
            # +ve means it is chemical (gm/cm^3)
            self.normalisation.densityUnits = (
                UnitsOfDensity.ATOMIC if
                density < 0
                else UnitsOfDensity.CHEMICAL
            )

            self.normalisation.tempForNormalisationPC = (
                nthfloat(self.getNextToken(), 0)
            )
            crossSectionSource = firstword(self.getNextToken())
            if (
                crossSectionSource == "TABLES"
                or crossSectionSource == "TRANSMISSION"
            ):
                self.normalisation.totalCrossSectionSource = (
                    CrossSectionSource[crossSectionSource]
                )
            else:
                self.normalisation.totalCrossSectionSource = (
                    CrossSectionSource.FILE
                )
                self.normalisation.crossSectionFilename = crossSectionSource

            self.normalisation.normalisationDifferentialCrossSectionFile = (
                firstword(self.getNextToken())
            )
            self.normalisation.lowerLimitSmoothedNormalisation = (
                nthfloat(self.getNextToken(), 0)
            )
            self.normalisation.normalisationDegreeSmoothing = (
                nthfloat(self.getNextToken(), 0)
            )
            self.normalisation.minNormalisationSignalBR = (
                nthfloat(self.getNextToken(), 0)
            )

            # Consume whitespace and the closing brace.
            self.consumeUpToDelim("}")

        except Exception as e:
            raise ParserException(
                    "Whilst parsing Normalisation, an exception occured."
                    " The input file is most likely of an incorrect format, "
                    "and some attributes were missing."
            ) from e

    def parseSampleBackground(self):
        """
        Intialises a SampleBackground object.
        Parses the attributes of the SampleBackground from the input stream.
        Raises a ParserException if any mandatory attributes are missing.
        Returns the parsed object.

        Parameters
        ----------
        None
        Returns
        -------
        sampleBackground : SampleBackground
            The SampleBackground that was parsed from the input lines.
        """

        try:
            sampleBackground = SampleBackground()
            line = self.peekNextToken()
            if "SAMPLE BACKGROUND" in line and "{" in line:
                self.consumeTokens(1)
            self.consumeWhitespace()
            dataFileInfo = self.getNextToken()
            numberOfFiles = nthint(dataFileInfo, 0)
            sampleBackground.periodNumber = nthint(dataFileInfo, 1)

            dataFiles = []
            for _ in range(numberOfFiles):
                dataFiles.append(firstword(self.getNextToken()))
            sampleBackground.dataFiles = (
                DataFiles(dataFiles, "SAMPLE BACKGROUND")
            )

            # Consume whitespace and the closing brace.
            self.consumeUpToDelim("}")

            return sampleBackground
        except Exception as e:
            raise ParserException(
                    "Whilst parsing Sample Background, an exception occured."
                    " The input file is most likely of an incorrect format, "
                    "and some attributes were missing."
            ) from e

    def parseSample(self):
        """
        Intialises a Sample object.
        Parses the attributes of the Sample from the input stream.
        Raises a ParserException if any mandatory attributes are missing.
        Returns the parsed object.

        Parameters
        ----------
        None
        Returns
        -------
        sample : Sample
            The Sample that was parsed from the input lines.
        """

        try:
            # Create a new instance of Sample.
            sample = Sample()

            # Extract the sample name, and then discard whitespace lines.
            sample.name = (
                str(self.getNextToken()[:-2]).strip()
                .replace("SAMPLE", "").strip()
            )
            if not sample.name:
                sample.name = "SAMPLE"
            self.consumeWhitespace()

            # The number of files and period number are both stored
            # on the same line.
            # So we extract the 0th integer for the number of files,
            # and the 1st integer for the period number.
            dataFileInfo = self.getNextToken()
            numberOfFiles = nthint(dataFileInfo, 0)
            sample.periodNumber = nthint(dataFileInfo, 1)

            # Extract data files
            dataFiles = []
            for _ in range(numberOfFiles):
                dataFiles.append(firstword(self.getNextToken()))
            # Create a DataFiles object from the dataFiles list constructed.
            sample.dataFiles = DataFiles(dataFiles, sample.name)

            # For boolean attributes, we convert the first
            # integer in the line to its boolean value.
            sample.forceCalculationOfCorrections = (
                boolifyNum(nthint(self.getNextToken(), 0))
            )

            # Construct composition
            composition = []
            line = self.getNextToken()

            # Extract the composition.
            # Each element in the composition consists of the first 'word',
            # integer at the second position, and float t the first position,
            # (Atomic Symbol, MassNo, Abundance) in the line.
            # If the marker line is encountered,
            # then the panel has been parsed.
            while "end of composition input" not in line:

                atomicSymbol = firstword(line)
                massNo = nthint(line, 1)
                abundance = nthfloat(line, 2)

                # Create an Element object and append to the composition list.
                composition.append(Element(atomicSymbol, massNo, abundance))
                line = self.getNextToken()

            # Create a Composition object from the dataFiles list constructed.
            sample.composition = Composition("Sample", elements=composition)

            # For enumerated attributes,
            # where the member name of the attribute is
            # the first 'word' in the line, and we must get the member,
            # we do this: Enum[memberName].
            sample.geometry = Geometry[firstword(self.getNextToken())]

            # Is the geometry FLATPLATE?
            if (
                (
                    sample.geometry == Geometry.SameAsBeam
                    and config.geometry == Geometry.FLATPLATE
                )
                    or sample.geometry == Geometry.FLATPLATE):
                # If is is FLATPLATE, then extract the upstream and downstream
                # thickness, the angle of rotation and sample width.
                thickness = self.getNextToken()
                sample.upstreamThickness = nthfloat(thickness, 0)
                sample.downstreamThickness = nthfloat(thickness, 1)

                geometryInfo = self.getNextToken()
                sample.angleOfRotation = nthfloat(geometryInfo, 0)
                sample.sampleWidth = nthfloat(geometryInfo, 1)
            else:

                # Otherwise, it is CYLINDRICAL,
                # then extract the inner and outer
                # radii and the sample height.
                radii = self.getNextToken()
                sample.innerRadius = nthfloat(radii, 0)
                sample.outerRadius = nthfloat(radii, 1)
                sample.sampleHeight = nthfloat(self.getNextToken(), 0)

            # Extract the density.
            density = nthfloat(self.getNextToken(), 0)

            # Decide on the units of density.
            # -ve density means it is atomic (atoms/A^3)
            # +ve means it is chemical (gm/cm^3)
            sample.density = abs(density)
            sample.densityUnits = (
                UnitsOfDensity.ATOMIC if
                density < 0
                else UnitsOfDensity.CHEMICAL
            )
            sample.tempForNormalisationPC = nthfloat(self.getNextToken(), 0)
            crossSectionSource = firstword(self.getNextToken())
            if (
                crossSectionSource == "TABLES"
                or crossSectionSource == "TRANSMISSION"
            ):
                sample.totalCrossSectionSource = (
                    CrossSectionSource[crossSectionSource]
                )
            else:
                sample.totalCrossSectionSource = CrossSectionSource.FILE
                sample.crossSectionFilename = crossSectionSource
            sample.sampleTweakFactor = nthfloat(self.getNextToken(), 0)

            topHatW = nthfloat(self.getNextToken(), 0)
            if topHatW == 0:
                sample.topHatW = 0
                sample.FTMode = FTModes.NO_FT
            elif topHatW < 0:
                sample.topHatW = abs(topHatW)
                sample.FTMode = FTModes.SUB_AVERAGE
            else:
                sample.topHatW = topHatW
                sample.FTMode = FTModes.ABSOLUTE

            sample.minRadFT = nthfloat(self.getNextToken(), 0)
            sample.grBroadening = nthfloat(self.getNextToken(), 0)

            # Extract the resonance values.
            # Each row consists of the first 2 floats.
            # (minWavelength, maxWavelength) in the line.
            # If the marker line is encountered,
            # then the values has been parsed.
            line = self.getNextToken()
            while (
                    "to finish specifying wavelength range of resonance"
                    not in line
                    ):
                sample.resonanceValues.append(
                    tuple(extract_floats_from_string(line))
                )
                line = self.getNextToken()

            # Extract the exponential values.
            # Each row consists of the first 3 numbers.
            # (Amplitude, Decay, N) in the line.
            # If the marker line is encountered,
            # then the values has been parsed.
            line = self.getNextToken()
            while "to specify end of exponential parameter input" not in line:
                sample.exponentialValues.append(
                    tuple(extract_nums_from_string(line))
                )

                line = self.getNextToken()

            sample.normalisationCorrectionFactor = (
                nthfloat(self.getNextToken(), 0)
            )
            sample.fileSelfScattering = firstword(self.getNextToken())
            sample.normaliseTo = (
                NormalisationType[
                    NormalisationType(nthint(self.getNextToken(), 0)).name
                ]
            )
            sample.maxRadFT = nthfloat(self.getNextToken(), 0)
            sample.outputUnits = (
                OutputUnits[OutputUnits(nthint(self.getNextToken(), 0)).name]
            )
            sample.powerForBroadening = nthfloat(self.getNextToken(), 0)
            sample.stepSize = nthfloat(self.getNextToken(), 0)
            sample.runThisSample = boolifyNum(nthint(self.getNextToken(), 0))
            environmentValues = self.getNextToken()
            sample.scatteringFraction = nthfloat(environmentValues, 0)
            sample.attenuationCoefficient = nthfloat(environmentValues, 1)

            # Consume whitespace and the closing brace.
            self.consumeUpToDelim("}")

            return sample

        except Exception as e:
            raise ParserException(
                    "Whilst parsing Sample, an exception occured."
                    " The input file is most likely of an incorrect format, "
                    "and some attributes were missing."
            ) from e

    def parseContainer(self):
        """
        Intialises a Container object.
        Parses the attributes of the Container from the input stream.
        Raises a ParserException if any mandatory attributes are missing.
        Returns the parsed object.

        Parameters
        ----------
        None
        Returns
        -------
        container : Container
            The Container that was parsed from the input lines.
        """

        try:
            # Create a new instance of Container.
            container = Container()

            # Extract the name from the lines,
            # and then discard the unnecessary lines.
            container.name = (
                str(self.getNextToken()[:-2]).strip()
                .replace("CONTAINER", "").strip()
            )
            if not container.name:
                container.name = "CONTAINER"
            self.consumeWhitespace()

            # The number of files and period number are both stored
            # on the same line.
            # So we extract the 0th integer for the number of files,
            # and the 1st integer for the period number.
            dataFileInfo = self.getNextToken()
            numberOfFiles = nthint(dataFileInfo, 0)
            container.periodNumber = nthint(dataFileInfo, 1)

            # Extract data files
            dataFiles = []
            for _ in range(numberOfFiles):
                dataFiles.append(firstword(self.getNextToken()))

            # Create a DataFiles object from the dataFiles list constructed.
            container.dataFiles = DataFiles(dataFiles, container.name)

            # Construct composition
            composition = []
            line = self.getNextToken()
            # Extract the composition.
            # Each element in the composition consists of the first 'word',
            # integer at the second position, and float t the first position,
            # (Atomic Symbol, MassNo, Abundance) in the line.
            # If the marker line is encountered,
            # then the panel has been parsed.
            while "end of composition input" not in line:

                atomicSymbol = firstword(line)
                massNo = nthint(line, 1)
                abundance = nthfloat(line, 2)

                # Create an Element object and append to the composition list.
                composition.append(Element(atomicSymbol, massNo, abundance))
                line = self.getNextToken()
            # Create a Composition object from the dataFiles list constructed.
            container.composition = Composition(
                "Container",
                elements=composition
            )

            # For enumerated attributes,
            # where the member name of the attribute is
            # the first 'word' in the line, and we must get the member,
            # we do this: Enum[memberName].
            container.geometry = Geometry[firstword(self.getNextToken())]

            # Is the geometry FLATPLATE?
            if (
                (
                    container.geometry == Geometry.SameAsBeam
                    and config.geometry == Geometry.FLATPLATE
                )
                    or container.geometry == Geometry.FLATPLATE):
                # If is is FLATPLATE, then extract the upstream and downstream
                # thickness, the angle of rotation and sample width.
                thickness = self.getNextToken()
                container.upstreamThickness = nthfloat(thickness, 0)
                container.downstreamThickness = nthfloat(thickness, 1)

                geometryValues = self.getNextToken()
                container.angleOfRotation = nthfloat(geometryValues, 0)
                container.sampleWidth = nthfloat(geometryValues, 1)
            else:

                # Otherwise, it is CYLINDRICAL,
                # then extract the inner and outer
                # radii and the sample height.
                radii = self.getNextToken()
                container.innerRadius = nthfloat(radii, 0)
                container.outerRadius = nthfloat(radii, 1)
                container.sampleHeight = nthfloat(self.getNextToken(), 0)

            # Extract the density.
            density = nthfloat(self.getNextToken(), 0)

            # Take the absolute value of the density - since it could be -ve.
            container.density = abs(density)

            # Decide on the units of density.
            # -ve density means it is atomic (atoms/A^3)
            # +ve means it is chemical (gm/cm^3)
            container.densityUnits = (
                UnitsOfDensity.ATOMIC if
                density < 0
                else UnitsOfDensity.CHEMICAL
            )
            crossSectionSource = firstword(self.getNextToken())
            if (
                crossSectionSource == "TABLES"
                or crossSectionSource == "TRANSMISSION"
            ):
                container.totalCrossSectionSource = (
                    CrossSectionSource[crossSectionSource]
                )
            else:
                container.totalCrossSectionSource = CrossSectionSource.FILE
                container.crossSectionFilename = crossSectionSource
            container.tweakFactor = nthfloat(self.getNextToken(), 0)

            environmentValues = self.getNextToken()
            container.scatteringFraction = nthfloat(environmentValues, 0)
            container.attenuationCoefficient = nthfloat(environmentValues, 1)

            # Consume whitespace and the closing brace.
            self.consumeUpToDelim("}")

            return container

        except Exception as e:
            raise ParserException(
                    "Whilst parsing Container, an exception occured."
                    " The input file is most likely of an incorrect format, "
                    "and some attributes were missing."
            ) from e

    def makeParse(self, key):
        """
        Calls a parsing function from a dictionary of parsing functions
        by the input key.
        Returns the result of the called parsing function.
        Only use case is as a helper function during parsing.

        Parameters
        ----------
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
        return parsingFunctions[key]()

    def sampleBackgroundHelper(self):
        """
        Helper method for parsing Sample Background and its
        Samples and their Containers.
        Returns the SampleBackground object.
        Parameters
        ----------
        None
        Returns
        -------
        SampleBackground
            The SampleBackground parsed from the lines.
        """

        # Parse sample background.
        sampleBackground = self.makeParse("SAMPLE BACKGROUND")

        self.consumeWhitespace()
        line = self.peekNextToken()

        # Parse all Samples and Containers belonging to the sample background.
        while "END" not in line and "SAMPLE BACKGROUND" not in line:
            if not line:
                raise ParserException("Unexpected EOF during parsing.")
            elif "GO" in line:
                self.getNextToken()
            elif "SAMPLE" in line and firstword(line) == "SAMPLE":
                sampleBackground.samples.append(self.makeParse("SAMPLE"))
            elif "CONTAINER" in line and firstword(line) == "CONTAINER":
                sampleBackground.samples[-1].containers.append(
                    self.makeParse("CONTAINER")
                )
            self.consumeWhitespace()
            line = self.peekNextToken()
        return sampleBackground

    def parse(self, config=False):
        """
        Parse the GudrunFile from its path.
        Assign objects from the file to the attributes of the class.
        Raises ParserException if Instrument,
        Beam or Normalisation are missing.

        Parameters
        ----------
        None
        Returns
        -------
        None
        """

        # Ensure only valid files are given.
        if not self.path:
            raise ParserException(
                "Path not supplied. Cannot parse from an empty path!"
            )
        if not isfile(self.path):
            raise ParserException(
                "The path supplied is invalid.\
                 Cannot parse from an invalid path"
            )
        parsing = ""
        KEYWORDS = {"INSTRUMENT": False, "BEAM": False, "NORMALISATION": False}

        # Decide the encoding
        import chardet
        with open(self.path, 'rb') as fp:
            encoding = chardet.detect(fp.read())['encoding']

        # Read the input stream into our attribute.
        with open(self.path, encoding=encoding) as fp:
            self.stream = fp.readlines()

        # Here we go! Get the first token and begin parsing.
        line = self.getNextToken()

        # Iterate through the file,
        # parsing the Instrument, Beam and Normalisation.
        while self.stream and not all(value for value in KEYWORDS.values()):
            if (
                firstword(line) in KEYWORDS.keys()
                and not KEYWORDS[firstword(line)]
            ):
                parsing = firstword(line)
                self.makeParse(parsing)
                KEYWORDS[parsing] = True
            line = self.getNextToken()

        # If we didn't parse each one of the keywords, then panic.
        if not all(KEYWORDS.values()) and not config:
            raise ParserException((
               'INSTRUMENT, BEAM and NORMALISATION'
               ' were not parsed. It\'s possible the file'
               ' supplied is of an incorrect format!'
            ))
        elif not KEYWORDS["INSTRUMENT"] and config:
            raise ParserException((
                'INSTRUMENT was not parsed. It\'s possible the file'
                ' supplied is of an incorrect format!'
            ))

        # Ignore whitespace.
        self.consumeWhitespace()
        line = self.peekNextToken()

        # Parse sample backgrounds, alongside their samples and containers.
        while self.stream:
            if ("SAMPLE BACKGROUND") in line and "{" in line:
                self.sampleBackgrounds.append(
                    self.sampleBackgroundHelper()
                )
            line = self.getNextToken()

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

    def write_out(self, path='', overwrite=False):
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
        if path:
            f = open(path, "w", encoding="utf-8")
        elif not overwrite:
            f = open(
                os.path.join(
                    self.instrument.GudrunInputFileDir,
                    self.outpath
                ), "w", encoding="utf-8")
        else:
            f = open(self.path, "w", encoding="utf-8")
        f.write(str(self))
        f.close()

    def dcs(self, path='', headless=True):
        """
        Call gudrun_dcs on the path supplied.
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
            path = os.path.basename(self.path)
        if headless:
            try:
                gudrun_dcs = resolve("bin", f"gudrun_dcs{SUFFIX}")
                cwd = os.getcwd()
                os.chdir(self.instrument.GudrunInputFileDir)
                result = subprocess.run(
                    [gudrun_dcs, path], capture_output=True, text=True
                )
                os.chdir(cwd)
            except FileNotFoundError:
                os.chdir(cwd)
                return False
            return result
        else:
            if hasattr(sys, '_MEIPASS'):
                gudrun_dcs = os.path.join(sys._MEIPASS, f"gudrun_dcs{SUFFIX}")
            else:
                gudrun_dcs = resolve("bin", f"gudrun_dcs{SUFFIX}")
            if not os.path.exists(gudrun_dcs):
                return FileNotFoundError()
            else:
                proc = QProcess()
                proc.setProgram(gudrun_dcs)
                proc.setArguments([path])
                return (
                    proc,
                    self.write_out,
                    [
                        path,
                        False
                    ]
                )

    def process(self, headless=True):
        """
        Write out the current state of the file,
        and then call gudrun_dcs on the file that
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
        cwd = os.getcwd()
        os.chdir(self.instrument.GudrunInputFileDir)
        self.write_out()
        dcs = self.dcs(path=self.outpath, headless=headless)
        os.chdir(cwd)
        return dcs

    def purge(self, *args, **kwargs):
        """
        Call Purge.purge() to purge the detectors.

        Parameters
        ----------
        None
        Returns
        -------
        subprocess.CompletedProcess
            The result of calling purge_det using subprocess.run.
            Can access stdout/stderr from this.
        """
        self.purgeFile = PurgeFile(self)
        result = self.purgeFile.purge(*args, **kwargs)
        if result:
            self.purged = True
        return result


if __name__ == "__main__":
    g = GudrunFile(
        path="/home/jared/GudPy/GudPy/tests/TestData/NIMROD-water/water.txt"
        )
