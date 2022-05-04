from PySide6.QtWidgets import QMessageBox

from gui.widgets.dialogs.composition_dialog import CompositionDialog
from core import config
from core.element import Element
from core.exception import ChemicalFormulaParserException


class ComponentSlots():

    def __init__(self, widget, parent):
        self.widget = widget
        self.parent = parent
        self.widgetsRefreshing = False
        self.setupComponentSlots()
        self.widget.useComponentsCheckBox.setChecked(config.GUI.useComponents)

    def setComponents(self, components):
        self.components = components
        self.loadComponentsList()

    def setupComponentSlots(self):
        self.widgetsRefreshing = True
        self.widget.addComponentButton.clicked.connect(
            self.insertComponent
        )
        self.widget.removeComponentButton.clicked.connect(
            self.removeComponent
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
        self.widget.duplicateButton.clicked.connect(
            self.duplicateComponent
        )
        self.widgetsRefreshing = False

    def loadComponentsList(self):
        self.widget.componentList.makeModel(
            self.components, self.widget.componentCompositionTable
        )
        self.widget.componentList.model().dataChanged.connect(
            self.handleDataChanged
        )

        self.setComponentsActionsEnabled(self.components.count())
        self.setSubComponentsEnabled(self.components.count())

    def handleDataChanged(self, index, _):
        component = index.internalPointer()
        try:
            if component.parse(persistent=False):
                compositionDialog = CompositionDialog(self.widget, component)
                result = compositionDialog.widget.exec()
                if result:
                    component.parse()
                row = index.row()
                self.loadComponentsList()
                self.widget.componentList.setCurrentIndex(
                    self.widget.componentList.model().index(
                        row, 0
                    )
                )
            if not self.widgetsRefreshing:
                self.parent.setModified()
        except ChemicalFormulaParserException as cfpm:
            QMessageBox.warning(
                self.widget, "GudPy Warning",
                str(cfpm)
            )

    def addSubComponent(self):
        self.widget.componentCompositionTable.model().insertRow(
            Element("", 0, 0.), self.widget.componentList.currentIndex()
        )
        if not self.widgetsRefreshing:
            self.parent.setModified()

    def insertComponent(self):
        self.widget.componentList.insertComponent()
        self.setSubComponentsEnabled(self.components.count())
        self.setComponentsActionsEnabled(self.components.count())

    def removeComponent(self):
        self.widget.componentList.removeComponent()
        if not self.widgetsRefreshing:
            self.parent.setModified()
        self.setSubComponentsEnabled(self.components.count())
        self.setComponentsActionsEnabled(self.components.count())

    def removeSubComponent(self):
        self.widget.componentCompositionTable.model().removeRow(
            self.widget.componentCompositionTable
            .currentIndex()
        )
        if not self.widgetsRefreshing:
            self.parent.setModified()

    def setUseComponentDefinitions(self, state):
        config.USE_USER_DEFINED_COMPONENTS = bool(state)
        self.widget.normaliseCompositionsCheckBox.setEnabled(bool(state))

    def toggleNormaliseCompositions(self, state):
        config.NORMALISE_COMPOSITIONS = bool(state)

    def duplicateComponent(self):
        self.widget.componentList.duplicate()
        if not self.widgetsRefreshing:
            self.parent.setModified()

    def setSubComponentsEnabled(self, enabled):
        self.widget.addSubcomponentButton.setEnabled(enabled)
        self.widget.removeSubcomponentButton.setEnabled(enabled)
        self.widget.componentCompositionTable.setEnabled(enabled)
    
    def setComponentsActionsEnabled(self, enabled):
        self.widget.removeComponentButton.setEnabled(enabled)
        self.widget.duplicateButton.setEnabled(enabled)