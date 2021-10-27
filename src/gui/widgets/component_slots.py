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
        # self.widget.componentList.pair(self.widget.componentCompositionTable, self.components)
        self.loadComponentsList()

    def setupComponentSlots(self):
        self.widget.addComponentButton.clicked.connect(self.widget.componentList.insertComponent)
        self.widget.removeComponentButton.clicked.connect(self.widget.componentList.removeComponent)
        self.widget.addSubcomponentButton.clicked.connect(self.addSubComponent)
        self.widget.removeSubcomponentButton.clicked.connect(self.removeSubComponent)
    
    def loadComponentsList(self):
        component = Component("H2O")
        component.addElement(Element("H", 0, 2.))
        self.components.addComponent(component)
        self.widget.componentList.makeModel(self.components,self.widget.componentCompositionTable )



    def addSubComponent(self):
        self.widget.componentCompositionTable.model().insertRow(
            Element("", 0, 0.), self.widget.componentList.currentIndex()
        )

    def removeComponent(self):
        self.widget.componentList.removeRow(
            self.widget.componentList
            .selectionModel().selectedRows()
        )

    def removeSubComponent(self):
        self.widget.componentCompositionTable.model().removeRow(
            self.widget.componentCompositionTable
            .currentIndex()
        )