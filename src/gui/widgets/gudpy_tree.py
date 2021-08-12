
from PyQt5 import QtCore
from PyQt5.QtGui import QResizeEvent, QStandardItemModel, QStandardItem
from PyQt5.QtWidgets import QTreeView
from PyQt5.QtCore import Qt, pyqtSlot
# from PyQt5.QtCore import ItemIsUserCheckable
from widgets.attribute import Attribute


class GudPyTreeView(QTreeView):
    def __init__(self, parent, gudrunFile):
        super(GudPyTreeView, self).__init__(parent)

        self.gudrunFile = gudrunFile
        self.parent = parent

        self.model = QStandardItemModel()
        self.map = {}

        self.makeModel()
        self.setModel(self.model)
        self.setHeaderHidden(True)

    def makeModel(self):

        root = self.model.invisibleRootItem()
        instrumentItem = QStandardItem("Instrument")
        instrumentItem.setEditable(False)
        self.map["Instrument"] = Attribute("Instrument", self.gudrunFile.instrument, self.gudrunFile.instrument.__str__)
        beamItem = QStandardItem("Beam")
        beamItem.setEditable(False)
        self.map["Beam"] = Attribute("Beam", self.gudrunFile.beam, self.gudrunFile.beam.__str__)
        normalistionItem = QStandardItem("Normalisation")
        normalistionItem.setEditable(False)
        self.map["Normalisation"] = Attribute("Normalisation", self.gudrunFile.normalisation, self.gudrunFile.normalisation.__str__)
        root.appendRow(instrumentItem)
        root.appendRow(beamItem)
        root.appendRow(normalistionItem)

        for i, sampleBackground in enumerate(self.gudrunFile.sampleBackgrounds):
            sampleBackgroundItem = QStandardItem(f'Sample Background {i+1}')
            sampleBackgroundItem.setEditable(False)
            root.appendRow(sampleBackgroundItem)
            self.map[f'Sample Background {i+1}'] = Attribute(f'Sample Background {i+1}', sampleBackground, sampleBackground.__str__)
            for sample in sampleBackground.samples:
                sampleItem = QStandardItem(sample.name)
                sampleItem.setCheckable(True)
                sampleItem.setFlags(sampleItem.flags() | Qt.ItemIsUserCheckable)
                sampleItem.setCheckState(Qt.Unchecked)
                sampleBackgroundItem.appendRow(sampleItem)
                self.map[sample.name] = Attribute(sample.name, sample, sample.__str__, parent=f'Sample Background {i+1}')
                for container in sample.containers:
                    containerItem = QStandardItem(container.name)
                    sampleItem.appendRow(containerItem)
                    self.map[container.name] = Attribute(container.name, container, container.__str__, parent=sample.name)