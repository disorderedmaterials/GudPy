from src.gudrun_classes.gud_file import GudFile
import os
import time
from scipy.optimize import minimize, minimize_scalar
import sys
import numpy as np
class CompositionIterator():
    def __init__(self, gudrunFile):
        """
        Constructs all the necessary attributes for the
        SingleParamIterator object.

        Parameters
        ----------
        gudrunFile : GudrunFile
            Input GudrunFile that we will be using for iterating.
        """
        self.gudrunFile = gudrunFile
        self.components = []
        self.ratio = 0

    def setComponent(self, component, ratio=1):
        self.components = [component]
        self.ratio = ratio
    
    def setComponents(self, components, ratio=1):
        self.components = components
        self.ratio = ratio

    def costFunction(self, x):
        if isinstance(x, (list, np.ndarray)):
            x = x[0]
        x = abs(x)
        print(x)
        sys.stdout.flush()
        if len(self.components) == 1:
            for sample in [s for s in self.gudrunFile.sampleBackgrounds[0].samples if s.runThisSample]:
                weightedComponents = [wc for wc in sample.composition.weightedComponents for c in self.components if c == wc.component]
                for component in weightedComponents:
                    component.ratio = x
                sample.composition.translate()
            (self.gudrunFile.process())
            time.sleep(1)
            for sampleBackground in self.gudrunFile.sampleBackgrounds:
                for sample in [s for s in sampleBackground.samples if s.runThisSample]:
                        gudPath = sample.dataFiles.dataFiles[0].replace(
                                    self.gudrunFile.instrument.dataFileType,
                                    "gud"
                                )
                        gudFile = GudFile(
                            os.path.join(
                                self.gudrunFile.instrument.GudrunInputFileDir, gudPath
                            )
                        )
                        print(gudFile.averageLevelMergedDCS, gudFile.expectedDCS, (gudFile.expectedDCS-gudFile.averageLevelMergedDCS)**2)
                        if gudFile.averageLevelMergedDCS == gudFile.expectedDCS:
                            return 0
                        else:
                            return (gudFile.expectedDCS-gudFile.averageLevelMergedDCS)**2
    def iterate(self, n):

        # Nelder-Mead
        result = minimize(self.costFunction, x0=self.ratio, tol=1e-4, method='Nelder-Mead', options={"maxiter":n, "disp":True})
        print(f"final ratio: {result['x']}")
        print(f"Success: {result['success']}")

        # Golden Section Sort
        result = minimize_scalar(self.costFunction, method='Golden', options={"maxiter":n, "disp":2, "xtol": 1})
        print(f"final ratio: {result['x']}")
        print(f"Success: {result['success']}")