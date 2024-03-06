from abc import abstractmethod
import os
import sys

from PySide6 import QtCore, QtGui, QtUiTools, QtWidgets, QtCharts

from core.container import Container
from core.sample import Sample

from gui.widgets.dialogs.iterators import (
    CompositionIterationDialog,
    DensityIterationDialog,
    InelasticitySubtractionIterationDialog,
    RadiusIterationDialog,
    ThicknessIterationDialog,
    TweakFactorIterationDialog,
)

from gui.widgets.dialogs.purge import PurgeDialog
from gui.widgets.dialogs.view_input_dialog import ViewInputDialog
from gui.widgets.dialogs.composition_dialog import CompositionDialog
from gui.widgets.dialogs.view_output_dialog import ViewOutputDialog
from gui.widgets.dialogs.configuration import ConfigurationDialog
from gui.widgets.dialogs.composition_acceptance import (
    CompositionAcceptanceDialog,
)
from gui.widgets.dialogs.io import ExportDialog, MissingFilesDialog
from gui.widgets.dialogs.batch import BatchProcessingDialog
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

from gui.widgets.slots.instrument_slots import InstrumentSlots
from gui.widgets.slots.beam_slots import BeamSlots
from gui.widgets.slots.component_slots import ComponentSlots
from gui.widgets.slots.normalisation_slots import NormalisationSlots
from gui.widgets.slots.container_slots import ContainerSlots
from gui.widgets.slots.sample_background_slots import SampleBackgroundSlots
from gui.widgets.slots.sample_slots import SampleSlots
from gui.widgets.slots.output_slots import OutputSlots
# from gui.widgets.resources import resources_rc  # noqa
from core import enums
from core import config


class GudPyMainWindow(QtWidgets.QMainWindow):
    """
    Class to represent the GudPyMainWindow. Inherits QtWidgets.QMainWindow.
    This is the main window for the GudPy application.

    ...

    Attributes
    ----------
    self.gudrunFile : GudrunFile
        self.gudrunFile object currently associated with the application.
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
        super().__init__()

        self.gudrunFile = None
        self.modified = False
        self.clipboard = None
        self.results = {}
        self.gudrunOutput = None

        self.allPlots = []
        self.plotModes = {}

        self.initComponents()

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

        self.timer = QtCore.QTimer(self)

    def initComponents(self):
        """
        Loads the UI file for the GudPyMainWindow.
        """
        if hasattr(sys, "_MEIPASS"):
            uifile = QtCore.QFile(
                os.path.join(sys._MEIPASS, "ui_files", "mainWindow.ui")
            )
            current_dir = os.path.sep
        else:
            current_dir = os.path.dirname(os.path.realpath(__file__))
            uifile = QtCore.QFile(
                os.path.join(current_dir, "../ui_files", "mainWindow.ui")
            )

        loader = QtUiTools.QUiLoader()
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
        loader.registerCustomWidget(MissingFilesDialog)
        loader.registerCustomWidget(ExportDialog)
        loader.registerCustomWidget(CompositionDialog)
        loader.registerCustomWidget(ConfigurationDialog)
        loader.registerCustomWidget(CompositionAcceptanceDialog)
        loader.registerCustomWidget(BatchProcessingDialog)
        loader.registerCustomWidget(ExponentialSpinBox)
        loader.registerCustomWidget(GudPyChartView)
        self.ui = loader.load(uifile)

        self.ui.statusBar_ = QtWidgets.QStatusBar(self)
        self.ui.statusBarWidget = QtWidgets.QWidget(self.ui.statusBar_)
        self.ui.statusBarLayout = QtWidgets.QHBoxLayout(
            self.ui.statusBarWidget
        )
        self.ui.currentTaskLabel = QtWidgets.QLabel(
            self.ui.statusBarWidget
        )
        self.ui.currentTaskLabel.setText("No task running.")
        self.ui.currentTaskLabel.setSizePolicy(
            QtWidgets.QSizePolicy(
                QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Preferred)
        )
        self.ui.stopTaskButton = QtWidgets.QToolButton(
            self.ui.statusBarWidget
        )
        self.ui.stopTaskButton.setIcon(QtGui.QIcon(":/icons/stop"))
        self.ui.stopTaskButton.setEnabled(False)

        self.ui.stopTaskButton.setSizePolicy(
            QtWidgets.QSizePolicy(
                QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Preferred)
        )

        self.ui.progressBar = QtWidgets.QProgressBar(
            self.ui.statusBarWidget
        )
        self.ui.progressBar.setSizePolicy(
            QtWidgets.QSizePolicy(
                QtWidgets.QSizePolicy.Expanding,
                QtWidgets.QSizePolicy.Preferred)
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

        self.ui.plotTab.setEnabled(False)

        self.ui.beamPlot = QtCharts.QChartView(self.ui)
        self.ui.beamPlot.setRenderHint(QtGui.QPainter.Antialiasing)

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

        actionMap = {
            name: lambda: self.ui.objectTree.insertContainer(
                container=Container(config=path)
            )
            for name, path in config.containerConfigurations.items()
        }
        insertContainerFromTemplate = QtWidgets.QMenu(
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

    def autosaveMessage(
            self, autosavePath: str, autoDate: str, currDate: str
    ):
        messageBox = QtWidgets.QMessageBox(self.mainWidget)
        messageBox.setWindowTitle("Autosave found")
        messageBox.setText(
            f"Found autosaved file: {autosavePath}.\n"
            f"This file is newer ({autoDate})"
            f" than the loaded file"
            f" ({currDate}).\n"
            f"Would you like to load the autosaved file instead?"
        )
        messageBox.addButton(QtWidgets.QMessageBox.No)
        messageBox.addButton(QtWidgets.QMessageBox.Yes)
        return messageBox.exec()

    def handleObjectsChanged(self):
        if not self.widgetsRefreshing:
            self.setModified()

    def updateWidgets(self, gudrunFile, gudrunOutput=None):
        self.gudrunFile = gudrunFile
        self.ui.gudrunFile = gudrunFile
        self.widgetsRefreshing = True
        self.ui.tabWidget.setVisible(True)
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
        self.ui.objectTree.buildTree(self.gudrunFile, self)
        self.ui.objectTree.model().dataChanged.connect(
            self.handleObjectsChanged
        )
        if gudrunOutput:
            self.updateResults(gudrunOutput)
        self.widgetsRefreshing = False

    def updateGeometries(self):
        """
        Iteratively updates geometries of objects,
        where the geometry is SameAsBeam.
        """
        if (
            self.gudrunFile.normalisation.geometry ==
            enums.Geometry.SameAsBeam
        ):
            self.normalisationSlots.widgetsRefreshing = True
            self.ui.geometryInfoStack.setCurrentIndex(
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
        self.ui.normalisationCompositionTable.farmCompositions()
        self.ui.sampleCompositionTable.farmCompositions()
        self.ui.sampleRatioCompositionTable.farmCompositions()
        self.ui.containerCompositionTable.farmCompositions()

    def focusResult(self):
        if not self.gudrunOutput:
            return

        self.updateSamples()

        if self.ui.objectStack.currentIndex() == 5 and isinstance(
            self.ui.objectTree.currentObject(), Sample
        ):
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
            topPlot, bottomPlot, gudFile = self.results[
                self.ui.objectTree.currentObject()
            ]
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

    def updateProgressBar(self, progress: int, taskName: str):
        self.ui.progressBar.setValue(
            progress if progress <= 100 else 100
        )
        self.ui.currentTaskLabel.setText(taskName)

    def updateSamples(self):
        if not self.gudrunOutput:
            return

        samples = [
            *self.ui.objectTree.getSamples(),
            *self.ui.objectTree.getContainers(),
        ]
        for sample in samples:
            topChart = GudPyChart(self.gudrunOutput)
            topChart.addSample(sample)
            bottomChart = GudPyChart(self.gudrunOutput)
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
            gf = self.gudrunOutput.gudFile(name=sample.name)
            self.results[sample] = [
                topChart, bottomChart, gf if gf else None]

    def updateAllSamples(self):
        samples = [
            *self.ui.objectTree.getSamples(),
            *self.ui.objectTree.getContainers(),
        ]
        allTopChart = GudPyChart(self.gudrunOutput)
        allTopChart.addSamples(samples)
        allTopChart.plot(
            self.ui.allPlotComboBox.itemData(
                self.ui.allPlotComboBox.currentIndex()
            )
        )
        allBottomChart = GudPyChart(self.gudrunOutput)
        allBottomChart.addSamples(samples)
        self.allPlots = [allTopChart, allBottomChart]
        self.ui.allSampleTopPlot.setChart(allTopChart)
        self.ui.allSampleBottomPlot.setChart(allBottomChart)

    def updateResults(self, gudrunOutput):
        self.ui.plotTab.setEnabled(True)
        self.gudrunOutput = gudrunOutput
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

    def sendError(self, error: str):
        QtWidgets.QMessageBox.critical(
            self.ui, "GudPy Error", str(error))

    def sendWarning(self, warning: str):
        QtWidgets.QMessageBox.warning(
            self.ui,
            "GudPy Warning",
            warning
        )

    def iterationResultsDialog(self, results, name):
        if not results:
            return
        dialog = QtWidgets.QDialog(self.ui)
        dialog.setWindowTitle("GudPy Iteration Results")
        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(QtWidgets.QLabel(
            name.capitalize() + " Iteration Results"))

        resultsTable = QtWidgets.QTableWidget(dialog)
        resultsTable.horizontalHeader().setSectionResizeMode(
            QtWidgets.QHeaderView.ResizeMode.ResizeToContents
        )
        resultsTable.verticalHeader().hide()

        labels = ["Sample"]
        for sample, sampleResults in results.items():
            if labels == ["Sample"]:
                # Get list of keys for header
                labels += ["Starting " +
                           k for k in sampleResults["Old"].keys()]
                labels += ["New " + k for k in sampleResults["New"].keys()]
                resultsTable.setColumnCount(len(labels))
                resultsTable.setHorizontalHeaderLabels(labels)

            currentRow = resultsTable.rowCount()
            resultsTable.insertRow(currentRow)
            resultsTable.setItem(
                currentRow, 0, QtWidgets.QTableWidgetItem(sample))

            for col, (_, value) in enumerate(sampleResults["Old"].items()):
                col = col + 1
                resultsTable.setItem(
                    currentRow, col, QtWidgets.QTableWidgetItem(str(value)))

            for col, (_, value) in enumerate(sampleResults["New"].items()):
                col = col + len(sampleResults["Old"].keys()) + 1
                resultsTable.setItem(
                    currentRow, col, QtWidgets.QTableWidgetItem(str(value)))

        layout.addWidget(resultsTable)
        okButton = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.Ok)
        layout.addWidget(okButton)
        okButton.accepted.connect(dialog.close)
        dialog.setLayout(layout)

        # Resize dialog to fit the table
        tableWidth = resultsTable.horizontalHeader().length()
        tableWidth += 50
        dialogWidth = tableWidth
        dialog.resize(dialogWidth, 400)

        dialog.exec()

    def purgeOptionsMessageBox(self, text):
        messageBox = QtWidgets.QMessageBox(self)
        messageBox.setWindowTitle("GudPy Warning")
        messageBox.setText(text)

        messageBox.addButton(QtWidgets.QMessageBox.Yes)
        messageBox.addButton(QtWidgets.QMessageBox.No)
        messageBox.addButton(QtWidgets.QMessageBox.Cancel)
        return messageBox.exec()

    def setModified(self):
        if not self.modified:
            if self.gudrunFile.path():
                self.modified = True
                self.ui.setWindowModified(True)
                self.ui.save.setEnabled(True)
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
            state & self.modified
            if self.gudrunFile.path()
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

    def viewInput(self):
        self.currentState = str(self.gudrunFile)
        viewInputDialog = ViewInputDialog(self.gudrunFile, self)
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
