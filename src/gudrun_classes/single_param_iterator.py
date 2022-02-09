from src.gudrun_classes.gud_file import GudFile
import os
import time


class SingleParamIterator():

    def __init__(self, gudrunFile):
        self.gudrunFile = gudrunFile
    
    def performIteration(self, _n):

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
                    coefficient = gudFile.averageLevelMergedDCS / gudFile.expectedDCS
                    self.applyCoefficientToAttribute(sample, coefficient)
    
    def applyCoefficientToAttribute(self, object, coefficient):
        pass

    def iterate(self, n):
        for i in range(n):
            self.gudrunFile.process()
            time.sleep(1)
            self.performIteration(i)