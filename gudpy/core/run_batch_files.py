from abc import abstractclassmethod
from copy import deepcopy
from enum import Enum

class BatchProcessor():

    def __init__(self, gudrunFile):
        self.gudrunFile = gudrunFile
    
    def batch(self, batchSize):
        batches = []
        
        for i, sampleBackground in enumerate(self.gudrunFile.sampleBackgrounds):
            gudrunFile = deepcopy(self.gudrunFile)
            batchedSampleBackground = deepcopy(sampleBackground)
            batchedSampleBackground.samples = []
            for sample in sampleBackground.samples:
                batchedSample = deepcopy(sample)
                batch = sample.dataFiles[i*batchSize:(i+1)*batchSize]
                batchedSample.dataFiles.dataFiles = batch
                batchedSampleBackground.samples.append(batchedSample)
            gudrunFile.sampleBackgrounds = []
            batches.append(gudrunFile)
        
        return gudrunFile

    @abstractclassmethod
    def createTasks(self, batchSize, headless, iterationMode)

    def process(self, maintainAverage=False, batchSize=1, headless=True, iterationMode=IterationModes.NONE, rtol=10.0):
        batches = self.batch(batchSize=batchSize)
        tasks = []
        """
        Run Gudrun on batchSize files at a time.
        If an iteration mode is specified, then iterate using that mode until convergence (do this at each batch).
        Otherwise, a single run of gudrun is sufficient.
        Start out by targeting a single sample (the first one)
        """