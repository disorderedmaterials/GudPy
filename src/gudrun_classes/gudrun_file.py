from src.gudrun_classes.exception import ParserException
import sys
import os
from os.path import isfile
import subprocess
import time
from copy import deepcopy
from src.scripts.utils import (
        extract_nums_from_string,
        firstword, boolifyNum,
        extract_ints_from_string,
        extract_floats_from_string,
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
from src.gudrun_classes.config import geometry


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
        try:
            # Initialise instrument attribute to a new instance of Intrument.
            self.instrument = Instrument()

            # For string attributes,
            # we simply extract the firstword in the line.
            self.instrument.name = Instruments[firstword(lines[0])]
            self.instrument.GudrunInputFileDir = firstword(lines[1])
            self.instrument.dataFileDir = firstword(lines[2])
            self.instrument.dataFileType = firstword(lines[3])
            self.instrument.detectorCalibrationFileName = firstword(lines[4])

            # For single integer attributes,
            # we extract the zeroth int from the line.
            self.instrument.columnNoPhiVals = nthint(lines[5], 0)
            self.instrument.groupFileName = firstword(lines[6])
            self.instrument.deadtimeConstantsFileName = firstword(lines[7])

            # For N integer attributes,
            # we extract the first N integers from the line.
            self.instrument.spectrumNumbersForIncidentBeamMonitor = (
                extract_ints_from_string(lines[8])
            )

            # For integer pair attributes,
            # we extract the first 2 integers from the line.
            self.instrument.wavelengthRangeForMonitorNormalisation = (
                tuple(firstNFloats(lines[9], 2))
            )

            if all(
                self.instrument.wavelengthRangeForMonitorNormalisation
            ) == 0.0:
                self.instrument.wavelengthRangeForMonitorNormalisation = (
                    0, 0
                )

            self.instrument.spectrumNumbersForTransmissionMonitor = (
                extract_ints_from_string(lines[10])
            )

            # For single float attributes,
            # we extract the zeroth float from the line.
            self.instrument.incidentMonitorQuietCountConst = (
                nthfloat(lines[11], 0)
            )
            self.instrument.transmissionMonitorQuietCountConst = (
                nthfloat(lines[12], 0)
            )

            self.instrument.channelNosSpikeAnalysis = (
                tuple(firstNInts(lines[13], 2))
            )
            self.instrument.spikeAnalysisAcceptanceFactor = (
                nthfloat(lines[14], 0)
            )

            # Extract wavelength range
            # Which consists of the first 3 floats
            # (min, max, step) in the line.
            wavelengthRange = firstNFloats(lines[15], 3)
            self.instrument.wavelengthMin = wavelengthRange[0]
            self.instrument.wavelengthMax = wavelengthRange[1]
            self.instrument.wavelengthStep = wavelengthRange[2]

            self.instrument.NoSmoothsOnMonitor = nthint(lines[16], 0)

            # Extract X range
            # Which consists of the first 3 floats
            # (min, max, step) in the line.
            XRange = firstNFloats(lines[17], 3)

            self.instrument.XMin = XRange[0]
            self.instrument.XMax = XRange[1]
            self.instrument.XStep = XRange[2]

            # Extract the grouping parameter panel.
            # Each row in the panel consists of the first 4 ints
            # (Group, XMin, XMax, Background Factor) in the line.
            # If the marker line is encountered,
            # then the panel has been parsed.
            i = 18
            line = lines[i]
            while "to end input of specified values" not in line:
                self.instrument.groupingParameterPanel.append(
                    tuple(firstNInts(line, 4))
                )
                i += 1

            # The groupingParameterPanel alters our indexing,
            # which can no longer be absolute,
            # we must account for the offset,
            # by adding 18+i+1+n for each next n attributes.
            # where i is the number of rows in the grouping parameter panel.

            self.instrument.groupsAcceptanceFactor = nthfloat(lines[i+1], 0)
            self.instrument.mergePower = nthint(lines[i+2], 0)

            # For boolean attributes, we convert the first
            # integer in the line to its boolean value.
            self.instrument.subSingleAtomScattering = (
                boolifyNum(nthint(lines[i+3], 0))
            )

            # For enumerated attributes, where the value  of the attribute is
            # the first integer in the line, and we must get the member,
            # we do this: Enum[Enum(value).name]
            self.instrument.mergeWeights = (
                MergeWeights[MergeWeights(nthint(lines[i+4], 0)).name]
            )
            self.instrument.incidentFlightPath = nthfloat(lines[i+5], 0)
            self.instrument.spectrumNumberForOutputDiagnosticFiles = (
                nthint(lines[i+6], 0)
            )

            self.instrument.neutronScatteringParametersFile = (
                firstword(lines[i+7])

            )
            self.instrument.scaleSelection = (
                Scales[Scales(nthint(lines[i+8], 0)).name]
            )
            self.instrument.subWavelengthBinnedData = (
                boolifyNum(nthint(lines[i+9], 0))
            )
            self.instrument.GudrunStartFolder = firstword(lines[i+10])
            self.instrument.startupFileFolder = firstword(lines[i+11])
            self.instrument.logarithmicStepSize = nthfloat(lines[i+12], 0)
            self.instrument.hardGroupEdges = (
                boolifyNum(nthint(lines[i+13], 0))
            )

            # If NeXus files are being used, then we expect a NeXus definition
            # file to be present, and extract it.
            if (
                self.instrument.dataFileType == "NXS"
                or self.instrument.dataFileType == "nxs"
            ):
                self.instrument.nxsDefinitionFile = firstword(lines[i+14])

                # Increment i to account for the NeXus definition file.
                i += 1
            self.instrument.numberIterations = nthint(lines[i+14], 0)
            self.instrument.tweakTweakFactors = (
                boolifyNum(nthint(lines[i+15], 0))
            )
        except Exception as e:
            raise ParserException(
                    "Whilst parsing Instrument, an exception occured."
                    " The input file is most likely of an incorrect format, "
                    "and some attributes were missing."
            ) from e

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

        try:
            # Initialise beam attribute to a new instance of Beam.
            self.beam = Beam()

            # For enumerated attributes,
            # where the member name of the attribute is
            # the first 'word' in the line, and we must get the member,
            # we do this: Enum[memberName].
            self.beam.sampleGeometry = Geometry[firstword(lines[0])]

            # Set the global geometry.
            global geometry
            geometry = self.beam.sampleGeometry

            # For single integer attributes,
            # we extract the zeroth int from the line.
            self.beam.noBeamProfileValues = nthint(lines[1], 0)

            # For N float attributes,
            # we extract the first N floats from the line.
            self.beam.beamProfileValues = extract_floats_from_string(lines[2])

            # For single float attributes,
            # we extract the zeroth float from the line.
            self.beam.stepSizeAbsorption = nthfloat(lines[3], 0)
            self.beam.stepSizeMS = nthfloat(lines[3], 1)
            self.beam.noSlices = nthint(lines[3], 2)
            self.beam.angularStepForCorrections = nthint(lines[4], 0)

            # Extract the incident beam edges
            # relative to the centroid of the sample.
            self.beam.incidentBeamLeftEdge = nthfloat(lines[5], 0)
            self.beam.incidentBeamRightEdge = nthfloat(lines[5], 1)
            self.beam.incidentBeamTopEdge = nthfloat(lines[5], 2)
            self.beam.incidentBeamBottomEdge = nthfloat(lines[5], 3)

            # Extract the scattered beam edges
            # relative to the centroid of the sample.
            self.beam.scatteredBeamLeftEdge = nthfloat(lines[6], 0)
            self.beam.scatteredBeamRightEdge = nthfloat(lines[6], 1)
            self.beam.scatteredBeamTopEdge = nthfloat(lines[6], 2)
            self.beam.scatteredBeamBottomEdge = nthfloat(lines[6], 3)

            # For string attributes,
            # we simply extract the firstword in the line.
            self.beam.filenameIncidentBeamSpectrumParams = firstword(lines[7])

            self.beam.overallBackgroundFactor = nthfloat(lines[8], 0)
            self.beam.sampleDependantBackgroundFactor = nthfloat(lines[9], 0)
            self.beam.shieldingAttenuationCoefficient = nthfloat(lines[10], 0)
        except Exception as e:
            raise ParserException(
                    "Whilst parsing Beam, an exception occured."
                    " The input file is most likely of an incorrect format, "
                    "and some attributes were missing."
            ) from e

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

        try:
            # Initialise normalisation attribute
            # to a new instance of Normalisation.
            self.normalisation = Normalisation()

            # The number of files and period number are both stored
            # on the same line.
            # So we extract the 0th integer for the number of files,
            # and the 1st integer for the period number.
            numberOfFiles = nthint(lines[0], 0)
            self.normalisation.periodNumber = nthint(lines[0], 1)

            # Extract data files
            dataFiles = []
            for i in range(numberOfFiles):
                dataFiles.append(firstword(lines[i+1]))

            # Create a DataFiles object from the dataFiles list constructed.
            self.normalisation.dataFiles = (
                DataFiles(dataFiles, "NORMALISATION")
            )

            # Calculate the index which we should continue from.
            i = 1 + numberOfFiles

            # The number of background files and
            # background period number are both stored
            # on the same line.
            # So we extract the 0th integer for the number of background files,
            # and the 1st integer for the background riod number.
            numberOfFilesBg = nthint(lines[i], 0)
            self.normalisation.periodNumberBg = nthint(lines[i], 1)

            # Extract background data files
            dataFilesBg = []
            for j in range(numberOfFilesBg):
                dataFilesBg.append(firstword(lines[i+j+1]))

            # Create a DataFiles object from the dataFiles list constructed.
            self.normalisation.dataFilesBg = (
                DataFiles(dataFilesBg, "NORMALISATION BACKGROUND")
            )

            # Calculate the index which we should continue from.
            # Account for the number of data files
            # and number of background data files.
            j = 1 + i + numberOfFilesBg

            # For boolean attributes, we convert the first
            # integer in the line to its boolean value.
            self.normalisation.forceCalculationOfCorrections = (
                boolifyNum(nthint(lines[j], 0))
            )

            # Construct composition
            composition = []
            n = 1
            line = lines[j+n]
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
                composition.append(
                    Element(atomicSymbol, massNo, abundance)
                )

                n += 1
                line = lines[j+n]

            # Create a Composition object from the dataFiles list constructed.
            self.normalisation.composition = (
                Composition(composition, "Normalisation")
            )

            # Calculate the index we must continue from.
            # By adding the number of elements+1 to the current index.
            j += n + 1

            # For enumerated attributes,
            # where the member name of the attribute is
            # the first 'word' in the line, and we must get the member,
            # we do this: Enum[memberName].
            self.normalisation.geometry = Geometry[firstword(lines[j])]

            # Is the geometry FLATPLATE?
            if (
                (
                    self.normalisation.geometry == Geometry.SameAsBeam
                    and geometry == Geometry.FLATPLATE
                )
                    or self.normalisation.geometry == Geometry.FLATPLATE):
                # If is is FLATPLATE, then extract the upstream and downstream
                # thickness, the angle of rotation and sample width.
                self.normalisation.upstreamThickness = nthfloat(lines[j+1], 0)
                self.normalisation.downstreamThickness = (
                    nthfloat(lines[j+1], 1)
                )
                self.normalisation.angleOfRotation = nthfloat(lines[j+2], 0)
                self.normalisation.sampleWidth = nthfloat(lines[j+2], 1)
            else:

                # Otherwise, it is CYLINDRICAL,
                # then extract the inner and outer
                # radii and the sample height.
                self.normalisation.innerRadius = nthfloat(lines[j+1], 0)
                self.normalisation.outerRadius = nthfloat(lines[j+1], 1)
                self.normalisation.sampleHeight = nthfloat(lines[j+2], 0)

            # Extract the density.
            density = nthfloat(lines[j+3], 0)

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

            self.normalisation.tempForNormalisationPC = nthfloat(lines[j+4], 0)
            self.normalisation.totalCrossSectionSource = firstword(lines[j+5])
            self.normalisation.normalisationDifferentialCrossSectionFile = (
                firstword(lines[j+6])
            )
            self.normalisation.lowerLimitSmoothedNormalisation = (
                nthfloat(lines[j+7], 0)
            )
            self.normalisation.normalisationDegreeSmoothing = (
                nthfloat(lines[j+8], 0)
            )
            self.normalisation.minNormalisationSignalBR = (
                nthfloat(lines[j+9], 0)
            )
        except Exception as e:
            raise ParserException(
                    "Whilst parsing Normalisation, an exception occured."
                    " The input file is most likely of an incorrect format, "
                    "and some attributes were missing."
            ) from e

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

        try:
            sampleBackground = SampleBackground()

            numberOfFiles = nthint(lines[0], 0)
            sampleBackground.periodNumber = nthint(lines[0], 1)

            dataFiles = []
            for i in range(numberOfFiles):
                dataFiles.append(firstword(lines[i+1]))
            sampleBackground.dataFiles = (
                DataFiles(dataFiles, "SAMPLE BACKGROUND")
            )

            return sampleBackground
        except Exception as e:
            raise ParserException(
                    "Whilst parsing Sample Background, an exception occured."
                    " The input file is most likely of an incorrect format, "
                    "and some attributes were missing."
            ) from e

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

        try:
            # Create a new instance of Sample.
            sample = Sample()

            # Extract the sample name, and then discard whitespace lines.
            sample.name = str(lines[0][:-2]).strip()
            lines[:] = lines[2:]

            # The number of files and period number are both stored
            # on the same line.
            # So we extract the 0th integer for the number of files,
            # and the 1st integer for the period number.
            numberOfFiles = nthint(lines[0], 0)
            sample.periodNumber = nthint(lines[0], 1)

            # Extract data files
            dataFiles = []
            for i in range(numberOfFiles):
                dataFiles.append(firstword(lines[i+1]))

            # Create a DataFiles object from the dataFiles list constructed.
            sample.dataFiles = DataFiles(dataFiles, sample.name)

            # Calculate the index which we should continue from.
            i = 1 + numberOfFiles

            # For boolean attributes, we convert the first
            # integer in the line to its boolean value.
            sample.forceCalculationOfCorrections = (
                boolifyNum(nthint(lines[i], 0))
            )

            # Construct composition
            composition = []
            n = 1
            line = lines[i+n]
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
                n += 1
                line = lines[i+n]

            # Create a Composition object from the dataFiles list constructed.
            sample.composition = Composition(composition, "Sample")

            # Calculate the index we must continue from.
            # By adding the number of elements+1 to the current index.
            i += n + 1

            # For enumerated attributes,
            # where the member name of the attribute is
            # the first 'word' in the line, and we must get the member,
            # we do this: Enum[memberName].
            sample.geometry = Geometry[firstword(lines[i])]

            # Is the geometry FLATPLATE?
            if (
                (
                    sample.geometry == Geometry.SameAsBeam
                    and geometry == Geometry.FLATPLATE
                )
                    or sample.geometry == Geometry.FLATPLATE):
                # If is is FLATPLATE, then extract the upstream and downstream
                # thickness, the angle of rotation and sample width.
                sample.upstreamThickness = nthfloat(lines[i+1], 0)
                sample.downstreamThickness = nthfloat(lines[i+1], 1)
                sample.angleOfRotation = nthfloat(lines[i+2], 0)
                sample.sampleWidth = nthfloat(lines[i+2], 1)
            else:

                # Otherwise, it is CYLINDRICAL,
                # then extract the inner and outer
                # radii and the sample height.
                sample.innerRadius = nthfloat(lines[i+1], 0)
                sample.outerRadius = nthfloat(lines[i+1], 1)
                sample.sampleHeight = nthfloat(lines[i+2], 0)

            # Extract the density.
            density = nthfloat(lines[i+3], 0)

            # Decide on the units of density.
            # -ve density means it is atomic (atoms/A^3)
            # +ve means it is chemical (gm/cm^3)
            sample.density = abs(density)
            sample.densityUnits = (
                UnitsOfDensity.ATOMIC if
                density < 0
                else UnitsOfDensity.CHEMICAL
            )
            sample.tempForNormalisationPC = nthfloat(lines[i+4], 0)
            sample.totalCrossSectionSource = firstword(lines[i+5])
            sample.sampleTweakFactor = nthfloat(lines[i+6], 0)
            sample.topHatW = nthfloat(lines[i+7], 0)
            sample.minRadFT = nthfloat(lines[i+8], 0)
            sample.grBroadening = nthfloat(lines[i+9], 0)

            # Extract the resonance values.
            # Each row consists of the first 2 floats.
            # (minWavelength, maxWavelength) in the line.
            # If the marker line is encountered,
            # then the values has been parsed.
            n = 10
            line = lines[i+n]
            while (
                    "to finish specifying wavelength range of resonance"
                    not in line
                    ):
                sample.resonanceValues.append(
                    tuple(extract_floats_from_string(line))
                )
                n += 1
                line = lines[i+n]
            i += n + 1

            # Extract the exponential values.
            # Each row consists of the first 3 numbers.
            # (Amplitude, Decay, N) in the line.
            # If the marker line is encountered,
            # then the values has been parsed.
            n = 0
            line = lines[i+n]
            while "to specify end of exponential parameter input" not in line:
                sample.exponentialValues.append(
                    tuple(extract_nums_from_string(line))
                )
                n += 1
                line = lines[i+n]
            i += n + 1

            sample.normalisationCorrectionFactor = nthfloat(lines[i], 0)
            sample.fileSelfScattering = firstword(lines[i+1])
            sample.normaliseTo = (
                NormalisationType[
                    NormalisationType(nthint(lines[i+2], 0)).name
                ]
            )
            sample.maxRadFT = nthfloat(lines[i+3], 0)
            sample.outputUnits = (
                OutputUnits[OutputUnits(nthint(lines[i+4], 0)).name]
            )
            sample.powerForBroadening = nthfloat(lines[i+5], 0)
            sample.stepSize = nthfloat(lines[i+6], 0)
            sample.include = boolifyNum(nthint(lines[i+7], 0))
            sample.scatteringFraction = nthfloat(lines[i+8], 0)
            sample.attenuationCoefficient = nthfloat(lines[i+8], 1)

            return sample
        except Exception as e:
            raise ParserException(
                    "Whilst parsing Sample, an exception occured."
                    " The input file is most likely of an incorrect format, "
                    "and some attributes were missing."
            ) from e

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

        try:
            # Create a new instance of Container.
            container = Container()

            # Extract the name from the lines,
            # and then discard the unnecessary lines.
            container.name = str(lines[0][:-2]).strip()
            lines[:] = lines[2:]

            # The number of files and period number are both stored
            # on the same line.
            # So we extract the 0th integer for the number of files,
            # and the 1st integer for the period number.
            numberOfFiles = nthint(lines[0], 0)
            container.periodNumber = nthint(lines[0], 1)

            # Extract data files
            dataFiles = []
            for i in range(numberOfFiles):
                dataFiles.append(firstword(lines[i+1]))

            # Create a DataFiles object from the dataFiles list constructed.
            container.dataFiles = DataFiles(dataFiles, container.name)

            # Calculate the index which we should continue from.
            i = 1 + numberOfFiles

            # Construct composition
            composition = []
            n = 0
            line = lines[i+n]
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
                n += 1
                line = lines[i+n]

            # Create a Composition object from the dataFiles list constructed.
            container.composition = Composition(composition, "Container")

            # Calculate the index we must continue from.
            # By adding the number of elements+1 to the current index.
            i += n + 1

            # For enumerated attributes,
            # where the member name of the attribute is
            # the first 'word' in the line, and we must get the member,
            # we do this: Enum[memberName].
            container.geometry = Geometry[firstword(lines[i])]

            # Is the geometry FLATPLATE?
            if (
                (
                    container.geometry == Geometry.SameAsBeam
                    and geometry == Geometry.FLATPLATE
                )
                    or container.geometry == Geometry.FLATPLATE):
                # If is is FLATPLATE, then extract the upstream and downstream
                # thickness, the angle of rotation and sample width.
                container.upstreamThickness = nthfloat(lines[i+1], 0)
                container.downstreamThickness = nthfloat(lines[i+1], 1)
                container.angleOfRotation = nthfloat(lines[i+2], 0)
                container.sampleWidth = nthfloat(lines[i+2], 1)
            else:

                # Otherwise, it is CYLINDRICAL,
                # then extract the inner and outer
                # radii and the sample height.
                container.innerRadius = nthfloat(lines[i+1], 0)
                container.outerRadius = nthfloat(lines[i+1], 1)
                container.sampleHeight = nthfloat(lines[i+2], 0)

            # Extract the density.
            density = nthfloat(lines[i+3], 0)

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
            container.totalCrossSectionSource = firstword(lines[i+4])
            container.tweakFactor = nthfloat(lines[i+5], 0)
            container.scatteringFraction = nthfloat(lines[i+6], 0)
            container.attenuationCoefficient = nthfloat(lines[i+6], 1)

            return container
        except Exception as e:
            raise ParserException(
                    "Whilst parsing Container, an exception occured."
                    " The input file is most likely of an incorrect format, "
                    "and some attributes were missing."
            ) from e

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
