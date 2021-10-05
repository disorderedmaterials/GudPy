from src.gudrun_classes.purge_file import PurgeFile
from src.gudrun_classes.gudrun_file import GudrunFile
from src.gudrun_classes.data_files import DataFiles
from copy import deepcopy
import multiprocessing

class RunBatchFiles():
    """
    Class for running data files in batches.
    ...

    Attributes
    ----------
    gudrunFile : GudrunFile
        GudrunFile to create new instance from, for running
        data files individually.
    batchSize : int
        Size to use for batching
    threaded : bool
        Should threading be used?
    batches : dict
        Dictionary of batches.
    tasks : function[]
        List of functions to run.
    maxProcs : int
        Maximum number of paralell processes.
    Methods
    -------
    run()
        Runs the batch processing routine.
    process()
        Performs the batch processing routine.
    batchSamples()
        Creates batches.
    prepareTasks()
        Prepares tasks for execution.
    """
    def __init__(self, gudrunFile, batchSize, threaded=True):
        """
        Constructs all the necessary attributes for the RunBatchFiles object.
        Then runs the batch processing routine.

        Parameters
        ----------
        gudrunFile : GudrunFile
            GudrunFile object to perform batch processing on.
        batchSize : int
            Batch size to use.
        threaded : bool, optional
            Should threading be used?
        """
        self.gudrunFile = gudrunFile
        self.batchSize = batchSize
        self.batches = {}
        self.tasks = []
        self.threaded = threaded
        self.maxProcs = multiprocessing.cpu_count()
        self.run()

    def run(self):
        """
        Run the batch processing routine.
        Purges detectors, then batches samples,
        and prepares the tasks,
        then runs the batch processing routine.
        """
        # Purge detectors.
        PurgeFile(self.gudrunFile).purge()
        # Batch samples.
        self.batchSamples()
        # Prepare the tasks.
        self.prepareTasks()
        # Run batch processing routine.
        self.process()

    def process(self):
        """
        Performs the batch processing routine.
        Creates a pool, and then adds all of the tasks to it,
        if threading is being used.
        """
        # Threaded
        if self.threaded:
            # Create the pool.
            pool = multiprocessing.Pool(self.maxProcs)
            # Add the tasks
            for task in self.tasks:
                pool.apply_async(task, kwds={"purge": False})
            pool.close()
            # Wait for it to finish.
            pool.join()
        else:
            # Sequentially execute tasks.
            for task in self.tasks:
                task()

    def batchSamples(self):
        """
        Splits the samples into batches.
        """
        # Iterate through sample backgrounds.
        for sampleBackground in self.gudrunFile.sampleBackgrounds:
            # Add the sample background as a key to the dict.
            self.batches[sampleBackground] = []
            # Iterate through samples.
            for sample in sampleBackground.samples:
                # Iterate through data files, incremementing by batch size.
                for i in range(0, len(sample.dataFiles), self.batchSize):
                    batchedSample = deepcopy(sample)
                    if i+self.batchSize > len(sample.dataFiles):
                        # If a full batch is not available,
                        # use all the remaining data files.
                        batchedSample.dataFiles = DataFiles(batchedSample.dataFiles.dataFiles[i:], sample.name)
                    else:
                        # Create a batch.
                        batchedSample.dataFiles = DataFiles(batchedSample.dataFiles.dataFiles[i:i+self.batchSize], sample.name)
                    # Add the batch to the sample background in the dict.
                    self.batches[sampleBackground].append(batchedSample)

    def prepareTasks(self):
        """
        Prepares the tasks to be run.
        """
        # Calculate number of samples per batch of samples.
        # Count the existing batches.
        numSamplesInBatch = sum([len(samples) for samples in self.batches.values()])
        # If we have too many batches for the number of processes available,
        # then floor divide by the number of processes.
        # otherwise, the number of samples per batch is set
        # to the size of the largest batch of samples.
        if numSamplesInBatch > self.maxProcs:
            numSamplesInBatch //= self.maxProcs
        else:
            numSamplesInBatch = max([len(samples) for samples in self.batches.values()])
        # Enumerate through sample backgrounds in the dict.
        for j, sampleBackground in enumerate(self.batches.keys()):
            batchedSampleBackground = deepcopy(sampleBackground)
            # Iterate through batches associated with the sample background
            # incrementing by the number of samples per bathc.
            for i in range(0, len(self.batches[sampleBackground]), numSamplesInBatch):
                batchedGudrunFile = deepcopy(self.gudrunFile)
                if len(self.batches[sampleBackground]) > numSamplesInBatch:
                    # Create a batch of batches.
                    batchedSampleBackground.samples = self.batches[sampleBackground][i:i+numSamplesInBatch]
                else:
                    # If there aren't enough batches left,
                    # then use all the remaining.
                    batchedSampleBackground.samples = self.batches[sampleBackground][i:]
                # Construct the batched GudrunFile.
                batchedGudrunFile.sampleBackgrounds = [sampleBackground]
                # Set the outpath, to avoid race conditions / locks.
                batchedGudrunFile.outpath = f"gudrun_dcs-{j}-{i}.dat"
                # Append the task
                self.tasks.append(batchedGudrunFile.process)
