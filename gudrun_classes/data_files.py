class DataFiles:
    def __init__(self, dataFiles, name):
        self.dataFiles = dataFiles
        self.name = name
        self.str = [df + '        ' + name + ' data files' for df in dataFiles]

    def __str__(self):
        return ("""\n""".join(self.str))
