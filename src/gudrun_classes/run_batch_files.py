from src.gudrun_classes.gudrun_file import GudrunFile
from src.gudrun_classes.data_files import DataFiles
from copy import deepcopy
class RunBatchFiles():

    dcs = GudrunFile.dcs
    purge = GudrunFile.purge
    write_out = GudrunFile.write_out
    process = GudrunFile.process

    def __init__(self, gudrunFile, batchSize, threads=1):
        self.gudrunFile = deepcopy(gudrunFile)
        self.batchSize = batchSize
        self.threads = []
        self.batches = {}

    def partition(self):
        gudrunFile = deepcopy(self.gudrunFile)
        gudrunFile.sampleBackgrounds = []
        for sampleBackground in self.gudrunFile.sampleBackgrounds:
            gudrunFile.sampleBackgrounds.append(deepcopy(sampleBackground))
            gudrunFile.sampleBackgrounds[-1].samples = []
            for sample in sampleBackground.samples:
                newSample = deepcopy(sample)
                for j in range(0, len(sample.dataFiles), self.batchSize):
                    newSample.dataFiles = DataFiles(sample.dataFiles.dataFiles[j:j+self.batchSize], sample.name)
                    print(newSample.dataFiles)
                    print(f"creating batch between {j} and {j+self.batchSize}")
                    gudrunFile.sampleBackgrounds[-1].samples.append(newSample)
        gudrunFile.path = gudrunFile.outpath = "gudrun_dcs.dat"
        gudrunFile.write_out()

batcher = RunBatchFiles(GudrunFile("tests/TestData/NIMROD-water/water.txt"), 4)
batcher.partition()