#!/usr/bin/env python3
from core.run_batch_files import BatchProcessor
from core.gudrun_file import GudrunFile
from core.enums import IterationModes
g = GudrunFile("test/TestData/NIMROD-water/water.txt")
bproc = BatchProcessor(g)
bproc.process(batchSize=2, iterationMode=IterationModes.TWEAK_FACTOR, rtol=0.0, maxIterations=5)