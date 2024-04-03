from copy import deepcopy
import os
from enum import Enum
from ruamel.yaml import YAML, YAMLError
import typing as typ

from core.data_files import DataFiles
from core.element import Element
from core.gui_config import GUIConfig
from core import utils
from core.exception import YAMLException
from core.instrument import Instrument
from core.beam import Beam
from core.normalisation import Normalisation
from core import composition as comp
from core.sample_background import SampleBackground
from core.sample import Sample
from core.container import Container
from core.output_file_handler import GudrunOutput, SampleOutput
from core.gudrun_file import GudrunFile
from core.gud_file import GudFile
from core import config as cfg


class GudrunParameters:
    def __init__(self):
        self.instrument = Instrument()
        self.beam = Beam()
        self.normalisation = Normalisation()
        self.sampleBackgrounds = []
        self.components = comp.Components()

        self.purgeLocation = ""

    def setGudrunDir(self, dir):
        self.instrument.GudrunInputFileDir = dir


class GudPyData:
    """
    Class to store all relevant GudPyData, responsible for parsing
    and writing out the data in YAML form.

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
    outputData : GudrunOutput
        Paths to all of the gudrun outputs
    yaml : ruamel.yaml.YAML
        YAML writer/parser

    """

    def __init__(self):
        self.gudrunParams = GudrunParameters()
        self.gudrunOutput = None

        # I/O
        self.yaml = self.getYamlModule()
        self.gudrunFile = GudrunFile()

        # Paths
        self.projectDir = ""
        self.loadFile = ""
        self.filename = ""
        self.autosaveLocation = ""

        cfg.GUI = GUIConfig()

    def __deepcopy__(self, memo):
        result = self.__class__.__new__(self.__class__)
        memo[id(self)] = result
        for k, v in self.__dict__.items():
            if k == "yaml":
                continue
            setattr(result, k, deepcopy(v, memo))
        return result

    def getYamlModule(self):
        yaml_ = YAML()
        yaml_.preserve_quotes = True
        yaml_.default_flow_style = None
        yaml_.encoding = 'utf-8'
        return yaml_

# ------------------------------ I / O -------------------------------- #

    def path(self) -> str:
        if not self.projectDir:
            return None
        else:
            return os.path.join(self.projectDir, self.filename)

    def importGudrunFile(self, loadFile) -> None:
        self.loadFile = loadFile
        self.gudrunParams = self.gudrunFile.parse(path=loadFile)

    def importProject(self, projectDir) -> None:
        """Loads GudPy from a project directory

        Parameters
        ----------
        projectDir : str
            Path to GudPy project folder

        Raises
        ------
        FileNotFoundError
            Raised if there is no YAML input file in the
            project directory
        """

        loadFile = ""

        if os.path.exists(os.path.join(
            projectDir,
            f"{os.path.basename(projectDir)}.yaml"
        )):
            # If default file exists
            loadFile = os.path.join(
                projectDir,
                f"{os.path.basename(projectDir)}.yaml"
            )
        else:
            # Try to find yaml files
            for f in os.listdir(projectDir):
                if os.path.splitext(f)[1] == ".yaml":
                    # If file is yaml
                    loadFile = os.path.join(projectDir, f)
        if not loadFile:
            raise FileNotFoundError(
                "Could not find GudPy input file within the project")
        self.loadFile = loadFile
        self.projectDir = projectDir
        self.gudrunParams = self.yaml.parseYaml(path=loadFile)

    def writeGudrunFile(self):
        self.gudrunFile.writeGudrunFile(
            params=self.gudrunParams,
            path=os.path.join(
                self.gudrunParams.instrument.GudrunInputFileDir,
                self.gudrunFile.OUTPATH)
        )

    def writeYAMLFile(self, path=''):
        with open(path, "wb") as fp:
            if not path:
                path = self.path()
            outyaml = {
                "Instrument": self.instrument,
                "Beam": self.beam,
                "Components": self.components,
                "Normalisation": self.normalisation,
                "SampleBackgrounds": self.sampleBackgrounds,
                "GudrunOutput": self.gudrunOutput,
                "GUI": cfg.GUI
            }
            self.yaml.dump(
                {k: self.toYaml(v) for k, v in outyaml.items()},
                fp
            )

    def exportGudrunFile(self, path, params):
        self.gudrunFile.writeGudrunFile(
            params=params,
            path=path
        )

# -------------------------- YAML Helpers --------------------------- #

    def parseYaml(self, path):
        try:
            self.constructClasses(self.yamlToDict(path))
        except YAMLError as e:
            # Exception caused by yaml parsing library
            raise YAMLException(f"Invalid YAML file: {str(e)}")
        except YAMLException as e:
            # Exception caused by invalid arguments
            raise YAMLException(e)

    def yamlToDict(self, path):
        # Read the input stream into our attribute.
        with open(path, encoding=self.yaml.encoding) as fp:
            return self.yaml.load(fp)

    def constructClasses(self, yamldict):
        instrument = Instrument()
        if "Instrument" in yamldict:
            self.maskYAMLDicttoClass(instrument, yamldict["Instrument"])
        instrument.GudrunInputFileDir = os.path.dirname(
            os.path.abspath(
                self.path
            )
        )

        self.beam = Beam()
        if "Beam" in yamldict:
            self.maskYAMLDicttoClass(self.beam, yamldict["Beam"])

        self.components = comp.Components()
        if "Components" in yamldict:
            self.maskYAMLSeqtoClass(
                self.components, yamldict["Components"])

        self.normalisation = Normalisation()
        if "Normalisation" in yamldict:
            self.maskYAMLDicttoClass(
                self.normalisation, yamldict["Normalisation"])

        sampleBackgrounds = []
        if "SampleBackgrounds" in yamldict:
            for sbyaml in yamldict["SampleBackgrounds"]:
                sampleBackground = SampleBackground()
                self.maskYAMLDicttoClass(sampleBackground, sbyaml)
                sampleBackgrounds.append(sampleBackground)

        self.gudrunOutput = GudrunOutput()
        if "GudrunOuptput" in yamldict:
            self.maskYAMLDicttoClass(GudrunOutput, yamldict["GudrunOutput"])
            for sampname, sampleOutput in yamldict["GudrunOutput"][
                    "sampleOutputs"].items():
                self.gudrunOutput.sampleOutputs[sampname] = SampleOutput()
                self.maskYAMLDicttoClass(
                    SampleOutput, self.gudrunOutput.sampleOutputs[sampname]
                )
            print(self.gudrunOutput)

        GUI = GUIConfig()
        if "GUI" in yamldict:
            self.maskYAMLDicttoClass(GUI, yamldict["GUI"])
        cfg.GUI = GUI

    def maskYAMLDicttoClass(self, cls, yamldict):
        for k, v in yamldict.items():
            if not hasattr(cls, k):
                # If attribute is not valid
                raise YAMLException(
                    f"Invalid attribute '{k}' given to '{type(cls).__name__}'")

            if isinstance(cls.__dict__[k], Enum):
                setattr(cls, k, type(cls.__dict__[k])[v])

            elif isinstance(cls.__dict__[k], DataFiles):
                setattr(
                    cls, k,
                    DataFiles(
                        [v_ for v_ in v["dataFiles"]], v["name"])
                )

            elif (
                isinstance(
                    cls,
                    (comp.Component, comp.Composition)
                )
                and k == "elements"
            ):
                elements = []
                for idx, element in enumerate(v):
                    # Ensuring correct arguements are provided
                    if (
                        "atomicSymbol" not in element
                        or "massNo" not in element
                        or "abundance" not in element
                    ):
                        raise YAMLException(
                            "Insufficient arguments given to element"
                            + f" {idx + 1}. Expects 'atomicSymbol', 'massNo'"
                            + " and 'abundance'"
                        )

                    # Setting element properties
                    try:
                        element_ = Element(
                            **{
                                "atomicSymbol": element["atomicSymbol"],
                                "massNo": float(element["massNo"]),
                                "abundance": float(element["abundance"])
                            }
                        )
                        elements.append(element_)
                    except ValueError:
                        raise YAMLException(
                            f"Invalid number given to element {idx + 1}"
                            + f" in '{type(cls).__name__}")
                setattr(cls, k, elements)

            elif (isinstance(cls, comp.Composition)
                  and k == "WeightedComponents"):
                comp.WeightedComponents = []
                for comp.WeightedComponent in v:
                    if (
                        "component" not in comp.WeightedComponent
                        or "ratio" not in comp.WeightedComponent
                    ):
                        raise YAMLException(
                            "WeightedComponent expects 'component' and"
                            + " 'ratio' to be provided")
                    component = comp.Component()
                    self.maskYAMLDicttoClass(
                        component, comp.WeightedComponent["component"]
                    )
                    ratio = comp.WeightedComponent["ratio"]
                    try:
                        comp.WeightedComponents.append(
                            comp.WeightedComponent(
                                component, float(ratio))
                        )
                    except ValueError:
                        raise YAMLException(
                            "Invalid ratio given to Weighted Component")
                setattr(cls, k, comp.WeightedComponents)

            elif (
                isinstance(
                    cls,
                    (Normalisation, Sample, Container)
                )
                and k == "composition"
            ):
                self.maskYAMLDicttoClass(cls.__dict__[k], v)

            elif isinstance(cls, SampleBackground) and k == "samples":
                for sampleyaml in yamldict[k]:
                    sample = Sample()
                    self.maskYAMLDicttoClass(sample, sampleyaml)
                    sample.name = utils.replace_unwanted_chars(sample.name)
                    cls.samples.append(sample)

            elif isinstance(cls, Sample) and k == "containers":
                for contyaml in yamldict[k]:
                    container = Container()
                    self.maskYAMLDicttoClass(container, contyaml)
                    cls.containers.append(container)

            else:
                setattr(cls, k, type(cls.__dict__[k])(self.toBuiltin(v)))

    def maskYAMLSeqtoClass(self, cls, yamlseq):
        if isinstance(cls, comp.Components):
            components = []
            for component in yamlseq:
                component_ = comp.Component()
                self.maskYAMLDicttoClass(component_, component)
                components.append(component_)
            setattr(cls, "components", components)

    def toYaml(self, var):
        if var.__class__.__module__ == "ruamel.yaml.scalarfloat":
            return float(var)
        if var.__class__.__module__ == "builtins":
            if isinstance(var, (list, tuple)):
                return type(var)([self.toYaml(v) for v in var])
            else:
                return var
        elif isinstance(var, Enum):
            return type(var)(var.value).name
        elif isinstance(var, (
            Instrument, Beam, comp.Components, Normalisation,
            SampleBackground, Sample, Container, comp.WeightedComponent,
            comp.Component, comp.Composition, Element, DataFiles, GUIConfig
        )):
            return {
                k: self.toYaml(v)
                for k, v in var.__dict__.items()
                if k not in var.yamlignore
            }

    def toBuiltin(self, yamlvar) -> typ.Any:
        if isinstance(yamlvar, (list, tuple)):
            return [self.toBuiltin(v) for v in yamlvar]
        elif yamlvar.__class__.__module__ == "builtins":
            return yamlvar
        elif yamlvar.__class__.__module__ == "ruamel.yaml.scalarfloat":
            return float(yamlvar)
        elif yamlvar.__class__.__module__ == "ruamel.yaml.scalarstring":
            return str(yamlvar)

# ------------------------- DATA UTILITIES ---------------------------- #

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
            (1.0 - (gudFile.averageLevelMergedDCS / gudFile.expectedDCS)
             ) * 100, 1)
        return error
