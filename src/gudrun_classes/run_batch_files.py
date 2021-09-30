from src.gudrun_classes.purge_file import PurgeFile
from src.gudrun_classes.gudrun_file import GudrunFile
from src.gudrun_classes.data_files import DataFiles
from copy import deepcopy
import multiprocessing

class RunBatchFiles():

    def __init__(self, gudrunFile, batchSize, threaded=True):

        self.gudrunFile = gudrunFile
        self.batchSize = batchSize
        self.batches = {}
        self.tasks = []
        self.maxProcs = multiprocessing.cpu_count()
        self.run()

    def run(self):
        # Purge detectors.
        (PurgeFile(self.gudrunFile).purge())
        self.batchSamples()
        self.prepareSampleBackgrounds()
        self.process()
    
    @staticmethod
    def result(result):
        print("Received a result!")
        # print(result)

    def process(self):
        minimalGudrunFile = deepcopy(self.gudrunFile)
        minimalGudrunFile.sampleBackgrounds = []
        pool = multiprocessing.Pool(self.maxProcs)
        for task in self.tasks:
            print("Running!!!")
            pool.apply_async(task, kwds={"purge": False}, callback=self.result)
        pool.close()
        pool.join()

    def batchSamples(self):
        for sampleBackground in self.gudrunFile.sampleBackgrounds:
            self.batches[sampleBackground] = []
            for sample in sampleBackground.samples:
                for i in range(0, len(sample.dataFiles), self.batchSize):
                    batchedSample = deepcopy(sample)
                    if i+self.batchSize > len(sample.dataFiles):
                        batchedSample.dataFiles = DataFiles(batchedSample.dataFiles.dataFiles[i:], sample.name)
                    else:
                        batchedSample.dataFiles = DataFiles(batchedSample.dataFiles.dataFiles[i:i+self.batchSize], sample.name)
                        print("created batch: ")
                        print(str(batchedSample.dataFiles))
                        print("*************")
                    self.batches[sampleBackground].append(batchedSample)

    def prepareSampleBackgrounds(self):
        numSamplesInBatch = sum([len(samples) for samples in self.batches.values()])
        if numSamplesInBatch > self.maxProcs:
            numSamplesInBatch //= self.maxProcs
        else:
            numSamplesInBatch = max([len(samples) for samples in self.batches.values()])
        for j, sampleBackground in enumerate(self.batches.keys()):
            batchedSampleBackground = deepcopy(sampleBackground)
            for i in range(0, len(self.batches[sampleBackground]), numSamplesInBatch):
                batchedGudrunFile = deepcopy(self.gudrunFile)
                if len(self.batches[sampleBackground]) > numSamplesInBatch:
                    batchedSampleBackground.samples = self.batches[sampleBackground][i:i+numSamplesInBatch]
                    print(str(batchedSampleBackground.samples))
                else:
                    batchedSampleBackground.samples = self.batches[sampleBackground][i:]
                batchedGudrunFile.sampleBackgrounds = [sampleBackground]
                batchedGudrunFile.outpath = f"gudrun_dcs-{j}-{i}.dat"
                print(batchedGudrunFile.outpath)
                # print("*"*50)
                # print(batchedGudrunFile)
                # print("*"*50)
                self.tasks.append(batchedGudrunFile.process)

g = GudrunFile("tests/TestData/gudpy_good_water.txt")
RunBatchFiles(g, 1) 