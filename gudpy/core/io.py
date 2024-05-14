from abc import abstractmethod
from enum import Enum
from ruamel.yaml import YAML as yaml
from ruamel.yaml import YAMLError
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
from core import config
import core.enums as enums


class YamlParser:
    def __init__(self):
        self.yaml = self.getYamlModule()

    @property
    def path(self, format: enums.Format):
        if not self.projectDir or self.projectDir:
            raise RuntimeError("Save location not set.")

        if format == enums.Format.TXT:
            return os.path.join(self.projectDir, f"{self.projectName}.txt")
        elif format == enums.Format.YAML:
            return os.path.join(self.projectDir, f"{self.projectName}.yaml")
        else:
            raise RuntimeError("Unsupported format.")

    def save(self, path: str = '', format: enums.Format = None):
        if not path:
            path = self.path()

        if not format:
            format = self.format
        if format == enums.Format.TXT:
            self.write_out(
                path=self.txtPath(), overwrite=True)
        elif format == enums.Format.YAML:
            if self.path():
                self.write_yaml(self.yamlPath())

    @property
    def projectName(self):
        os.path.dirname(self.projectDir)

    def write_out(
            self,
            path: str = '',
            overwrite: bool = False,
            writeParameters: bool = True
    ):
        """
        Writes out the string representation of the GudrunFile.
        If 'overwrite' is True, then the initial file is overwritten.
        Otherwise, it is written to 'gudpy_{initial filename}.txt'.

        Parameters
        ----------
        overwrite : bool, optional
            Overwrite the initial file? (default is False).
        path : str, optional
            Path to write to.
        Returns
        -------
        None
        """
        if path:
            if not overwrite:
                assert (not os.path.exists(path))
            f = open(
                path, "w", encoding="utf-8"
            )
        elif not overwrite:
            assert (not os.path.exists(os.path.join(
                    self.instrument.GudrunInputFileDir,
                    self.OUTPATH)
            ))
            f = open(
                os.path.join(
                    self.instrument.GudrunInputFileDir,
                    self.OUTPATH
                ), "w", encoding="utf-8")
        else:
            if not self.path():
                path = os.path.join(
                    self.instrument.GudrunInputFileDir,
                    self.OUTPATH)
            f = open(path, "w", encoding="utf-8")

        if os.path.basename(f.name) == self.OUTPATH:
            for sampleBackground in self.sampleBackgrounds:
                sampleBackground.writeAllSamples = False
        f.write(str(self))
        f.close()

        if writeParameters:
            for sb in self.sampleBackgrounds:
                for s in sb.samples:
                    if s.runThisSample:
                        gf = deepcopy(self)
                        gf.sampleBackgrounds = [deepcopy(sb)]
                        gf.sampleBackgrounds[0].samples = [deepcopy(s)]
                        gf.write_out(
                            path=os.path.join(
                                self.instrument.GudrunInputFileDir,
                                s.pathName(),
                            ),
                            overwrite=True,
                            writeParameters=False
                        )

# =================================================================
#                           YAML PARSING
# =================================================================

    def getYamlModule(self) -> yaml:
        yaml_ = yaml()
        yaml_.preserve_quotes = True
        yaml_.default_flow_style = None
        yaml_.encoding = 'utf-8'
        return yaml_

    def parseYaml(self, path) -> GudrunFile:
        yamldict = self.yamlToDict(path)
        gudrunFile = GudrunFile()
        for k, v in yamldict.items():
            if k == "GUI":
                GUI = GUIConfig()
                self.yamlToObject(GUI, v)
                config.GUIConfig = GUI
                continue
            if not hasattr(gudrunFile, k):
                # If attribute is not valid
                print(f"Ignoring depreciated attribute '{k}'")
                continue

            objType = type(gudrunFile.__dict__[k])
            parsingFunc = self.parsingFuncMap(objType)
            if parsingFunc:
                try:
                    obj = parsingFunc(v)
                    setattr(gudrunFile, k, obj)
                except YAMLException as e:
                    raise YAMLException(e)
                except YAMLError as e:
                    # Exception caused by yaml parsing library
                    raise YAMLException(f"Invalid YAML file: {str(e)}")
        return gudrunFile

    def writeYAML(self, gudrunFile: GudrunFile, path: str) -> None:
        with open(path, "wb") as fp:
            outyaml = {
                "Instrument": gudrunFile.instrument,
                "Beam": gudrunFile.beam,
                "Components": gudrunFile.components.components,
                "Normalisation": gudrunFile.normalisation,
                "SampleBackgrounds": gudrunFile.sampleBackgrounds,
                "GUI": config.GUI
            }
            self.yaml.dump(
                {k: self.toYaml(v) for k, v in outyaml.items()},
                fp
            )

    def parsingFuncMap(self, type: type) -> typ.Callable | None:
        parsingFuncs = {
            Instrument: self.parseYamlInstrument,
            Beam: self.parseYamlBeam,
            Normalisation: self.parseYamlNormalisation,
            SampleBackground: self.parseYamlSampleBackground,
            Sample: self.parseYamlSample,
            Composition: self.parseYamlComposition,
            Component: self.parseYamlComponent,
            Components: self.parseYamlComponents,
            list[Element]: self.parseYamlElements,
            DataFiles: self.parseYamlDataFiles
        }
        if type in parsingFuncs.keys():
            return parsingFuncs[type]
        else:
            return None

    def yamlToDict(self, path) -> any:
        # Read the input stream into our attribute.
        with open(path, encoding=self.yaml.encoding) as fp:
            return self.yaml.load(fp)

    def yamlToObject(self, obj: any, yamldict: any) -> any:
        for k, v in yamldict.items():
            self.assignYamlToAttr(obj, k, v)
        return obj

    def assignYamlToAttr(self, obj: any, key, val) -> None:
        if not hasattr(obj, key):
            # If attribute is not valid
            print(
                f"Ignoring depreciated attribute '{key}'"
                f"given to '{type(obj).__name__}'"
            )
            return
        setattr(obj, key, type(obj.__dict__[key])(self.toBuiltin(val)))

    def parseYamlInstrument(self, yamldict: any) -> Instrument:
        instrument = Instrument()
        instrument = self.yamlToObject(instrument, yamldict)
        return instrument

    def parseYamlBeam(self, yamldict: any) -> Normalisation:
        beam = Beam()
        beam = self.yamlToObject(beam, yamldict)
        return beam

    def parseYamlNormalisation(self, yamldict: any) -> Normalisation:
        normalisation = Normalisation()
        for k, v in yamldict.items():
            if k == "composition":
                composition = self.parseYamlComposition(yamldict[k])
                setattr(normalisation, k, composition)
            else:
                self.assignYamlToAttr(normalisation, k, v)
        return normalisation

    def parseYamlSample(self, yamldict: any) -> Sample:
        sample = Sample()
        for k, v in yamldict.items():
            if k == "composition":
                composition = self.parseYamlComposition()
                setattr(sample, k, composition)
            elif k == "containers":
                for contyaml in yamldict[k]:
                    container = self.parseYamlContainer(contyaml)
                    sample.containers.append(container)
            else:
                self.assignYamlToAttr(sample, k, v)
        return sample

    def parseYamlSampleBackground(self, yamldict: any) -> SampleBackground:
        sampleBg = SampleBackground()
        for k, v in yamldict.items():
            if k == "samples":
                for sampleyaml in yamldict[k]:
                    sample = self.parseYamlSample(sampleyaml)
                    sample.name = utils.replace_unwanted_chars(sample.name)
                    sampleBg.samples.append(sample)
            else:
                self.assignYamlToAttr(sampleBg, k, v)

    def parseYamlComposition(self, yamldict: any) -> Composition:
        composition = Composition()
        for k, v in yamldict.items():
            if k == "elements":
                elements = self.parseYamlElements(yamldict[k])
                setattr(composition, k, elements)
            elif k == "weightedComponents":
                weightedComponents = []
                for wc in yamldict[k]:
                    component = self.parseYamlComponent(wc)
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
                self.assignYamlToAttr(composition, k, v)
        return composition

    def parseYamlContainer(self, yamldict: any) -> Container:
        container = Container()
        for k, v in yamldict.items():
            if k == "composition":
                composition = self.parseYamlComposition()
                setattr(container, k, composition)
            else:
                self.assignYamlToAttr(container, k, v)
        return container

    def parseYamlDataFiles(self, yamldict: any) -> DataFiles:
        dataFiles = DataFiles()
        for df in yamldict["_dataFiles"]:
            dataFile = DataFile(df["filename"])
            dataFile = self.yamlToObject(dataFile, df)
            dataFiles.dataFiles.append(dataFile)
        return dataFiles

    def parseYamlComponent(self, yamldict: any) -> Component:
        if (
            "component" not in yamldict
            or "ratio" not in yamldict
        ):
            raise YAMLException(
                "Weighted Component expects 'component' and"
                + " 'ratio' to be provided")
        component = Component()
        self.yamlToObject(
            component, yamldict["component"]
        )
        return component

    def parseYamlComponents(self, yamllist: list[dict]) -> Components:
        components = []
        for c in yamllist:
            components.append(self.parseYamlComponent(c))
        return components

    def parseYamlElements(self, yamllist: list[str]) -> list[Element]:
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

# =================================================================
#                           TXT PARSING
# =================================================================


class TxtParser:
    def __init__(self):
