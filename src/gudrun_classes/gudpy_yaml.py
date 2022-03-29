from abc import abstractmethod
from enum import Enum
from ruamel.yaml import YAML as yaml
import os
import pathlib

from src.gudrun_classes.composition import (
    Component, Components, Composition, WeightedComponent
)
from src.gudrun_classes.data_files import DataFiles
from src.gudrun_classes.element import Element
from src.gudrun_classes.gui_config import GUIConfig

from src.gudrun_classes.instrument import Instrument
from src.gudrun_classes.beam import Beam
from src.gudrun_classes.normalisation import Normalisation
from src.gudrun_classes.sample_background import SampleBackground
from src.gudrun_classes.sample import Sample
from src.gudrun_classes.container import Container
from src.gudrun_classes import config


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
        with open(path, "r") as fp:
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
                setattr(cls, k, type(cls.__dict__[k])(v))

    def maskYAMLSeqtoClss(self, cls, yamlseq):
        if isinstance(cls, Components):
            components = []
            for component in yamlseq:
                component_ = Component()
                self.maskYAMLDicttoClass(component_, component)
                components.append(component_)
            setattr(cls, "components", components)

    def writeYAML(self, base, path):
        with open(path, "wb", encoding='utf-8') as fp:
            outyaml = {
                "Instrument": base.instrument,
                "Beam": base.beam,
                "Components": config.components.components,
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
