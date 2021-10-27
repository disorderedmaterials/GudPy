from PySide6.QtCore import QModelIndex, QStringListModel

from src.gudrun_classes.components import Component, Components
from src.gudrun_classes.element import Element

class ComponentSlots():

    def __init__(self, widget, parent):
        self.widget = widget
        self.parent = parent

        self.setupComponentSlots()

    def setComponents(self, components):
        self.components = components
        self.widget.componentList.pair(self.widget.componentCompositionTable, self.components)
        self.loadComponentsList()

    def setupComponentSlots(self):
        self.widget.addComponentButton.clicked.connect(self.addComponent)
        self.widget.removeComponentButton.clicked.connect(self.removeComponent)
        self.widget.addSubcomponentButton.clicked.connect(self.addSubComponent)
        self.widget.removeSubcomponentButton.clicked.connect(self.removeSubComponent)
    
    def loadComponentsList(self):
        self.componentModel = QStringListModel(
            [c.name for c in self.components.components]
        )
        self.widget.componentList.setModel(self.componentModel)
        self.widget.componentList.setCurrentIndex(
            self.widget.componentList.model().index(0, 0, QModelIndex())
        )

    def addComponent(self) : pass
    def removeComponent(self) : pass
    def addSubComponent(self) : pass
    def removeSubComponent(self) : pass