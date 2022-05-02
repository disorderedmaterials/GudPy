import os
from queue import Queue
import sys
import h5py as h5

from PySide6.QtWidgets import QDialog, QFileDialog
from PySide6.QtCore import QFile, Qt, QProcess
from PySide6.QtUiTools import QUiLoader
from PySide6.QtCharts import QChartView
from PySide6.QtGui import QPainter
from core.enums import ExtrapolationModes

from core.utils import resolve
from core import config
from gui.widgets.charts.spectra_plot import SpectraChart


SUFFIX = ".exe" if os.name == "nt" else ""


class ModexDialog(QDialog):

    def __init__(self, gudrunFile, parent):
        super(ModexDialog, self).__init__(parent=parent)
        self.gudrunFile = gudrunFile
        self.gudrunFile.modex.sample = (
            gudrunFile.sampleBackgrounds[0].samples[0]
        )
        self.cancelled = False
        self.proc = None
        self.queue = None
        self.useTempDir = True

        self.loadUI()
        self.initComponents()
        if hasattr(sys, '_MEIPASS'):
            self.partition_events = os.path.join(
                sys._MEIPASS, f"partition_events{SUFFIX}"
            )
        else:
            self.partition_events = resolve(
                os.path.join(
                    config.__rootdir__, "bin"
                ), f"partition_events{SUFFIX}"
            )
        self.run()

    def loadUI(self):
        """
        Loads the UI file for the ModexDialog object.
        """
        if hasattr(sys, '_MEIPASS'):
            uifile = QFile(
                os.path.join(
                    sys._MEIPASS, "ui_files", "modulationExcitationDialog.ui"
                )
            )
        else:
            current_dir = os.path.dirname(os.path.realpath(__file__))
            uifile = QFile(
                os.path.join(
                    current_dir, "..", "ui_files",
                    "modulationExcitationDialog.ui"
                )
            )
        loader = QUiLoader()
        self.widget = loader.load(uifile)

    def initComponents(self):

        self.widget.pulseTableView.makeModel(
            self.gudrunFile.modex.period.pulses, self.gudrunFile.modex
        )
        self.widget.addPulseButton.clicked.connect(
            self.widget.pulseTableView.insertRow
        )

        with h5.File(
            os.path.join(
                self.gudrunFile.instrument.dataFileDir,
                self.gudrunFile.sampleBackgrounds[0].
                samples[0].dataFiles.dataFiles[0]
            )
        ) as fp:
            spectra = fp[
                "/raw_data_1/detector_1/spectrum_index"
                ][()][:].tolist()
            start = 0
            end = fp["/raw_data_1/duration"][()]
            self.widget.lowerSpecSpinBox.setRange(min(spectra), max(spectra))
            self.widget.upperSpecSpinBox.setRange(min(spectra), max(spectra))

        self.widget.lowerSpecSpinBox.setValue(min(spectra))
        self.widget.upperSpecSpinBox.setValue(max(spectra))

        self.widget.periodDurationSpinBox.valueChanged.connect(
            self.periodDurationChanged
        )

        self.widget.updateSpectraButton.clicked.connect(
            self.partitionEvents
        )
        self.widget.useAllPulsesCheckBox.toggled.connect(
            self.toggleUseAllPulses
        )

        for m in ExtrapolationModes:
            self.widget.extrapolationModeComboBox.addItem(m.name, m)

        self.widget.extrapolationModeComboBox.currentIndexChanged.connect(
            self.extrapolationModeChanged
        )

        self.widget.buttonBox.accepted.connect(
            self.run
        )

        self.widget.buttonBox.rejected.connect(
            self.cancel
        )

        self.widget.periodGroupBox.toggled.connect(
            self.useDefinedPulsesToggled
        )

        self.widget.browseOutputDirButton.clicked.connect(
            self.browseSaveDirectory
        )

        self.widget.useTempDirButton.toggled.connect(
            self.useTempDirToggled
        )

        self.widget.useDataFileDirButton.toggled.connect(
            self.useDataFileDirToggled
        )


        self.widget.useDataFileDirButton.setEnabled(
            os.access(self.gudrunFile.instrument.dataFileDir, os.W_OK)
        )

        self.widget.spectraPlot = QChartView(
            self.widget
        )
        self.widget.spectraPlot.setRenderHint(QPainter.Antialiasing)
        self.widget.pulsePlotLayout.addWidget(
            self.widget.spectraPlot
        )
        self.widget.spectraChart = SpectraChart(self.widget)
        self.widget.spectraPlot.setChart(self.widget.spectraChart)
        self.widget.spectraChart.setTimeBoundaries(start, end)
        self.widget.spectraPlot.setRenderHint(QPainter.Antialiasing)

    def process(self, files):
        pass
        
    def run(self):
        self.preprocess = self.gudrunFile.modex.preprocess(useTempDir=self.useTempDir, headless=False)
        self.widget.close()

    def cancel(self):
        self.cancelled = True
        self.widget.close()

    def partitionEvents(self):
        self.setControlsEnabled(False)
        self.proc = QProcess()
        self.proc.setProgram(self.partition_events)
        self.proc.setArguments(
            [
                os.path.join(
                    self.gudrunFile.instrument.dataFileDir,
                    self.gudrunFile.sampleBackgrounds[0]
                    .samples[0].dataFiles.dataFiles[0]
                ),
                str(self.widget.lowerSpecSpinBox.value()),
                str(self.widget.upperSpecSpinBox.value()),
                "output.nxs"
            ]
        )
        self.proc.finished.connect(self.updateSpectra)
        self.proc.start()

    def updateSpectra(self):
        self.widget.spectraTableView.makeModel(
            list(
                range(
                    self.widget.lowerSpecSpinBox.value(),
                    self.widget.upperSpecSpinBox.value()+1
                )
            )
        )
        self.widget.spectraTableView.selectionModel().selectionChanged.connect(
            self.loadEvents
        )
        self.proc = None
        self.setControlsEnabled(True)

    def loadEvents(self, item):
        if self.widget.spectraTableView.selectionModel().hasSelection():
            if len(item.indexes()):
                index = item.indexes()[0]
                spec = self.widget.spectraTableView.model().data(
                    index, role=Qt.DisplayRole
                )
                self.widget.eventTableView.makeModel(
                    "output.nxs", str(spec)
                )
                self.widget.eventTableView.selectionModel().selectionChanged.connect(
                    self.startPulseChanged
                )
                self.widget.spectraChart.setSpectra(spec, self.widget.eventTableView.model()._data)

    def toggleUseAllPulses(self, state):
        self.widget.extrapolationModeComboBox.setEnabled(not state)
        self.gudrunFile.modex.useDefinedPulses = not state

    def extrapolationModeChanged(self, index):
        extrapolationMode = self.widget.extrapolationModeComboBox.itemData(
            index
        )
        self.gudrunFile.modex.extrapolationMode = extrapolationMode

    def periodDurationChanged(self, value):
        self.gudrunFile.modex.period.duration = value

    def startPulseChanged(self, item):
        if self.widget.eventTableView.selectionModel().hasSelection():
            if len(item.indexes()):
                index = item.indexes()[0]
                startPulse = self.widget.eventTableView.model().data(
                    index, role=Qt.DisplayRole
                )
                self.gudrunFile.modex.period.startPulse = startPulse

    def setControlsEnabled(self, state):
        self.widget.periodGroupBox.setEnabled(state)
        self.widget.spectraGroupBox.setEnabled(state)
        self.widget.runGroupBox.setEnabled(state)

    def browseSaveDirectory(self):
        self.gudrunFile.modex.outputDir = (
            QFileDialog.getExistingDirectory(
                self.widget, "Ouput Directory", os.path.expanduser("~")
            )
        )
        self.widget.outputDirLineEdit.setText(self.gudrunFile.modex.outputDir)

    def useTempDirToggled(self, state):
        self.useTempDir = state
    
    def useDataFileDirToggled(self, state):
        self.useDataFileDir = state

    def useDefinedPulsesToggled(self, state):
        self.gudrunFile.modex.definedPulses = state