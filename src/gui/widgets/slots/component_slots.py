from enum import Flag
from PySide6.QtCore import QModelIndex, Qt
from PySide6.QtWidgets import QDialogButtonBox, QMessageBox
from src.gudrun_classes import config
from src.gudrun_classes.element import Element
from src.gui.widgets.dialogs.composition_dialog import CompositionDialog
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

    def loadComponentsList(self):
        self.widget.componentList.makeModel(
            self.components, self.widget.componentCompositionTable
        )
        self.widget.componentCompositionTable.model().dataChanged.connect(
            self.handleDataChanged
        )

    def handleDataChanged(self, index, _):
        component = index.internalPointer()
        compositionDialog = CompositionDialog(self.widget, component)
        result = compositionDialog.widget.exec()
        if result:
            component.parse()
        self.loadComponentsList()

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
