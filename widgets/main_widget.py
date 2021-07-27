from PyQt5.QtWidgets import QVBoxLayout, QWidget

from sidebar import GudPySiderbar


class MainWidget(QWidget):

    def __init__(self, parent, gudrunFile):

        self.parent = parent
        self.gudrunFile = gudrunFile

        super().__init__(self.parent)

        self.layout = QVBoxLayout(self)

        tabs = [key.upper() for key in self.gudrunFile.__dict__.keys()
                if not key == 'path' and not key == 'sample']
        for sample in self.gudrunFile.samples:
            tabs.append('SAMPLE BACKGROUND')
            tabs.append(sample.name)
            for container in sample.containers:
                tabs.append(container.name)

        self.layout.addWidget(GudPySiderbar(self, tabs))
