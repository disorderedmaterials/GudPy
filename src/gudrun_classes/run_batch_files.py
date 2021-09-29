from src.gudrun_classes.gudrun_file import GudrunFile
from src.gudrun_classes.data_files import DataFiles
from copy import deepcopy
import multiprocessing
# class RunBatchFiles():

#     dcs = GudrunFile.dcs
#     purge = GudrunFile.purge
#     write_out = GudrunFile.write_out
#     process = GudrunFile.process

#     def __init__(self, gudrunFile, batchSize, threads=1):
#         self.gudrunFile = deepcopy(gudrunFile)
#         self.batchSize = batchSize
#         self.threads = []
#         self.batches = {}

#     def partition(self):
#         gudrunFile = deepcopy(self.gudrunFile)
#         gudrunFile.sampleBackgrounds = []
#         for sampleBackground in self.gudrunFile.sampleBackgrounds:
#             gudrunFile.sampleBackgrounds.append(deepcopy(sampleBackground))
#             gudrunFile.sampleBackgrounds[-1].samples = []
#             for sample in sampleBackground.samples:
#                 newSample = deepcopy(sample)
#                 for j in range(0, len(sample.dataFiles), self.batchSize):
#                     newSample.dataFiles = DataFiles(sample.dataFiles.dataFiles[j:j+self.batchSize], sample.name)
#                     print(newSample.dataFiles)
#                     print(f"creating batch between {j} and {j+self.batchSize}")
#                     gudrunFile.sampleBackgrounds[-1].samples.append(newSample)
#         gudrunFile.path = gudrunFile.outpath = "gudrun_dcs.dat"
#         gudrunFile.write_out()

# batcher = RunBatchFiles(GudrunFile("tests/TestData/NIMROD-water/water.txt"), 4)
# batcher.partition()


class RunBatchFiles():

    def __init__(self, gudrunFile, batchSize, threaded=True):

        self.gudrunFile = gudrunFile
        self.batchSize = batchSize
        self.stacks = {}
        self.stack = []
        self.maxProcs = multiprocessing.cpu_count()
        # self.maxTasks = self.maxProcs // self.batchSize
        self.run()

    def run(self):
        self.buildStack()
        self.prepareSampleBackgrounds()
        self.process()
    

    def process(self):
        minimalGudrunFile = deepcopy(self.gudrunFile)
        minimalGudrunFile.sampleBackgrounds = []
        pool = multiprocessing.Pool(self.maxProcs)
        for task in self.stack:
            pool.apply_async(task, args=())
        pool.close()
        pool.join()

    def buildStack(self):
        for sampleBackground in self.gudrunFile.sampleBackgrounds:
            self.stacks[sampleBackground] = []
            for sample in sampleBackground.samples:
                for i in range(0, len(sample.dataFiles), self.batchSize):
                    batchedSample = deepcopy(sample)
                    if i+self.batchSize > len(sample.dataFiles):
                        batchedSample.dataFiles = DataFiles(batchedSample.dataFiles.dataFiles[i:], sample.name)
                    else:
                        batchedSample.dataFiles = DataFiles(batchedSample.dataFiles.dataFiles[i:i+self.batchSize], sample.name)
                    self.stacks[sampleBackground].append(batchedSample)
        print("stack built: " + str(self.stacks))
    def prepareSampleBackgrounds(self):
        for sampleBackground, samples in self.stacks.items():
            sampleBackground.samples = samples
            batchedGudrunFile = deepcopy(self.gudrunFile)
            batchedGudrunFile.sampleBackgrounds = [sampleBackground]
            self.stack.append(batchedGudrunFile.dcs)
        print("SBs prepared: " + str(self.stack))


g = GudrunFile("tests/TestData/NIMROD-water/water.txt")
RunBatchFiles(g, 1)