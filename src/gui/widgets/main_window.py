from PySide6.QtCore import QFile
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
    QWidget
)
from src.gudrun_classes.sample import Sample

from src.gui.widgets.dialogs.iteration_dialog import IterationDialog
from src.gui.widgets.dialogs.purge_dialog import PurgeDialog
from src.gui.widgets.dialogs.view_input_dialog import ViewInputDialog
from src.gui.widgets.dialogs.missing_files_dialog import MissingFilesDialog
from src.gui.widgets.dialogs.composition_dialog import CompositionDialog

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

from src.gui.widgets.gudpy_charts import (
  GudPyChart, PlotModes, GudPyChartView
)

from src.gudrun_classes.enums import Geometry
from src.gui.widgets.slots.instrument_slots import InstrumentSlots
from src.gui.widgets.slots.beam_slots import BeamSlots
from src.gui.widgets.slots.component_slots import ComponentSlots
from src.gui.widgets.slots.normalisation_slots import NormalisationSlots
from src.gui.widgets.slots.container_slots import ContainerSlots
from src.gui.widgets.slots.sample_background_slots import SampleBackgroundSlots
from src.gui.widgets.slots.sample_slots import SampleSlots
from src.gui.widgets.resources import resources_rc  # noqa

from src.gudrun_classes.file_library import GudPyFileLibrary
from src.gudrun_classes.gudrun_file import GudrunFile
from src.gudrun_classes.exception import ParserException
from src.gudrun_classes import config
from src.gudrun_classes.tweak_factor_iterator import TweakFactorIterator
from src.gudrun_classes.wavelength_subtraction_iterator import (
    WavelengthSubtractionIterator
)
from src.gudrun_classes.gud_file import GudFile

from src.scripts.utils import nthint

import os
import sys
import math
import traceback
from queue import Queue


import time
import threading
from pathlib import Path

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
        self.cwd = os.getcwd()
        self.initComponents()
        self.tryAutorecover()


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
        loader.registerCustomWidget(CompositionDialog)
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

        self.mainWidget.topAllPlotComboBox.addItem(
            "Structure Factor",
            PlotModes.STRUCTURE_FACTOR
        )

        self.mainWidget.topAllPlotComboBox.currentIndexChanged.connect(
            self.handleTopAllPlotModeChanged
        )

        self.mainWidget.bottomAllPlotComboBox.addItem(
            "Radial Distribution Functions",
            PlotModes.RADIAL_DISTRIBUTION_FUNCTIONS
        )

        self.mainWidget.bottomAllPlotComboBox.currentIndexChanged.connect(
            self.handleBottomAllPlotModeChanged
        )

        self.mainWidget.topPlotComboBox.addItem(
            "Structure Factor",
            PlotModes.STRUCTURE_FACTOR
        )

        self.mainWidget.topPlotComboBox.currentIndexChanged.connect(
            self.handleTopPlotModeChanged
        )

        self.mainWidget.bottomPlotComboBox.addItem(
            "Radial Distribution Functions",
            PlotModes.RADIAL_DISTRIBUTION_FUNCTIONS
        )

        self.mainWidget.bottomPlotComboBox.currentIndexChanged.connect(
            self.handleBottomPlotModeChanged
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
        self.mainWidget.runPurge.triggered.connect(
            self.runPurge_
        )
        self.mainWidget.runGudrun.triggered.connect(
            self.runGudrun_
        )
        self.mainWidget.iterateGudrun.triggered.connect(
            self.iterateGudrun_
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

        self.mainWidget.insertContainer.triggered.connect(
            self.mainWidget.objectTree.insertContainer
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

        self.mainWidget.loadConfiguration.triggered.connect(
            self.loadConfiguration_
        )

        self.mainWidget.new_.triggered.connect(
            self.newInputFile
        )

        self.mainWidget.objectStack.currentChanged.connect(
            self.updateComponents
        )

        self.mainWidget.exit.triggered.connect(self.exit_)

        self.setActionsEnabled(False)
        self.mainWidget.tabWidget.setVisible(False)
    
    def tryAutorecover(self):
        for f in os.listdir():
            if f.endswith(".recovery"):
                messageBox = QMessageBox(self.mainWidget)
                messageBox.setWindowTitle("GudPy Warning")
                messageBox.setText(f"Found recovery file: {f}.\n Would you like to load it?")
                messageBox.addButton(QMessageBox.No)
                messageBox.addButton(QMessageBox.Yes)
                deleteRecoveryFile = QPushButton("Delete recovery file", messageBox)

                messageBox.addButton(deleteRecoveryFile, QMessageBox.RejectRole)

                result = messageBox.exec()

                if messageBox.clickedButton() == deleteRecoveryFile:
                    os.remove(f)
                elif result == messageBox.Yes:
                    self.gudrunFile = GudrunFile(f)
                    self.updateWidgets()
                    self.mainWidget.setWindowTitle(self.gudrunFile.path)       
                else:
                    messageBox.close() 

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
        self.mainWidget.objectTree.buildTree(self.gudrunFile, self)
        self.setActionsEnabled(True)
        self.updateResults()

    def loadInputFile_(self):
        """
        Opens a QFileDialog to load an input file.
        """
        filename, _ = QFileDialog.getOpenFileName(
            self, "Select Input file for GudPy", ".", "GudPy input (*.txt)"
        )
        if filename:
            try:
                if self.gudrunFile:
                    del self.gudrunFile
                self.gudrunFile = GudrunFile(path=filename)
                self.updateWidgets()
                self.mainWidget.setWindowTitle(self.gudrunFile.path)
            except ParserException as e:
                QMessageBox.critical(self.mainWidget, "GudPy Error", str(e))

    def loadConfiguration_(self):
        """
        Opens a QFileDialog to load a configuration file.
        """
        targetDir = (
            os.path.join(sys._MEIPASS, "bin", "configs")
            if hasattr(sys, "_MEIPASS")
            else os.path.join("bin", "configs")
        )
        filename, _ = QFileDialog.getOpenFileName(
            self,
            "Select configuration file for GudPy",
            targetDir,
            "GudPy Configuration (*.txt)"
        )
        if filename:
            try:
                if not self.gudrunFile:
                    self.gudrunFile = GudrunFile()
                instrument = GudrunFile(path=filename, config=True).instrument
                self.gudrunFile.instrument = instrument
                self.updateWidgets()
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
            self, "Save input file as..", "."
        )
        if filename:
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
            and isinstance(self.mainWidget.objectTree.currentObject(), Sample)
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
                PlotModes.STRUCTURE_FACTOR: 0,
                PlotModes.RADIAL_DISTRIBUTION_FUNCTIONS: 0
            }

            self.mainWidget.topPlotComboBox.setCurrentIndex(
                plotsMap[topPlot.plotMode]
            )
            self.mainWidget.bottomPlotComboBox.setCurrentIndex(
                plotsMap[bottomPlot.plotMode]
            )
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

    def updateSamples(self):
        samples = self.mainWidget.objectTree.getSamples()
        for sample in samples:
            topChart = GudPyChart(
                self.gudrunFile
            )
            topChart.addSample(sample)
            topChart.plot(PlotModes.STRUCTURE_FACTOR)
            bottomChart = GudPyChart(
                self.gudrunFile
            )
            bottomChart.addSample(sample)
            bottomChart.plot(PlotModes.RADIAL_DISTRIBUTION_FUNCTIONS)
            path = None
            if len(sample.dataFiles.dataFiles):
                path = sample.dataFiles.dataFiles[0].replace(
                    self.gudrunFile.instrument.dataFileType, "gud"
                )
                if not os.path.exists(path):
                    path = os.path.join(
                        self.gudrunFile.instrument.GudrunInputFileDir, path
                    )
            gf = GudFile(path) if path and os.path.exists(path) else None
            self.results[sample] = [topChart, bottomChart, gf]

    def updateAllSamples(self):

        samples = self.mainWidget.objectTree.getSamples()
        if len(self.allPlots):
            allTopChart = GudPyChart(
                self.gudrunFile
            )
            allTopChart.addSamples(samples)
            allTopChart.plot(PlotModes.STRUCTURE_FACTOR)
            allBottomChart = GudPyChart(
                self.gudrunFile
            )
            allBottomChart.addSamples(samples)
            allBottomChart.plot(PlotModes.RADIAL_DISTRIBUTION_FUNCTIONS)
        else:
            allTopChart = GudPyChart(
                self.gudrunFile
            )
            allTopChart.addSamples(samples)
            allTopChart.plot(PlotModes.STRUCTURE_FACTOR)
            allBottomChart = GudPyChart(
                self.gudrunFile
            )
            allBottomChart.addSamples(samples)
            allBottomChart.plot(PlotModes.RADIAL_DISTRIBUTION_FUNCTIONS)
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

    def makeProc(self, cmd, slot):
        self.proc = cmd
        self.proc.readyReadStandardOutput.connect(slot)
        self.proc.started.connect(self.procStarted)
        self.proc.finished.connect(self.procFinished)
        self.proc.start()

    def runPurge_(self):
        self.setControlsEnabled(False)
        purgeDialog = PurgeDialog(self.gudrunFile, self)
        result = purgeDialog.widget.exec_()
        purge = purgeDialog.purge_det
        if purgeDialog.cancelled or result == QDialogButtonBox.No:
            self.setControlsEnabled(True)
            self.queue = Queue()
        elif not purge:
            QMessageBox.critical(
                self.mainWidget,
                "GudPy Error", "Couldn't find purge_det binary."
            )
            self.setControlsEnabled(True)
        else:
            os.chdir(self.gudrunFile.instrument.GudrunInputFileDir)
            self.makeProc(purge, self.progressPurge)

    def runGudrun_(self):
        self.setControlsEnabled(False)
        self.gudrunFile.write_out()
        dcs = self.gudrunFile.dcs(path="gudpy.txt", headless=False)
        if not dcs:
            QMessageBox.critical(
                self.mainWidget, "GudPy Error",
                "Couldn't find gudrun_dcs binary."
            )
        elif not self.gudrunFile.purged and os.path.exists('purge_det.dat'):
            os.chdir(self.gudrunFile.instrument.GudrunInputFileDir)
            self.purgeOptionsMessageBox(
                dcs,
                "purge_det.dat found, but wasn't run in this session. "
                "Continue?"
            )
        elif not self.gudrunFile.purged:
            os.chdir(self.gudrunFile.instrument.GudrunInputFileDir)
            self.purgeOptionsMessageBox(
                dcs,
                "It looks like you may not have purged detectors. Continue?"
            )
        else:
            os.chdir(self.gudrunFile.instrument.GudrunInputFileDir)
            self.gudrunFile.write_out()
            self.makeProc(dcs, self.progressDCS)

    def purgeOptionsMessageBox(self, dcs, text):
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
            self.gudrunFile.write_out()
            self.makeProc(dcs, self.progressDCS)
        else:
            messageBox.close()
            self.setControlsEnabled(True)

    def purgeBeforeRunning(self, default=True):
        self.setControlsEnabled(False)
        if default:
            purge_det = self.gudrunFile.purge(
                headless=False
            )
            os.chdir(self.gudrunFile.instrument.GudrunInputFileDir)
            self.makeProc(purge_det, self.progressPurge)
        else:
            self.runPurge_()
        self.gudrunFile.write_out()
        dcs = self.gudrunFile.dcs(path="gudpy.txt", headless=False)
        self.queue.put((dcs, self.progressDCS))

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
            self.gudrunFile.write_out()
            self.nextIterableProc()

    def nextIteration(self):
        if isinstance(self.iterator, TweakFactorIterator):
            self.iterator.performIteration(self.currentIteration)
            self.gudrunFile.write_out()
        elif isinstance(self.iterator, WavelengthSubtractionIterator):
            if (self.currentIteration + 1) % 2 == 0:
                self.iterator.QIteration(self.currentIteration)
            else:
                self.iterator.wavelengthIteration(self.currentIteration)
            self.gudrunFile.write_out()
        self.nextIterableProc()
        self.currentIteration += 1

    def nextIterableProc(self):
        self.proc = self.queue.get()
        self.proc.started.connect(self.iterationStarted)
        if not self.queue.empty():
            self.proc.finished.connect(self.nextIteration)
        else:
            self.proc.finished.connect(self.procFinished)
        self.proc.readyReadStandardOutput.connect(self.progressIteration)
        self.proc.started.connect(self.iterationStarted)
        self.proc.start()

    def iterationStarted(self):
        if isinstance(self.iterator, TweakFactorIterator):
            self.mainWidget.currentTaskLabel.setText(
                f"{self.text}"
                f" {self.currentIteration+1}/{self.numberIterations}"
            )
        elif isinstance(self.iterator, WavelengthSubtractionIterator):
            self.mainWidget.currentTaskLabel.setText(
                f"{self.text}"
                f" {(self.currentIteration+1)//2}/{self.numberIterations}"
            )

    def progressIteration(self):
        progress = self.progressIncrementDCS()
        if progress == -1:
            QMessageBox.critical(
                self.mainWidget, "GudPy Error",
                f"An error occurred. See the following traceback"
                f" from gudrun_dcs\n{self.error}"
            )
            return
        if isinstance(self.iterator, TweakFactorIterator):
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
        time.sleep(30)
        self.gudrunFile.write_out(overwrite=True)

    def setModified(self):
        if not self.modified:
            if self.gudrunFile.path:
                self.mainWidget.setWindowTitle(self.gudrunFile.path + " *")
                self.modified = True
                if not self.proc:
                    self._thread = threading.Thread(target = self.autosave, args=())
                    self._thread.setDaemon(True)
                    self._thread.start()


    def setUnModified(self):
        self.mainWidget.setWindowTitle(self.gudrunFile.path)
        self.modified = False

    def setControlsEnabled(self, state):
        self.mainWidget.instrumentPage.setEnabled(state)
        self.mainWidget.beamPage.setEnabled(state)
        self.mainWidget.normalisationPage.setEnabled(state)
        self.mainWidget.sampleTab.setEnabled(state)
        self.mainWidget.advancedTab.setEnabled(state)
        self.mainWidget.containerPage.setEnabled(state)
        self.mainWidget.sampleBackgroundPage.setEnabled(state)
        self.mainWidget.objectTree.setContextDisabled()

        self.mainWidget.insertSampleBackground.setEnabled(state)
        self.mainWidget.insertSample.setEnabled(state)
        self.mainWidget.insertContainer.setEnabled(state)
        self.mainWidget.copy.setEnabled(state)
        self.mainWidget.cut.setEnabled(state)
        self.mainWidget.paste.setEnabled(state)
        self.mainWidget.delete_.setEnabled(state)
        self.mainWidget.runPurge.setEnabled(state)
        self.mainWidget.runGudrun.setEnabled(state)
        self.mainWidget.iterateGudrun.setEnabled(state)
        self.mainWidget.viewLiveInputFile.setEnabled(state)
        self.mainWidget.save.setEnabled(
            state &
            len(self.gudrunFile.path) > 0
            if self.gudrunFile.path
            else False
        )
        self.mainWidget.saveAs.setEnabled(state)
        self.mainWidget.loadInputFile.setEnabled(state)
        self.mainWidget.loadConfiguration.setEnabled(state)

    def setActionsEnabled(self, state):

        self.mainWidget.insertSampleBackground.setEnabled(state)
        self.mainWidget.insertSample.setEnabled(state)
        self.mainWidget.insertContainer.setEnabled(state)
        self.mainWidget.copy.setEnabled(state)
        self.mainWidget.cut.setEnabled(state)
        self.mainWidget.paste.setEnabled(state)
        self.mainWidget.delete_.setEnabled(state)

        self.mainWidget.runPurge.setEnabled(state)
        self.mainWidget.runGudrun.setEnabled(state)
        self.mainWidget.iterateGudrun.setEnabled(state)
        self.mainWidget.checkFilesExist.setEnabled(state)

        self.mainWidget.viewLiveInputFile.setEnabled(state)
        self.mainWidget.save.setEnabled(state)
        self.mainWidget.saveAs.setEnabled(state)

    def progressIncrementDCS(self):
        data = self.proc.readAllStandardOutput()
        stdout = bytes(data).decode("utf8")
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
            QMessageBox.critical(
                self.mainWidget, "GudPy Error",
                f"An error occurred. See the following traceback"
                f" from gudrun_dcs\n{self.error}"
            )
            self.procFinished()
            self.queue = Queue()
            return
        progress += self.mainWidget.progressBar.value()
        self.mainWidget.progressBar.setValue(
            progress if progress <= 100 else 100
        )
        if progress >= 100:
            os.chdir(self.cwd)

    def progressIncrementPurge(self):
        data = self.proc.readAllStandardOutput()
        stdout = bytes(data).decode("utf8")
        print(stdout)
        dataFiles = [self.gudrunFile.instrument.groupFileName]

        def appendDfs(dfs):
            for df in dfs.splitlines():
                dataFiles.append(df.split()[0].replace(
                    self.gudrunFile.instrument.dataFileType, "grp")
                )

        appendDfs(self.gudrunFile.purgeFile.normalisationDataFiles)
        appendDfs(self.gudrunFile.purgeFile.sampleBackgroundDataFiles)
        if not self.gudrunFile.purgeFile.excludeSampleAndCan:
            appendDfs(self.gudrunFile.purgeFile.sampleDataFiles)
            appendDfs(self.gudrunFile.purgeFile.containerDataFiles)

        stepSize = math.ceil(100/len(dataFiles))
        progress = 0
        for df in dataFiles:
            if df in stdout:
                progress += stepSize
        if "Error" in stdout or "error" in stdout or "not found" in stdout:
            self.error = stdout
            return -1, False, -1
        elif dataFiles[-1] in stdout:
            return 100, True, nthint(stdout, 0)
        else:
            return progress, False, -1

    def progressPurge(self):
        progress, finished, detectors = self.progressIncrementPurge()
        if progress == -1:
            QMessageBox.critical(
                self.mainWidget, "GudPy Error",
                f"An error occurred. See the following traceback"
                f" from purge_det\n{self.error}"
            )
            self.gudrunFile.purged = False
            self.procFinished()
            self.queue = Queue()
        progress += self.mainWidget.progressBar.value()
        self.mainWidget.progressBar.setValue(
            progress if progress <= 100 else 100
        )
        if finished:
            QMessageBox.warning(
                self.mainWidget, "GudPy Warning",
                f"{detectors} detectors made it through the purge."
            )
            os.chdir(self.cwd)

    def procStarted(self):
        self.mainWidget.currentTaskLabel.setText(
            self.proc.program().split(os.path.sep)[-1]
        )

    def procFinished(self):
        self.proc = None
        if isinstance(self.iterator, TweakFactorIterator):
            self.sampleSlots.setSample(self.sampleSlots.sample)
        self.iterator = None
        if "purge_det" not in self.mainWidget.currentTaskLabel.text():
            self.updateResults()
        self.mainWidget.currentTaskLabel.setText("No task running.")
        self.mainWidget.progressBar.setValue(0)
        if not self.queue.empty():
            self.makeProc(*self.queue.get())
        else:
            self.setControlsEnabled(True)

    def viewInput(self):
        self.currentState = str(self.gudrunFile)
        viewInputDialog = ViewInputDialog(self.gudrunFile, self)
        viewInputDialog.widget.exec_()

    def handleTopPlotModeChanged(self, index):
        self.handlePlotModeChanged(
            self.mainWidget.sampleTopPlot.chart().plot,
            self.mainWidget.topPlotComboBox.itemData(index)
        )

    def handleBottomPlotModeChanged(self, index):
        self.handlePlotModeChanged(
            self.mainWidget.sampleBottomPlot.chart().plot,
            self.mainWidget.bottomPlotComboBox.itemData(index)
        )

    def handleTopAllPlotModeChanged(self, index):
        self.handlePlotModeChanged(
            self.mainWidget.allSampleTopPlot.chart().plot,
            self.mainWidget.topAllPlotComboBox.itemData(index)
        )

    def handleBottomAllPlotModeChanged(self, index):
        self.handlePlotModeChanged(
            self.mainWidget.allSampleBottomPlot.chart().plot,
            self.mainWidget.bottomAllPlotComboBox.itemData(index)
        )

    def handlePlotModeChanged(self, plot, plotMode):
        plot(plotMode)

    def onException(self, cls, exception, tb):
        QMessageBox.critical(
            self.mainWidget,
            "GudPy Error",
            f"{''.join(traceback.format_exception(cls, exception, tb))}"
        )
        self.gudrunFile.write_out(overwrite=False, path = Path(self.gudrunFile.path).stem + ".recovery")
