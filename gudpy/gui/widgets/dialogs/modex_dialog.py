import os
import sys
import subprocess
import h5py as h5

from PySide6.QtWidgets import QDialog, QFileDialog
from PySide6.QtCore import QFile, Qt, QProcess
from PySide6.QtUiTools import QUiLoader
from core.enums import ExtrapolationModes

from core.utils import resolve
from core import config


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

        self.loadUI()
        self.initComponents()
        if hasattr(sys, '_MEIPASS'):
            self.partition_events = os.path.join(
                sys._MEIPASS, f"partition_events{SUFFIX}"
            )
            self.modex = os.path.join(
                sys._MEIPASS, f"modulation_excitation{SUFFIX}"
            )
        else:
            self.partition_events = resolve(
                os.path.join(
                    config.__rootdir__, "bin"
                ), f"partition_events{SUFFIX}"
            )
            self.modex = resolve(
                os.path.join(
                    config.__rootdir__, "bin"
                ), f"modulation_excitation{SUFFIX}"
            )
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
            self.widget.lowerSpecSpinBox.setRange(min(spectra), max(spectra))
            self.widget.upperSpecSpinBox.setRange(min(spectra), max(spectra))

        self.widget.lowerSpecSpinBox.setValue(min(spectra))
        self.widget.upperSpecSpinBox.setValue(max(spectra))

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
            self.close
        )

        self.widget.buttonBox.rejected.connect(
            self.cancel
        )

        self.widget.browseOutputDirButton.clicked.connect(
            self.browseSaveDirectory
        )

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
                str(self.widget.upperSpecSpinBox.value())
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

    def toggleUseAllPulses(self, state):
        self.widget.extrapolationModeComboBox.setEnabled(not state)
        self.gudrunFile.modex.useDefinedPulses = not state

    def extrapolationModeChanged(self, index):
        extrapolationMode = self.widget.extrapolationModeComboBox.itemData(
            index
        )
        self.gudrunFile.modex.extrapolationMode = extrapolationMode


    def startPulseChanged(self, item):
        if self.widget.eventTableView.selectionModel().hasSelection():
            if len(item.indexes()):
                index = item.indexes()[0]
                startPulse = self.widget.eventTableView.model().data(
                    index, role=Qt.DisplayRole
                )
                self.gudrunFile.modex.startPulse = startPulse

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
