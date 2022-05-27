from copy import deepcopy
import os

class BatchProcessor():

    def __init__(self, gudrunFile):
        self.gudrunFile = gudrunFile
    
    def batch(self, batchSize=1):
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

    def process(self, batchSize=1, headless=True):
        batches = self.batch(batchSize=batchSize)
        if headless:
            for i, batch in enumerate(batches):
                batch.process()
                batch.iterativeOrganise(f"Batch_{i*batchSize}-{(i+1)*batchSize}")
        else:
            tasks = []
            for i, batch in enumerate(batches):
                tasks.append(
                    [
                        batch.dcs(
                            path=os.path.join(
                                batch.instrument.GudrunInputFileDirectory,
                                "gudpy.txt"
                            ),
                            headless=False
                        ),
                        [
                            batch.iterativeOrganise,
                            [
                                f"Batch_{i*batchSize}-{(i+1)*batchSize}",
                            ]
                        ]
                        
                    ]
                )
            return tasks