import os
import time
from copy import deepcopy

from core.instrument import Instrument
from core.beam import Beam
from core.normalisation import Normalisation
from core.sample_background import SampleBackground
from core.composition import Components
from core import config as cfg
from core.gud_file import GudFile

SUFFIX = ".exe" if os.name == "nt" else ""


class GudrunFile:
    OUTPATH = "gudpy.txt"
    """
    Class to represent a GudFile (files with .gud extension).
    .gud files are outputted by gudrun_dcs, via merge_routines
    each .gud file belongs to an individual sample.

    ...

    Attributes
    ----------
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
    """

    def __init__(
        self,
        instrument=Instrument(),
        beam=Beam(),
        normalisation=Normalisation(),
        sampleBackgrounds: list[SampleBackground] = [],
        components=Components()
    ):
        """
        Constructs all the necessary attributes for the GudrunFile object.
        Calls the GudrunFile's parse method,
        to parse the GudrunFile from its path.

        Parameters
        ----------
        path : str
            Path to the file.
        projectDir : str
            Path to the project folder
        format : Format enum
            Format of the file
        config : bool
            If a new input file should be constructed from a config
        """
        self.instrument = instrument
        self.normalisation = normalisation
        self.beam = beam
        self.sampleBackgrounds = sampleBackgrounds
        self.components = components
        self.purged = False

    @property
    def path(self):
        return os.path.join(self.outputFolder, self.OUTPATH)

    def __deepcopy__(self, memo):
        result = self.__class__.__new__(self.__class__)
        memo[id(self)] = result
        for k, v in self.__dict__.items():
            if k == "yaml":
                continue
            setattr(result, k, deepcopy(v, memo))
        return result

    def setGudrunDir(self, dir):
        self.instrument.GudrunInputFileDir = dir

    def convertToSample(self, container, persist=False):

        sample = container.convertToSample()

        if persist:
            for i, sampleBackground in enumerate(self.sampleBackgrounds):
                for sample in sampleBackground.samples:
                    if container in sample.containers:
                        sample.containers.remove(container)
                        break
            self.sampleBackgrounds[i].append(sample)
        return sample

    def determineError(self, sample):
        gudPath = sample.dataFiles[0].replace(
            self.instrument.dataFileType,
            "gud"
        )
        gudFile = GudFile(
            os.path.join(
                self.instrument.GudrunInputFileDir, gudPath
            )
        )
        error = round(
            (
                1.0 - (gudFile.averageLevelMergedDCS / gudFile.expectedDCS)
            ) * 100, 1
        )
        return error

    def runSamples(self):
        return [
            s for sb in self.sampleBackgrounds
            for s in sb.samples
            if s.runThisSample]

    def checkNormDataFiles(self):
        return (len(self.normalisation.dataFiles)
                and len(self.normalisation.dataFilesBg))

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
        header = (
            f"'{cfg.spc2}'{cfg.spc2}'{cfg.spc10}'"
            f"{cfg.spc2}'{os.path.sep}'{LINEBREAK}"
        )
        instrument = (
            f"INSTRUMENT{cfg.spc10}{{\n\n"
            + str(self.instrument)
            + LINEBREAK
            + "}"
        )
        beam = f"BEAM{cfg.spc10}{{\n\n" + str(self.beam) + LINEBREAK + "}"
        normalisation = (
            f"NORMALISATION{cfg.spc10}{{\n\n"
            + str(self.normalisation)
            + LINEBREAK
            + "}"
        )
        sampleBackgrounds = "\n".join(
            [str(x) for x in self.sampleBackgrounds]
        ).rstrip()
        footer = (
            f"\n\n\nEND{cfg.spc10}"
            f"\n1\nDate and time last written:  "
            f"{time.strftime('%Y%m%d %H:%M:%S')}{cfg.spc10}"
            f"\nN"
        )

        components = (
            f"\n\nCOMPONENTS:\n{str(self.components)}"
            if len(self.components.components)
            else ""
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
            + components
        )
