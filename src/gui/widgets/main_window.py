from PySide6.QtCore import QFile
from PySide6.QtGui import QPainter
from src.gui.widgets.exponential_spinbox import ExponentialSpinBox
from src.gudrun_classes.tweak_factor_iterator import TweakFactorIterator
from src.gudrun_classes.wavelength_subtraction_iterator import (
    WavelengthSubtractionIterator
)
from src.gudrun_classes.gud_file import GudFile
from src.gui.widgets.gudpy_charts import (
  GudPyChart, PlotModes, GudPyChartView
)
from src.scripts.utils import nthint
from src.gudrun_classes.file_library import GudPyFileLibrary
from src.gui.widgets.iteration_dialog import IterationDialog
import sys
from src.gudrun_classes.gudrun_file import GudrunFile
from src.gudrun_classes.exception import ParserException
from src.gudrun_classes import config
from PySide6.QtWidgets import (
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMessageBox,
    QProgressBar,
    QSizePolicy,
    QStatusBar,
    QWidget
)
from src.gui.widgets.purge_dialog import PurgeDialog
from src.gui.widgets.view_input import ViewInput
from src.gui.widgets.gudpy_tree import GudPyTreeView
from src.gui.widgets.gudpy_tables import GroupingParameterTable
from src.gui.widgets.gudpy_tables import BeamProfileTable
from src.gui.widgets.gudpy_tables import ResonanceTable
from src.gui.widgets.gudpy_tables import CompositionTable
from src.gui.widgets.gudpy_tables import ExponentialTable
from src.gudrun_classes.enums import Geometry
import os
from PySide6.QtUiTools import QUiLoader
from src.gui.widgets.beam_slots import BeamSlots
from src.gui.widgets.container_slots import ContainerSlots
from src.gui.widgets.instrument_slots import InstrumentSlots
from src.gui.widgets.normalisation_slots import NormalisationSlots
from src.gui.widgets.sample_background_slots import SampleBackgroundSlots
from src.gui.widgets.sample_slots import SampleSlots
import math
from src.gui.widgets.resources import resources_rc  # noqa


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
        self.initComponents()
        self.clipboard = None
        self.modified = False
        self.iterator = None
        self.allPlots = []
        self.results = {}

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
        loader.registerCustomWidget(ExponentialTable)
        loader.registerCustomWidget(ResonanceTable)
        loader.registerCustomWidget(IterationDialog)
        loader.registerCustomWidget(PurgeDialog)
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
        self.mainWidget.bottomAllPlotComboBox.addItem(
            "Radial Distribution Functions",
            PlotModes.RADIAL_DISTRIBUTION_FUNCTIONS
        )

        self.mainWidget.topPlotComboBox.addItem(
            "Structure Factor",
            PlotModes.STRUCTURE_FACTOR
        )
        self.mainWidget.bottomPlotComboBox.addItem(
            "Radial Distribution Functions",
            PlotModes.RADIAL_DISTRIBUTION_FUNCTIONS
        )

        self.mainWidget.setWindowTitle("GudPy")
        self.mainWidget.show()
        self.instrumentSlots = InstrumentSlots(self.mainWidget, self)
        self.beamSlots = BeamSlots(self.mainWidget, self)
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
            lambda: ViewInput(self.gudrunFile, parent=self)
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
        self.mainWidget.objectStack.currentChanged.connect(
            self.updateComponents
        )

        self.mainWidget.exit.triggered.connect(self.exit_)

        self.setActionsEnabled(False)
        self.mainWidget.tabWidget.setVisible(False)

    def updateWidgets(self):
        self.mainWidget.gudrunFile = self.gudrunFile
        self.mainWidget.tabWidget.setVisible(True)
        self.instrumentSlots.setInstrument(self.gudrunFile.instrument)
        self.beamSlots.setBeam(self.gudrunFile.beam)
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
        filename = QFileDialog.getOpenFileName(
            self, "Select Input file for GudPy", ".", "GudPy input (*.txt)"
        )[0]
        if filename:
            try:
                self.gudrunFile = GudrunFile(filename)
                self.updateWidgets()
            except ParserException as e:
                QMessageBox.critical(self.mainWidget, "GudPy Error", str(e))

    def saveInputFile(self):
        """
        Saves the current state of the input file.
        """
        self.gudrunFile.write_out(overwrite=True)
        self.setUnModified()

    def saveInputFileAs(self):
        """
        Saves the current state of the input file as...
        """
        filename = QFileDialog.getSaveFileName(
            self, "Save input file as..", "."
        )[0]
        if filename:
            self.gudrunFile.outpath = filename
            self.gudrunFile.write_out()
            self.setUnModified()

    def updateFromFile(self):
        """
        Calls initComponents() again, to update the UI.
        """
        self.initComponents()

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
        self.mainWidget.containerCompositionTable.farmCompositions()

    def updateResults(self):
        if self.mainWidget.objectStack.currentIndex() == 4:
            sample = self.mainWidget.objectTree.currentObject()
            self.mainWidget.sampleChart = GudPyChart(
                self.gudrunFile.instrument.dataFileType,
                self.gudrunFile.instrument.GudrunInputFileDir,
                sample=sample
            )
            self.mainWidget.sampleTopPlot.setChart(
                self.mainWidget.sampleChart
            )
            self.mainWidget.sampleRDFChart = GudPyChart(
                self.gudrunFile.instrument.dataFileType,
                self.gudrunFile.instrument.GudrunInputFileDir,
                sample=sample,
                plotMode=PlotModes.RADIAL_DISTRIBUTION_FUNCTIONS
            )
            self.mainWidget.sampleBottomPlot.setChart(
                self.mainWidget.sampleRDFChart
            )
            path = sample.dataFiles.dataFiles[0].replace(
                self.gudrunFile.instrument.dataFileType, "gud"
            )
            if not os.path.exists(path):
                path = os.path.join(
                    self.gudrunFile.instrument.GudrunInputFileDir, path
                )
            if os.path.exists(path):
                gf = GudFile(path)
                dcsLevel = gf.averageLevelMergedDCS
                self.mainWidget.dcsLabel.setText(
                    f"DCS Level: {dcsLevel}"
                )
                self.mainWidget.resultLabel.setText(gf.output)
                if gf.err:
                    self.mainWidget.resultLabel.setStyleSheet(
                        "background-color: red"
                    )
                else:
                    self.mainWidget.resultLabel.setStyleSheet(
                        "background-color: green"
                    )

        self.mainWidget.allSamplesChart = GudPyChart(
            self.gudrunFile.instrument.dataFileType,
            self.gudrunFile.instrument.GudrunInputFileDir,
            samples=[
                sample
                for sampleBackground in self.gudrunFile.sampleBackgrounds
                for sample in sampleBackground.samples
            ]
        )
        self.mainWidget.allSampleTopPlot.setChart(
            self.mainWidget.allSamplesChart
        )

        self.mainWidget.allSamplesRDFChart = GudPyChart(
            self.gudrunFile.instrument.dataFileType,
            self.gudrunFile.instrument.GudrunInputFileDir,
            samples=[
                sample
                for sampleBackground in self.gudrunFile.sampleBackgrounds
                for sample in sampleBackground.samples
            ],
            plotMode=PlotModes.RADIAL_DISTRIBUTION_FUNCTIONS
        )
        self.mainWidget.allSampleBottomPlot.setChart(
            self.mainWidget.allSamplesRDFChart
        )

    def updateComponents(self):
        """
        Updates geometries and compositions.
        """
        self.updateGeometries()
        self.updateCompositions()
        self.updateResults()

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
        self.setControlsEnabled(True)
        purgeDialog = PurgeDialog(self.gudrunFile, self)
        purgeDialog.widget.exec()
        purge = purgeDialog.purge_det
        if purgeDialog.cancelled:
            self.setControlsEnabled(True)
        elif not purge:
            QMessageBox.critical(
                self.mainWidget,
                "GudPy Error", "Couldn't find purge_det binary."
            )
            self.setControlsEnabled(True)
        else:
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
        elif not self.gudrunFile.purged:
            choice = QMessageBox.warning(
                self.mainWidget, "GudPy Warning",
                "It looks like you may not have purged detectors. Continue?",
                QMessageBox.Yes | QMessageBox.No
            )
            if choice == QMessageBox.No:
                self.setControlsEnabled(True)
            else:
                self.gudrunFile.write_out()
                self.makeProc(dcs, self.progressDCS)
        else:
            self.gudrunFile.write_out()
            self.makeProc(dcs, self.progressDCS)

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
        progress = self.progressIncrement()
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
            unresolved = "\n".join(r[1] for r in result if not r[0])
            QMessageBox.critical(
                self.mainWidget, "GudPy Error",
                f"Couldn't resolve some files!"
                f" Check that all paths are correct and try again."
                f"{unresolved}"
            )

    def setModified(self):
        if not self.modified:
            self.setWindowTitle(self.gudrunFile.path + " *")
            self.modified = True

    def setUnModified(self):
        if self.modified:
            self.setWindowTitle(self.gudrunFile.path)
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
        self.mainWidget.save.setEnabled(state)
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

        self.mainWidget.viewLiveInputFile.setEnabled(state)
        self.mainWidget.save.setEnabled(state)
        self.mainWidget.saveAs.setEnabled(state)

    def progressIncrement(self):
        data = self.proc.readAllStandardOutput()
        stdout = bytes(data).decode("utf8")
        print(stdout)
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
        progress = self.progressIncrement()
        if progress == -1:
            QMessageBox.critical(
                self.mainWidget, "GudPy Error",
                f"An error occurred. See the following traceback"
                f" from gudrun_dcs\n{self.error}"
            )
            return
        progress += self.mainWidget.progressBar.value()
        self.mainWidget.progressBar.setValue(
            progress if progress <= 100 else 100
        )

    def progressPurge(self):
        data = self.proc.readAllStandardOutput()
        stdout = bytes(data).decode("utf8")
        print(stdout)
        if "Total run time" in stdout:
            QMessageBox.warning(
                self.mainWidget, "GudPy Warning",
                f"{nthint(stdout, 0)} detectors made it through the purge."
            )
        elif "Error" in stdout or "error" in stdout:
            QMessageBox.critical(
                self.mainWidget, "GudPy Error",
                f"An error occurred. See the following traceback"
                f" from purge_det\n{stdout}"
            )

    def procStarted(self):
        self.mainWidget.currentTaskLabel.setText(
            self.proc.program().split(os.path.sep)[-1]
        )

    def procFinished(self):
        self.proc = None
        if isinstance(self.iterator, TweakFactorIterator):
            self.sampleSlots.setSample(self.sampleSlots.sample)
        self.iterator = None
        self.setControlsEnabled(True)
        self.mainWidget.currentTaskLabel.setText("No task running.")
        self.mainWidget.progressBar.setValue(0)
        self.updateResults()
