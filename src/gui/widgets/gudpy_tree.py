
from abc import abstractclassmethod
from types import ModuleType
from PyQt5 import QtCore
from PyQt5.QtGui import QResizeEvent, QStandardItemModel, QStandardItem
from PyQt5.QtWidgets import QTreeView, QTreeWidgetItem
from PyQt5.QtCore import QModelIndex, Qt, pyqtSlot
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
        self.clicked.connect(self.click)

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
                sampleItem.setCheckState(Qt.Checked if sample.include else Qt.Unchecked)
                sampleBackgroundItem.appendRow(sampleItem)
                self.map[sample.name] = Attribute(sample.name, sample, sample.__str__, parent=f'Sample Background {i+1}')
                for container in sample.containers:
                    containerItem = QStandardItem(container.name)
                    sampleItem.appendRow(containerItem)
                    self.map[container.name] = Attribute(container.name, container, container.__str__, parent=sample.name)

    def click(self, modelIndex):
        self.parent.stack.setCurrentIndex(self.absoluteIndex(modelIndex))            

    def siblings(self, modelIndex):

        s = []
        sibling = modelIndex.sibling(0,0)
        i = 0
        while sibling.row() != -1:
            if modelIndex.parent() == sibling.parent():
                s.append(sibling)
            i+=1
            sibling = modelIndex.sibling(i,0)
        return s

    def children(self, modelIndex):

        c = []
        child = modelIndex.child(0,0)
        i = 0
        while child.row() != -1:
            if child.parent() == modelIndex:
                c.append(child)
            i+=1
            child = modelIndex.child(i,0)
        return c

    def absoluteIndex(self, modelIndex):
        index = 1
        if modelIndex.parent().row() == -1:
            return modelIndex.row()                
        else:
            siblings = self.siblings(modelIndex)
            for sibling in siblings:
                if sibling.row() < modelIndex.row():
                    index+=1+len(self.children(sibling))
            index+=self.absoluteIndex(modelIndex.parent())
        return index            

    def depth(self, modelIndex, depth):
        row = modelIndex.parent().row()
        if row < 0:
            return depth
        return self.depth(modelIndex.parent(), depth+1)