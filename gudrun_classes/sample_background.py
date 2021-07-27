from inspect import cleandoc

try:
    from utils import spacify
    from data_files import DataFiles
except ModuleNotFoundError:
    from scripts.utils import spacify
    from gudrun_classes.data_files import DataFiles


class SampleBackground:
    def __init__(self):
        self.numberOfFilesPeriodNumber = (0, 0)
        self.dataFiles = DataFiles([], "SAMPLE BACKGROUND")
        self.samples = []

    def __str__(self):

        SAMPLES = "\n".join([str(x) for x in self.samples])

        return cleandoc(
            """
SAMPLE BACKGROUND          {{

{}        Number of files and period number
{}

}}

{}        """.format(
                spacify(self.numberOfFilesPeriodNumber),
                str(self.dataFiles),
                SAMPLES,
            )
        )
