from abc import abstractmethod
from copy import deepcopy
from PySide6.QtCore import QFile, QFileInfo, QTimer, QThread
from PySide6.QtGui import QPainter
from PySide6.QtUiTools import QUiLoader
from PySide6.QtWidgets import (
    QDialogButtonBox,
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMessageBox,
    QProgressBar,
    QPushButton,
    QSizePolicy,
    QStatusBar,
    QWidget,
    QMenu
)
from PySide6.QtCharts import QChartView
from src.gudrun_classes.composition import WeightedComponent
from src.gudrun_classes.composition_iterator import CompositionIterator, gss, calculateTotalMolecules
from src.gudrun_classes.density_iterator import DensityIterator

from src.gudrun_classes.sample import Sample
from src.gudrun_classes.container import Container
from src.gudrun_classes.thickness_iterator import ThicknessIterator
from src.gui.widgets.dialogs.export_dialog import ExportDialog

from src.gui.widgets.dialogs.iteration_dialog import IterationDialog
from src.gui.widgets.dialogs.purge_dialog import PurgeDialog
from src.gui.widgets.dialogs.view_input_dialog import ViewInputDialog
from src.gui.widgets.dialogs.missing_files_dialog import MissingFilesDialog
from src.gui.widgets.dialogs.composition_dialog import CompositionDialog
from src.gui.widgets.dialogs.view_output_dialog import ViewOutputDialog
from src.gui.widgets.dialogs.configuration_dialog import ConfigurationDialog
from src.gui.widgets.dialogs.composition_iteration_dialog import CompositionIterationDialog

from src.gui.widgets.gudpy_tree import GudPyTreeView

from src.gui.widgets.tables.composition_table import CompositionTable
from src.gui.widgets.tables.ratio_composition_table import (
    RatioCompositionTable
)
from src.gui.widgets.tables.beam_profile_table import BeamProfileTable
from src.gui.widgets.tables.grouping_parameter_table import (
    GroupingParameterTable
)
from src.gui.widgets.tables.exponential_table import ExponentialTable
from src.gui.widgets.tables.resonance_table import ResonanceTable
from src.gui.widgets.tables.components_table import ComponentsList

from src.gui.widgets.exponential_spinbox import ExponentialSpinBox

from src.gui.widgets.charts.chart import GudPyChart
from src.gui.widgets.charts.chartview import GudPyChartView
from src.gui.widgets.charts.beam_plot import BeamChart
from src.gui.widgets.charts.enums import PlotModes, SPLIT_PLOTS

from src.gudrun_classes.enums import Geometry
from src.gui.widgets.slots.instrument_slots import InstrumentSlots
from src.gui.widgets.slots.beam_slots import BeamSlots
from src.gui.widgets.slots.component_slots import ComponentSlots
from src.gui.widgets.slots.normalisation_slots import NormalisationSlots
from src.gui.widgets.slots.container_slots import ContainerSlots
from src.gui.widgets.slots.sample_background_slots import SampleBackgroundSlots
from src.gui.widgets.slots.sample_slots import SampleSlots
from src.gui.widgets.slots.output_slots import OutputSlots
from src.gui.widgets.resources import resources_rc  # noqa

from src.gudrun_classes.file_library import GudPyFileLibrary
from src.gudrun_classes.gudrun_file import GudrunFile
from src.gudrun_classes.exception import ParserException
from src.gudrun_classes import config
from src.gudrun_classes.tweak_factor_iterator import TweakFactorIterator
from src.gudrun_classes.wavelength_subtraction_iterator import (
    WavelengthSubtractionIterator
)
from src.gudrun_classes.run_containers_as_samples import RunContainersAsSamples
from src.gudrun_classes.gud_file import GudFile

from src.scripts.utils import breplace, nthint

from src.gui.widgets.worker import CompositionWorker

import os
import sys
import time
import math
import traceback
from queue import Queue
from collections.abc import Sequence


class GudPyMainWindow(QMainWindow):
    """
    Class to represent the GudPyMainWindow. Inherits QMainWindow.
    This is the main window for the GudPy application.

    ...

    Attributes
    ----------
    gudrunFile : GudrunFile
        GudrunFile object currently associated with the application.
    clipboard : SampleBackground | Sample | Container
        Stores copied objects.
    iterator : TweakFactorIterator | WavelengthSubtractionIterator
        Iterator to use in iterations.
    Methods
    -------
    initComponents()
        Loads the UI file for the GudPyMainWindow
    loadInputFile_()
        Loads an input file.
    saveInputFile()
        Saves the current GudPy file.
    updateFromFile()
        Updates from the original input file.
    updateGeometries()
        Updates geometries across objects.
    updateCompositions()
        Updates compositions across objects
        Deletes the current object.
    exit_()
        Exits GudPy.
    """
    def __init__(self):
        """
        Constructs all the necessary attributes for the GudPyMainWindow object.
        Calls initComponents() to load the UI file.
        """
        super(GudPyMainWindow, self).__init__()
        self.gudrunFile = None
        self.modified = False
        self.clipboard = None
        self.iterator = None
        self.queue = Queue()
        self.results = {}
        self.allPlots = []
        self.plotModes = {}
        self.proc = None
        self.output = ""
        self.outputIterations = {}
        self.previousProcTitle = ""
        self.error = ""
        self.cwd = os.getcwd()
        self.warning = ""
        self.initComponents()
        self.timer = QTimer(self)
        self.timer.setSingleShot(True)
        self.timer.timeout.connect(self.autosave)

    def initComponents(self):
        """
        Loads the UI file for the GudPyMainWindow.
        """
        if hasattr(sys, '_MEIPASS'):
            uifile = QFile(
                os.path.join(
                    sys._MEIPASS, "ui_files", "mainWindow.ui"
                )
            )
            current_dir = os.path.sep
        else:
            current_dir = os.path.dirname(os.path.realpath(__file__))
            uifile = QFile(
                os.path.join(
                    current_dir, "ui_files", "mainWindow.ui"
                )
            )

        loader = QUiLoader()
        loader.registerCustomWidget(GudPyTreeView)
        loader.registerCustomWidget(GroupingParameterTable)
        loader.registerCustomWidget(BeamProfileTable)
        loader.registerCustomWidget(CompositionTable)
        loader.registerCustomWidget(RatioCompositionTable)
        loader.registerCustomWidget(ExponentialTable)
        loader.registerCustomWidget(ResonanceTable)
        loader.registerCustomWidget(ComponentsList)
        loader.registerCustomWidget(IterationDialog)
        loader.registerCustomWidget(PurgeDialog)
        loader.registerCustomWidget(ViewInputDialog)
        loader.registerCustomWidget(ViewOutputDialog)
        loader.registerCustomWidget(ExportDialog)
        loader.registerCustomWidget(CompositionDialog)
        loader.registerCustomWidget(ConfigurationDialog)
        loader.registerCustomWidget(CompositionIterationDialog)
        loader.registerCustomWidget(ExponentialSpinBox)
        loader.registerCustomWidget(GudPyChartView)
        self.mainWidget = loader.load(uifile)

        self.mainWidget.statusBar_ = QStatusBar(self)
        self.mainWidget.statusBarWidget = QWidget(self.mainWidget.statusBar_)
        self.mainWidget.statusBarLayout = QHBoxLayout(
            self.mainWidget.statusBarWidget
        )
        self.mainWidget.currentTaskLabel = QLabel(
            self.mainWidget.statusBarWidget
        )
        self.mainWidget.currentTaskLabel.setText("No task running.")
        self.mainWidget.currentTaskLabel.setSizePolicy(
            QSizePolicy(QSizePolicy.Minimum, QSizePolicy.Preferred)
        )
        self.mainWidget.progressBar = QProgressBar(
            self.mainWidget.statusBarWidget
        )
        self.mainWidget.progressBar.setSizePolicy(
            QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        )
        self.mainWidget.progressBar.setTextVisible(False)
        self.mainWidget.statusBarLayout.addWidget(
            self.mainWidget.currentTaskLabel
        )
        self.mainWidget.statusBarLayout.addWidget(self.mainWidget.progressBar)
        self.mainWidget.statusBarWidget.setLayout(
            self.mainWidget.statusBarLayout
        )
        self.mainWidget.statusBar_.addWidget(self.mainWidget.statusBarWidget)
        self.mainWidget.setStatusBar(self.mainWidget.statusBar_)

        self.mainWidget.beamPlot = QChartView(
            self.mainWidget
        )
        self.mainWidget.beamPlot.setRenderHint(QPainter.Antialiasing)

        self.mainWidget.beamProfileLayout.insertWidget(
            1, self.mainWidget.beamPlot
        )

        self.mainWidget.beamChart = BeamChart()

        self.mainWidget.beamPlot.setChart(self.mainWidget.beamChart)

        self.mainWidget.sampleTopPlot = GudPyChartView(
            self.mainWidget
        )

        self.mainWidget.topPlotLayout.addWidget(
            self.mainWidget.sampleTopPlot
        )

        self.mainWidget.sampleBottomPlot = GudPyChartView(self.mainWidget)

        self.mainWidget.bottomPlotLayout.addWidget(
            self.mainWidget.sampleBottomPlot
        )

        self.mainWidget.bottomSamplePlotFrame.setVisible(False)

        self.mainWidget.containerTopPlot = GudPyChartView(
            self.mainWidget
        )

        self.mainWidget.topContainerPlotLayout.addWidget(
            self.mainWidget.containerTopPlot
        )

        self.mainWidget.containerBottomPlot = GudPyChartView(
            self.mainWidget
        )

        self.mainWidget.bottomContainerPlotLayout.addWidget(
            self.mainWidget.containerBottomPlot
        )

        self.mainWidget.bottomContainerPlotFrame.setVisible(False)

        self.mainWidget.allSampleTopPlot = GudPyChartView(
            self.mainWidget
        )

        self.mainWidget.topAllPlotLayout.addWidget(
            self.mainWidget.allSampleTopPlot
        )

        self.mainWidget.allSampleBottomPlot = GudPyChartView(self.mainWidget)

        self.mainWidget.bottomAllPlotLayout.addWidget(
            self.mainWidget.allSampleBottomPlot
        )

        self.mainWidget.bottomPlotFrame.setVisible(False)

        for plotMode in [
            plotMode for plotMode in PlotModes
            if plotMode not in [
                PlotModes.SF, PlotModes.SF_RDF,
                PlotModes.SF_CANS, PlotModes.SF_RDF_CANS
            ]
        ]:
            self.mainWidget.allPlotComboBox.addItem(plotMode.name, plotMode)

        self.mainWidget.allPlotComboBox.currentIndexChanged.connect(
            self.handleAllPlotModeChanged
        )

        for plotMode in [
            plotMode for plotMode in PlotModes
            if "(Cans)" not in plotMode.name
        ]:
            self.mainWidget.plotComboBox.addItem(plotMode.name, plotMode)

        self.mainWidget.plotComboBox.currentIndexChanged.connect(
            self.handleSamplePlotModeChanged
        )

        for plotMode in [
            plotMode for plotMode in PlotModes if "(Cans)" in plotMode.name
        ]:
            self.mainWidget.containerPlotComboBox.addItem(
                plotMode.name, plotMode
            )

        self.mainWidget.containerPlotComboBox.currentIndexChanged.connect(
            self.handleContainerPlotModeChanged
        )

        self.mainWidget.setWindowTitle("GudPy")
        self.mainWidget.show()
        self.instrumentSlots = InstrumentSlots(self.mainWidget, self)
        self.beamSlots = BeamSlots(self.mainWidget, self)
        self.componentSlots = ComponentSlots(self.mainWidget, self)
        self.normalisationSlots = NormalisationSlots(self.mainWidget, self)
        self.sampleBackgroundSlots = SampleBackgroundSlots(
            self.mainWidget, self
        )
        self.sampleSlots = SampleSlots(self.mainWidget, self)
        self.containerSlots = ContainerSlots(self.mainWidget, self)
        self.outputSlots = OutputSlots(self.mainWidget, self)
        self.mainWidget.runPurge.triggered.connect(
            self.runPurge_
        )
        self.mainWidget.runGudrun.triggered.connect(
            self.runGudrun_
        )
        self.mainWidget.iterateGudrun.triggered.connect(
            self.iterateGudrun_
        )
        self.mainWidget.runContainersAsSamples.triggered.connect(
            self.runContainersAsSamples
        )

        self.mainWidget.checkFilesExist.triggered.connect(
            self.checkFilesExist_
        )

        self.mainWidget.save.triggered.connect(self.saveInputFile)

        self.mainWidget.saveAs.triggered.connect(self.saveInputFileAs)

        self.mainWidget.viewLiveInputFile.triggered.connect(
            self.viewInput
        )

        self.mainWidget.insertSampleBackground.triggered.connect(
            self.mainWidget.objectTree.insertSampleBackground
        )

        self.mainWidget.insertSample.triggered.connect(
            self.mainWidget.objectTree.insertSample
        )

        self.mainWidget.insertDefaultContainer.triggered.connect(
            self.mainWidget.objectTree.insertContainer
        )

        actionMap = {
            name:
            lambda:
            self.mainWidget.objectTree.insertContainer(
                container=Container(
                    config=path
                )
            )
            for name, path in config.containerConfigurations.items()
        }
        insertContainerFromTemplate = QMenu(
            "From Template..",
            self.mainWidget.insertContainerMenu
        )
        for name, action in actionMap.items():
            insertContainerFromTemplate.addAction(name, action)

        self.mainWidget.insertContainerMenu.addMenu(
            insertContainerFromTemplate
        )

        self.mainWidget.copy.triggered.connect(
            self.mainWidget.objectTree.copy
        )
        self.mainWidget.cut.triggered.connect(
            self.mainWidget.objectTree.cut
        )
        self.mainWidget.paste.triggered.connect(
            self.mainWidget.objectTree.paste
        )
        self.mainWidget.delete_.triggered.connect(
            self.mainWidget.objectTree.del_
        )

        self.mainWidget.loadInputFile.triggered.connect(
            self.loadInputFile_
        )

        self.mainWidget.new_.triggered.connect(
            self.newInputFile
        )

        self.mainWidget.objectStack.currentChanged.connect(
            self.updateComponents
        )

        self.mainWidget.exportArchive.triggered.connect(self.export)

        self.mainWidget.exit.triggered.connect(self.exit_)

        self.setActionsEnabled(False)
        self.mainWidget.tabWidget.setVisible(False)
        self.setWindowModified(False)

    def tryLoadAutosaved(self, path):
        dir = os.path.dirname(path)
        for f in os.listdir(dir):
            if os.path.abspath(f) == path + ".autosave":

                if str(GudrunFile(path))[:-5] == str(GudrunFile(f))[:-5]:
                    return path

                autoFileInfo = QFileInfo(f)
                autoLastModified = autoFileInfo.lastModified()

                fileInfo = QFileInfo(path)
                lastModified = fileInfo.lastModified()

                if autoLastModified > lastModified:
                    messageBox = QMessageBox(self.mainWidget)
                    messageBox.setWindowTitle("Autosave found")
                    messageBox.setText(
                        f"Found autosaved file: {os.path.abspath(f)}.\n"
                        f"This file is newer ({autoLastModified.toString()})"
                        f" than the loaded file"
                        f" ({lastModified.toString()}).\n"
                        f"Would you like to load the autosaved file instead?"
                    )
                    messageBox.addButton(QMessageBox.No)
                    messageBox.addButton(QMessageBox.Yes)
                    result = messageBox.exec()
                    if result == messageBox.Yes:
                        return os.path.abspath(f)
                    else:
                        return path
                else:
                    return path
        return path

    def updateWidgets(self, fromFile=False):
        if fromFile:
            self.gudrunFile = GudrunFile(path=self.gudrunFile.path)
        self.mainWidget.gudrunFile = self.gudrunFile
        self.mainWidget.tabWidget.setVisible(True)
        self.instrumentSlots.setInstrument(self.gudrunFile.instrument)
        self.beamSlots.setBeam(self.gudrunFile.beam)
        self.componentSlots.setComponents(config.components)
        self.normalisationSlots.setNormalisation(self.gudrunFile.normalisation)

        if len(self.gudrunFile.sampleBackgrounds):
            self.sampleBackgroundSlots.setSampleBackground(
                self.gudrunFile.sampleBackgrounds[0]
            )

            if len(self.gudrunFile.sampleBackgrounds[0].samples):
                self.sampleSlots.setSample(
                    self.gudrunFile.sampleBackgrounds[0].
                    samples[0]
                )

                if len(
                    self.gudrunFile.sampleBackgrounds[0].
                    samples[0].containers
                ):
                    self.containerSlots.setContainer(
                        self.gudrunFile.sampleBackgrounds[0]
                        .samples[0].containers[0]
                    )
        self.setActionsEnabled(True)
        self.mainWidget.objectTree.buildTree(self.gudrunFile, self)
        self.updateResults()

    def loadInputFile_(self):
        """
        Opens a QFileDialog to load an input file.
        """
        filename, _ = QFileDialog.getOpenFileName(
            self,
            "Select Input file for GudPy",
            ".",
            "GudPy Input (*.txt);;Sample Parameters (*.sample)"
        )
        if filename:
            try:
                if self.gudrunFile:
                    del self.gudrunFile
                path = self.tryLoadAutosaved(filename)
                self.gudrunFile = GudrunFile(path=path)
                self.updateWidgets()
                self.mainWidget.setWindowTitle(self.gudrunFile.path + " [*]")
            except ParserException as e:
                QMessageBox.critical(self.mainWidget, "GudPy Error", str(e))

    def saveInputFile(self):
        """
        Saves the current state of the input file.
        """
        if not self.gudrunFile.path:
            self.saveInputFileAs()
        else:
            self.gudrunFile.write_out(overwrite=True)
            self.setUnModified()

    def saveInputFileAs(self):
        """
        Saves the current state of the input file as...
        """
        filename, _ = QFileDialog.getSaveFileName(
            self, "Save input file as..", ".", "(*.txt)"
        )
        if filename:
            if os.path.basename(filename) == "gudpy.txt":
                QMessageBox.warning(
                    self.mainWidget,
                    "GudPy Warning",
                    f"Cannot save to {filename}, gudpy.txt is reserved."
                )
                return
            self.gudrunFile.instrument.GudrunInputFileDir = (
                os.path.dirname(os.path.abspath(filename))
            )
            self.gudrunFile.path = filename
            self.gudrunFile.write_out(overwrite=True)
            self.setUnModified()

    def newInputFile(self):
        if self.gudrunFile:
            del self.gudrunFile
        self.gudrunFile = GudrunFile()
        configurationDialog = ConfigurationDialog(self)
        result = configurationDialog.widget.exec()
        if not configurationDialog.cancelled and result:
            self.gudrunFile.instrument = GudrunFile(
                configurationDialog.configuration, config=True
            ).instrument
            self.updateWidgets()

    def updateFromFile(self):
        """
        Calls updateFromFile(), to update the UI.
        """
        try:
            self.updateWidgets(fromFile=True)
        except ParserException as e:
            QMessageBox.critical(
                self.mainWidget,
                "GudPy Error",
                f"An error occured reverting to the previous state.\n{str(e)}"
            )
            with open(self.gudrunFile.path, "w", encoding="utf-8") as fp:
                fp.write(str(self.currentState))

    def updateGeometries(self):
        """
        Iteratively updates geometries of objects,
        where the Geometry is SameAsBeam.
        """
        if self.gudrunFile.normalisation.geometry == Geometry.SameAsBeam:
            self.normalisationSlots.widgetsRefreshing = True
            self.mainWidget.geometryInfoStack.setCurrentIndex(
                config.geometry.value
            )
            self.widgetsRefreshing = False
        for i, sampleBackground in enumerate(
            self.gudrunFile.sampleBackgrounds
        ):
            for j, sample in enumerate(sampleBackground.samples):
                self.gudrunFile.sampleBackgrounds[i].samples[j].geometry = (
                    config.geometry
                )
                for k in range(len(sample.containers)):
                    sample = self.gudrunFile.sampleBackgrounds[i].samples[j]
                    sample.containers[k].geometry = config.geometry

    def updateCompositions(self):
        """
        Iteratively shares compositions between objects,
        for copying and pasting compositions between eachother.
        """
        self.mainWidget.normalisationCompositionTable.farmCompositions()
        self.mainWidget.sampleCompositionTable.farmCompositions()
        self.mainWidget.sampleRatioCompositionTable.farmCompositions()
        self.mainWidget.containerCompositionTable.farmCompositions()

    def focusResult(self):
        if (
            self.mainWidget.objectStack.currentIndex() == 5
            and isinstance(
                self.mainWidget.objectTree.currentObject(), Sample
            )
        ):
            try:
                topPlot, bottomPlot, gudFile = (
                    self.results[self.mainWidget.objectTree.currentObject()]
                )
            except KeyError:
                self.updateSamples()
                topPlot, bottomPlot, gudFile = (
                    self.results[self.mainWidget.objectTree.currentObject()]
                )
            self.mainWidget.sampleTopPlot.setChart(
                topPlot
            )
            self.mainWidget.sampleBottomPlot.setChart(
                bottomPlot
            )

            plotsMap = {
                PlotModes.SF: 0,
                PlotModes.SF_MINT01: 1,
                PlotModes.SF_MDCS01: 2,
                PlotModes.RDF: 3,
                PlotModes.SF_RDF: 4,
                PlotModes.SF_MINT01_RDF: 5,
                PlotModes.SF_MDCS01_RDF: 6
            }

            if (
                self.mainWidget.objectTree.currentObject()
                in self.plotModes.keys()
            ):
                self.mainWidget.plotComboBox.setCurrentIndex(
                    plotsMap[
                        self.plotModes[
                            self.mainWidget.objectTree.currentObject()
                        ]
                    ]
                )
            else:
                self.mainWidget.plotComboBox.setCurrentIndex(0)

            if gudFile:
                dcsLevel = gudFile.averageLevelMergedDCS
                self.mainWidget.dcsLabel.setText(
                    f"DCS Level: {dcsLevel}"
                )
                self.mainWidget.resultLabel.setText(gudFile.output)
                if gudFile.err:
                    self.mainWidget.resultLabel.setStyleSheet(
                        "background-color: red"
                    )
                else:
                    self.mainWidget.resultLabel.setStyleSheet(
                        "background-color: green"
                    )

                tweakFactor = gudFile.suggestedTweakFactor
                self.mainWidget.suggestedTweakFactorLabel.setText(
                    f"Suggested Tweak Factor: {tweakFactor}"
                )
            else:
                self.mainWidget.dcsLabel.setText(
                    "DCS Level"
                )
                self.mainWidget.resultLabel.setText("Error")
                self.mainWidget.resultLabel.setStyleSheet(
                    ""
                )
                self.mainWidget.suggestedTweakFactorLabel.setText(
                    "Suggested Tweak Factor"
                )
        elif (
            self.mainWidget.objectStack.currentIndex() == 6
            and isinstance(
                self.mainWidget.objectTree.currentObject(), Container
            )
        ):
            try:
                topPlot, bottomPlot, gudFile = (
                    self.results[self.mainWidget.objectTree.currentObject()]
                )
            except KeyError:
                self.updateSamples()
                topPlot, bottomPlot, gudFile = (
                    self.results[self.mainWidget.objectTree.currentObject()]
                )
            if sum(
                [
                    *[s.count() for s in topPlot.series()],
                    *[s.count() for s in bottomPlot.series()]
                ]
            ):
                self.mainWidget.containerSplitter.setSizes([2, 1])
            else:
                self.mainWidget.containerSplitter.setSizes([1, 0])

            self.mainWidget.containerTopPlot.setChart(
                topPlot
            )
            self.mainWidget.containerBottomPlot.setChart(
                bottomPlot
            )

            plotsMap = {
                PlotModes.SF_CANS: 0,
                PlotModes.SF_MINT01_CANS: 1,
                PlotModes.SF_MDCS01_CANS: 2,
                PlotModes.RDF_CANS: 3,
                PlotModes.SF_RDF_CANS: 4,
                PlotModes.SF_MINT01_RDF_CANS: 5,
                PlotModes.SF_MDCS01_RDF_CANS: 6
            }

            if (
                self.mainWidget.objectTree.currentObject()
                in self.plotModes.keys()
            ):
                self.mainWidget.plotComboBox.setCurrentIndex(
                    plotsMap[
                        self.plotModes[
                            self.mainWidget.objectTree.currentObject()
                        ]
                    ]
                )
            else:
                self.mainWidget.plotComboBox.setCurrentIndex(0)

            if gudFile:
                dcsLevel = gudFile.averageLevelMergedDCS
                self.mainWidget.containerDcsLabel.setText(
                    f"DCS Level: {dcsLevel}"
                )
                self.mainWidget.containerResultLabel.setText(gudFile.output)
                if gudFile.err:
                    self.mainWidget.containerResultLabel.setStyleSheet(
                        "background-color: red"
                    )
                else:
                    self.mainWidget.containerResultLabel.setStyleSheet(
                        "background-color: green"
                    )

                tweakFactor = gudFile.suggestedTweakFactor
                self.mainWidget.containerSuggestedTweakFactorLabel.setText(
                    f"Suggested Tweak Factor: {tweakFactor}"
                )

    def updateSamples(self):
        samples = [
            *self.mainWidget.objectTree.getSamples(),
            *self.mainWidget.objectTree.getContainers()
        ]
        for sample in samples:
            topChart = GudPyChart(
                self.gudrunFile
            )
            topChart.addSample(sample)
            bottomChart = GudPyChart(
                self.gudrunFile
            )
            bottomChart.addSample(sample)
            if sample not in self.plotModes.keys():
                plotMode = (
                    PlotModes.SF if isinstance(sample, Sample)
                    else PlotModes.SF_CANS
                )
                self.plotModes[sample] = plotMode
            plotMode = self.plotModes[sample]
            if self.isPlotModeSplittable(plotMode):
                top, bottom = self.splitPlotMode(plotMode)
                topChart.plot(top)
                bottomChart.plot(bottom)
            else:
                topChart.plot(plotMode)
            path = None
            if len(sample.dataFiles.dataFiles):
                path = breplace(
                    sample.dataFiles.dataFiles[0],
                    self.gudrunFile.instrument.dataFileType,
                    "gud"
                )
                if not os.path.exists(path):
                    path = os.path.join(
                        self.gudrunFile.instrument.GudrunInputFileDir, path
                    )
            gf = GudFile(path) if path and os.path.exists(path) else None
            self.results[sample] = [topChart, bottomChart, gf]

    def updateAllSamples(self):

        samples = [
            *self.mainWidget.objectTree.getSamples(),
            *self.mainWidget.objectTree.getContainers()
        ]
        if len(self.allPlots):
            allTopChart = GudPyChart(
                self.gudrunFile
            )
            allTopChart.addSamples(samples)
            allTopChart.plot(
                self.mainWidget.allPlotComboBox.itemData(
                    self.mainWidget.allPlotComboBox.currentIndex()
                )
            )
            allBottomChart = GudPyChart(
                self.gudrunFile
            )
            allBottomChart.addSamples(samples)
        else:
            allTopChart = GudPyChart(
                self.gudrunFile
            )
            allTopChart.addSamples(samples)
            allTopChart.plot(
                self.mainWidget.allPlotComboBox.itemData(
                    self.mainWidget.allPlotComboBox.currentIndex()
                )
            )
            allBottomChart = GudPyChart(
                self.gudrunFile
            )
            allBottomChart.addSamples(samples)
        self.allPlots = [allTopChart, allBottomChart]
        self.mainWidget.allSampleTopPlot.setChart(allTopChart)
        self.mainWidget.allSampleBottomPlot.setChart(allBottomChart)

    def updateResults(self):

        self.updateSamples()
        self.updateAllSamples()
        self.focusResult()

    def updateComponents(self):
        """
        Updates geometries and compositions.
        """
        self.updateGeometries()
        self.updateCompositions()
        self.focusResult()

    def exit_(self):
        """
        Exits GudPy - questions user if they want to save on exit or not.
        """
        messageBox = QMessageBox
        result = (
            messageBox.question(
                self.mainWidget, '',
                "Do you want to save?", messageBox.No | messageBox.Yes
            )
        )

        if result == messageBox.Yes:
            self.gudrunFile.write_out(overwrite=True)
        sys.exit(0)

    def makeProc(self, cmd, slot, func=None, args=None):
        self.proc = cmd
        self.proc.readyReadStandardOutput.connect(slot)
        self.proc.started.connect(self.procStarted)
        self.proc.finished.connect(self.procFinished)
        self.proc.setWorkingDirectory(
            self.gudrunFile.instrument.GudrunInputFileDir
        )
        if func:
            func(*args)
        self.proc.start()

    def runPurge_(self):
        self.setControlsEnabled(False)
        purgeDialog = PurgeDialog(self.gudrunFile, self)
        result = purgeDialog.widget.exec_()
        purge = purgeDialog.purge_det
        if isinstance(purge, Sequence):
            purge, func, args = purge
        if purgeDialog.cancelled or result == QDialogButtonBox.No:
            self.setControlsEnabled(True)
            self.queue = Queue()
        elif isinstance(purge, FileNotFoundError):
            QMessageBox.critical(
                self.mainWidget,
                "GudPy Error", "Couldn't find purge_det binary."
            )
            self.setControlsEnabled(True)
        elif not purge:
            self.setControlsEnabled(True)
        else:
            os.chdir(self.gudrunFile.instrument.GudrunInputFileDir)
            self.gudrunFile.purgeFile.write_out()
            self.makeProc(purge, self.progressPurge, func, args)

    def runGudrun_(self):
        self.setControlsEnabled(False)
        dcs = self.gudrunFile.dcs(
            path=os.path.join(
                self.gudrunFile.instrument.GudrunInputFileDir,
                self.gudrunFile.outpath
            ),
            headless=False
        )
        if isinstance(dcs, Sequence):
            dcs, func, args = dcs
        if isinstance(dcs, FileNotFoundError):
            QMessageBox.critical(
                self.mainWidget, "GudPy Error",
                "Couldn't find gudrun_dcs binary."
            )
        elif (
            not self.gudrunFile.purged
            and os.path.exists(
                os.path.join(
                    self.gudrunFile.instrument.GudrunInputFileDir,
                    'purge_det.dat'
                )
            )
        ):
            self.purgeOptionsMessageBox(
                dcs, func, args,
                "purge_det.dat found, but wasn't run in this session. "
                "Continue?"
            )
        elif not self.gudrunFile.purged:
            self.purgeOptionsMessageBox(
                dcs, func, args,
                "It looks like you may not have purged detectors. Continue?"
            )
        else:
            self.makeProc(dcs, self.progressDCS, func, args)

    def runContainersAsSamples(self):
        self.setControlsEnabled(False)
        dcs = RunContainersAsSamples(self.gudrunFile).runContainersAsSamples(
            path=os.path.join(
                self.gudrunFile.instrument.GudrunInputFileDir,
                self.gudrunFile.outpath
            ),
            headless=False
        )
        if isinstance(dcs, Sequence):
            dcs, func, args = dcs
        if isinstance(dcs, FileNotFoundError):
            QMessageBox.critical(
                self.mainWidget, "GudPy Error",
                "Couldn't find gudrun_dcs binary."
            )
        elif (
            not self.gudrunFile.purged
            and os.path.exists(
                os.path.join(
                    self.gudrunFile.instrument.GudrunInputFileDir,
                    'purge_det.dat'
                )
            )
        ):
            self.purgeOptionsMessageBox(
                dcs, func, args,
                "purge_det.dat found, but wasn't run in this session. "
                "Continue?"
            )
        elif not self.gudrunFile.purged:
            self.purgeOptionsMessageBox(
                dcs, func, args,
                "It looks like you may not have purged detectors. Continue?"
            )
        else:
            self.makeProc(dcs, self.progressDCS, func, args)

    def purgeOptionsMessageBox(self, dcs, func, args, text):
        messageBox = QMessageBox(self.mainWidget)
        messageBox.setWindowTitle("GudPy Warning")
        messageBox.setText(text)
        messageBox.addButton(QMessageBox.No)
        openPurgeDialog = QPushButton(
            "Open purge dialog", messageBox
        )
        purgeDefault = QPushButton(
            "Purge with default parameters", messageBox
        )

        messageBox.addButton(openPurgeDialog, QMessageBox.ApplyRole)
        messageBox.addButton(purgeDefault, QMessageBox.ApplyRole)

        messageBox.addButton(QMessageBox.Yes)
        result = messageBox.exec()

        if messageBox.clickedButton() == openPurgeDialog:
            self.purgeBeforeRunning(default=False)
        elif messageBox.clickedButton() == purgeDefault:
            self.purgeBeforeRunning()
        elif result == messageBox.Yes:
            self.makeProc(dcs, self.progressDCS, func, args)
        else:
            messageBox.close()
            self.setControlsEnabled(True)

    def purgeBeforeRunning(self, default=True):
        self.setControlsEnabled(False)
        if default:
            purge_det = self.gudrunFile.purge(
                headless=False
            )
            if isinstance(purge_det, Sequence):
                purge, func, args = purge_det
                self.makeProc(purge, self.progressPurge, func, args)
            elif isinstance(purge_det, FileNotFoundError):
                QMessageBox.critical(
                    self.mainWidget,
                    "GudPy Error", "Couldn't find purge_det binary."
                )
            self.setControlsEnabled(True)
            return
        else:
            self.runPurge_()
        dcs = self.gudrunFile.dcs(
            path=os.path.join(
                self.gudrunFile.instrument.GudrunInputFileDir,
                self.gudrunFile.outpath
            ),
            headless=False
        )
        if isinstance(dcs, Sequence):
            dcs, func, args = dcs
        elif isinstance(dcs, FileNotFoundError):
            QMessageBox.critical(
                self.mainWidget, "GudPy Error",
                "Couldn't find gudrun_dcs binary."
            )
            return
        self.queue.put((dcs, self.progressDCS, func, args))

    def iterateGudrun_(self):
        self.setControlsEnabled(False)
        iterationDialog = IterationDialog(self.gudrunFile, self.mainWidget)
        iterationDialog.widget.exec()
        if iterationDialog.cancelled or not iterationDialog.iterator:
            self.setControlsEnabled(True)
        else:
            self.queue = iterationDialog.queue
            self.iterator = iterationDialog.iterator
            self.numberIterations = iterationDialog.numberIterations
            self.currentIteration = 0
            self.text = iterationDialog.text
            self.outputIterations = {}
            if isinstance(self.iterator, CompositionIterator):
                self.iterateByComposition()
            else:
                self.nextIterableProc()

    def finishedCompositionIteration(self, originalSample, updatedSample):
        self.compositionMap[originalSample] = updatedSample
        self.mainWidget.progressBar.setValue(int((self.currentIteration/self.totalIterations)*100))
        print("Finished composition iteration!!!")
        if not self.queue.empty():
            self.nextCompositionIteration()
        else:
            print("Finished all iterations.")
            self.finishedCompositionIterations()

    def finishedCompositionIterations(self):
        for original, new in self.compositionMap.items():
            dialog = CompositionIterationDialog(new, self.mainWidget)
            result = dialog.widget.exec()
            if result:
                original.composition = new.composition
                if self.sampleSlots.sample == original:
                    self.sampleSlots.setSample(original)
        self.setControlsEnabled(True)
        self.mainWidget.progressBar.setValue(0)
        self.mainWidget.currentTaskLabel.setText("No task running.")
        self.queue = Queue()

    def startedCompositionIteration(self, sample):
        self.mainWidget.currentTaskLabel.setText(
            f"{self.text}"
            f" ({sample.name})"
        )

    def errorCompositionIteration(self, output):
        QMessageBox.critical(
            self.mainWidget, "GudPy Error",
            "An error occured whilst iterating by composition."
            " Please check the output to see what went wrong."
        )
        self.setControlsEnabled(True)
        self.mainWidget.currentTaskLabel.setText("No task running.")
        self.mainWidget.progressBar.setValue(0)
        self.outputSlots.setOutput(output, "gudrun_dcs")
        self.queue = Queue()

    def nextCompositionIteration(self):
        args, kwargs, sample = self.queue.get()
        print(args, kwargs, sample.name)
        self.worker = CompositionWorker(args, kwargs, sample)
        self.worker.started.connect(self.startedCompositionIteration)
        self.workerThread = QThread()
        self.worker.moveToThread(self.workerThread)
        self.worker.finished.connect(self.workerThread.quit)
        self.workerThread.started.connect(self.worker.work)
        self.workerThread.start()
        print("Started worker.")
        self.worker.errorOccured.connect(self.errorCompositionIteration)
        self.worker.errorOccured.connect(self.workerThread.quit)
        self.worker.finished.connect(self.finishedCompositionIteration)
        self.currentIteration+=1

    def iterateByComposition(self):
        if not self.iterator.components:
            self.setControlsEnabled(True)
            return
        elif self.queue.empty():
            QMessageBox.warning(self.mainWidget, "GudPy Warning", "No iterations were queued. It's likely no Samples selected for analysis use the Component(s) selected for iteration.")
        else:
            print(list(self.queue.queue))
            self.compositionMap = {}
            self.totalIterations = len(
                [s for sb in self.gudrunFile.sampleBackgrounds for s in sb.samples if s.runThisSample and len([wc for c in self.iterator.components for wc in s.composition.weightedComponents if wc.component.eq(c) ])]
            )
            print(self.totalIterations)
            self.nextCompositionIteration()

    def nextIteration(self):
        if self.error:
            self.proc.finished.connect(self.procFinished)
        if isinstance(self.iterator, (TweakFactorIterator, DensityIterator, ThicknessIterator, CompositionIterator)):
            time.sleep(1)
            self.iterator.performIteration(self.currentIteration)
            self.gudrunFile.write_out()
            self.outputIterations[self.currentIteration+1] = self.output
        elif isinstance(self.iterator, WavelengthSubtractionIterator):
            time.sleep(1)
            if (self.currentIteration + 1) % 2 == 0:
                self.iterator.QIteration(self.currentIteration)
            else:
                self.iterator.wavelengthIteration(self.currentIteration)
                if self.currentIteration == 0:
                    self.outputIterations[1] = self.output
                else:
                    self.outputIterations[self.currentIteration] = self.output
            self.gudrunFile.write_out()
        self.nextIterableProc()
        self.currentIteration += 1
        self.output = ""

    def nextIterableProc(self):
        self.proc, func, args = self.queue.get()
        self.proc.started.connect(self.iterationStarted)
        if not self.queue.empty():
            self.proc.finished.connect(self.nextIteration)
        else:
            self.proc.finished.connect(self.procFinished)
        self.proc.readyReadStandardOutput.connect(self.progressIteration)
        self.proc.started.connect(self.iterationStarted)
        self.proc.setWorkingDirectory(
            self.gudrunFile.instrument.GudrunInputFileDir
        )
        if func:
            func(*args)
        self.proc.start()

    def iterationStarted(self):
        if isinstance(self.iterator, (TweakFactorIterator, ThicknessIterator, DensityIterator)):
            self.mainWidget.currentTaskLabel.setText(
                f"{self.text}"
                f" {self.currentIteration+1}/{self.numberIterations}"
            )
        elif isinstance(self.iterator, WavelengthSubtractionIterator):
            iteration = math.ceil((self.currentIteration+1)/2)
            self.mainWidget.currentTaskLabel.setText(
                f"{self.text}"
                f" {iteration}/{self.numberIterations}"
            )
        self.previousProcTitle = self.mainWidget.currentTaskLabel.text()

    def progressIteration(self):
        progress = self.progressIncrementDCS()
        if progress == -1:
            self.error = (
                f"An error occurred. See the following traceback"
                f" from gudrun_dcs\n{self.error}"
            )
            return
        if isinstance(self.iterator, (TweakFactorIterator, ThicknessIterator, DensityIterator)):
            progress /= self.numberIterations
        elif isinstance(self.iterator, WavelengthSubtractionIterator):
            progress /= self.numberIterations
        progress += self.mainWidget.progressBar.value()
        self.mainWidget.progressBar.setValue(
            progress if progress <= 100 else 100
        )

    def checkFilesExist_(self):
        result = GudPyFileLibrary(self.gudrunFile).checkFilesExist()
        if not all(r[0] for r in result):
            unresolved = [r[1] for r in result if not r[0]]
            missingFilesDialog = MissingFilesDialog(
                unresolved, self.mainWidget
            )
            missingFilesDialog.widget.exec_()

    def autosave(self):
        if self.gudrunFile.path:
            autosavePath = self.gudrunFile.path + ".autosave"
            self.gudrunFile.write_out(path=autosavePath)

    def setModified(self):

        if not self.modified:
            if self.gudrunFile.path:
                self.modified = True
                self.mainWidget.setWindowModified(True)
                self.mainWidget.save.setEnabled(True)
        if not self.proc:
            self.timer.start(30000)

    def setUnModified(self):
        self.mainWidget.setWindowModified(False)
        self.modified = False
        self.mainWidget.save.setEnabled(False)

    def setControlsEnabled(self, state):
        self.mainWidget.instrumentPage.setEnabled(state)
        self.mainWidget.beamPage.setEnabled(state)
        self.mainWidget.normalisationPage.setEnabled(state)
        self.mainWidget.sampleTab.setEnabled(state)
        self.mainWidget.advancedTab.setEnabled(state)
        self.mainWidget.containerPage.setEnabled(state)
        self.mainWidget.sampleBackgroundPage.setEnabled(state)
        self.mainWidget.objectTree.setContextEnabled(state)
        self.mainWidget.objectTree.model().setEnabled(state)
        self.setTreeActionsEnabled(state)

        self.mainWidget.runPurge.setEnabled(state)
        self.mainWidget.runGudrun.setEnabled(state)
        self.mainWidget.iterateGudrun.setEnabled(state)
        self.mainWidget.viewLiveInputFile.setEnabled(state)
        self.mainWidget.save.setEnabled(
            state &
            self.modified &
            len(self.gudrunFile.path) > 0
            if self.gudrunFile.path
            else False
        )
        self.mainWidget.saveAs.setEnabled(state)
        self.mainWidget.loadInputFile.setEnabled(state)
        self.mainWidget.exportArchive.setEnabled(state)
        self.mainWidget.new_.setEnabled(state)
        self.mainWidget.checkFilesExist.setEnabled(state)
        self.mainWidget.runContainersAsSamples.setEnabled(state)

    def setActionsEnabled(self, state):

        self.setTreeActionsEnabled(state)

        self.mainWidget.runPurge.setEnabled(state)
        self.mainWidget.runGudrun.setEnabled(state)
        self.mainWidget.iterateGudrun.setEnabled(state)
        self.mainWidget.checkFilesExist.setEnabled(state)
        self.mainWidget.runContainersAsSamples.setEnabled(state)

        self.mainWidget.viewLiveInputFile.setEnabled(state)
        self.mainWidget.save.setEnabled(
            state &
            self.modified
        )
        self.mainWidget.saveAs.setEnabled(state)
        self.mainWidget.exportArchive.setEnabled(state)

    def setTreeActionsEnabled(self, state):
        self.mainWidget.insertSampleBackground.setEnabled(state)
        self.mainWidget.insertSample.setEnabled(state)
        self.mainWidget.insertContainerMenu.setEnabled(state)
        self.mainWidget.copy.setEnabled(state)
        self.mainWidget.cut.setEnabled(state)
        self.mainWidget.paste.setEnabled(state)
        self.mainWidget.delete_.setEnabled(state)

    def progressIncrementDCS(self):
        data = self.proc.readAllStandardOutput()
        stdout = bytes(data).decode("utf8")
        self.output += stdout
        ERROR_KWDS = [
            "does not exist",
            "error",
            "Error"
        ]
        if [KWD for KWD in ERROR_KWDS if KWD in stdout]:
            self.error = stdout
            return -1
        # Number of GudPy objects.
        markers = (
            config.NUM_GUDPY_CORE_OBJECTS
            + len(self.gudrunFile.sampleBackgrounds)
            + sum(
                [
                    sum(
                        [
                            len(sampleBackground.samples), *[
                                len(sample.containers)
                                for sample in sampleBackground.samples
                            ]
                        ]
                    ) for sampleBackground in self.gudrunFile.sampleBackgrounds
                ]
            )
        )
        stepSize = math.ceil(100/markers)
        progress = stepSize * sum(
            [
                stdout.count("Got to: INSTRUMENT"),
                stdout.count("Got to: BEAM"),
                stdout.count("Got to: NORMALISATION"),
                stdout.count("Got to: SAMPLE BACKGROUND"),
                stdout.count("Finished merging data for sample"),
                stdout.count("Got to: CONTAINER")
            ]
        )
        return progress

    def progressDCS(self):
        progress = self.progressIncrementDCS()
        if progress == -1:
            self.queue = Queue()
            self.error = (
                f"An error occurred. See the following traceback"
                f" from gudrun_dcs\n{self.error}"
            )
            return
        progress += self.mainWidget.progressBar.value()
        self.mainWidget.progressBar.setValue(
            progress if progress <= 100 else 100
        )

    def progressIncrementPurge(self):
        data = self.proc.readAllStandardOutput()
        stdout = bytes(data).decode("utf8")
        self.output += stdout
        dataFiles = [self.gudrunFile.instrument.groupFileName]

        def appendDfs(dfs):
            for df in dfs:
                dataFiles.append(df.replace(
                    self.gudrunFile.instrument.dataFileType, "grp")
                )

        appendDfs(self.gudrunFile.purgeFile.normalisationDataFiles[0])
        appendDfs(
            self.gudrunFile.purgeFile.normalisationBackgroundDataFiles[0]
        )
        for dfs, _ in self.gudrunFile.purgeFile.sampleBackgroundDataFiles:
            appendDfs(dfs)
        if not self.gudrunFile.purgeFile.excludeSampleAndCan:
            for dfs, _ in self.gudrunFile.purgeFile.sampleDataFiles:
                appendDfs(dfs)
            for dfs, _ in self.gudrunFile.purgeFile.containerDataFiles:
                appendDfs(dfs)

        stepSize = math.ceil(100/len(dataFiles))
        progress = 0
        for df in dataFiles:
            if df in stdout:
                progress += stepSize
        if "Error" in stdout or "error" in stdout or "not found" in stdout:
            self.error = stdout
            return -1, False, -1
        elif dataFiles[-1] in stdout:
            try:
                lines = stdout.split("\n")
                targetLine = next(
                    (
                        s for s in lines
                        if "spectra in" in s
                        and dataFiles[-1] in s
                    )
                )
            except StopIteration:
                return progress, False, -1
            return 100, True, nthint(targetLine, 0)
        else:
            return progress, False, -1

    def progressPurge(self):
        progress, finished, detectors = self.progressIncrementPurge()
        if progress == -1:
            self.error = (
                f"An error occurred. See the following traceback"
                f" from purge_det\n{self.error}"
            )
            self.gudrunFile.purged = False
            return
        progress += self.mainWidget.progressBar.value()
        self.mainWidget.progressBar.setValue(
            progress if progress <= 100 else 100
        )

        if finished:
            thresh = self.gudrunFile.instrument.goodDetectorThreshold
            if thresh and detectors < thresh:
                self.warning = (
                    f"{detectors} detectors made it through the purge."
                    " The acceptable minimum for "
                    f"{self.gudrunFile.instrument.name.name} is {thresh}"
                )
            self.mainWidget.goodDetectorsLabel.setText(
                f"Number of Good Detectors: {detectors}"
            )

    def procStarted(self):
        self.mainWidget.currentTaskLabel.setText(
            self.proc.program().split(os.path.sep)[-1]
        )
        self.previousProcTitle = self.mainWidget.currentTaskLabel.text()
        self.output = ""

    def procFinished(self):
        self.proc = None
        output = self.output
        if isinstance(self.iterator, (TweakFactorIterator, ThicknessIterator, DensityIterator)):
            self.outputIterations[self.currentIteration+1] = self.output
            self.sampleSlots.setSample(self.sampleSlots.sample)
        if self.iterator:
            output = self.outputIterations
        self.iterator = None

        if self.error:
            QMessageBox.critical(
                self.mainWidget, "GudPy Error",
                self.error
            )
            self.error = ""
            self.queue = Queue()
        if not self.queue.empty():
            self.makeProc(*self.queue.get())
        else:
            if self.warning:
                QMessageBox.warning(
                    self.mainWidget, "GudPy Warning",
                    self.warning
                )
                self.warning = ""
            self.setControlsEnabled(True)
        if "purge_det" not in self.mainWidget.currentTaskLabel.text():
            try:
                self.updateResults()
            except ParserException:
                QMessageBox.warning(
                    self.mainWidget, "GudPy Warning",
                    "The process did not entirely finish,"
                    " please check your parameters."
                )
            self.outputSlots.setOutput(output, "gudrun_dcs")
        else:
            self.outputSlots.setOutput(output, "purge_det")
        self.mainWidget.currentTaskLabel.setText("No task running.")
        self.mainWidget.progressBar.setValue(0)

    def viewInput(self):
        self.currentState = str(self.gudrunFile)
        viewInputDialog = ViewInputDialog(self.gudrunFile, self)
        viewInputDialog.widget.exec_()

    def handleAllPlotModeChanged(self, index):
        plotMode = self.mainWidget.allPlotComboBox.itemData(index)
        self.plotModes["All"] = plotMode
        if self.isPlotModeSplittable(plotMode):
            top, bottom = self.splitPlotMode(plotMode)
            self.handlePlotModeChanged(
                self.mainWidget.allSampleTopPlot.chart().plot, top
            )
            self.handlePlotModeChanged(
                self.mainWidget.allSampleBottomPlot.chart().plot, bottom
            )
            self.mainWidget.bottomPlotFrame.setVisible(True)
            self.mainWidget.allPlotSplitter.setSizes([1, 1])
        else:
            self.handlePlotModeChanged(
                self.mainWidget.allSampleTopPlot.chart().plot, plotMode
            )
            self.mainWidget.bottomPlotFrame.setVisible(False)
            self.mainWidget.allPlotSplitter.setSizes([1, 0])

    def handleSamplePlotModeChanged(self, index):
        plotMode = self.mainWidget.plotComboBox.itemData(index)
        self.plotModes[self.mainWidget.objectTree.currentObject()] = plotMode
        if self.isPlotModeSplittable(plotMode):
            top, bottom = self.splitPlotMode(plotMode)
            self.handlePlotModeChanged(
                self.mainWidget.sampleTopPlot.chart().plot, top
            )
            self.handlePlotModeChanged(
                self.mainWidget.sampleBottomPlot.chart().plot, bottom
            )
            self.mainWidget.bottomSamplePlotFrame.setVisible(True)
            self.mainWidget.samplePlotSplitter.setSizes([1, 1])
        else:
            self.handlePlotModeChanged(
                self.mainWidget.sampleTopPlot.chart().plot, plotMode
            )
            self.mainWidget.bottomSamplePlotFrame.setVisible(False)
            self.mainWidget.samplePlotSplitter.setSizes([1, 0])

    def handleContainerPlotModeChanged(self, index):
        plotMode = self.mainWidget.plotComboBox.itemData(index)
        self.plotModes[self.mainWidget.objectTree.currentObject()] = plotMode
        if self.isPlotModeSplittable(plotMode):
            top, bottom = self.splitPlotMode(plotMode)
            self.handlePlotModeChanged(
                self.mainWidget.containerTopPlot.chart().plot, top
            )
            self.handlePlotModeChanged(
                self.mainWidget.containerBottomPlot.chart().plot, bottom
            )
            self.mainWidget.bottomContainerPlotFrame.setVisible(True)
            self.mainWidget.containerPlotSplitter.setSizes([1, 1])
        else:
            self.handlePlotModeChanged(
                self.mainWidget.containerTopPlot.chart().plot, plotMode
            )
            self.mainWidget.bottomContainerPlotFrame.setVisible(False)
            self.mainWidget.containerPlotSplitter.setSizes([1, 0])

    @abstractmethod
    def isPlotModeSplittable(self, plotMode):
        return plotMode in SPLIT_PLOTS.keys()

    @abstractmethod
    def splitPlotMode(self, plotMode):
        return SPLIT_PLOTS[plotMode]

    def handlePlotModeChanged(self, plot, plotMode):
        plot(plotMode)

    def onException(self, cls, exception, tb):
        QMessageBox.critical(
            self.mainWidget,
            "GudPy Error",
            f"{''.join(traceback.format_exception(cls, exception, tb))}"
        )

    def export(self):
        exportDialog = ExportDialog(self.gudrunFile, self)
        exportDialog.widget.exec()
