from PySide6.QtWidgets import QMessageBox
from src.gudrun_classes import config
from src.gudrun_classes.element import Element
from src.gudrun_classes.exception import ChemicalFormulaParserException
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
        self.widget.normaliseCompositionsCheckBox.stateChanged.connect(
            self.toggleNormaliseCompositions
        )
        self.widget.duplicateButton.clicked.connect(
            self.duplicateComponent
        )

    def loadComponentsList(self):
        self.widget.componentList.makeModel(
            self.components, self.widget.componentCompositionTable
        )
        self.widget.componentList.model().dataChanged.connect(
            self.handleDataChanged
        )

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
        except ChemicalFormulaParserException as cfpm:
            QMessageBox.warning(
                self.widget, "GudPy Warning",
                str(cfpm)
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

    def duplicateComponent(self):
        self.widget.componentList.duplicate()
