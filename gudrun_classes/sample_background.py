from inspect import cleandoc
from data_files import DataFiles

from utils import *

class SampleBackground:
    def __init__(self):
        self.numberOfFilesPeriodNumber = (0,0)
        self.dataFiles = DataFiles([], 'SAMPLE BACKGROUND')
    
    def __str__(self):
        return cleandoc("""
SAMPLE BACKGROUND        {{

{}        Number of files and period number
{}

}}

        """.format(
            spacify(self.numberOfFilesPeriodNumber),
            str(self.dataFiles)
        ))