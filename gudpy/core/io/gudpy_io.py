from abc import abstractmethod
from enum import Enum
from ruamel.yaml import YAML as yaml
from ruamel.yaml import YAMLError
import shutil
import os
import typing as typ

from core.composition import (
    Component, Components, Composition, WeightedComponent
)
from core.data_files import DataFile, DataFiles
from core.element import Element
from core.exception import YAMLException
from core.gui_config import GUIConfig
from core import utils
from core.instrument import Instrument
from core.beam import Beam
from core.normalisation import Normalisation
from core.sample_background import SampleBackground
from core.sample import Sample
from core.container import Container
from core.gudrun_file import GudrunFile
from core.io.gudrun_file_parser import GudrunFileParser
from core import config


class GudPyIO:
    projectDir = ""
    loadFile = ""

    def __init__(self):
        self.yaml = self._getYamlModule()
        self.gudrunFileParser = GudrunFileParser()

    @classmethod
    def projectName(cls) -> str:
        return os.path.dirname(cls.projectDir)

    @classmethod
    def autosavePath(cls) -> str:
        return f"{os.path.basename(cls.projectDir)}.autosave"

    @classmethod
    def path(cls):
        """Returns the path to the yaml file

        Returns
        -------
        str
            Path to yaml file

        Raises
        ------
        RuntimeError
            Raised if project directory is not set
        """
        if not cls.projectDir:
            raise RuntimeError("Save location not set.")
        return os.path.join(cls.projectDir, f"{cls.projectName()}.yaml")

    @classmethod
    def setSaveLocation(cls, projectDir: str):
        """Sets the save location/project directory

        Parameters
        ----------
        projectDir : str
            Path to new save location
        """
        cls.projectDir = projectDir

    @classmethod
    def checkSaveLocation(cls) -> bool:
        """Checks if user has set the save location
        """
        return bool(cls.projectDir)

    def save(self, gudrunFile):
        """Saves yaml file to project directory
        """
        self._writeYAML(gudrunFile, self.path())

    def importGudrunFile(self, path, config=False) -> GudrunFile:
        GudPyIO.loadFile = path
        return self.gudrunFileParser.parse(path, config)

    def importProject(self, projectDir) -> GudrunFile:
        """Imports from a project directory

        Parameters
        ----------
        projectDir : str
            Path to GudPy project folder

        Raises
        ------
        FileNotFoundError
            Raised if there is no YAML input file in the
            project directory

        Returns
        -------
        GudrunFile
            Genererated GudrunFile from input
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

        self.setSaveLocation(projectDir)
        return self._parseYaml(loadFile)

    def importFromYamlFile(self, loadFile) -> GudrunFile:
        return self._parseYaml(loadFile)

    def exportProject(self, gudrunFile, targetDir):
        if os.path.exists(targetDir):
            raise IsADirectoryError("Cannot be an existing directory")

        oldFile = os.path.join(targetDir, os.path.basename(self.loadFile))
        os.makedirs(targetDir)
        print("TARGET DIR: " + targetDir)

        if self.projectDir and oldFile:
            shutil.copytree(self.projectDir, targetDir)
            os.rename(oldFile, self.path())
        else:
            yamlPath = os.path.join(
                targetDir,
                f"{os.path.basename(targetDir)}.yaml"
            )
            print("yaml PATH: " + yamlPath)
            self.exportYamlFile(gudrunFile, yamlPath)

    def exportYamlFile(self, gudrunFile, path):
        self._writeYAML(gudrunFile, path)

    @classmethod
    def exportGudrunFile(cls, gudrunFile, path):
        return GudrunFileParser.export(gudrunFile, path)

    @classmethod
    def writeGudrunFile(cls, gudrunFile, path):
        GudrunFileParser.writeGudrunFile(gudrunFile, path)

    @classmethod
    def writeObject(cls, obj, path):
        with open(path, "w", encoding="utf-8") as f:
            f.write(str(obj))
            f.close()

# =================================================================
#                         PARSING HELPERS
# =================================================================

    def _getYamlModule(self) -> yaml:
        yaml_ = yaml()
        yaml_.preserve_quotes = True
        yaml_.default_flow_style = None
        yaml_.encoding = 'utf-8'
        return yaml_

    def _parseYaml(self, path) -> GudrunFile:
        self.loadFile = path
        yamldict = self._yamlToDict(path)
        gudrunFile = GudrunFile()
        for k, v in yamldict.items():
            k = k.lower()
            if k == "GUI":
                GUI = GUIConfig()
                self._yamlToObject(GUI, v)
                config.GUIConfig = GUI
                continue
            if not hasattr(gudrunFile, k):
                # If attribute is not valid
                print(f"Ignoring depreciated attribute '{k}'")
                continue

            objType = type(gudrunFile.__dict__[k])
            parsingFunc = self._parsingFuncMap(objType)
            if parsingFunc:
                try:
                    obj = parsingFunc(v)
                    setattr(gudrunFile, k, obj)
                except YAMLException as e:
                    raise YAMLException(e)
                except YAMLError as e:
                    # Exception caused by yaml parsing library
                    raise YAMLException(f"Invalid YAML file: {str(e)}")
                except Exception as e:
                    raise YAMLException(f"Failed at: {k}. Details: {e}")
        return gudrunFile

    def _writeYAML(self, gudrunFile: GudrunFile, path: str) -> None:
        with open(path, "wb") as fp:
            outyaml = {
                "instrument": gudrunFile.instrument,
                "beam": gudrunFile.beam,
                "components": gudrunFile.components.components,
                "normalisation": gudrunFile.normalisation,
                "sampleBackgrounds": gudrunFile.sampleBackgrounds,
                "GUI": config.GUI
            }
            self.yaml.dump(
                {k: self.toYaml(v) for k, v in outyaml.items()},
                fp
            )
            print(fp)

    def _parsingFuncMap(self, type: type) -> typ.Union[typ.Callable, None]:
        parsingFuncs = {
            Instrument: self._parseYamlInstrument,
            Beam: self._parseYamlBeam,
            Normalisation: self._parseYamlNormalisation,
            SampleBackground: self._parseYamlSampleBackground,
            Sample: self._parseYamlSample,
            Composition: self._parseYamlComposition,
            Component: self._parseYamlComponent,
            Components: self._parseYamlComponents,
            list[Element]: self._parseYamlElements,
            DataFiles: self._parseYamlDataFiles
        }
        if type in parsingFuncs.keys():
            return parsingFuncs[type]
        else:
            return None

    def _yamlToDict(self, path) -> any:
        # Read the input stream into our attribute.
        with open(path, encoding=self.yaml.encoding) as fp:
            return self.yaml.load(fp)

    def _yamlToObject(self, obj: any, yamldict: any) -> any:
        for k, v in yamldict.items():
            self._assignYamlToAttr(obj, k, v)
        return obj

    def _assignYamlToAttr(self, obj: any, key, val) -> None:
        if not hasattr(obj, key):
            # If attribute is not valid
            print(
                f"Ignoring depreciated attribute '{key}'"
                f"given to '{type(obj).__name__}'"
            )
            return

        try:
            if isinstance(obj.__dict__[key], Enum):
                setattr(obj, key, type(obj.__dict__[key])[val])
                return

            setattr(obj, key, type(obj.__dict__[key])(self.toBuiltin(val)))
        except Exception as e:
            raise YAMLException(
                "Parsing failed while trying to assign attribute"
                f"'{key}' to {type(obj).__name__}") from e

    def _parseYamlInstrument(self, yamldict: any) -> Instrument:
        instrument = Instrument()
        instrument = self._yamlToObject(instrument, yamldict)
        return instrument

    def _parseYamlBeam(self, yamldict: any) -> Normalisation:
        beam = Beam()
        beam = self._yamlToObject(beam, yamldict)
        return beam

    def _parseYamlNormalisation(self, yamldict: any) -> Normalisation:
        normalisation = Normalisation()
        for k, v in yamldict.items():
            if k == "composition":
                composition = self._parseYamlComposition(yamldict[k])
                setattr(normalisation, k, composition)
            if k == "dataFiles":
                dataFiles = self._parseYamlDataFiles(yamldict[k])
                setattr(normalisation, k, dataFiles)
            else:
                self._assignYamlToAttr(normalisation, k, v)
        return normalisation

    def _parseYamlSample(self, yamldict: any) -> Sample:
        sample = Sample()
        for k, v in yamldict.items():
            if k == "composition":
                composition = self._parseYamlComposition()
                setattr(sample, k, composition)
            elif k == "containers":
                for contyaml in yamldict[k]:
                    container = self._parseYamlContainer(contyaml)
                    sample.containers.append(container)
            else:
                self._assignYamlToAttr(sample, k, v)
        return sample

    def _parseYamlSampleBackground(self, yamldict: any) -> SampleBackground:
        sampleBg = SampleBackground()
        for k, v in yamldict.items():
            if k == "samples":
                for sampleyaml in yamldict[k]:
                    sample = self._parseYamlSample(sampleyaml)
                    sample.name = utils.replace_unwanted_chars(sample.name)
                    sampleBg.samples.append(sample)
            else:
                self._assignYamlToAttr(sampleBg, k, v)

    def _parseYamlComposition(self, yamldict: any) -> Composition:
        composition = Composition()
        for k, v in yamldict.items():
            if k == "elements":
                elements = self._parseYamlElements(yamldict[k])
                setattr(composition, k, elements)
            elif k == "weightedComponents":
                weightedComponents = []
                for wc in yamldict[k]:
                    component = self._parseYamlComponent(wc)
                    ratio = wc["ratio"]
                    try:
                        weightedComponents.append(
                            WeightedComponent(
                                component, float(ratio))
                        )
                    except ValueError:
                        raise YAMLException(
                            "Invalid ratio given to Weighted Component")
                setattr(composition, k, weightedComponents)
            else:
                self._assignYamlToAttr(composition, k, v)
        return composition

    def _parseYamlContainer(self, yamldict: any) -> Container:
        container = Container()
        for k, v in yamldict.items():
            if k == "composition":
                composition = self._parseYamlComposition()
                setattr(container, k, composition)
            else:
                self._assignYamlToAttr(container, k, v)
        return container

    def _parseYamlDataFiles(self, yamldict: any) -> DataFiles:
        dataFiles = DataFiles([], yamldict["name"])
        for df in yamldict["_dataFiles"]:
            dataFile = DataFile(df["filename"])
            dataFile = self._yamlToObject(dataFile, df)
            dataFiles.dataFiles.append(dataFile)
        return dataFiles

    def _parseYamlComponent(self, yamldict: any) -> Component:
        if (
            "component" not in yamldict
            or "ratio" not in yamldict
        ):
            raise YAMLException(
                "Weighted Component expects 'component' and"
                + " 'ratio' to be provided")
        component = Component()
        self._yamlToObject(
            component, yamldict["component"]
        )
        return component

    def _parseYamlComponents(self, yamllist: list[dict]) -> Components:
        components = []
        for c in yamllist:
            components.append(self._parseYamlComponent(c))
        return Components(components)

    def _parseYamlElements(self, yamllist: list[str]) -> list[Element]:
        elements = []
        for idx, element in enumerate(yamllist):
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
            except ValueError as e:
                raise YAMLException(
                    f"Invalid number given to element {idx + 1}:"
                    f"{e}")
        return elements

    @abstractmethod
    def toYaml(self, var: any):
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
            Instrument, Beam, Components, Normalisation,
            SampleBackground, Sample, Container, WeightedComponent,
            Component, Composition, Element, DataFiles, DataFile, GUIConfig
        )):
            return {
                k: self.toYaml(v)
                for k, v in var.__dict__.items()
                if k not in var.yamlignore
            }

    @abstractmethod
    def toBuiltin(self, yamlvar: any):
        if yamlvar is None:
            return None
        if isinstance(yamlvar, (list, tuple)):
            return [self.toBuiltin(v) for v in yamlvar]
        elif (yamlvar.__class__.__module__ ==
              "ruamel.yaml.comments.CommentedMap"):
            dict = {}
            for k, v in yamlvar.items():
                dict[k] = v
            return dict
        elif yamlvar.__class__.__module__ == "builtins":
            return yamlvar
        elif yamlvar.__class__.__module__ == "ruamel.yaml.scalarfloat":
            return float(yamlvar)
        elif yamlvar.__class__.__module__ == "ruamel.yaml.scalarstring":
            return str(yamlvar)
