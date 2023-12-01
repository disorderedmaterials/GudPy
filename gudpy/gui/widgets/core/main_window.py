from abc import abstractmethod
import os
import sys
import math
import traceback
import tempfile
from queue import Queue
from collections.abc import Sequence
import re
from PySide6.QtCore import (
    QFile,
    QFileInfo,
    QTimer,
    QThread,
    QProcess,
    QElapsedTimer,
    QCoreApplication,
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
    QPushButton,
    QSizePolicy,
    QStatusBar,
    QWidget,
    QMenu,
    QToolButton,
)
from PySide6.QtCharts import QChartView

from core.container import Container
from core.iterators.composition import CompositionIterator
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
from gui.widgets.dialogs.composition_acceptance_dialog import (
    CompositionAcceptanceDialog,
)
from gui.widgets.dialogs.nexus_processing_dialog import NexusProcessingDialog
from gui.widgets.dialogs.batch_processing_dialog import BatchProcessingDialog
from gui.widgets.core.gudpy_tree import GudPyTreeView
from gui.widgets.core.output_tree import OutputTreeView

from gui.widgets.tables.composition_table import CompositionTable
from gui.widgets.tables.ratio_composition_table import RatioCompositionTable
from gui.widgets.tables.beam_profile_table import BeamProfileTable
from gui.widgets.tables.grouping_parameter_table import GroupingParameterTable
from gui.widgets.tables.exponential_table import ExponentialTable
from gui.widgets.tables.resonance_table import ResonanceTable
from gui.widgets.tables.pulse_table import PulseTable
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
from gui.widgets.resources import resources_rc  # noqa
from core.file_library import GudPyFileLibrary
from core.gudrun_file import GudrunFile
from core.exception import ParserException
from core import config
from core.run_containers_as_samples import RunContainersAsSamples
from core.run_individual_files import RunIndividualFiles
from core.gud_file import GudFile
from core.utils import breplace, nthint
from gui.widgets.core.worker import CompositionWorker


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
    iterator : Iterator | CompositionIterator
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
        Exits
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
        self.nexusProcessingOutput = {}
        self.outputIterations = {}
        self.previousProcTitle = ""
        self.error = ""
        self.cwd = os.getcwd()
        self.warning = ""
        self.worker = None
        self.workerThread = None
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
        loader.registerCustomWidget(PulseTable)
        loader.registerCustomWidget(SpectraTable)
        loader.registerCustomWidget(EventTable)
        loader.registerCustomWidget(DataFilesList)
        loader.registerCustomWidget(ComponentsList)
        loader.registerCustomWidget(CompositionIterationDialog)
        loader.registerCustomWidget(DensityIterationDialog)
        loader.registerCustomWidget(
            InelasticitySubtractionIterationDialog
        )
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
        loader.registerCustomWidget(NexusProcessingDialog)
        loader.registerCustomWidget(BatchProcessingDialog)
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
        self.mainWidget.stopTaskButton = QToolButton(
            self.mainWidget.statusBarWidget
        )
        self.mainWidget.stopTaskButton.setIcon(QIcon(":/icons/stop"))
        self.mainWidget.stopTaskButton.clicked.connect(self.stopProc)
        self.mainWidget.stopTaskButton.setEnabled(False)

        self.mainWidget.stopTaskButton.setSizePolicy(
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
        self.mainWidget.statusBarLayout.addWidget(
            self.mainWidget.stopTaskButton
        )
        self.mainWidget.statusBarLayout.addWidget(self.mainWidget.progressBar)
        self.mainWidget.statusBarWidget.setLayout(
            self.mainWidget.statusBarLayout
        )
        self.mainWidget.statusBar_.addWidget(self.mainWidget.statusBarWidget)
        self.mainWidget.setStatusBar(self.mainWidget.statusBar_)

        self.mainWidget.beamPlot = QChartView(self.mainWidget)
        self.mainWidget.beamPlot.setRenderHint(QPainter.Antialiasing)

        self.mainWidget.beamProfileLayout.insertWidget(
            1, self.mainWidget.beamPlot
        )

        self.mainWidget.beamChart = BeamChart()

        self.mainWidget.beamPlot.setChart(self.mainWidget.beamChart)

        self.mainWidget.sampleTopPlot = GudPyChartView(self.mainWidget)

        self.mainWidget.topPlotLayout.addWidget(self.mainWidget.sampleTopPlot)

        self.mainWidget.sampleBottomPlot = GudPyChartView(self.mainWidget)

        self.mainWidget.bottomPlotLayout.addWidget(
            self.mainWidget.sampleBottomPlot
        )

        self.mainWidget.bottomSamplePlotFrame.setVisible(False)

        self.mainWidget.containerTopPlot = GudPyChartView(self.mainWidget)

        self.mainWidget.topContainerPlotLayout.addWidget(
            self.mainWidget.containerTopPlot
        )

        self.mainWidget.containerBottomPlot = GudPyChartView(self.mainWidget)

        self.mainWidget.bottomContainerPlotLayout.addWidget(
            self.mainWidget.containerBottomPlot
        )

        self.mainWidget.bottomContainerPlotFrame.setVisible(False)

        self.mainWidget.allSampleTopPlot = GudPyChartView(self.mainWidget)

        self.mainWidget.topAllPlotLayout.addWidget(
            self.mainWidget.allSampleTopPlot
        )

        self.mainWidget.allSampleBottomPlot = GudPyChartView(self.mainWidget)

        self.mainWidget.bottomAllPlotLayout.addWidget(
            self.mainWidget.allSampleBottomPlot
        )

        self.mainWidget.bottomPlotFrame.setVisible(False)

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
            self.mainWidget.allPlotComboBox.addItem(plotMode.name, plotMode)

        self.mainWidget.allPlotComboBox.currentIndexChanged.connect(
            self.handleAllPlotModeChanged
        )

        for plotMode in [
            plotMode for plotMode in PlotModes if "(Cans)" not in plotMode.name
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
        self.mainWidget.runPurge.triggered.connect(self.runPurge_)
        self.mainWidget.runGudrun.triggered.connect(self.runGudrun_)

        self.mainWidget.iterateInelasticitySubtractions.triggered.connect(
            lambda: self.iterateGudrun(
                InelasticitySubtractionIterationDialog,
                "iterateInelasticitySubtractionsDialog",
            )
        )

        self.mainWidget.iterateTweakFactor.triggered.connect(
            lambda: self.iterateGudrun(
                TweakFactorIterationDialog, "iterateTweakFactorDialog"
            )
        )

        self.mainWidget.iterateDensity.triggered.connect(
            lambda: self.iterateGudrun(
                DensityIterationDialog, "iterateDensityDialog"
            )
        )

        self.mainWidget.iterateThickness.triggered.connect(
            lambda: self.iterateGudrun(
                ThicknessIterationDialog, "iterateThicknessDialog"
            )
        )

        self.mainWidget.iterateRadius.triggered.connect(
            lambda: self.iterateGudrun(
                RadiusIterationDialog, "iterateRadiusDialog"
            )
        )

        self.mainWidget.iterateComposition.triggered.connect(
            lambda: self.iterateGudrun(
                CompositionIterationDialog, "iterateCompositionDialog"
            )
        )

        self.mainWidget.runContainersAsSamples.triggered.connect(
            self.runContainersAsSamples
        )

        self.mainWidget.runFilesIndividually.triggered.connect(
            self.runFilesIndividually
        )

        self.mainWidget.batchProcessing.triggered.connect(self.batchProcessing)

        self.mainWidget.checkFilesExist.triggered.connect(
            self.checkFilesExist_
        )

        self.mainWidget.save.triggered.connect(self.saveInputFile)

        self.mainWidget.saveAs.triggered.connect(self.saveInputFileAs)

        self.mainWidget.viewLiveInputFile.triggered.connect(self.viewInput)

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
            name: lambda: self.mainWidget.objectTree.insertContainer(
                container=Container(config_=path)
            )
            for name, path in config.containerConfigurations.items()
        }
        insertContainerFromTemplate = QMenu(
            "From Template..", self.mainWidget.insertContainerMenu
        )
        for name, action in actionMap.items():
            insertContainerFromTemplate.addAction(name, action)

        self.mainWidget.insertContainerMenu.addMenu(
            insertContainerFromTemplate
        )

        self.mainWidget.copy.triggered.connect(self.mainWidget.objectTree.copy)
        self.mainWidget.cut.triggered.connect(self.mainWidget.objectTree.cut)
        self.mainWidget.paste.triggered.connect(
            self.mainWidget.objectTree.paste
        )
        self.mainWidget.delete_.triggered.connect(
            self.mainWidget.objectTree.del_
        )

        self.mainWidget.loadInputFile.triggered.connect(self.loadInputFile_)

        self.mainWidget.new_.triggered.connect(self.newInputFile)

        self.mainWidget.objectStack.currentChanged.connect(
            self.updateComponents
        )

        self.mainWidget.exportArchive.triggered.connect(self.export)

        self.mainWidget.exit.triggered.connect(self.exit_)

        self.setActionsEnabled(False)
        self.mainWidget.tabWidget.setVisible(False)
        self.setWindowModified(False)

        if os.environ.get("NEXUS_PROCESSING_ENABLED", False):
            self.mainWidget.runNexusProcessing.setVisible(True)

        self.mainWidget.runNexusProcessing.triggered.connect(
            self.nexusProcessing
        )

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
        self.widgetsRefreshing = True
        if fromFile:
            self.gudrunFile = GudrunFile(
                path=self.gudrunFile.path,
                format=self.gudrunFile.format)
        self.mainWidget.gudrunFile = self.gudrunFile
        self.mainWidget.tabWidget.setVisible(True)
        self.instrumentSlots.setInstrument(self.gudrunFile.instrument)
        self.beamSlots.setBeam(self.gudrunFile.beam)
        self.componentSlots.setComponents(self.gudrunFile.components)
        self.normalisationSlots.setNormalisation(self.gudrunFile.normalisation)

        if len(self.gudrunFile.sampleBackgrounds):
            self.sampleBackgroundSlots.setSampleBackground(
                self.gudrunFile.sampleBackgrounds[0]
            )

            if len(self.gudrunFile.sampleBackgrounds[0].samples):
                self.sampleSlots.setSample(
                    self.gudrunFile.sampleBackgrounds[0].samples[0]
                )

                if len(
                    self.gudrunFile.sampleBackgrounds[0].samples[0].containers
                ):
                    self.containerSlots.setContainer(
                        self.gudrunFile.sampleBackgrounds[0]
                        .samples[0]
                        .containers[0]
                    )
        self.setActionsEnabled(True)
        self.mainWidget.objectTree.buildTree(self.gudrunFile, self)
        self.mainWidget.objectTree.model().dataChanged.connect(
            self.handleObjectsChanged
        )
        self.updateResults()
        self.widgetsRefreshing = False

    def handleObjectsChanged(self):
        if not self.widgetsRefreshing:
            self.setModified()

    def loadInputFile_(self):
        """
        Opens a QFileDialog to load an input file.
        """
        filters = {
            "YAML (*.yaml)": Format.YAML,
            "Gudrun Compatible (*.txt)": Format.TXT,
            "Sample Parameters (*.sample)": Format.TXT
        }

        filename, filter = QFileDialog.getOpenFileName(
            self.mainWidget,
            "Select Input file for GudPy",
            ".",
            f"{list(filters.keys())[0]};;" +
            f"{list(filters.keys())[1]};;" +
            f"{list(filters.keys())[2]};;"
        )
        if filename:
            if not filter:
                filter = "YAML (*.yaml)"
            fmt = filters[filter]
            try:
                if self.gudrunFile:
                    self.gudrunFile = None
                path = self.tryLoadAutosaved(filename)
                self.gudrunFile = GudrunFile(path=path, format=fmt)
                self.updateWidgets()
                self.mainWidget.setWindowTitle(self.gudrunFile.path + " [*]")
            except ParserException as e:
                QMessageBox.critical(self.mainWidget, "GudPy Error", str(e))
            except IOError:
                QMessageBox.critical(self.mainWidget,
                                     "GudPy Error",
                                     "Could not open file")

    def saveInputFile(self):
        """
        Saves the current state of the input file.
        """
        if not self.gudrunFile.path:
            self.saveInputFileAs()
        else:
            self.gudrunFile.save()
            self.setUnModified()

    def saveInputFileAs(self):
        """
        Saves the current state of the input file as...
        """
        filename, filter = QFileDialog.getSaveFileName(
            self,
            "Save input file as..",
            ".",
            "YAML (*.yaml);;Gudrun Compatible (*.txt)",
        )
        if filename:
            ext = re.search(r"\((.+?)\)", filter).group(1).replace("*", "")
            fmt = Format.TXT if ext == ".txt" else Format.YAML
            if filter and sys.platform.startswith("linux"):
                filename += ext
            if os.path.basename(filename) == "gudpy.txt":
                QMessageBox.warning(
                    self.mainWidget,
                    "GudPy Warning",
                    f"Cannot save to {filename}, gudpy.txt is reserved.",
                )
                return
            self.gudrunFile.instrument.GudrunInputFileDir = os.path.dirname(
                os.path.abspath(filename)
            )
            self.gudrunFile.path = filename
            self.gudrunFile.save(path=filename, format=fmt)
            self.setUnModified()

    def newInputFile(self):
        if self.gudrunFile:
            self.gudrunFile = None
        self.gudrunFile = GudrunFile()
        configurationDialog = ConfigurationDialog(self)
        result = configurationDialog.widget.exec()
        if not configurationDialog.cancelled and result:
            self.gudrunFile.instrument = GudrunFile(
                configurationDialog.configuration, config_=True
            ).instrument
            self.gudrunFile.instrument.dataFileType = (
                configurationDialog.dataFileType
            )
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
                f"An error occured reverting to the previous state.\n{str(e)}",
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
            self.normalisationSlots.widgetsRefreshing = False
        for i, sampleBackground in enumerate(
            self.gudrunFile.sampleBackgrounds
        ):
            for j, sample in enumerate(sampleBackground.samples):
                self.gudrunFile.sampleBackgrounds[i].samples[
                    j
                ].geometry = config.geometry
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
        if self.mainWidget.objectStack.currentIndex() == 5 and isinstance(
            self.mainWidget.objectTree.currentObject(), Sample
        ):
            try:
                topPlot, bottomPlot, gudFile = self.results[
                    self.mainWidget.objectTree.currentObject()
                ]
            except KeyError:
                self.updateSamples()
                topPlot, bottomPlot, gudFile = self.results[
                    self.mainWidget.objectTree.currentObject()
                ]
            self.mainWidget.sampleTopPlot.setChart(topPlot)
            self.mainWidget.sampleBottomPlot.setChart(bottomPlot)

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
                self.mainWidget.dcsLabel.setText(f"DCS Level: {dcsLevel}")
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
                self.mainWidget.dcsLabel.setText("DCS Level")
                self.mainWidget.resultLabel.setText("Error")
                self.mainWidget.resultLabel.setStyleSheet("")
                self.mainWidget.suggestedTweakFactorLabel.setText(
                    "Suggested Tweak Factor"
                )
        elif self.mainWidget.objectStack.currentIndex() == 6 and isinstance(
            self.mainWidget.objectTree.currentObject(), Container
        ):
            try:
                topPlot, bottomPlot, gudFile = self.results[
                    self.mainWidget.objectTree.currentObject()
                ]
            except KeyError:
                self.updateSamples()
                topPlot, bottomPlot, gudFile = self.results[
                    self.mainWidget.objectTree.currentObject()
                ]
            if sum(
                [
                    *[s.count() for s in topPlot.series()],
                    *[s.count() for s in bottomPlot.series()],
                ]
            ):
                self.mainWidget.containerSplitter.setSizes([2, 1])
            else:
                self.mainWidget.containerSplitter.setSizes([1, 0])

            self.mainWidget.containerTopPlot.setChart(topPlot)
            self.mainWidget.containerBottomPlot.setChart(bottomPlot)

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
            *self.mainWidget.objectTree.getContainers(),
        ]
        for sample in samples:
            topChart = GudPyChart(self.gudrunFile)
            topChart.addSample(sample)
            bottomChart = GudPyChart(self.gudrunFile)
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
                    self.gudrunFile.instrument.dataFileType,
                    "gud",
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
            *self.mainWidget.objectTree.getContainers(),
        ]
        allTopChart = GudPyChart(self.gudrunFile)
        allTopChart.addSamples(samples)
        allTopChart.plot(
            self.mainWidget.allPlotComboBox.itemData(
                self.mainWidget.allPlotComboBox.currentIndex()
            )
        )
        allBottomChart = GudPyChart(self.gudrunFile)
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
        result = messageBox.question(
            self.mainWidget,
            "",
            "Do you want to save?",
            messageBox.No | messageBox.Yes,
        )

        if result == messageBox.Yes:
            self.gudrunFile.write_out(overwrite=True)
        sys.exit(0)

    def makeProc(
        self,
        cmd,
        slot,
        dir_=None,
        func=None,
        args=None,
        started=None,
        finished=None,
    ):
        if not started:
            started = self.procStarted
        if not finished:
            finished = self.procFinished
        if not dir_:
            dir_ = self.gudrunFile.instrument.GudrunInputFileDir

        dir_ = self.tmp.name

        self.proc = cmd
        self.proc.readyReadStandardOutput.connect(slot)
        self.proc.started.connect(started)
        self.proc.finished.connect(finished)
        self.proc.setWorkingDirectory(dir_)
        if func:
            func(*args)
        self.proc.start()

    def prepareRun(self):
        if not self.checkFilesExist_():
            return False
        self.setControlsEnabled(False)

        self.tmp = tempfile.TemporaryDirectory()
        self.gudrunFile.setGudrunDir(self.tmp.name)

        return True

    def cleanupRun(self):
        if self.tmp:
            self.tmp.cleanup()
            self.tmp = None

        self.setControlsEnabled(True)
        self.mainWidget.progressBar.setValue(0)
        self.mainWidget.currentTaskLabel.setText("No task running.")
        self.queue = Queue()

    def runGudrun_(self):
        if not self.prepareRun():
            return False

        dcs = self.gudrunFile.dcs(
            path=os.path.join(
                self.gudrunFile.instrument.GudrunInputFileDir,
                self.gudrunFile.outpath,
            ),
            headless=False,
        )
        if isinstance(dcs, Sequence):
            dcs, func, args = dcs
        if isinstance(dcs, FileNotFoundError):
            QMessageBox.critical(
                self.mainWidget,
                "GudPy Error",
                "Couldn't find gudrun_dcs binary.",
            )
        elif not self.gudrunFile.purged and os.path.exists(
            os.path.join(
                self.gudrunFile.projectDir, "Purge", "purge_det.dat"
            )
        ):
            self.purgeOptionsMessageBox(
                dcs,
                self.runGudrunFinished,
                func,
                args,
                "purge_det.dat found, but wasn't run in this session. "
                "Continue?",
            )
        elif not self.gudrunFile.purged:
            self.purgeOptionsMessageBox(
                dcs,
                self.runGudrunFinished,
                func,
                args,
                "It looks like you may not have purged detectors. Continue?",
            )
        else:
            self.makeProc(
                dcs,
                self.progressDCS,
                func=func,
                args=args,
                finished=self.runGudrunFinished,
            )

        return True

    def runContainersAsSamples(self):
        if not self.prepareRun():
            return False

        runContainersAsSamples = RunContainersAsSamples(self.gudrunFile)
        dcs = runContainersAsSamples.runContainersAsSamples(
            path=os.path.join(
                self.gudrunFile.instrument.GudrunInputFileDir,
                self.gudrunFile.outpath,
            ),
            headless=False,
        )

        def finished(ec, es):
            self.runGudrunFinished(
                gudrunFile=runContainersAsSamples.gudrunFile
            )

        if isinstance(dcs, Sequence):
            dcs, func, args = dcs
        if isinstance(dcs, FileNotFoundError):
            QMessageBox.critical(
                self.mainWidget,
                "GudPy Error",
                "Couldn't find gudrun_dcs binary.",
            )
        elif not self.gudrunFile.purged and os.path.exists(
            os.path.join(
                self.gudrunFile.instrument.GudrunInputFileDir, "purge_det.dat"
            )
        ):
            self.purgeOptionsMessageBox(
                dcs,
                finished,
                func,
                args,
                "purge_det.dat found, but wasn't run in this session. "
                "Continue?",
            )
        elif not self.gudrunFile.purged:
            self.purgeOptionsMessageBox(
                dcs,
                finished,
                func,
                args,
                "It looks like you may not have purged detectors. Continue?",
            )
        else:
            self.makeProc(
                dcs, self.progressDCS, finished=finished, func=func, args=args
            )

    def runFilesIndividually(self):
        if not self.prepareRun():
            return False
        runIndividualFiles = RunIndividualFiles(self.gudrunFile)
        dcs = runIndividualFiles.gudrunFile.dcs(
            path=os.path.join(
                self.gudrunFile.instrument.GudrunInputFileDir,
                self.gudrunFile.outpath,
            ),
            headless=False,
        )

        def finished(ec, es):
            self.runGudrunFinished(gudrunFile=runIndividualFiles.gudrunFile)

        if isinstance(dcs, Sequence):
            dcs, func, args = dcs
        if isinstance(dcs, FileNotFoundError):
            QMessageBox.critical(
                self.mainWidget,
                "GudPy Error",
                "Couldn't find gudrun_dcs binary.",
            )
        elif not self.gudrunFile.purged and os.path.exists(
            os.path.join(
                self.gudrunFile.instrument.GudrunInputFileDir, "purge_det.dat"
            )
        ):
            self.purgeOptionsMessageBox(
                dcs,
                finished,
                func,
                args,
                "purge_det.dat found, but wasn't run in this session. "
                "Continue?",
            )
        elif not self.gudrunFile.purged:
            self.purgeOptionsMessageBox(
                dcs,
                finished,
                func,
                args,
                "It looks like you may not have purged detectors. Continue?",
            )
        else:
            self.makeProc(
                dcs, self.progressDCS,
                func=func, args=args,
                finished=finished
            )

    def purgeOptionsMessageBox(self, dcs, finished, func, args, text):
        messageBox = QMessageBox(self.mainWidget)
        messageBox.setWindowTitle("GudPy Warning")
        messageBox.setText(text)
        messageBox.addButton(QMessageBox.No)
        openPurgeDialog = QPushButton("Open purge dialog", messageBox)
        purgeDefault = QPushButton("Purge with default parameters", messageBox)

        messageBox.addButton(openPurgeDialog, QMessageBox.ApplyRole)
        messageBox.addButton(purgeDefault, QMessageBox.ApplyRole)

        messageBox.addButton(QMessageBox.Yes)
        result = messageBox.exec()

        if messageBox.clickedButton() == openPurgeDialog:
            self.purgeBeforeRunning(default=False)
        elif messageBox.clickedButton() == purgeDefault:
            self.purgeBeforeRunning()
        elif result == QMessageBox.Yes:
            self.makeProc(
                dcs, self.progressDCS,
                func=func, args=args,
                finished=finished
            )
        else:
            messageBox.close()
            self.setControlsEnabled(True)

    def purgeBeforeRunning(self, default=True):
        self.setControlsEnabled(False)
        if default:
            if not self.prepareRun():
                return False
            purge_det = self.gudrunFile.purge(headless=False)
            if isinstance(purge_det, Sequence):
                purge, func, args = purge_det
                self.makeProc(purge, self.progressPurge, func=func, args=args)
            elif isinstance(purge_det, FileNotFoundError):
                QMessageBox.critical(
                    self.mainWidget,
                    "GudPy Error",
                    "Couldn't find purge_det binary.",
                )
                self.setControlsEnabled(True)
                return
        else:
            self.runPurge_()
        dcs = self.gudrunFile.dcs(
            path=os.path.join(
                self.gudrunFile.instrument.GudrunInputFileDir,
                self.gudrunFile.outpath,
            ),
            headless=False,
        )
        if isinstance(dcs, Sequence):
            dcs, func, args = dcs
        elif isinstance(dcs, FileNotFoundError):
            QMessageBox.critical(
                self.mainWidget,
                "GudPy Error",
                "Couldn't find gudrun_dcs binary.",
            )
            self.setControlsEnabled(True)
            return
        self.queue.put(
            (
                (dcs, self.progressDCS),
                {
                    "func": func,
                    "args": args,
                    "finished": self.runGudrunFinished,
                },
            )
        )

    def nexusProcessing(self):
        if not self.checkFilesExist_():
            return

        self.setControlsEnabled(False)
        nexusProcessingDialog = NexusProcessingDialog(
            self.gudrunFile, self.mainWidget
        )
        nexusProcessingDialog.widget.exec()
        if (
            nexusProcessingDialog.cancelled
            or not nexusProcessingDialog.preprocess
        ):
            self.setControlsEnabled(True)
        else:
            tasks = nexusProcessingDialog.preprocess
            for task in tasks[:-1]:
                func, args = task
                func(*args)

            self.proc = tasks[-1]
            self.proc.started.connect(self.nexusProcessingStarted)
            self.proc.readyReadStandardOutput.connect(
                self.progressNexusPreprocess
            )
            self.proc.readyReadStandardError.connect(self.errorNexusPreprocess)
            self.proc.finished.connect(self.preprocessNexusFinished)
            self.proc.start()

    def nexusProcessingStarted(self):
        self.nexusProcessingFiles = set()
        self.text = "NeXuS Pre-processing"
        self.mainWidget.currentTaskLabel.setText(self.text)

    def progressNexusPreprocess(self):
        data = self.proc.readAllStandardOutput()
        stdout = bytes(data).decode("utf8")
        _, _, data = stdout.partition("Finished processing: ")
        if data:
            self.nexusProcessingFiles.add(data.split()[0])

        progress = re.findall(r"(\d+(?:\.\d+)?)%", stdout)
        if progress:
            self.mainWidget.progressBar.setValue(int(float(progress[-1])))

    def errorNexusPreprocess(self):
        data = self.proc.readAllStandardError()
        stderr = bytes(data).decode("utf8")
        if stderr:
            self.error = (
                f"An error occurred. See the following traceback"
                f" from modulation_excitation\n{stderr}"
            )
            QMessageBox.critical(
                self.mainWidget, "GudPy Error",
                self.error
            )
            self.gudrunFile.nexus_processing.tmp.cleanup()

    def progressNexusProcess(self):
        progress = self.progressIncrementDCS(
            self.gudrunFile.nexus_processing.gudrunFile
        )
        progress /= self.nPulses
        progress += self.mainWidget.progressBar.value()
        self.mainWidget.progressBar.setValue(
            progress if progress <= 100 else 100
        )

    def preprocessNexusFinished(self):
        self.nexusProcessingFiles = list(self.nexusProcessingFiles)
        self.nPulses = len(self.nexusProcessingFiles)
        self.mainWidget.progressBar.setValue(0)
        if self.nPulses > 0:
            tasks = self.gudrunFile.nexus_processing.process(
                self.nexusProcessingFiles, headless=False
            )
            self.text = "NeXuS Processing"
            self.mainWidget.currentTaskLabel.setText(self.text)
            self.queue = Queue()
            for t in tasks:
                self.queue.put(t)
            self.currentFile = 0
            self.keyMap = {
                n + 1: os.path.splitext(
                    os.path.basename(
                        self.nexusProcessingFiles[n]
                    )
                )[0]
                for n in range(len(self.nexusProcessingFiles))
            }
            self.processPulse()
        else:
            self.setControlsEnabled(True)
            self.mainWidget.currentTaskLabel.setText("No task running.")

    def processPulse(self):
        task = self.queue.get()
        if isinstance(task[0], QProcess):
            dcs, func, args, dir_ = task
            self.makeProc(
                dcs,
                self.progressNexusProcess,
                dir_=dir_,
                func=func,
                args=args,
                started=self.processPulseStarted,
                finished=self.processPulseFinished,
            )
        else:
            func, args = task
            func(*args)
            self.nexusProcessingFinished()

    def processPulseStarted(self):
        return

    def processPulseFinished(self):
        timer = QElapsedTimer()
        timer.start()
        while timer.elapsed() < 5000:
            QCoreApplication.processEvents()
        self.nexusProcessingOutput[self.currentFile + 1] = self.output
        self.currentFile += 1
        self.output = ""
        func, args = self.queue.get()
        func(*args)
        if not self.queue.empty():
            self.processPulse()
        else:
            self.nexusProcessingFinished()

    def nexusProcessingFinished(self):
        self.cleanupRun()
        self.proc = None
        self.outputSlots.setOutput(
            self.nexusProcessingOutput,
            "gudrun_dcs",
            gudrunFile=self.gudrunFile.nexus_processing.gudrunFile,
            keyMap=self.keyMap
        )
        self.gudrunFile.nexus_processing.tmp.cleanup()

    def batchProcessing(self):
        if not self.prepareRun():
            return False
        batchProcessingDialog = BatchProcessingDialog(
            self.gudrunFile, self.mainWidget
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
            self.mainWidget.currentTaskLabel.setText(self.text)
            self.mainWidget.stopTaskButton.setEnabled(True)
            self.nextBatchProcess()

    def batchProcessFinished(self, ec, es):
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
                    self.gudrunFile.instrument.GudrunInputFileDir
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
        progress += self.mainWidget.progressBar.value()
        self.mainWidget.progressBar.setValue(
            progress if progress <= 100 else 100
        )

    def batchProcessingFinished(self):
        self.setControlsEnabled(True)
        self.queue = Queue()
        self.proc = None
        self.text = "No task running."
        self.mainWidget.currentTaskLabel.setText(self.text)
        self.mainWidget.progressBar.setValue(0)
        self.mainWidget.stopTaskButton.setEnabled(False)
        self.outputSlots.setOutput(
            self.outputBatches,
            "gudrun_dcs",
            gudrunFile=self.batchProcessor.batchedGudrunFile,
        )
        self.outputBatches = {}
        self.output = ""

    def finishedCompositionIteration(self, originalSample, updatedSample):
        self.compositionMap[originalSample] = updatedSample
        self.mainWidget.progressBar.setValue(
            int((self.iterator.nCurrent / self.iterator.nTotal) * 100)
        )
        self.gudrunFile.gudrunOutput = self.iterator.organiseOutput()
        self.cleanupRun()
        if not self.queue.empty():
            self.nextCompositionIteration()
        else:
            self.finishedCompositionIterations()

    def finishedCompositionIterations(self):
        for original, new in self.compositionMap.items():
            dialog = CompositionAcceptanceDialog(
                new, self.gudrunFile, self.mainWidget)
            result = dialog.widget.exec()
            if result:
                original.composition = new.composition
                if self.sampleSlots.sample == original:
                    self.sampleSlots.setSample(original)

    def startedCompositionIteration(self, sample):
        self.mainWidget.currentTaskLabel.setText(
            f"{self.text}" f" ({sample.name})"
        )

    def errorCompositionIteration(self, output):
        QMessageBox.critical(
            self.mainWidget,
            "GudPy Error",
            "An error occured whilst iterating by composition."
            " Please check the output to see what went wrong.",
        )
        self.cleanupRun()
        self.outputSlots.setOutput(
            output, "gudrun_dcs", gudrunFile=self.gudrunFile
        )

    def progressCompositionIteration(self, currentIteration):
        self.iterator.nCurrent += 1
        print(self.iterator.nCurrent)
        print(self.iterator.nTotal)
        progress = (self.iterator.nCurrent / self.iterator.nTotal)
        self.mainWidget.progressBar.setValue(int(progress * 100))

    def nextCompositionIteration(self):
        if not self.prepareRun():
            return False
        args, kwargs, sample = self.queue.get()
        self.worker = CompositionWorker(args, kwargs, sample, self.gudrunFile)
        self.worker.started.connect(self.startedCompositionIteration)
        self.workerThread = QThread()
        self.worker.moveToThread(self.workerThread)
        self.worker.finished.connect(self.workerThread.quit)
        self.worker.nextIteration.connect(self.progressCompositionIteration)
        self.workerThread.started.connect(self.worker.work)
        self.workerThread.start()
        self.worker.errorOccured.connect(self.errorCompositionIteration)
        self.worker.errorOccured.connect(self.workerThread.quit)
        self.worker.finished.connect(self.finishedCompositionIteration)

    def iterateByComposition(self):
        if not self.iterator.components:
            self.setControlsEnabled(True)
            return
        elif self.queue.empty():
            QMessageBox.warning(
                self.mainWidget,
                "GudPy Warning",
                "No iterations were queued."
                " It's likely no Samples selected for analysis"
                " use the Component(s) selected for iteration.",
            )
            self.setControlsEnabled(True)
        else:
            self.compositionMap = {}
            self.nextCompositionIteration()

    def iterateGudrun(self, dialog, name):
        """
        Iteratively runs Gudrun dcs and applies a change depending on which
        parameter is iterated. The first iteration is a default iteration in
        which no parameters are altered.

        Parameters
        ----------
        dialog : IterationDialog
            Dialog to be run to get user information
        name : str
            Name of dialog
        """
        iterationDialog = dialog(name, self.gudrunFile, self.mainWidget)
        iterationDialog.widget.exec()
        if not iterationDialog.iterator:
            self.setControlsEnabled(True)
        else:
            self.queue = iterationDialog.queue
            self.iterator = iterationDialog.iterator
            self.currentIteration = 0
            self.text = iterationDialog.text
            self.outputIterations = {}
            if isinstance(self.iterator, CompositionIterator):
                self.iterator.nTotal = self.iterationDialog.rtol + 1
                self.iterateByComposition()
            else:
                self.nextIterableProc()
            self.mainWidget.stopTaskButton.setEnabled(True)

    def nextIteration(self):
        self.cleanupRun
        if self.error:
            self.procFinished(9, QProcess.NormalExit)
            return
        self.gudrunFile.gudrunOutput = self.iterator.organiseOutput()
        if self.iterator.nCurrent != -1:
            # If this is not the default run
            self.outputIterations[
                f"{self.iterator.iterationType} {self.iterator.nCurrent}"
            ] = self.output
        else:
            self.outputIterations["Default"] = self.output
        self.outputSlots.setOutput(
            self.outputIterations, "gudrun_dcs",
            gudrunFile=self.iterator.gudrunFile
        )
        if not self.queue.empty():
            self.nextIterableProc()
        else:
            self.procFinished(0, QProcess.NormalExit)
        self.output = ""

    def nextIterableProc(self):
        if not self.prepareRun():
            return False
        if self.queue.empty():
            return
        iterInfo = f" {self.iterator.nCurrent + 1}/{self.iterator.nTotal}" if (
            self.iterator.nCurrent != -1
        ) else "- Default run"
        # Set progress bar
        self.mainWidget.currentTaskLabel.setText(f"{self.text} {iterInfo}")
        self.previousProcTitle = self.mainWidget.currentTaskLabel.text()
        self.iterator.performIteration()
        self.iterator.gudrunFile.write_out()
        self.proc, func, args = self.queue.get()
        self.proc.finished.connect(self.nextIteration)
        self.proc.readyReadStandardOutput.connect(self.progressIteration)
        self.proc.setWorkingDirectory(
            self.iterator.gudrunFile.instrument.GudrunInputFileDir
        )
        if func:
            func(*args)
        self.proc.start()

    def progressIteration(self):
        progress = self.progressIncrementDCS(self.gudrunFile)
        if progress == -1:
            self.error = (
                f"An error occurred. See the following traceback"
                f" from gudrun_dcs\n{self.error}"
            )
            return
        progress /= self.iterator.nTotal
        progress += self.mainWidget.progressBar.value()
        self.mainWidget.progressBar.setValue(
            progress if progress <= 100 else 100
        )

    def checkFilesExist_(self):
        result = GudPyFileLibrary(self.gudrunFile).checkFilesExist()
        if not all(r[0] for r in result[0]) or not all(r[0]
                                                       for r in result[1]):
            undefined = [
                r[1] for r in result[0] if not r[0]
            ]
            unresolved = [r[2] for r in result[1] if not r[0] and r[2]]
            missingFilesDialog = MissingFilesDialog(
                undefined, unresolved, self.mainWidget
            )
            missingFilesDialog.widget.exec_()
            return False
        return True

    def autosave(self):
        if (
            self.gudrunFile
            and self.gudrunFile.path
            and not self.proc
            and not self.workerThread
        ):
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
        self.mainWidget.componentPage.setEnabled(state)
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
        self.mainWidget.runFilesIndividually.setEnabled(state)
        self.mainWidget.batchProcessing.setEnabled(state)
        self.mainWidget.viewLiveInputFile.setEnabled(state)
        self.mainWidget.save.setEnabled(
            state & self.modified & len(self.gudrunFile.path) > 0
            if self.gudrunFile.path
            else False
        )
        self.mainWidget.saveAs.setEnabled(state)
        self.mainWidget.loadInputFile.setEnabled(state)
        self.mainWidget.exportArchive.setEnabled(state)
        self.mainWidget.new_.setEnabled(state)
        self.mainWidget.checkFilesExist.setEnabled(state)
        self.mainWidget.runFilesIndividually.setEnabled(state)
        self.mainWidget.runContainersAsSamples.setEnabled(state)

        if os.environ.get("NEXUS_PROCESSING_ENABLED", False):
            self.mainWidget.runNexusProcessing.setEnabled(
                state
                & (
                    self.gudrunFile.instrument.dataFileType == "nxs"
                    or self.gudrunFile.instrument.dataFileType == "NXS"
                )
                if self.gudrunFile
                else False
            )

    def setActionsEnabled(self, state):
        self.setTreeActionsEnabled(state)

        self.mainWidget.runPurge.setEnabled(state)
        self.mainWidget.runGudrun.setEnabled(state)
        self.mainWidget.iterateGudrun.setEnabled(state)
        self.mainWidget.runFilesIndividually.setEnabled(state)
        self.mainWidget.checkFilesExist.setEnabled(state)
        self.mainWidget.runFilesIndividually.setEnabled(state)
        self.mainWidget.runContainersAsSamples.setEnabled(state)
        self.mainWidget.batchProcessing.setEnabled(state)
        self.mainWidget.viewLiveInputFile.setEnabled(state)
        self.mainWidget.save.setEnabled(state & self.modified)
        self.mainWidget.saveAs.setEnabled(state)
        self.mainWidget.exportArchive.setEnabled(state)

        if os.environ.get("NEXUS_PROCESSING_ENABLED", False):
            self.mainWidget.runNexusProcessing.setEnabled(
                state
                & (
                    self.gudrunFile.instrument.dataFileType == "nxs"
                    or self.gudrunFile.instrument.dataFileType == "NXS"
                )
                if self.gudrunFile
                else False
            )

    def setTreeActionsEnabled(self, state):
        self.mainWidget.insertSampleBackground.setEnabled(state)
        self.mainWidget.insertSample.setEnabled(state)
        self.mainWidget.insertContainerMenu.setEnabled(state)
        self.mainWidget.copy.setEnabled(state)
        self.mainWidget.cut.setEnabled(state)
        self.mainWidget.paste.setEnabled(state)
        self.mainWidget.delete_.setEnabled(state)

    def progressIncrementDCS(self, gudrunFile=None):
        if not gudrunFile:
            gudrunFile = self.gudrunFile
        if not self.proc:
            return 0
        data = self.proc.readAllStandardOutput()
        stdout = bytes(data).decode("utf8")
        self.output += stdout
        ERROR_KWDS = ["does not exist", "error", "Error"]
        if [KWD for KWD in ERROR_KWDS if KWD in stdout]:
            self.error = stdout
            return -1
        # Number of GudPy objects.
        markers = (
            config.NUM_GUDPY_CORE_OBJECTS
            - 1
            + len(gudrunFile.sampleBackgrounds)
            + sum(
                [
                    sum(
                        [
                            len(
                                [
                                    sample
                                    for sample in sampleBackground.samples
                                    if sample.runThisSample
                                ]
                            ),
                            *[
                                len(sample.containers)
                                for sample in sampleBackground.samples
                                if sample.runThisSample
                            ],
                        ]
                    )
                    for sampleBackground in gudrunFile.sampleBackgrounds
                ]
            )
        )
        stepSize = math.ceil(100 / markers)
        progress = stepSize * sum(
            [
                stdout.count("Got to: INSTRUMENT"),
                stdout.count("Got to: BEAM"),
                stdout.count("Got to: NORMALISATION"),
                stdout.count("Got to: SAMPLE BACKGROUND"),
                stdout.count("Finished merging data for sample"),
                stdout.count("Got to: CONTAINER"),
            ]
        )
        return progress

    def progressDCS(self):
        progress = self.progressIncrementDCS(self.gudrunFile)
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

    def runPurge_(self):
        if not self.prepareRun():
            return False

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
                "GudPy Error",
                "Couldn't find purge_det binary.",
            )
            self.setControlsEnabled(True)
        elif not purge:
            self.setControlsEnabled(True)
        else:
            os.chdir(self.gudrunFile.instrument.GudrunInputFileDir)
            self.gudrunFile.purgeFile.write_out()
            self.makeProc(purge, self.progressPurge, func=func,
                          dir_=self.gudrunFile.instrument.GudrunInputFileDir,
                          args=args)

    def progressIncrementPurge(self):
        if not self.proc:
            return 0
        data = self.proc.readAllStandardOutput()
        stdout = bytes(data).decode("utf8")
        self.output += stdout
        dataFiles = [self.gudrunFile.instrument.groupFileName]

        def appendDfs(dfs):
            for df in dfs:
                dataFiles.append(
                    df.replace(self.gudrunFile.instrument.dataFileType, "grp")
                )

        appendDfs(self.gudrunFile.normalisation.dataFiles[0])
        appendDfs(self.gudrunFile.normalisation.dataFilesBg[0])
        appendDfs(
            [
                df
                for sb in self.gudrunFile.sampleBackgrounds
                for df in sb.dataFiles
            ]
        )
        if not self.gudrunFile.purgeFile.excludeSampleAndCan:
            appendDfs(
                [
                    df
                    for sb in self.gudrunFile.sampleBackgrounds
                    for s in sb.samples
                    for df in s.dataFiles
                    if s.runThisSample
                ]
            )
            appendDfs(
                [
                    df
                    for sb in self.gudrunFile.sampleBackgrounds
                    for s in sb.samples
                    for c in s.containers
                    for df in c.dataFiles
                    if s.runThisSample
                ]
            )

        stepSize = math.ceil(100 / len(dataFiles))
        progress = 0
        for df in dataFiles:
            if df in stdout:
                progress += stepSize
        if (
            "Error" in stdout
            or "error" in stdout
            or "not found" in stdout
            or "does not exist" in stdout
        ):
            self.error = stdout
            return -1, False, -1
        elif dataFiles[-1] in stdout:
            try:
                lines = stdout.split("\n")
                targetLine = next(
                    (
                        s
                        for s in lines
                        if "spectra in" in s and dataFiles[-1] in s
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
            self.cleanupRun()
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
            self.gudrunFile.purgeFile.organiseOutput()
            self.cleanupRun()

    def procStarted(self):
        self.mainWidget.currentTaskLabel.setText(
            self.proc.program().split(os.path.sep)[-1]
        )
        self.mainWidget.stopTaskButton.setEnabled(True)
        self.previousProcTitle = self.mainWidget.currentTaskLabel.text()
        self.output = ""

    def runGudrunFinished(self, ec, es, gudrunFile=None):
        if gudrunFile:
            gudrunFile.organiseOutput()
        else:
            self.gudrunFile.organiseOutput()
        self.procFinished(ec, es)

    def procFinished(self, ec, es):
        self.proc = None
        output = self.output
        if self.iterator:
            self.outputIterations[
                f"{self.iterator.iterationType} {self.iterator.nCurrent}"
            ] = self.output
            self.sampleSlots.setSample(self.sampleSlots.sample)
            output = self.outputIterations
            self.iterator = None
        if self.error:
            QMessageBox.critical(
                self.mainWidget, "GudPy Error", repr(self.error)
            )
            self.error = ""
            self.cleanupRun()
        if "purge_det" not in self.mainWidget.currentTaskLabel.text():
            try:
                self.updateResults()
            except ParserException:
                QMessageBox.warning(
                    self.mainWidget,
                    "GudPy Warning",
                    "The process did not entirely finish,"
                    " please check your parameters.",
                )
            self.outputSlots.setOutput(
                output, "gudrun_dcs", gudrunFile=self.gudrunFile
            )
        else:
            self.outputSlots.setOutput(
                output, "purge_det", gudrunFile=self.gudrunFile
            )
        self.outputIterations = {}
        self.output = ""
        if self.queue.empty():
            if self.warning:
                QMessageBox.warning(
                    self.mainWidget, "GudPy Warning", repr(self.warning)
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
            f"{''.join(traceback.format_exception(cls, exception, tb))}",
        )

    def export(self):
        exportDialog = ExportDialog(self.gudrunFile, self)
        exportDialog.widget.exec()

    def cleanup(self):
        self.stopProc()
        self.autosave()
