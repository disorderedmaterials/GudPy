from abc import abstractmethod
import os
import sys
import shutil
import math
import traceback
from queue import Queue
import re
from PySide6.QtCore import (
    QFile,
    QFileInfo,
    QTimer,
    QThread,
    QProcess,
)
from PySide6.QtGui import QPainter, QIcon
from PySide6.QtUiTools import QUiLoader
from PySide6.QtWidgets import (
    QDialogButtonBox,
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMessageBox,
    QProgressBar,
    QSizePolicy,
    QStatusBar,
    QWidget,
    QMenu,
    QToolButton,
)
from PySide6.QtCharts import QChartView

from core.container import Container
from core import iterators
from core.sample import Sample
from gui.widgets.dialogs.export_dialog import ExportDialog

from gui.widgets.dialogs.iteration_dialog import (
    CompositionIterationDialog,
    DensityIterationDialog,
    InelasticitySubtractionIterationDialog,
    RadiusIterationDialog,
    ThicknessIterationDialog,
    TweakFactorIterationDialog,
)
from gui.widgets.dialogs.purge_dialog import PurgeDialog
from gui.widgets.dialogs.view_input_dialog import ViewInputDialog
from gui.widgets.dialogs.missing_files_dialog import MissingFilesDialog
from gui.widgets.dialogs.composition_dialog import CompositionDialog
from gui.widgets.dialogs.view_output_dialog import ViewOutputDialog
from gui.widgets.dialogs.configuration_dialog import ConfigurationDialog
from gudpy.gui.widgets.dialogs.composition_acceptance import (
    CompositionAcceptanceDialog,
)
from gui.widgets.dialogs.batch_processing_dialog import BatchProcessingDialog
from gui.widgets.core.gudpy_tree import GudPyTreeView
from gui.widgets.core.output_tree import OutputTreeView

from gui.widgets.tables.composition_table import CompositionTable
from gui.widgets.tables.ratio_composition_table import RatioCompositionTable
from gui.widgets.tables.beam_profile_table import BeamProfileTable
from gui.widgets.tables.grouping_parameter_table import GroupingParameterTable
from gui.widgets.tables.exponential_table import ExponentialTable
from gui.widgets.tables.resonance_table import ResonanceTable
from gui.widgets.tables.spectra_table import SpectraTable
from gui.widgets.tables.event_table import EventTable
from gui.widgets.tables.components_table import ComponentsList
from gui.widgets.core.exponential_spinbox import ExponentialSpinBox
from gui.widgets.tables.data_file_list import DataFilesList
from gui.widgets.charts.chart import GudPyChart
from gui.widgets.charts.chartview import GudPyChartView
from gui.widgets.charts.beam_plot import BeamChart
from gui.widgets.charts.enums import PlotModes, SPLIT_PLOTS

from core.enums import Format, Geometry
from gui.widgets.slots.instrument_slots import InstrumentSlots
from gui.widgets.slots.beam_slots import BeamSlots
from gui.widgets.slots.component_slots import ComponentSlots
from gui.widgets.slots.normalisation_slots import NormalisationSlots
from gui.widgets.slots.container_slots import ContainerSlots
from gui.widgets.slots.sample_background_slots import SampleBackgroundSlots
from gui.widgets.slots.sample_slots import SampleSlots
from gui.widgets.slots.output_slots import OutputSlots
# from gui.widgets.resources import resources_rc  # noqa
from core.file_library import GudPyFileLibrary
from core.gudrun_file import GudrunFile
from core.exception import ParserException
from core import config
from core.run_containers_as_samples import RunContainersAsSamples
from core.run_individual_files import RunIndividualFiles
from core.gud_file import GudFile
from core.utils import breplace, nthint
from gui.widgets.core.worker import (
    CompositionWorker,
    GudrunWorker,
    PurgeWorker
)


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
    iterator : Iterator | iterators.CompositionIterator
        Iterator to use in iterations.
    Methods
    -------
    initComponents()
        Loads the UI file for the GudPyMainWindow
    loadInputFile_()
        Loads an input file.
    saveInputFile()
        Saves the current GudPy file.
    updateGeometries(gudrunFile)()
        Updates geometries across objects.
    updateCompositions()
        Updates compositions across objects
        Deletes the current object.
    exit_()
        Exits
    """

    def __init__(self):
        """
        Constructs all the necessary attributes for the GudPyMainWindow object.
        Calls initComponents() to load the UI file.
        """
        super().__init__()
        self.modified = False
        self.clipboard = None
        self.results = {}

        self.allPlots = []
        self.plotModes = {}

        self.previousProcTitle = ""

        self.warning = ""

        self.initComponents()
        self.timer = QTimer(self)
        self.timer.setSingleShot(True)
        self.timer.timeout.connect(self.autosave)

    def initComponents(self):
        """
        Loads the UI file for the GudPyMainWindow.
        """
        if hasattr(sys, "_MEIPASS"):
            uifile = QFile(
                os.path.join(sys._MEIPASS, "ui_files", "mainWindow.ui")
            )
            current_dir = os.path.sep
        else:
            current_dir = os.path.dirname(os.path.realpath(__file__))
            uifile = QFile(
                os.path.join(current_dir, "../ui_files", "mainWindow.ui")
            )

        loader = QUiLoader()
        loader.registerCustomWidget(GudPyTreeView)
        loader.registerCustomWidget(OutputTreeView)
        loader.registerCustomWidget(GroupingParameterTable)
        loader.registerCustomWidget(BeamProfileTable)
        loader.registerCustomWidget(CompositionTable)
        loader.registerCustomWidget(RatioCompositionTable)
        loader.registerCustomWidget(ExponentialTable)
        loader.registerCustomWidget(ResonanceTable)
        loader.registerCustomWidget(SpectraTable)
        loader.registerCustomWidget(EventTable)
        loader.registerCustomWidget(DataFilesList)
        loader.registerCustomWidget(ComponentsList)
        loader.registerCustomWidget(CompositionIterationDialog)
        loader.registerCustomWidget(DensityIterationDialog)
        loader.registerCustomWidget(
            InelasticitySubtractionIterationDialog)
        loader.registerCustomWidget(RadiusIterationDialog)
        loader.registerCustomWidget(ThicknessIterationDialog)
        loader.registerCustomWidget(TweakFactorIterationDialog)
        loader.registerCustomWidget(PurgeDialog)
        loader.registerCustomWidget(ViewInputDialog)
        loader.registerCustomWidget(ViewOutputDialog)
        loader.registerCustomWidget(ExportDialog)
        loader.registerCustomWidget(CompositionDialog)
        loader.registerCustomWidget(ConfigurationDialog)
        loader.registerCustomWidget(CompositionAcceptanceDialog)
        loader.registerCustomWidget(BatchProcessingDialog)
        loader.registerCustomWidget(ExponentialSpinBox)
        loader.registerCustomWidget(GudPyChartView)
        self.ui = loader.load(uifile)

        self.ui.statusBar_ = QStatusBar(self)
        self.ui.statusBarWidget = QWidget(self.ui.statusBar_)
        self.ui.statusBarLayout = QHBoxLayout(
            self.ui.statusBarWidget
        )
        self.ui.currentTaskLabel = QLabel(
            self.ui.statusBarWidget
        )
        self.ui.currentTaskLabel.setText("No task running.")
        self.ui.currentTaskLabel.setSizePolicy(
            QSizePolicy(QSizePolicy.Minimum, QSizePolicy.Preferred)
        )
        self.ui.stopTaskButton = QToolButton(
            self.ui.statusBarWidget
        )
        self.ui.stopTaskButton.setIcon(QIcon(":/icons/stop"))
        self.ui.stopTaskButton.clicked.connect(self.stopProc)
        self.ui.stopTaskButton.setEnabled(False)

        self.ui.stopTaskButton.setSizePolicy(
            QSizePolicy(QSizePolicy.Minimum, QSizePolicy.Preferred)
        )

        self.ui.progressBar = QProgressBar(
            self.ui.statusBarWidget
        )
        self.ui.progressBar.setSizePolicy(
            QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        )
        self.ui.progressBar.setTextVisible(False)
        self.ui.statusBarLayout.addWidget(
            self.ui.currentTaskLabel
        )
        self.ui.statusBarLayout.addWidget(
            self.ui.stopTaskButton
        )
        self.ui.statusBarLayout.addWidget(self.ui.progressBar)
        self.ui.statusBarWidget.setLayout(
            self.ui.statusBarLayout
        )
        self.ui.statusBar_.addWidget(self.ui.statusBarWidget)
        self.ui.setStatusBar(self.ui.statusBar_)

        self.ui.beamPlot = QChartView(self.ui)
        self.ui.beamPlot.setRenderHint(QPainter.Antialiasing)

        self.ui.beamProfileLayout.insertWidget(
            1, self.ui.beamPlot
        )

        self.ui.beamChart = BeamChart()

        self.ui.beamPlot.setChart(self.ui.beamChart)

        self.ui.sampleTopPlot = GudPyChartView(self.ui)

        self.ui.topPlotLayout.addWidget(self.ui.sampleTopPlot)

        self.ui.sampleBottomPlot = GudPyChartView(self.ui)

        self.ui.bottomPlotLayout.addWidget(
            self.ui.sampleBottomPlot
        )

        self.ui.bottomSamplePlotFrame.setVisible(False)

        self.ui.containerTopPlot = GudPyChartView(self.ui)

        self.ui.topContainerPlotLayout.addWidget(
            self.ui.containerTopPlot
        )

        self.ui.containerBottomPlot = GudPyChartView(self.ui)

        self.ui.bottomContainerPlotLayout.addWidget(
            self.ui.containerBottomPlot
        )

        self.ui.bottomContainerPlotFrame.setVisible(False)

        self.ui.allSampleTopPlot = GudPyChartView(self.ui)

        self.ui.topAllPlotLayout.addWidget(
            self.ui.allSampleTopPlot
        )

        self.ui.allSampleBottomPlot = GudPyChartView(self.ui)

        self.ui.bottomAllPlotLayout.addWidget(
            self.ui.allSampleBottomPlot
        )

        self.ui.bottomPlotFrame.setVisible(False)

        for plotMode in [
            plotMode
            for plotMode in PlotModes
            if plotMode
            not in [
                PlotModes.SF,
                PlotModes.SF_RDF,
                PlotModes.SF_CANS,
                PlotModes.SF_RDF_CANS,
            ]
        ]:
            self.ui.allPlotComboBox.addItem(plotMode.name, plotMode)

        self.ui.allPlotComboBox.currentIndexChanged.connect(
            self.handleAllPlotModeChanged
        )

        for plotMode in [
            plotMode for plotMode in PlotModes if "(Cans)" not in plotMode.name
        ]:
            self.ui.plotComboBox.addItem(plotMode.name, plotMode)

        self.ui.plotComboBox.currentIndexChanged.connect(
            self.handleSamplePlotModeChanged
        )

        for plotMode in [
            plotMode for plotMode in PlotModes if "(Cans)" in plotMode.name
        ]:
            self.ui.containerPlotComboBox.addItem(
                plotMode.name, plotMode
            )

        self.ui.containerPlotComboBox.currentIndexChanged.connect(
            self.handleContainerPlotModeChanged
        )

        self.ui.setWindowTitle("GudPy")
        self.ui.show()

        self.instrumentSlots = InstrumentSlots(self.ui, self)
        self.beamSlots = BeamSlots(self.ui, self)
        self.componentSlots = ComponentSlots(self.ui, self)
        self.normalisationSlots = NormalisationSlots(self.ui, self)
        self.sampleBackgroundSlots = SampleBackgroundSlots(
            self.ui, self
        )
        self.sampleSlots = SampleSlots(self.ui, self)
        self.containerSlots = ContainerSlots(self.ui, self)
        self.outputSlots = OutputSlots(self.ui, self)

        actionMap = {
            name: lambda: self.ui.objectTree.insertContainer(
                container=Container(config=path)
            )
            for name, path in config.containerConfigurations.items()
        }
        insertContainerFromTemplate = QMenu(
            "From Template..", self.ui.insertContainerMenu
        )
        for name, action in actionMap.items():
            insertContainerFromTemplate.addAction(name, action)

        self.ui.insertContainerMenu.addMenu(
            insertContainerFromTemplate
        )

        self.setActionsEnabled(False)
        self.ui.tabWidget.setVisible(False)
        self.setWindowModified(False)

    def processStopped(self):
        self.setControlsEnabled(True)
        self.ui.progressBar.setValue(0)
        self.ui.currentTaskLabel.setText("No task running.")

    def processStarted(self):
        self.setControlsEnabled(False)
        self.ui.progressBar.setValue(0)

    def tryLoadAutosaved(self, path):
        dir_ = os.path.dirname(path)
        for f in os.listdir(dir_):
            if os.path.abspath(f) == path + ".autosave":
                with open(path, "r", encoding="utf-8") as fp:
                    original = fp.readlines()
                with open(f, "r", encoding="utf-8") as fp:
                    auto = fp.readlines()
                if original[:-5] == auto[:-5]:
                    return path

                autoFileInfo = QFileInfo(f)
                autoLastModified = autoFileInfo.lastModified()

                fileInfo = QFileInfo(path)
                lastModified = fileInfo.lastModified()

                if autoLastModified > lastModified:
                    messageBox = QMessageBox(self.ui)
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
                    if result == QMessageBox.Yes:
                        return os.path.abspath(f)
                    else:
                        return path
                else:
                    return path
        return path

    def updateWidgets(self, gudrunFile, fromFile=False):
        self.widgetsRefreshing = True
        if fromFile:
            gudrunFile = GudrunFile(
                loadFile=gudrunFile.path,
                format=gudrunFile.format)
        self.ui.gudrunFile = gudrunFile
        self.ui.tabWidget.setVisible(True)
        self.instrumentSlots.setInstrument(gudrunFile.instrument)
        self.beamSlots.setBeam(gudrunFile.beam)
        self.componentSlots.setComponents(gudrunFile.components)
        self.normalisationSlots.setNormalisation(gudrunFile.normalisation)

        if len(gudrunFile.sampleBackgrounds):
            self.sampleBackgroundSlots.setSampleBackground(
                gudrunFile.sampleBackgrounds[0]
            )

            if len(gudrunFile.sampleBackgrounds[0].samples):
                self.sampleSlots.setSample(
                    gudrunFile.sampleBackgrounds[0].samples[0]
                )

                if len(
                    gudrunFile.sampleBackgrounds[0].samples[0].containers
                ):
                    self.containerSlots.setContainer(
                        gudrunFile.sampleBackgrounds[0]
                        .samples[0]
                        .containers[0]
                    )
        self.setActionsEnabled(True)
        self.ui.objectTree.buildTree(gudrunFile, self)
        self.ui.objectTree.model().dataChanged.connect(
            self.handleObjectsChanged
        )
        self.updateResults(gudrunFile)
        self.widgetsRefreshing = False

    def handleObjectsChanged(self):
        if not self.widgetsRefreshing:
            self.setModified()

    def updateGeometries(self, gudrunFile):
        """
        Iteratively updates geometries of objects,
        where the Geometry is SameAsBeam.
        """
        if gudrunFile.normalisation.geometry == Geometry.SameAsBeam:
            self.normalisationSlots.widgetsRefreshing = True
            self.ui.geometryInfoStack.setCurrentIndex(
                config.geometry.value
            )
            self.normalisationSlots.widgetsRefreshing = False
        for i, sampleBackground in enumerate(
            gudrunFile.sampleBackgrounds
        ):
            for j, sample in enumerate(sampleBackground.samples):
                gudrunFile.sampleBackgrounds[i].samples[
                    j
                ].geometry = config.geometry
                for k in range(len(sample.containers)):
                    sample = gudrunFile.sampleBackgrounds[i].samples[j]
                    sample.containers[k].geometry = config.geometry

    def updateCompositions(self):
        """
        Iteratively shares compositions between objects,
        for copying and pasting compositions between eachother.
        """
        self.ui.normalisationCompositionTable.farmCompositions()
        self.ui.sampleCompositionTable.farmCompositions()
        self.ui.sampleRatioCompositionTable.farmCompositions()
        self.ui.containerCompositionTable.farmCompositions()

    def focusResult(self):
        if self.ui.objectStack.currentIndex() == 5 and isinstance(
            self.ui.objectTree.currentObject(), Sample
        ):
            try:
                topPlot, bottomPlot, gudFile = self.results[
                    self.ui.objectTree.currentObject()
                ]
            except KeyError:
                self.updateSamples()
                topPlot, bottomPlot, gudFile = self.results[
                    self.ui.objectTree.currentObject()
                ]
            self.ui.sampleTopPlot.setChart(topPlot)
            self.ui.sampleBottomPlot.setChart(bottomPlot)

            plotsMap = {
                PlotModes.SF: 0,
                PlotModes.SF_MINT01: 1,
                PlotModes.SF_MDCS01: 2,
                PlotModes.RDF: 3,
                PlotModes.SF_RDF: 4,
                PlotModes.SF_MINT01_RDF: 5,
                PlotModes.SF_MDCS01_RDF: 6,
            }

            if (
                self.ui.objectTree.currentObject()
                in self.plotModes.keys()
            ):
                self.ui.plotComboBox.setCurrentIndex(
                    plotsMap[
                        self.plotModes[
                            self.ui.objectTree.currentObject()
                        ]
                    ]
                )
            else:
                self.ui.plotComboBox.setCurrentIndex(0)

            if gudFile:
                dcsLevel = gudFile.averageLevelMergedDCS
                self.ui.dcsLabel.setText(f"DCS Level: {dcsLevel}")
                self.ui.resultLabel.setText(gudFile.output)
                if gudFile.err:
                    self.ui.resultLabel.setStyleSheet(
                        "background-color: red"
                    )
                else:
                    self.ui.resultLabel.setStyleSheet(
                        "background-color: green"
                    )

                tweakFactor = gudFile.suggestedTweakFactor
                self.ui.suggestedTweakFactorLabel.setText(
                    f"Suggested Tweak Factor: {tweakFactor}"
                )
            else:
                self.ui.dcsLabel.setText("DCS Level")
                self.ui.resultLabel.setText("Error")
                self.ui.resultLabel.setStyleSheet("")
                self.ui.suggestedTweakFactorLabel.setText(
                    "Suggested Tweak Factor"
                )
        elif self.ui.objectStack.currentIndex() == 6 and isinstance(
            self.ui.objectTree.currentObject(), Container
        ):
            try:
                topPlot, bottomPlot, gudFile = self.results[
                    self.ui.objectTree.currentObject()
                ]
            except KeyError:
                self.updateSamples()
                topPlot, bottomPlot, gudFile = self.results[
                    self.ui.objectTree.currentObject()
                ]
            if sum(
                [
                    *[s.count() for s in topPlot.series()],
                    *[s.count() for s in bottomPlot.series()],
                ]
            ):
                self.ui.containerSplitter.setSizes([2, 1])
            else:
                self.ui.containerSplitter.setSizes([1, 0])

            self.ui.containerTopPlot.setChart(topPlot)
            self.ui.containerBottomPlot.setChart(bottomPlot)

            plotsMap = {
                PlotModes.SF_CANS: 0,
                PlotModes.SF_MINT01_CANS: 1,
                PlotModes.SF_MDCS01_CANS: 2,
                PlotModes.RDF_CANS: 3,
                PlotModes.SF_RDF_CANS: 4,
                PlotModes.SF_MINT01_RDF_CANS: 5,
                PlotModes.SF_MDCS01_RDF_CANS: 6,
            }

            if (
                self.ui.objectTree.currentObject()
                in self.plotModes.keys()
            ):
                self.ui.plotComboBox.setCurrentIndex(
                    plotsMap[
                        self.plotModes[
                            self.ui.objectTree.currentObject()
                        ]
                    ]
                )
            else:
                self.ui.plotComboBox.setCurrentIndex(0)

            if gudFile:
                dcsLevel = gudFile.averageLevelMergedDCS
                self.ui.containerDcsLabel.setText(
                    f"DCS Level: {dcsLevel}"
                )
                self.ui.containerResultLabel.setText(gudFile.output)
                if gudFile.err:
                    self.ui.containerResultLabel.setStyleSheet(
                        "background-color: red"
                    )
                else:
                    self.ui.containerResultLabel.setStyleSheet(
                        "background-color: green"
                    )

                tweakFactor = gudFile.suggestedTweakFactor
                self.ui.containerSuggestedTweakFactorLabel.setText(
                    f"Suggested Tweak Factor: {tweakFactor}"
                )

    def updateSamples(self, gudrunFile):
        samples = [
            *self.ui.objectTree.getSamples(),
            *self.ui.objectTree.getContainers(),
        ]
        for sample in samples:
            topChart = GudPyChart(gudrunFile)
            topChart.addSample(sample)
            bottomChart = GudPyChart(gudrunFile)
            bottomChart.addSample(sample)
            if sample not in self.plotModes.keys():
                plotMode = (
                    PlotModes.SF
                    if isinstance(sample, Sample)
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
            if len(sample.dataFiles):
                path = breplace(
                    sample.dataFiles[0],
                    gudrunFile.instrument.dataFileType,
                    "gud",
                )
                if not os.path.exists(path):
                    path = os.path.join(
                        gudrunFile.instrument.GudrunInputFileDir, path
                    )
            gf = GudFile(path) if path and os.path.exists(path) else None
            self.results[sample] = [topChart, bottomChart, gf]

    def updateAllSamples(self, gudrunFile):
        samples = [
            *self.ui.objectTree.getSamples(),
            *self.ui.objectTree.getContainers(),
        ]
        allTopChart = GudPyChart(gudrunFile)
        allTopChart.addSamples(samples)
        allTopChart.plot(
            self.ui.allPlotComboBox.itemData(
                self.ui.allPlotComboBox.currentIndex()
            )
        )
        allBottomChart = GudPyChart(gudrunFile)
        allBottomChart.addSamples(samples)
        self.allPlots = [allTopChart, allBottomChart]
        self.ui.allSampleTopPlot.setChart(allTopChart)
        self.ui.allSampleBottomPlot.setChart(allBottomChart)

    def updateResults(self, gudrunFile):
        self.updateSamples(gudrunFile)
        self.updateAllSamples(gudrunFile)
        self.focusResult()

    def updateComponents(self, gudrunFile):
        """
        Updates geometries and compositions.
        """
        self.updateGeometries(gudrunFile)
        self.updateCompositions()
        self.focusResult()

    def sendError(self, error: str):
        QtWidgets.QMessageBox.critical(
            self.ui, "GudPy Error", str(error))

    def sendWarning(self, warning: str):
        QtWidgets.QMessageBox.warning(
            self.ui,
            "GudPy Warning",
            warning
        )

    def iterationResultsDialog(self, results):
        messageBox = QMessageBox(self.ui)
        messageBox.setWindowTitle("GudPy Iteration Results")
        results = '\n'.join(
            [f"{key}: {value}" for key, value in results.items()])
        messageBox.setText(results)
        messageBox.exec()

    def purgeOptionsMessageBox(self, text):
        messageBox = QMessageBox(self.ui)
        messageBox.setWindowTitle("GudPy Warning")
        messageBox.setText(text)
        messageBox.addButton(QMessageBox.Yes)
        messageBox.addButton(QMessageBox.No)
        messageBox.addButton(QMessageBox.Cancel)
        return messageBox.exec()

    def batchProcessing(self):
        if not self.prepareRun():
            self.cleanupRun()
            return False
        batchProcessingDialog = BatchProcessingDialog(
            gudrunFile, self.ui
        )
        batchProcessingDialog.widget.exec()
        if not batchProcessingDialog.batchProcessor:
            self.setControlsEnabled(True)
        else:
            self.queue = batchProcessingDialog.queue
            self.outputBatches = {}
            self.text = batchProcessingDialog.text
            self.numberIterations = batchProcessingDialog.numberIterations
            self.currentIteration = 0
            self.batchProcessor = batchProcessingDialog.batchProcessor
            self.ui.currentTaskLabel.setText(self.text)
            self.ui.stopTaskButton.setEnabled(True)
            self.nextBatchProcess()

    def batchProcessFinished(self):
        self.outputBatches[self.currentIteration + 1] = self.output
        self.output = ""
        self.currentIteration += 1
        self.nextBatchProcess()

    def nextBatchProcess(self):
        if not self.queue.empty():
            task = self.queue.get()
            if isinstance(task[0], QProcess):
                self.proc, func, args = task
                self.proc.readyReadStandardOutput.connect(
                    self.progressBatchProcess
                )
                self.proc.finished.connect(self.batchProcessFinished)
                self.proc.setWorkingDirectory(
                    gudrunFile.instrument.GudrunInputFileDir
                )
                func(*args)
                self.proc.start()
            else:
                func, args = task
                ret = func(*args)
                if isinstance(ret, bool) and ret:
                    self.batchProcessingFinished()
                elif isinstance(ret, tuple) and ret[0]:
                    with self.queue.mutex:
                        remaining = list(self.queue.queue)
                    n = remaining.index(None)
                    for _ in range(n + 1):
                        self.queue.get()
                    self.nextBatchProcess()
                else:
                    self.nextBatchProcess()
        else:
            self.setControlsEnabled(True)
            self.batchProcessingFinished()

    def progressBatchProcess(self):
        progress = self.progressIncrementDCS(
            self.batchProcessor.batchedGudrunFile
        )
        if progress == -1:
            self.error = (
                f"An error occurred. See the following traceback"
                f" from gudrun_dcs\n{self.error}"
            )
            return
        progress /= self.numberIterations
        progress += self.ui.progressBar.value()
        self.ui.progressBar.setValue(
            progress if progress <= 100 else 100
        )

    def batchProcessingFinished(self, ec, es):
        self.setControlsEnabled(True)
        self.queue = Queue()
        self.proc = None
        self.text = "No task running."
        self.ui.currentTaskLabel.setText(self.text)
        self.ui.progressBar.setValue(0)
        self.ui.stopTaskButton.setEnabled(False)
        self.outputSlots.setOutput(
            self.outputBatches,
            "gudrun_dcs",
            gudrunFile=self.batchProcessor.batchedGudrunFile,
        )
        self.outputBatches = {}
        self.output = ""

    def autosave(self):
        if (
            gudrunFile
            and gudrunFile.path
            and not self.proc
            and not self.workerThread
        ):
            autosavePath = os.path.join(
                gudrunFile.projectDir,
                gudrunFile.filename + ".autosave")
            gudrunFile.write_out(path=autosavePath, overwrite=True)

    def setModified(self):
        if not self.modified:
            if gudrunFile.path:
                self.modified = True
                self.ui.setWindowModified(True)
                self.ui.save.setEnabled(True)
        if not self.proc:
            self.timer.start(30000)

    def setUnModified(self):
        self.ui.setWindowModified(False)
        self.modified = False
        self.ui.save.setEnabled(False)

    def setControlsEnabled(self, state):
        self.ui.instrumentPage.setEnabled(state)
        self.ui.beamPage.setEnabled(state)
        self.ui.componentPage.setEnabled(state)
        self.ui.normalisationPage.setEnabled(state)
        self.ui.sampleTab.setEnabled(state)
        self.ui.advancedTab.setEnabled(state)
        self.ui.containerPage.setEnabled(state)
        self.ui.sampleBackgroundPage.setEnabled(state)
        self.ui.objectTree.setContextEnabled(state)
        self.ui.objectTree.model().setEnabled(state)
        self.setTreeActionsEnabled(state)

        self.ui.runPurge.setEnabled(state)
        self.ui.runGudrun.setEnabled(state)
        self.ui.iterateGudrun.setEnabled(state)
        self.ui.runFilesIndividually.setEnabled(state)
        self.ui.batchProcessing.setEnabled(state)
        self.ui.viewLiveInputFile.setEnabled(state)
        self.ui.save.setEnabled(
            state & self.modified & len(gudrunFile.path) > 0
            if gudrunFile.path
            else False
        )
        self.ui.exportInputFile.setEnabled(state)
        self.ui.saveAs.setEnabled(state)
        self.ui.loadInputFile.setEnabled(state)
        self.ui.loadProject.setEnabled(state)
        self.ui.exportArchive.setEnabled(state)
        self.ui.new_.setEnabled(state)
        self.ui.checkFilesExist.setEnabled(state)
        self.ui.runFilesIndividually.setEnabled(state)
        self.ui.runContainersAsSamples.setEnabled(state)

    def setActionsEnabled(self, state):
        self.setTreeActionsEnabled(state)

        self.ui.runPurge.setEnabled(state)
        self.ui.runGudrun.setEnabled(state)
        self.ui.iterateGudrun.setEnabled(state)
        self.ui.runFilesIndividually.setEnabled(state)
        self.ui.checkFilesExist.setEnabled(state)
        self.ui.runFilesIndividually.setEnabled(state)
        self.ui.runContainersAsSamples.setEnabled(state)
        self.ui.batchProcessing.setEnabled(state)
        self.ui.viewLiveInputFile.setEnabled(state)
        self.ui.save.setEnabled(state & self.modified)
        self.ui.exportInputFile.setEnabled(state)
        self.ui.exportArchive.setEnabled(state)

    def setTreeActionsEnabled(self, state):
        self.ui.insertSampleBackground.setEnabled(state)
        self.ui.insertSample.setEnabled(state)
        self.ui.insertContainerMenu.setEnabled(state)
        self.ui.copy.setEnabled(state)
        self.ui.cut.setEnabled(state)
        self.ui.paste.setEnabled(state)
        self.ui.delete_.setEnabled(state)

    def progressDCS(self, stdout):
        progress = self.progressIncrementDCS(gudrunFile, stdout)
        if progress == -1:
            self.queue = Queue()
            self.error = (
                f"An error occurred. See the following traceback"
                f" from gudrun_dcs\n{self.error}"
            )
            return
        if isinstance(self.iterator, iterators.InelasticitySubtraction):
            progress /= 2

    def progressPurge(self, stdout):
        progress, finished, detectors = self.progressIncrementPurge(stdout)
        if progress == -1:
            self.error = (
                f"An error occurred. See the following traceback"
                f" from purge_det\n{self.error}"
            )
            gudrunFile.purged = False
            self.cleanupRun()
            return
        progress += self.ui.progressBar.value()
        self.ui.progressBar.setValue(
            progress if progress <= 100 else 100
        )

        if finished:
            gudrunFile.purged = True
            thresh = gudrunFile.instrument.goodDetectorThreshold
            if thresh and detectors < thresh:
                self.warning = (
                    f"{detectors} detectors made it through the purge."
                    " The acceptable minimum for "
                    f"{gudrunFile.instrument.name.name} is {thresh}"
                )
            self.ui.goodDetectorsLabel.setText(
                f"Number of Good Detectors: {detectors}"
            )
            self.cleanupRun()

    def procStarted(self):
        self.ui.currentTaskLabel.setText(
            self.worker.PROCESS
        )
        self.ui.stopTaskButton.setEnabled(True)
        self.previousProcTitle = self.ui.currentTaskLabel.text()
        self.output = ""

    def procFinished(self):
        if "purge_det" not in self.ui.currentTaskLabel.text():
            try:
                self.updateResults()
            except ParserException:
                QMessageBox.warning(
                    self.ui,
                    "GudPy Warning",
                    "The process did not entirely finish,"
                    " please check your parameters.",
                )
            self.outputSlots.setOutput(
                output, "gudrun_dcs", gudrunFile=gudrunFile
            )
        else:
            self.outputSlots.setOutput(
                output, "purge_det", gudrunFile=gudrunFile
            )
        self.outputIterations = {}
        self.output = ""
        if self.queue.empty():
            if self.warning:
                QMessageBox.warning(
                    self.ui, "GudPy Warning", repr(self.warning)
                )
                self.warning = ""
            self.cleanupRun()
        if not self.queue.empty():
            args, kwargs = self.queue.get()
            self.makeProc(*args, **kwargs)
            # self.makeProc(*self.queue.get())

    def stopProc(self):
        self.queue = Queue()
        if self.proc:
            if self.proc.state() == QProcess.Running:
                self.cleanupRun()
                self.proc.kill()
        if self.workerThread:
            self.workerThread.requestInterruption()

    def viewInput(self):
        self.currentState = str(gudrunFile)
        viewInputDialog = ViewInputDialog(gudrunFile, self)
        viewInputDialog.widget.exec_()

    def handleAllPlotModeChanged(self, index):
        plotMode = self.ui.allPlotComboBox.itemData(index)
        self.plotModes["All"] = plotMode
        if self.isPlotModeSplittable(plotMode):
            top, bottom = self.splitPlotMode(plotMode)
            self.handlePlotModeChanged(
                self.ui.allSampleTopPlot.chart().plot, top
            )
            self.handlePlotModeChanged(
                self.ui.allSampleBottomPlot.chart().plot, bottom
            )
            self.ui.bottomPlotFrame.setVisible(True)
            self.ui.allPlotSplitter.setSizes([1, 1])
        else:
            self.handlePlotModeChanged(
                self.ui.allSampleTopPlot.chart().plot, plotMode
            )
            self.ui.bottomPlotFrame.setVisible(False)
            self.ui.allPlotSplitter.setSizes([1, 0])

    def handleSamplePlotModeChanged(self, index):
        plotMode = self.ui.plotComboBox.itemData(index)
        self.plotModes[self.ui.objectTree.currentObject()] = plotMode
        if self.isPlotModeSplittable(plotMode):
            top, bottom = self.splitPlotMode(plotMode)
            self.handlePlotModeChanged(
                self.ui.sampleTopPlot.chart().plot, top
            )
            self.handlePlotModeChanged(
                self.ui.sampleBottomPlot.chart().plot, bottom
            )
            self.ui.bottomSamplePlotFrame.setVisible(True)
            self.ui.samplePlotSplitter.setSizes([1, 1])
        else:
            self.handlePlotModeChanged(
                self.ui.sampleTopPlot.chart().plot, plotMode
            )
            self.ui.bottomSamplePlotFrame.setVisible(False)
            self.ui.samplePlotSplitter.setSizes([1, 0])

    def handleContainerPlotModeChanged(self, index):
        plotMode = self.ui.plotComboBox.itemData(index)
        self.plotModes[self.ui.objectTree.currentObject()] = plotMode
        if self.isPlotModeSplittable(plotMode):
            top, bottom = self.splitPlotMode(plotMode)
            self.handlePlotModeChanged(
                self.ui.containerTopPlot.chart().plot, top
            )
            self.handlePlotModeChanged(
                self.ui.containerBottomPlot.chart().plot, bottom
            )
            self.ui.bottomContainerPlotFrame.setVisible(True)
            self.ui.containerPlotSplitter.setSizes([1, 1])
        else:
            self.handlePlotModeChanged(
                self.ui.containerTopPlot.chart().plot, plotMode
            )
            self.ui.bottomContainerPlotFrame.setVisible(False)
            self.ui.containerPlotSplitter.setSizes([1, 0])

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
            self.ui,
            "GudPy Error",
            f"{''.join(traceback.format_exception(cls, exception, tb))}",
        )

    def export(self):
        exportDialog = ExportDialog(gudrunFile, self)
        exportDialog.widget.exec()

    def cleanup(self):
        self.stopProc()
        self.autosave()
