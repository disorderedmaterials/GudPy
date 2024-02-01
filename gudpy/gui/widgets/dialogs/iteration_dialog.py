import os
from queue import Queue
import sys
from copy import deepcopy
from PySide6.QtWidgets import QDialog
from PySide6.QtCore import QFile, Qt
from PySide6.QtUiTools import QUiLoader

from core.enums import Geometry
from core import config
from core import iterators


class IterationDialog(QDialog):

    def __init__(self, name, gudrunFile, parent):
        super(IterationDialog, self).__init__(parent=parent)
        self.gudrunFile = gudrunFile
        self.name = name
        self.numberIterations = 1
        self.iterator = None
        self.text = ""
        self.loadUI()
        self.initComponents()

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
        pass

    def numberIterationsChanged(self, value):
        self.numberIterations = value

    def enqueueTasks(self):
        self.queue = Queue()
        for _ in range(self.numberIterations + 1):
            self.queue.put(
                self.iterator.gudrunFile.dcs(headless=False)
            )


class DensityIterationDialog(IterationDialog):

    def iterate(self):
        self.iterator = iterators.DensityIterator(self.gudrunFile, self.numberIterations)
        self.enqueueTasks()
        self.text = "Iterate by Density"
        self.widget.close()


class iterators.InelasticitySubtractionIterationDialog(IterationDialog):

    def numberIterationsChanged(self, value):
        self.numberIterations = value

    def iterate(self):
        self.iterator = iterators.InelasticitySubtraction(
            self.gudrunFile, self.numberIterations)
        self.enqueueTasks()
        self.text = "Inelasticity subtractions"
        self.widget.close()

    def enqueueTasks(self):
        self.queue = Queue()
        for _ in range((self.numberIterations * 2)):
            self.queue.put(
                self.iterator.gudrunFile.dcs(headless=False)
            )


class RadiusIterationDialog(IterationDialog):

    def initComponents(self):
        super().initComponents()
        self.widget.iterateButton.setEnabled(
            config.geometry == Geometry.CYLINDRICAL
        )

    def iterate(self):
        self.iterator = iterators.RadiusIterator(self.gudrunFile, self.numberIterations)
        self.iterator.setTargetRadius("inner")
        self.enqueueTasks()
        self.text = "Iterate by Radius"
        self.widget.close()


class ThicknessIterationDialog(IterationDialog):

    def initComponents(self):
        super().initComponents()
        self.widget.iterateButton.setEnabled(
            config.geometry == Geometry.FLATPLATE
        )

    def iterate(self):
        self.iterator = iterators.ThicknessIterator(
            self.gudrunFile, self.numberIterations)
        self.enqueueTasks()
        self.text = "Iterate by Thickness"
        self.widget.close()


class TweakFactorIterationDialog(IterationDialog):

    def iterate(self):
        self.iterator = iterators.TweakFactorIterator(
            self.gudrunFile, self.numberIterations)
        self.enqueueTasks()
        self.text = "Iterate by Tweak Factor"
        self.widget.close()


class CompositionIterationDialog(IterationDialog):

    def __init__(self, name, gudrunFile, parent):
        self.components = [None, None]
        self.rtol = 0.
        super().__init__(name, gudrunFile, parent)

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
        else:
            other = self.widget.secondComponentComboBox.model().item(
                self.widget.firstComponentComboBox.currentIndex()
            )
            self.setItemDisabled(
                self.widget.secondComponentComboBox,
                other
            )
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
        self.iterator = iterators.CompositionIterator(self.gudrunFile)
        self.iterator.setComponents(self.components)
        self.queue = Queue()
        for sampleBackground in self.gudrunFile.sampleBackgrounds:
            for sample in sampleBackground.samples:
                if sample.runThisSample:
                    if [
                        wc for wc in sample.composition.weightedComponents
                        if self.components[0].eq(wc.component)
                    ]:
                        sb = deepcopy(sampleBackground)
                        sb.samples = [deepcopy(sample)]
                        if len(self.iterator.components) == 1:
                            self.queue.put(
                                (
                                    (
                                        [1e-2, self.iterator.ratio, 10],
                                        0,
                                        self.numberIterations,
                                        self.rtol
                                    ),
                                    {
                                        "args": (
                                            self.gudrunFile,
                                            sb,
                                            self.iterator.components
                                        )
                                    },
                                    sample
                                )
                            )
                        elif len(self.iterator.components) == 2:
                            self.queue.put(
                                (
                                    (
                                        [1e-2, self.iterator.ratio, 10],
                                        0,
                                        self.numberIterations,
                                        self.rtol
                                    ),
                                    {
                                        "args": (
                                            self.gudrunFile,
                                            sb,
                                            self.iterator.components,
                                            iterators.calculateTotalMolecules(
                                                self.iterator.components,
                                                sample
                                            )
                                        )
                                    },
                                    sample
                                )
                            )
        self.text = "Iterate by Composition"
        self.widget.close()
