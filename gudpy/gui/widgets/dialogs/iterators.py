import os
import sys
from PySide6.QtWidgets import QDialog
from PySide6.QtCore import QFile, Qt
from PySide6.QtUiTools import QUiLoader

from core.enums import Geometry
from core import config
from core import iterators


class IterationDialog(QDialog):

    def __init__(self, name, iteratorType, parent):
        super(IterationDialog, self).__init__(parent=parent)
        self.numberIterations = 1
        self.name = name
        self.iteratorType = iteratorType
        self.text = ""
        self.loadUI()
        self.initComponents()
        self.params = {}

    def initComponents(self):
        self.widget.numberIterationsSpinBox.valueChanged.connect(
            self.numberIterationsChanged
        )

        self.widget.iterateButton.clicked.connect(
            self.iterate
        )

    def loadUI(self):
        """
        Loads the UI file for the IterationDialog object.
        """
        if hasattr(sys, '_MEIPASS'):
            uifile = QFile(
                os.path.join(
                    sys._MEIPASS, "ui_files", f"{self.name}.ui"
                )
            )
        else:
            current_dir = os.path.dirname(os.path.realpath(__file__))
            uifile = QFile(
                os.path.join(
                    current_dir, "..", "ui_files", f"{self.name}.ui"
                )
            )
        loader = QUiLoader()
        self.widget = loader.load(uifile)

    def iterate(self):
        self.widget.close()
        self.params = {
            "nTotal": self.numberIterations
        }

    def numberIterationsChanged(self, value):
        self.numberIterations = value


class DensityIterationDialog(IterationDialog):
    def __init__(self, parent, _):
        super().__init__(
            name="iterateDensityDialog",
            iteratorType=iterators.Density,
            parent=parent
        )


class InelasticitySubtractionIterationDialog(IterationDialog):
    def __init__(self, parent, _):
        super().__init__(
            name="iterateInelasticitySubtractionsDialog",
            iteratorType=iterators.InelasticitySubtraction,
            parent=parent
        )


class RadiusIterationDialog(IterationDialog):
    def __init__(self, parent, _):
        super().__init__(
            name="IterateRadiusDialog",
            iteratorType=iterators.Radius,
            parent=parent
        )

    def initComponents(self):
        super().initComponents()
        self.widget.iterateButton.setEnabled(
            config.geometry == Geometry.CYLINDRICAL
        )

    def iterate(self):
        self.widget.close()
        return {
            "nTotal": self.numberIterations,
        }


class ThicknessIterationDialog(IterationDialog):
    def __init__(self, parent, _):
        super().__init__(
            name="IterateThicknessDialog",
            iteratorType=iterators.Thickness,
            parent=parent
        )

    def initComponents(self):
        super().initComponents()
        self.widget.iterateButton.setEnabled(
            config.geometry == Geometry.FLATPLATE
        )


class TweakFactorIterationDialog(IterationDialog):
    def __init__(self, parent, _):
        super().__init__(
            name="iterateTweakFactorDialog",
            iteratorType=iterators.TweakFactor,
            parent=parent
        )


class CompositionIterationDialog(IterationDialog):
    def __init__(self, parent, gudrunFile):
        self.gudrunFile = gudrunFile
        self.components = [None, None]
        self.rtol = 0.
        self.mode = iterators.Composition.Mode.SINGLE
        super().__init__(
            name="IterateCompositionDialog",
            iteratorType=iterators.Composition,
            parent=parent
        )

    def loadFirstComponentsComboBox(self):
        self.widget.firstComponentComboBox.clear()
        for component in self.gudrunFile.components.components:
            self.widget.firstComponentComboBox.addItem(
                component.name, component
            )
        self.components[0] = self.gudrunFile.components.components[0]

    def loadSecondComponentsComboBox(self):
        self.widget.secondComponentComboBox.clear()
        for component in self.gudrunFile.components.components:
            self.widget.secondComponentComboBox.addItem(
                component.name, component
            )

    def firstComponentChanged(self, index):
        self.components[0] = self.widget.firstComponentComboBox.itemData(index)
        other = self.widget.secondComponentComboBox.model().item(index)
        self.setItemDisabled(
            self.widget.secondComponentComboBox,
            other
        )

    def secondComponentChanged(self, index):
        self.components[1] = (
            self.widget.secondComponentComboBox.itemData(index)
        )
        other = self.widget.firstComponentComboBox.model().item(index)
        self.setItemDisabled(
            self.widget.firstComponentComboBox,
            other
        )

    def compositionRtolChanged(self, value):
        self.rtol = value

    def enableItems(self, comboBox):
        for i in range(len(self.gudrunFile.components.components)):
            item = comboBox.model().item(i)
            if item:
                item.setFlags(
                    item.flags() | Qt.ItemIsEnabled
                )

    def setItemDisabled(self, comboBox, item):
        self.enableItems(comboBox)
        if item:
            item.setFlags(item.flags() & ~Qt.ItemIsEnabled)

    def toggleUseSingleComponent(self, state):
        if state:
            self.enableItems(self.widget.firstComponentComboBox)
            self.components[1] = None
            self.mode = iterators.Composition.Mode.SINGLE
        else:
            other = self.widget.secondComponentComboBox.model().item(
                self.widget.firstComponentComboBox.currentIndex()
            )
            self.setItemDisabled(
                self.widget.secondComponentComboBox,
                other
            )
            self.mode = iterators.Composition.Mode.DOUBLE
        self.widget.secondComponentComboBox.setEnabled(not state)
        self.widget.secondComponentComboBox.setCurrentIndex(-1)

    def initComponents(self):
        super().initComponents()
        self.widget.firstComponentComboBox.currentIndexChanged.connect(
            self.firstComponentChanged
        )
        self.widget.secondComponentComboBox.currentIndexChanged.connect(
            self.secondComponentChanged
        )
        self.widget.secondComponentComboBox.setCurrentIndex(-1)

        self.widget.compositionToleranceSpinBox.valueChanged.connect(
            self.compositionRtolChanged
        )
        self.widget.singleComponentCheckBox.toggled.connect(
            self.toggleUseSingleComponent
        )
        if len(self.gudrunFile.components.components):

            self.loadFirstComponentsComboBox()
            self.loadSecondComponentsComboBox()
            self.toggleUseSingleComponent(True)
        else:
            self.widget.iterateButton.setEnabled(False)

    def iterate(self):
        self.widget.close()
        self.params = {
            "gudrunFile": None,
            "mode": self.mode,
            "nTotal": self.numberIterations,
            "rtol": self.rtol,
            "components": self.components
        }