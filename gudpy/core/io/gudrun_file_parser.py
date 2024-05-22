import re
import os
import typing as typ

from core.composition import (
    Component, Components, Composition
)
from core.data_files import DataFiles
from core.element import Element
from core.exception import ParserException
from core import utils
from core.instrument import Instrument
from core.beam import Beam
from core.normalisation import Normalisation
from core.sample_background import SampleBackground
from core.sample import Sample
from core.container import Container
from core.gudrun_file import GudrunFile
from core import config
import core.enums as enums


class GudrunFileParser:
    """Class to manage the parsing of Gudrun input files
    """

    def __init__(self):
        # Text stream
        self.stream = None
        self.config = False

    @classmethod
    def writeGudrunFileTo(cls, gudrunFile: GudrunFile, path: str):
        gudrunFile.setGudrunDir(os.path.dirname(path))
        for sampleBackground in gudrunFile.sampleBackgrounds:
            sampleBackground.writeAllSamples = False

        with open(path, "w", encoding="utf-8") as f:
            f.write(str(gudrunFile))
            f.close()

    @classmethod
    def writeGudrunFile(cls, gudrunFile: GudrunFile, runDir: str):
        cls.writeGudrunFileTo(gudrunFile, os.path.join(
            runDir, GudrunFile.OUTPATH))

    @classmethod
    def export(cls, gudrunFile: GudrunFile, path: str):
        for sampleBackground in gudrunFile.sampleBackgrounds:
            sampleBackground.writeAllSamples = True

        with open(path, "w", encoding="utf-8") as f:
            f.write(str(gudrunFile))
            f.close()

    def parse(self, lines: list[str]) -> typ.Tuple[
            Instrument, Beam, Normalisation,
            list[SampleBackground], Components]:
        """
        Parse the GudrunFile from a list of lines.
        Assign objects from the file to the attributes of the class.
        Raises ParserException if Instrument,
        Beam or Normalisation are missing.
        """
        instrument = Instrument()
        beam = Beam()
        components = Components()
        normalisation = Normalisation()
        sampleBackgrounds = []

        KEYWORDS = {
            "INSTRUMENT": False,
            "BEAM": False,
            "NORMALISATION": False
        }
        self.stream = lines
        # Here we go! Get the first token and begin parsing.
        line = self._getNextToken()

        # Iterate through the file,
        # parsing the Instrument, Beam and Normalisation.
        while (self.stream and not all(value for value in KEYWORDS.values())):
            line = self._getNextToken()
            kwd = utils.firstword(line)
            if kwd == "INSTRUMENT":
                instrument = self._parseInstrument()
                KEYWORDS[kwd] = True
            elif kwd == "BEAM":
                beam = self._parseBeam()
                KEYWORDS[kwd] = True
            elif kwd == "NORMALISATION":
                normalisation = self._parseNormalisation()
                KEYWORDS[kwd] = True
        # If we didn't parse each one of the keywords, then panic.
        if not all(KEYWORDS.values()) and not config:
            unparsed = []
            for k, v in KEYWORDS.items():
                if not v:
                    unparsed.append(k)
            raise ParserException((
                'INSTRUMENT, BEAM, NORMALISATION,'
                ' were not parsed. It\'s possible the file'
                ' supplied is of an incorrect format!'
            ))
        elif not KEYWORDS["INSTRUMENT"] and config:
            raise ParserException((
                'INSTRUMENT was not parsed. It\'s possible the file'
                ' supplied is of an incorrect format!'
            ))

        # Ignore whitespace.
        self._consumeWhitespace()
        line = self._peekNextToken()

        # Parse sample backgrounds, alongside their samples and containers.
        while self.stream:
            if "SAMPLE BACKGROUND" in line and "{" in line:
                sampleBackgrounds.append(
                    self._sampleBackgroundHelper()
                )
            elif "COMPONENTS:" in line:
                components = self._parseComponents(line)
            line = self._getNextToken()

        return GudrunFile(
            instrument=instrument,
            beam=beam,
            normalisation=normalisation,
            sampleBackgrounds=sampleBackgrounds,
            components=components
        )

    def parseFromPath(
            self, path: str, config=False
        ) -> typ.Tuple[
            Instrument, Beam, Normalisation,
            list[SampleBackground], Components]:
        """
        Parse the GudrunFile from its path.
        Assign objects from the file to the attributes of the class.
        Raises ParserException if Instrument,
        Beam or Normalisation are missing.
        """
        self.config = config

        # Ensure only valid files are given.
        if not path:
            raise ParserException(
                "Path not supplied. Cannot parse from an empty path!"
            )
        if not os.path.exists(path):
            raise ParserException(
                "The path supplied is invalid.\
                 Cannot parse from an invalid path" + path
            )

        # Decide the encoding
        import chardet
        with open(path, 'rb') as fp:
            encoding = chardet.detect(fp.read())['encoding']
        # Read the input stream into our attribute.
        with open(path, encoding=encoding) as fp:
            lines = fp.readlines()
        return self.parse(lines)

# =================================================================
#                         PARSING HELPERS
# =================================================================

    def _getNextToken(self) -> typ.Union[str, None]:
        """
        Pops the 'next token' from the stream and returns it.
        Essentially removes the first line in the stream and returns it.
        """
        return self.stream.pop(0) if self.stream else None

    def _peekNextToken(self) -> typ.Union[str, None]:
        """
        Returns the next token in the input stream, without removing it.
        """
        return self.stream[0] if self.stream else None

    def _consumeTokens(self, n: int) -> None:
        """
        Consume n tokens from the input stream.
        """
        for _ in range(n):
            self._getNextToken()

    def _consumeUpToDelim(self, delim: str) -> None:
        """
        Consume tokens iteratively, until a delimiter is reached.
        """
        line = self._getNextToken()
        while line[0] != delim:
            line = self._getNextToken()

    def _consumeWhitespace(self) -> None:
        """
        Consume tokens iteratively, while they are whitespace.
        """
        line = self._peekNextToken()
        if line and line.isspace():
            self._getNextToken()
            line = self._peekNextToken()

    def _parseInstrument(self) -> Instrument:
        """
        Intialises an Instrument object and assigns it to the
        instrument attribute.
        Parses the attributes of the Instrument from the input stream.
        Raises a ParserException if any mandatory attributes are missing.
        """
        try:
            instrument = Instrument()
            self._consumeWhitespace()

            # For string attributes,
            # we simply extract the utils.firstword in the line.
            instrument.name = enums.Instruments[
                utils.firstword(self._getNextToken())]
            self._consumeTokens(1)
            instrument.dataFileDir = os.path.abspath(
                utils.firstword(self._getNextToken())) + os.path.sep
            instrument.dataFileType = utils.firstword(self._getNextToken())
            instrument.detectorCalibrationFileName = (
                utils.firstword(self._getNextToken())
            )

            # For single integer attributes,
            # we extract the zeroth int from the line.
            instrument.columnNoPhiVals = utils.nthint(self._getNextToken(), 0)
            instrument.groupFileName = utils.firstword(self._getNextToken())
            instrument.deadtimeConstantsFileName = (
                utils.firstword(self._getNextToken())
            )

            # For N integer attributes,
            # we extract the first N integers from the line.
            instrument.spectrumNumbersForIncidentBeamMonitor = (
                utils.extract_ints_from_string(self._getNextToken())
            )

            # For integer pair attributes,
            # we extract the first 2 integers from the line.
            instrument.wavelengthRangeForMonitorNormalisation = (
                utils.firstNFloats(self._getNextToken(), 2)
            )

            if all(
                instrument.wavelengthRangeForMonitorNormalisation
            ) == 0.0:
                instrument.wavelengthRangeForMonitorNormalisation = [
                    0, 0
                ]

            instrument.spectrumNumbersForTransmissionMonitor = (
                utils.extract_ints_from_string(self._getNextToken())
            )

            # For single float attributes,
            # we extract the zeroth float from the line.
            instrument.incidentMonitorQuietCountConst = (
                utils.nthfloat(self._getNextToken(), 0)
            )
            instrument.transmissionMonitorQuietCountConst = (
                utils.nthfloat(self._getNextToken(), 0)
            )

            instrument.channelNosSpikeAnalysis = (
                utils.firstNInts(self._getNextToken(), 2)
            )
            instrument.spikeAnalysisAcceptanceFactor = (
                utils.nthfloat(self._getNextToken(), 0)
            )

            # Extract wavelength range
            # Which consists of the first 3 floats
            # (min, max, step) in the line.
            wavelengthRange = utils.firstNFloats(self._getNextToken(), 3)
            instrument.wavelengthMin = wavelengthRange[0]
            instrument.wavelengthMax = wavelengthRange[1]
            instrument.wavelengthStep = wavelengthRange[2]

            instrument.NoSmoothsOnMonitor = utils.nthint(
                self._getNextToken(), 0)

            # Extract X range
            # Which consists of the first 3 floats
            # (min, max, step) in the line.
            XRange = utils.firstNFloats(self._getNextToken(), 3)

            instrument.XMin = XRange[0]
            instrument.XMax = XRange[1]
            instrument.XStep = XRange[2]

            # Extract the grouping parameter panel.
            # Each row in the panel consists of the first 4 ints
            # (Group, XMin, XMax, Background Factor) in the line.
            # If the marker line is encountered,
            # then the panel has been parsed.

            line = self._getNextToken()
            while "to end input of specified values" not in line:
                group = utils.nthint(line, 0)
                xMin = utils.nthfloat(line, 1)
                xMax = utils.nthfloat(line, 2)
                backgroundFactor = utils.nthfloat(line, 3)
                instrument.groupingParameterPanel.append(
                    [group, xMin, xMax, backgroundFactor]
                )
                line = self._getNextToken()

            instrument.groupsAcceptanceFactor = (
                utils.nthfloat(self._getNextToken(), 0)
            )
            instrument.mergePower = utils.nthint(self._getNextToken(), 0)

            # For boolean attributes, we convert the first
            # integer in the line to its boolean value.
            instrument.subSingleAtomScattering = (
                utils.boolifyNum(utils.nthint(self._getNextToken(), 0))
            )

            # For enumerated attributes, where the value  of the attribute is
            # the first integer in the line, and we must get the member,
            # we do this: Enum[Enum(value).name]
            instrument.mergeWeights = (
                enums.MergeWeights[enums.MergeWeights(
                    utils.nthint(self._getNextToken(), 0)).name]
            )
            instrument.incidentFlightPath = (
                utils.nthfloat(self._getNextToken(), 0)
            )
            instrument.spectrumNumberForOutputDiagnosticFiles = (
                utils.nthint(self._getNextToken(), 0)
            )

            instrument.neutronScatteringParametersFile = (
                utils.firstword(self._getNextToken())

            )
            instrument.scaleSelection = (
                enums.Scales[enums.Scales(
                    utils.nthint(self._getNextToken(), 0)).name]
            )
            instrument.subWavelengthBinnedData = (
                utils.boolifyNum(utils.nthint(self._getNextToken(), 0))
            )
            self._consumeTokens(2)
            instrument.logarithmicStepSize = (
                utils.nthfloat(self._getNextToken(), 0)
            )
            instrument.hardGroupEdges = (
                utils.boolifyNum(utils.nthint(self._getNextToken(), 0))
            )

            # If NeXus files are being used, then we expect a NeXus definition
            # file to be present, and extract it.
            if (
                instrument.dataFileType == "NXS"
                or instrument.dataFileType == "nxs"
            ):
                instrument.nxsDefinitionFile = (
                    utils.firstword(self._getNextToken())
                )

            if self.config:
                instrument.goodDetectorThreshold = utils.nthint(
                    self._getNextToken(), 0
                )

            # Consume whitespace and the closing brace.
            self._consumeUpToDelim("}")

            # Resolve the paths, to make them relative.
            # First construct the regular expression to match against.
            pattern = re.compile(r"StartupFiles\S*")

            match = re.search(
                pattern,
                instrument.detectorCalibrationFileName
            )

            if match:
                instrument.detectorCalibrationFileName = match.group()

            match = re.search(
                pattern,
                instrument.groupFileName
            )

            if match:
                instrument.groupFileName = match.group()

            match = re.search(
                pattern,
                instrument.deadtimeConstantsFileName
            )

            if match:
                instrument.deadtimeConstantsFileName = match.group()

            match = re.search(
                pattern,
                instrument.neutronScatteringParametersFile
            )

            if match:
                instrument.neutronScatteringParametersFile = match.group()

            match = re.search(
                pattern,
                instrument.neutronScatteringParametersFile
            )

            if match:
                instrument.neutronScatteringParametersFile = match.group()

            return instrument

        except Exception as e:
            raise ParserException(
                "Whilst parsing Instrument, an exception occured."
                " The input file is most likely of an incorrect format, "
                "and some attributes were missing."
                f"{str(e)}"
            ) from e

    def _parseBeam(self) -> Beam:
        """
        Intialises a Beam object and assigns it to the
        beam attribute.
        Parses the attributes of the Beam from the input stream.
        Raises a ParserException if any mandatory attributes are missing.
        """

        try:
            # Initialise beam attribute to a new instance of Beam.
            beam = Beam()

            self._consumeWhitespace()

            # For enumerated attributes,
            # where the member name of the attribute is
            # the first 'word' in the line, and we must get the member,
            # we do this: Enum[memberName].
            beam.sampleGeometry = enums.Geometry[utils.firstword(
                self._getNextToken())]

            # Set the global geometry.
            config.geometry = beam.sampleGeometry

            # Ignore the number of beam values.
            self._consumeTokens(1)

            # For N float attributes,
            # we extract the first N floats from the line.
            beam.beamProfileValues = (
                utils.extract_floats_from_string(self._getNextToken())
            )

            # For single float attributes,
            # we extract the zeroth float from the line.
            range = self._getNextToken()
            beam.stepSizeAbsorption = utils.nthfloat(range, 0)
            beam.stepSizeMS = utils.nthfloat(range, 1)
            beam.noSlices = utils.nthint(range, 2)
            beam.angularStepForCorrections = (
                utils.nthint(self._getNextToken(), 0)
            )

            # Extract the incident beam edges
            # relative to the centroid of the sample.
            incidentBeamEdges = self._getNextToken()
            beam.incidentBeamLeftEdge = utils.nthfloat(incidentBeamEdges, 0)
            beam.incidentBeamRightEdge = utils.nthfloat(incidentBeamEdges, 1)
            beam.incidentBeamBottomEdge = utils.nthfloat(incidentBeamEdges, 2)
            beam.incidentBeamTopEdge = utils.nthfloat(incidentBeamEdges, 3)

            # Extract the scattered beam edges
            # relative to the centroid of the sample.
            scatteredBeamEdges = self._getNextToken()
            beam.scatteredBeamLeftEdge = utils.nthfloat(scatteredBeamEdges, 0)
            beam.scatteredBeamRightEdge = utils.nthfloat(scatteredBeamEdges, 1)
            beam.scatteredBeamBottomEdge = utils.nthfloat(
                scatteredBeamEdges, 2)
            beam.scatteredBeamTopEdge = utils.nthfloat(scatteredBeamEdges, 3)

            # For string attributes,
            # we simply extract the utils.firstword in the line.
            beam.filenameIncidentBeamSpectrumParams = (
                utils.firstword(self._getNextToken())
            )

            # Now match it against a pattern,
            # to resolve the path to be relative.
            pattern = re.compile(r"StartupFiles\S*")

            match = re.search(
                pattern,
                beam.filenameIncidentBeamSpectrumParams
            )

            if match:
                beam.filenameIncidentBeamSpectrumParams = match.group()

            beam.overallBackgroundFactor = (
                utils.nthfloat(self._getNextToken(), 0)
            )
            beam.sampleDependantBackgroundFactor = (
                utils.nthfloat(self._getNextToken(), 0)
            )
            beam.shieldingAttenuationCoefficient = (
                utils.nthfloat(self._getNextToken(), 0)
            )

            # Consume whitespace and the closing brace.
            self._consumeUpToDelim("}")

            return beam

        except Exception as e:
            raise ParserException(
                "Whilst parsing Beam, an exception occured."
                " The input file is most likely of an incorrect format, "
                "and some attributes were missing."
                f"{e}"
            ) from e

    def _parseNormalisation(self) -> Normalisation:
        """
        Intialises a Normalisation object and assigns it to the
        normalisation attribute.
        Parses the attributes of the Normalisation from the input stream.
        Raises a ParserException if any mandatory attributes are missing.
        """

        try:
            # Initialise normalisation attribute
            # to a new instance of Normalisation.
            normalisation = Normalisation()

            self._consumeWhitespace()

            # The number of files and period number are both stored
            # on the same line.
            # So we extract the 0th integer for the number of files,
            # and the 1st integer for the period number.
            dataFileInfo = self._getNextToken()
            numberOfFiles = utils.nthint(dataFileInfo, 0)
            normalisation.periodNumber = utils.nthint(dataFileInfo, 1)

            # Extract params files
            dataFiles = []
            for _ in range(numberOfFiles):
                dataFiles.append(utils.firstword(self._getNextToken()))
            # Sorts list so that it is in ascending order
            dataFiles.sort()

            # Create a DataFiles object from the dataFiles list constructed.
            normalisation.dataFiles = (
                DataFiles(dataFiles, "NORMALISATION")
            )

            # The number of background files and
            # background period number are both stored
            # on the same line.
            # So we extract the 0th integer for the number of background files,
            # and the 1st integer for the background riod number.
            dataFileInfoBg = self._getNextToken()
            numberOfFilesBg = utils.nthint(dataFileInfoBg, 0)
            normalisation.periodNumberBg = utils.nthint(dataFileInfoBg, 1)

            # Extract background params files
            dataFilesBg = []
            for j in range(numberOfFilesBg):
                dataFilesBg.append(utils.firstword(self._getNextToken()))

            # Sorts list so that it is in ascending order
            dataFilesBg.sort()

            # Create a DataFiles object from the dataFiles list constructed.
            normalisation.dataFilesBg = (
                DataFiles(dataFilesBg, "NORMALISATION BACKGROUND")
            )

            # For boolean attributes, we convert the first
            # integer in the line to its boolean value.
            normalisation.forceCalculationOfCorrections = (
                utils.boolifyNum(utils.nthint(self._getNextToken(), 0))
            )

            # Construct composition
            composition = []
            line = self._getNextToken()
            # Extract the composition.
            # Each element in the composition consists of the first 'word',
            # integer at the second position, and float at the third position,
            # (Atomic Symbol, MassNo, Abundance) in the line.
            # If the marker line is encountered,
            # then the panel has been parsed.
            while "end of composition input" not in line:
                atomicSymbol = utils.firstword(line)
                massNo = utils.nthfloat(line, 1)
                abundance = utils.nthfloat(line, 2)

                # Create an Element object and append to the composition list.
                composition.append(
                    Element(atomicSymbol, massNo, abundance)
                )
                line = self._getNextToken()

            # Create a Composition object from the dataFiles list constructed.
            normalisation.composition = (
                Composition("Normalisation", elements=composition)
            )

            # For enumerated attributes,
            # where the member name of the attribute is
            # the first 'word' in the line, and we must get the member,
            # we do this: Enum[memberName].
            normalisation.geometry = (
                enums.Geometry[utils.firstword(self._getNextToken())]
            )

            # Is the geometry FLATPLATE?
            if (
                (
                    normalisation.geometry == enums.Geometry.SameAsBeam
                    and config.geometry == enums.Geometry.FLATPLATE
                )
                    or normalisation.geometry == enums.Geometry.FLATPLATE):
                # If is is FLATPLATE, then extract the upstream and downstream
                # thickness, the angle of rotation and sample width.
                thickness = self._getNextToken()
                normalisation.upstreamThickness = utils.nthfloat(thickness, 0)
                normalisation.downstreamThickness = (
                    utils.nthfloat(thickness, 1)
                )
                geometryInfo = self._getNextToken()
                normalisation.angleOfRotation = utils.nthfloat(geometryInfo, 0)
                normalisation.sampleWidth = utils.nthfloat(geometryInfo, 1)
            else:

                # Otherwise, it is CYLINDRICAL,
                # then extract the inner and outer
                # radii and the sample height.
                radii = self._getNextToken()
                normalisation.innerRadius = utils.nthfloat(radii, 0)
                normalisation.outerRadius = utils.nthfloat(radii, 1)
                normalisation.sampleHeight = (
                    utils.nthfloat(self._getNextToken(), 0)
                )

            # Extract the density.
            density = utils.nthfloat(self._getNextToken(), 0)

            # Take the absolute value of the density - since it could be -ve.
            normalisation.density = abs(density)

            # Decide on the units of density.
            # -ve density means it is atomic (atoms/A^3)
            # +ve means it is chemical (gm/cm^3)
            normalisation.densityUnits = (
                enums.UnitsOfDensity.ATOMIC if
                density < 0
                else enums.UnitsOfDensity.CHEMICAL
            )

            normalisation.tempForNormalisationPC = (
                utils.nthfloat(self._getNextToken(), 0)
            )
            crossSectionSource = utils.firstword(self._getNextToken())
            if (
                crossSectionSource == "TABLES"
                or crossSectionSource == "TRANSMISSION"
            ):
                normalisation.totalCrossSectionSource = (
                    enums.CrossSectionSource[crossSectionSource]
                )
            else:
                normalisation.totalCrossSectionSource = (
                    enums.CrossSectionSource.FILE
                )
                normalisation.crossSectionFilename = crossSectionSource

            normalisation.normalisationDifferentialCrossSectionFile = (
                utils.firstword(self._getNextToken())
            )

            normalisation.lowerLimitSmoothedNormalisation = (
                utils.nthfloat(self._getNextToken(), 0)
            )
            normalisation.normalisationDegreeSmoothing = (
                utils.nthfloat(self._getNextToken(), 0)
            )
            normalisation.minNormalisationSignalBR = (
                utils.nthfloat(self._getNextToken(), 0)
            )

            # Consume whitespace and the closing brace.
            self._consumeUpToDelim("}")

            # Resolve to relative.
            pattern = re.compile(r"StartupFiles\S*")

            match = re.search(
                pattern,
                normalisation.
                normalisationDifferentialCrossSectionFile
            )

            if match:
                (
                    normalisation.
                    normalisationDifferentialCrossSectionFile
                ) = match.group()

            return normalisation

        except Exception as e:
            raise ParserException(
                "Whilst parsing Normalisation, an exception occured."
                " The input file is most likely of an incorrect format, "
                "and some attributes were missing."
            ) from e

    def _parseSampleBackground(self) -> SampleBackground:
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
            line = self._peekNextToken()
            if "SAMPLE BACKGROUND" in line and "{" in line:
                self._consumeTokens(1)
            self._consumeWhitespace()
            dataFileInfo = self._getNextToken()
            numberOfFiles = utils.nthint(dataFileInfo, 0)
            sampleBackground.periodNumber = utils.nthint(dataFileInfo, 1)

            dataFiles = []
            for _ in range(numberOfFiles):
                dataFiles.append(utils.firstword(self._getNextToken()))
            sampleBackground.dataFiles = (
                DataFiles(dataFiles, "SAMPLE BACKGROUND")
            )

            # Consume whitespace and the closing brace.
            self._consumeUpToDelim("}")

            return sampleBackground
        except Exception as e:
            raise ParserException(
                "Whilst parsing Sample Background, an exception occured."
                " The input file is most likely of an incorrect format, "
                "and some attributes were missing."
            ) from e

    def _parseSample(self) -> Sample:
        """
        Intialises a Sample object.
        Parses the attributes of the Sample from the input stream.
        Raises a ParserException if any mandatory attributes are missing.
        Returns the parsed object.
        """

        try:
            # Create a new instance of Sample.
            sample = Sample()

            # Extract the sample name, and then discard whitespace lines.
            sample.name = (
                str(self._getNextToken()[:-2]).strip()
                .replace("SAMPLE", "").strip()
            )
            sample.name = utils.replace_unwanted_chars(sample.name)
            self._consumeWhitespace()
            # The number of files and period number are both stored
            # on the same line.
            # So we extract the 0th integer for the number of files,
            # and the 1st integer for the period number.
            dataFileInfo = self._getNextToken()
            numberOfFiles = utils.nthint(dataFileInfo, 0)
            sample.periodNumber = utils.nthint(dataFileInfo, 1)

            # Extract params files
            dataFiles = []
            for _ in range(numberOfFiles):
                dataFiles.append(utils.firstword(self._getNextToken()))
            # Create a DataFiles object from the dataFiles list constructed.
            sample.dataFiles = DataFiles(dataFiles, sample.name, True)

            # For boolean attributes, we convert the first
            # integer in the line to its boolean value.
            sample.forceCalculationOfCorrections = (
                utils.boolifyNum(utils.nthint(self._getNextToken(), 0))
            )

            # Construct composition
            composition = []
            line = self._getNextToken()

            # Extract the composition.
            # Each element in the composition consists of the first 'word',
            # integer at the second position, and float t the first position,
            # (Atomic Symbol, MassNo, Abundance) in the line.
            # If the marker line is encountered,
            # then the panel has been parsed.
            while "end of composition input" not in line:

                atomicSymbol = utils.firstword(line)
                massNo = utils.nthfloat(line, 1)
                abundance = utils.nthfloat(line, 2)

                # Create an Element object and append to the composition list.
                composition.append(Element(atomicSymbol, massNo, abundance))
                line = self._getNextToken()

            # Create a Composition object from the dataFiles list constructed.
            sample.composition = Composition("Sample", elements=composition)

            # For enumerated attributes,
            # where the member name of the attribute is
            # the first 'word' in the line, and we must get the member,
            # we do this: Enum[memberName].
            sample.geometry = enums.Geometry[utils.firstword(
                self._getNextToken())]

            # Is the geometry FLATPLATE?
            if (
                (
                    sample.geometry == enums.Geometry.SameAsBeam
                    and config.geometry == enums.Geometry.FLATPLATE
                )
                    or sample.geometry == enums.Geometry.FLATPLATE):
                # If is is FLATPLATE, then extract the upstream and downstream
                # thickness, the angle of rotation and sample width.
                thickness = self._getNextToken()
                sample.upstreamThickness = utils.nthfloat(thickness, 0)
                sample.downstreamThickness = utils.nthfloat(thickness, 1)

                geometryInfo = self._getNextToken()
                sample.angleOfRotation = utils.nthfloat(geometryInfo, 0)
                sample.sampleWidth = utils.nthfloat(geometryInfo, 1)
            else:

                # Otherwise, it is CYLINDRICAL,
                # then extract the inner and outer
                # radii and the sample height.
                radii = self._getNextToken()
                sample.innerRadius = utils.nthfloat(radii, 0)
                sample.outerRadius = utils.nthfloat(radii, 1)
                sample.sampleHeight = utils.nthfloat(self._getNextToken(), 0)

            # Extract the density.
            density = utils.nthfloat(self._getNextToken(), 0)

            # Decide on the units of density.
            # -ve density means it is atomic (atoms/A^3)
            # +ve means it is chemical (gm/cm^3)
            sample.density = abs(density)
            sample.densityUnits = (
                enums.UnitsOfDensity.ATOMIC if
                density < 0
                else enums.UnitsOfDensity.CHEMICAL
            )
            sample.tempForNormalisationPC = utils.nthfloat(
                self._getNextToken(), 0)
            crossSectionSource = utils.firstword(self._getNextToken())
            if (
                crossSectionSource == "TABLES"
                or crossSectionSource == "TRANSMISSION"
            ):
                sample.totalCrossSectionSource = (
                    enums.CrossSectionSource[crossSectionSource]
                )
            else:
                sample.totalCrossSectionSource = enums.CrossSectionSource.FILE
                sample.crossSectionFilename = crossSectionSource
            sample.sampleTweakFactor = utils.nthfloat(self._getNextToken(), 0)

            topHatW = utils.nthfloat(self._getNextToken(), 0)
            if topHatW == 0:
                sample.topHatW = 0
                sample.FTMode = enums.FTModes.NO_FT
            elif topHatW < 0:
                sample.topHatW = abs(topHatW)
                sample.FTMode = enums.FTModes.SUB_AVERAGE
            else:
                sample.topHatW = topHatW
                sample.FTMode = enums.FTModes.ABSOLUTE

            sample.minRadFT = utils.nthfloat(self._getNextToken(), 0)
            sample.grBroadening = utils.nthfloat(self._getNextToken(), 0)

            # Extract the resonance values.
            # Each row consists of the first 2 floats.
            # (minWavelength, maxWavelength) in the line.
            # If the marker line is encountered,
            # then the values has been parsed.
            line = self._getNextToken()
            while (
                    "to finish specifying wavelength range of resonance"
                    not in line
            ):
                sample.resonanceValues.append(
                    utils.extract_floats_from_string(line)
                )
                line = self._getNextToken()

            # Extract the exponential values.
            # Each row consists of the first 3 numbers.
            # (Amplitude, Decay, N) in the line.
            # If the marker line is encountered,
            # then the values has been parsed.
            line = self._getNextToken()
            if "to specify end of exponential parameter input" not in line:
                sample.exponentialValues = []
            while "to specify end of exponential parameter input" not in line:
                sample.exponentialValues.append(
                    utils.extract_nums_from_string(line)
                )

                line = self._getNextToken()

            sample.normalisationCorrectionFactor = (
                utils.nthfloat(self._getNextToken(), 0)
            )
            sample.fileSelfScattering = utils.firstword(self._getNextToken())
            sample.normaliseTo = (
                enums.NormalisationType[
                    enums.NormalisationType(utils.nthint(
                        self._getNextToken(), 0)).name
                ]
            )
            sample.maxRadFT = utils.nthfloat(self._getNextToken(), 0)
            sample.outputUnits = (
                enums.OutputUnits[enums.OutputUnits(
                    utils.nthint(self._getNextToken(), 0)).name]
            )
            sample.powerForBroadening = utils.nthfloat(self._getNextToken(), 0)
            sample.stepSize = utils.nthfloat(self._getNextToken(), 0)
            sample.runThisSample = utils.boolifyNum(
                utils.nthint(self._getNextToken(), 0))
            environmentValues = self._getNextToken()
            sample.scatteringFraction = utils.nthfloat(environmentValues, 0)
            sample.attenuationCoefficient = utils.nthfloat(
                environmentValues, 1)

            # Consume whitespace and the closing brace.
            self._consumeUpToDelim("}")

            return sample

        except Exception as e:
            raise ParserException(
                "Whilst parsing Sample, an exception occured."
                " The input file is most likely of an incorrect format, "
                "and some attributes were missing."
            ) from e

    def _parseContainer(self) -> Container:
        """
        Intialises a Container object.
        Parses the attributes of the Container from the input stream.
        Raises a ParserException if any mandatory attributes are missing.
        Returns the parsed object.
        """

        try:
            # Create a new instance of Container.
            container = Container()

            # Extract the name from the lines,
            # and then discard the unnecessary lines.
            container.name = (
                str(self._getNextToken()[:-2]).strip()
                .replace("CONTAINER", "").strip()
            )
            self._consumeWhitespace()

            # The number of files and period number are both stored
            # on the same line.
            # So we extract the 0th integer for the number of files,
            # and the 1st integer for the period number.
            dataFileInfo = self._getNextToken()
            numberOfFiles = utils.nthint(dataFileInfo, 0)
            container.periodNumber = utils.nthint(dataFileInfo, 1)

            # Extract params files
            dataFiles = []
            for _ in range(numberOfFiles):
                dataFiles.append(utils.firstword(self._getNextToken()))

            # Create a DataFiles object from the dataFiles list constructed.
            container.dataFiles = DataFiles(dataFiles, container.name, True)

            # Construct composition
            composition = []
            line = self._getNextToken()
            # Extract the composition.
            # Each element in the composition consists of the first 'word',
            # integer at the second position, and float t the first position,
            # (Atomic Symbol, MassNo, Abundance) in the line.
            # If the marker line is encountered,
            # then the panel has been parsed.
            while "end of composition input" not in line:

                atomicSymbol = utils.firstword(line)
                massNo = utils.nthfloat(line, 1)
                abundance = utils.nthfloat(line, 2)

                # Create an Element object and append to the composition list.
                composition.append(Element(atomicSymbol, massNo, abundance))
                line = self._getNextToken()
            # Create a Composition object from the dataFiles list constructed.
            container.composition = Composition(
                "Container",
                elements=composition
            )

            # For enumerated attributes,
            # where the member name of the attribute is
            # the first 'word' in the line, and we must get the member,
            # we do this: Enum[memberName].
            container.geometry = enums.Geometry[utils.firstword(
                self._getNextToken())]

            # Is the geometry FLATPLATE?
            if (
                (
                    container.geometry == enums.Geometry.SameAsBeam
                    and config.geometry == enums.Geometry.FLATPLATE
                )
                    or container.geometry == enums.Geometry.FLATPLATE):
                # If is is FLATPLATE, then extract the upstream and downstream
                # thickness, the angle of rotation and sample width.
                thickness = self._getNextToken()
                container.upstreamThickness = utils.nthfloat(thickness, 0)
                container.downstreamThickness = utils.nthfloat(thickness, 1)

                geometryValues = self._getNextToken()
                container.angleOfRotation = utils.nthfloat(geometryValues, 0)
                container.sampleWidth = utils.nthfloat(geometryValues, 1)
            else:

                # Otherwise, it is CYLINDRICAL,
                # then extract the inner and outer
                # radii and the sample height.
                radii = self._getNextToken()
                container.innerRadius = utils.nthfloat(radii, 0)
                container.outerRadius = utils.nthfloat(radii, 1)
                container.sampleHeight = utils.nthfloat(
                    self._getNextToken(), 0)

            # Extract the density.
            density = utils.nthfloat(self._getNextToken(), 0)

            # Take the absolute value of the density - since it could be -ve.
            container.density = abs(density)

            # Decide on the units of density.
            # -ve density means it is atomic (atoms/A^3)
            # +ve means it is chemical (gm/cm^3)
            container.densityUnits = (
                enums.UnitsOfDensity.ATOMIC if
                density < 0
                else enums.UnitsOfDensity.CHEMICAL
            )
            crossSectionSource = utils.firstword(self._getNextToken())
            if (
                crossSectionSource == "TABLES"
                or crossSectionSource == "TRANSMISSION"
            ):
                container.totalCrossSectionSource = (
                    enums.CrossSectionSource[crossSectionSource]
                )
            else:
                container.totalCrossSectionSource = (
                    enums.CrossSectionSource.FILE
                )
                container.crossSectionFilename = crossSectionSource
            container.tweakFactor = utils.nthfloat(self._getNextToken(), 0)

            environmentValues = self._getNextToken()
            container.scatteringFraction = utils.nthfloat(environmentValues, 0)
            container.attenuationCoefficient = utils.nthfloat(
                environmentValues, 1)

            # Consume whitespace and the closing brace.
            self._consumeUpToDelim("}")

            return container

        except Exception as e:
            raise ParserException(
                "Whilst parsing Container, an exception occured."
                " The input file is most likely of an incorrect format, "
                "and some attributes were missing."
            ) from e

    def _parseComponents(self) -> Components:
        components = Components()
        try:
            while self.stream:
                component = self._parseComponent()
                if component:
                    components.addComponent(component)
            return components
        except Exception as e:
            raise ParserException(
                "Whilst parsing Components, an exception occured."
                " The input file is most likely of an incorrect format."
            ) from e

    def _parseComponent(self) -> Component:
        name = self._getNextToken().rstrip()
        component = Component(name)
        line = self._peekNextToken()
        if "(" in line:
            self._consumeTokens(1)
        else:
            return
        line = self._getNextToken()
        while line and ")" not in line:
            atomicSymbol, massNo, abundance = line.split()
            element = Element(atomicSymbol, float(massNo), float(abundance))
            component.addElement(element)
            line = self._getNextToken()
        return component

    def _sampleBackgroundHelper(self) -> SampleBackground:
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
        sampleBackground = self._parseSampleBackground()

        self._consumeWhitespace()
        line = self._peekNextToken()

        # Parse all Samples and Containers belonging to the sample background.
        while "END" not in line and "SAMPLE BACKGROUND" not in line:
            if not line:
                raise ParserException("Unexpected EOF during parsing.")
            elif "GO" in line:
                self._getNextToken()
            elif "SAMPLE" in line and utils.firstword(line) == "SAMPLE":
                sample = self._parseSample()
                if not sample.name:
                    sample.name = utils.replace_unwanted_chars(
                        utils.uniquifyName(
                            "SAMPLE",
                            [s.name for s in sampleBackground.samples],
                            sep="",
                            incFirst=True
                        ))
                sampleBackground.samples.append(sample)
            elif "CONTAINER" in line and utils.firstword(line) == "CONTAINER":
                container = self._parseContainer()
                if not container.name:
                    container.name = utils.uniquifyName(
                        "CONTAINER",
                        [c.name
                         for c in sampleBackground.samples[-1].containers],
                        sep="",
                        incFirst=True)
                sampleBackground.samples[-1].containers.append(
                    container
                )
            self._consumeWhitespace()
            line = self._peekNextToken()
        return sampleBackground


Container._getNextToken = GudrunFileParser._getNextToken
Container._peekNextToken = GudrunFileParser._peekNextToken
Container._consumeUpToDelim = GudrunFileParser._consumeUpToDelim
Container._consumeWhitespace = GudrunFileParser._consumeWhitespace
