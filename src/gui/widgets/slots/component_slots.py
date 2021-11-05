from src.gudrun_classes import config
from src.gudrun_classes.element import Element


class ComponentSlots():

    def __init__(self, widget, parent):
        self.widget = widget
        self.parent = parent

        self.setupComponentSlots()

    def setComponents(self, components):
        self.components = components
        self.loadComponentsList()

    def setupComponentSlots(self):
        self.widget.addComponentButton.clicked.connect(
            self.widget.componentList.insertComponent
        )
        self.widget.removeComponentButton.clicked.connect(
            self.widget.componentList.removeComponent
        )
        self.widget.addSubcomponentButton.clicked.connect(
            self.addSubComponent
        )
        self.widget.removeSubcomponentButton.clicked.connect(
            self.removeSubComponent
        )
        self.widget.useComponentsCheckBox.stateChanged.connect(
            self.setUseComponentDefinitions
        )
        self.widget.normaliseCompositionsCheckBox.stateChanged.connect(
            self.toggleNormaliseCompositions
        )

    def loadComponentsList(self):
        self.widget.componentList.makeModel(
            self.components, self.widget.componentCompositionTable
        )

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

    def setUseComponentDefinitions(self, state):
        config.USE_USER_DEFINED_COMPONENTS = bool(state)
        self.widget.normaliseCompositionsCheckBox.setEnabled(bool(state))

    def toggleNormaliseCompositions(self, state):
        config.NORMALISE_COMPOSITIONS = bool(state)
