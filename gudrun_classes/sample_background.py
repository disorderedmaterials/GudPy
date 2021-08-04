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
        TAB = "          "
        SAMPLES = "\n".join([str(x) for x in self.samples if x.runThisSample])

        dataFilesLine = (
            f'{str(self.dataFiles)}\n'
            if len(self.dataFiles.dataFiles) > 0
            else
            ''
        )

        return (
            f'\nSAMPLE BACKGROUND{TAB}{{\n\n'
            f'{spacify(self.numberOfFilesPeriodNumber)}{TAB}'
            f'Number of files and period number\n'
            f'{dataFilesLine}\n\n'
            f'}}\n\n'
            f'{SAMPLES}'

        )
