from abc import abstractmethod
from enum import Enum
from ruamel.yaml import YAML as yaml
from ruamel.yaml import YAMLError
import os

from core.composition import (
    Component, Components, Composition, WeightedComponent
)
from core.data_files import DataFiles
from core.element import Element
from core.exception import YAMLException
from core.gui_config import GUIConfig

from core.instrument import Instrument
from core.beam import Beam
from core.normalisation import Normalisation
from core.sample_background import SampleBackground
from core.sample import Sample
from core.container import Container
from core import config


class YAML:

    def __init__(self):
        self.yaml = self.getYamlModule()

    def getYamlModule(self):
        yaml_ = yaml()
        yaml_.preserve_quotes = True
        yaml_.default_flow_style = None
        yaml_.encoding = 'utf-8'
        return yaml_

    def parseYaml(self, path):
        self.path = path
        try:
            parsedYAML = self.constructClasses(self.yamlToDict(path))
        except YAMLError:
            # Exception caused by yaml parsing library
            raise YAMLException("Invalid YAML file")
        except YAMLException as e:
            # Exception caused by invalid arguments
            raise YAMLException(e)
        else:
            return parsedYAML

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

        beam = Beam()
        if "Beam" in yamldict:
            self.maskYAMLDicttoClass(beam, yamldict["Beam"])

        components = Components()
        if "Components" in yamldict:
            self.maskYAMLSeqtoClass(components, yamldict["Components"])

        normalisation = Normalisation()
        if "Normalisation" in yamldict:
            self.maskYAMLDicttoClass(normalisation, yamldict["Normalisation"])

        sampleBackgrounds = []
        if "SampleBackgrounds" in yamldict:
            for sbyaml in yamldict["SampleBackgrounds"]:
                sampleBackground = SampleBackground()
                self.maskYAMLDicttoClass(sampleBackground, sbyaml)
                sampleBackgrounds.append(sampleBackground)

        GUI = GUIConfig()
        if "GUI" in yamldict:
            self.maskYAMLDicttoClass(GUI, yamldict["GUI"])

        return (
            instrument, beam, components,
            normalisation, sampleBackgrounds, GUI
        )

    @abstractmethod
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
                    (Component, Composition)
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

            elif isinstance(cls, Composition) and k == "weightedComponents":
                weightedComponents = []
                for weightedComponent in v:
                    if (
                        "component" not in weightedComponent
                        or "ratio" not in weightedComponent
                    ):
                        raise YAMLException(
                            "Weighted Component expects 'component' and"
                            + " 'ratio' to be provided")
                    component = Component()
                    self.maskYAMLDicttoClass(
                        component, weightedComponent["component"]
                    )
                    ratio = weightedComponent["ratio"]
                    try:
                        weightedComponents.append(
                            WeightedComponent(
                                component, float(ratio))
                        )
                    except ValueError:
                        raise YAMLException(
                            "Invalid ratio given to Weighted Component")
                setattr(cls, k, weightedComponents)

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
                    cls.samples.append(sample)

            elif isinstance(cls, Sample) and k == "containers":
                for contyaml in yamldict[k]:
                    container = Container()
                    self.maskYAMLDicttoClass(container, contyaml)
                    cls.containers.append(container)

            else:
                setattr(cls, k, type(cls.__dict__[k])(self.toBuiltin(v)))

    def maskYAMLSeqtoClss(self, cls, yamlseq):
        if isinstance(cls, Components):
            components = []
            for component in yamlseq:
                component_ = Component()
                self.maskYAMLDicttoClass(component_, component)
                components.append(component_)
            setattr(cls, "components", components)

    def writeYAML(self, base, path):
        with open(path, "wb") as fp:
            outyaml = {
                "Instrument": base.instrument,
                "Beam": base.beam,
                "Components": base.components.components,
                "Normalisation": base.normalisation,
                "SampleBackgrounds": base.sampleBackgrounds,
                "GUI": config.GUI
            }
            self.yaml.dump(
                {k: self.toYaml(v) for k, v in outyaml.items()},
                fp
            )

    @abstractmethod
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
            Instrument, Beam, Components, Normalisation,
            SampleBackground, Sample, Container, WeightedComponent,
            Component, Composition, Element, DataFiles, GUIConfig
        )):
            return {
                k: self.toYaml(v)
                for k, v in var.__dict__.items()
                if k not in var.yamlignore
            }

    @abstractmethod
    def toBuiltin(self, yamlvar):
        if isinstance(yamlvar, (list, tuple)):
            return [self.toBuiltin(v) for v in yamlvar]
        elif yamlvar.__class__.__module__ == "builtins":
            return yamlvar
        elif yamlvar.__class__.__module__ == "ruamel.yaml.scalarfloat":
            return float(yamlvar)
        elif yamlvar.__class__.__module__ == "ruamel.yaml.scalarstring":
            return str(yamlvar)
