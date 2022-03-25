from abc import abstractmethod
from enum import Enum
from ruamel.yaml import YAML as yaml

from src.gudrun_classes.composition import Composition
from src.gudrun_classes.data_files import DataFiles
from src.gudrun_classes.element import Element

from src.gudrun_classes.instrument import Instrument
from src.gudrun_classes.beam import Beam
from src.gudrun_classes.normalisation import Normalisation
from src.gudrun_classes.sample_background import SampleBackground
from src.gudrun_classes.sample import Sample
from src.gudrun_classes.container import Container

class YAML:

    def __init__(self):
        self.yaml = self.getYamlModule()

    def getYamlModule(self):
        yaml_ = yaml()
        yaml_.preserve_quotes = True
        yaml_.default_flow_style = None
        return yaml_

    def parseYaml(self, path):
        return self.constructClasses(self.yamlToDict(path))

    def yamlToDict(self, path):
        with open(path, "r") as fp:
            return self.yaml.load(fp)

    def constructClasses(self, yamldict):
        instrument = Instrument()
        self.maskYAMLtoClass(instrument, yamldict["Instrument"])
        beam = Beam()
        self.maskYAMLtoClass(beam, yamldict["Beam"])
        normalisation = Normalisation()
        self.maskYAMLtoClass(normalisation, yamldict["Normalisation"])

        sampleBackgrounds = []
        for sbyaml in yamldict["SampleBackgrounds"]:
            sampleBackground = SampleBackground()
            self.maskYAMLtoClass(sampleBackground, sbyaml)
            sampleBackgrounds.append(sampleBackground)

        return instrument, beam, normalisation, sampleBackgrounds

    @abstractmethod
    def maskYAMLtoClass(self, cls, yamldict):
        for k,v in yamldict.items():
            if isinstance(cls.__dict__[k], Enum):
                setattr(cls, k, type(cls.__dict__[k])[v])
            elif isinstance(cls.__dict__[k], DataFiles):
                setattr(cls, k, DataFiles(v, cls.__class__.__name__))
            elif isinstance(cls, SampleBackground) and k == "samples":
                for sampleyaml in yamldict[k]:
                    sample = Sample()
                    self.maskYAMLtoClass(sample, sampleyaml)
                    cls.samples.append(sample)
            elif isinstance(cls, Sample) and k == "containers":
                for contyaml in yamldict[k]:
                    container = Container()
                    self.maskYAMLtoClass(container, contyaml)
                    cls.containers.append(container)
            else:
                setattr(cls, k, type(cls.__dict__[k])(v))

    def writeYAML(self, base, path):
        with open(path, "w") as fp:
            outyaml = {
                "Instrument" : base.instrument,
                "Beam" : base.beam,
                "Normalisation" : base.normalisation,
                "SampleBackgrounds" : base.sampleBackgrounds
            }
            self.yaml.dump({k: self.toYaml(v) for k,v in outyaml.items()}, fp)

    @abstractmethod
    def toYaml(self, var):
        if var.__class__.__module__ == "builtins":
            if isinstance(var, (list, tuple)):
                return type(var)([self.toYaml(v) for v in var])
            else:
                return var
        elif isinstance(var, Enum):
            return type(var)(var.value).name
        elif isinstance(var, (Instrument, Beam, Normalisation, SampleBackground, Sample, Container, Composition, Element, DataFiles)):
            return {k : self.toYaml(v) for k,v in var.__dict__.items() if k not in var.yamlignore }