from abc import abstractmethod
from enum import Enum
from ruamel.yaml import YAML as yaml
import os

from core.composition import (
    Component, Components, Composition, WeightedComponent
)
from core.data_files import DataFiles
from core.element import Element
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
        return self.constructClasses(self.yamlToDict(path))

    def yamlToDict(self, path):
        # Decide the encoding
        import chardet
        with open(path, 'rb') as fp:
            encoding = chardet.detect(fp.read())['encoding']

        # Read the input stream into our attribute.
        with open(path, encoding=encoding) as fp:
            return self.yaml.load(fp)

    def constructClasses(self, yamldict):
        instrument = Instrument()
        self.maskYAMLDicttoClass(instrument, yamldict["Instrument"])
        instrument.GudrunInputFileDir = os.path.dirname(
            os.path.abspath(
                self.path
            )
        )
        beam = Beam()
        self.maskYAMLDicttoClass(beam, yamldict["Beam"])
        components = Components()
        self.maskYAMLSeqtoClss(components, yamldict["Components"])
        normalisation = Normalisation()
        self.maskYAMLDicttoClass(normalisation, yamldict["Normalisation"])
        sampleBackgrounds = []
        for sbyaml in yamldict["SampleBackgrounds"]:
            sampleBackground = SampleBackground()
            self.maskYAMLDicttoClass(sampleBackground, sbyaml)
            sampleBackgrounds.append(sampleBackground)

        GUI = GUIConfig()
        self.maskYAMLDicttoClass(GUI, yamldict["GUI"])


        return (
            instrument, beam, components,
            normalisation, sampleBackgrounds, GUI
        )

    @abstractmethod
    def maskYAMLDicttoClass(self, cls, yamldict):
        for k, v in yamldict.items():
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
                for element in v:
                    element_ = Element(
                        **{
                            "atomicSymbol": element["atomicSymbol"],
                            "massNo": float(element["massNo"]),
                            "abundance": float(element["abundance"])
                        }
                    )
                    elements.append(element_)
                setattr(cls, k, elements)
            elif isinstance(cls, Composition) and k == "weightedComponents":
                weightedComponents = []
                for weightedComponent in v:
                    component = Component()
                    self.maskYAMLDicttoClass(
                        component, weightedComponent["component"]
                    )
                    ratio = weightedComponent["ratio"]
                    weightedComponents.append(
                        WeightedComponent(
                            component, float(ratio))
                    )
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
