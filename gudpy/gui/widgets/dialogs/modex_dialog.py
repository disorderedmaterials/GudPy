import os
import sys
import subprocess
import h5py as h5

from PySide6.QtWidgets import QDialog
from PySide6.QtCore import QFile, Qt
from PySide6.QtUiTools import QUiLoader
from src.gudrun_classes.enums import ExtrapolationModes

from src.scripts.utils import resolve
from src.gudrun_classes import config


SUFFIX = ".exe" if os.name == "nt" else ""

class ModexDialog(QDialog):

    def __init__(self, gudrunFile, parent):
        super(ModexDialog, self).__init__(parent=parent)
        self.gudrunFile = gudrunFile
        self.loadUI()
        self.initComponents()
        if hasattr(sys, '_MEIPASS'):
            partition_events = os.path.join(sys._MEIPASS, f"partition_events{SUFFIX}")
        else:
            partition_events = resolve(
                os.path.join(
                    config.__rootdir__, "bin"
                ), f"partition_events{SUFFIX}"
            )
        # subprocess.run(
        #     [
        #         partition_events,
        #         os.path.join(
        #             self.gudrunFile.instrument.dataFileDir,
        #             self.gudrunFile.sampleBackgrounds[0].samples[0].dataFiles.dataFiles[0]
        #         ),
        #         str(spectraRange[0]),
        #         str(spectraRange[1])
        #     ]
        # )

    def loadUI(self):
        """
        Loads the UI file for the PeriodDialog object.
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
                    current_dir, "..", "ui_files", "modulationExcitationDialog.ui"
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
                self.gudrunFile.sampleBackgrounds[0].samples[0].dataFiles.dataFiles[0]
            )
        ) as fp:
            spectra = fp["/raw_data_1/detector_1/spectrum_index"][()][:].tolist()
            self.widget.lowerSpecSpinBox.setRange(min(spectra), max(spectra))
            self.widget.upperSpecSpinBox.setRange(min(spectra), max(spectra))

        # self.widget.lowerSpecSpinBox.valueChanged.connect(self.lowChanged)
        # self.widget.upperSpecSpinBox.valueChanged.connect(self.highChanged)

        self.widget.lowerSpecSpinBox.setValue(min(spectra))
        self.widget.upperSpecSpinBox.setValue(max(spectra))

        self.widget.updateSpectraButton.clicked.connect(
            self.updateSpectra
        )

        # self.widget.spectraTableView.makeModel(
        #     list(range(self.spectraRange[0], self.spectraRange[1]+1))
        # )
        # self.widget.spectraTableView.selectionModel().selectionChanged.connect(
        #     self.loadEvents
        # )
        self.widget.useAllPulsesCheckBox.toggled.connect(self.toggleUseAllPulses)

        for m in ExtrapolationModes:
            self.widget.extrapolationModeComboBox.addItem(m.name, m)

    def updateSpectra(self):
        self.widget.spectraTableView.makeModel(
            list(range(self.widget.lowerSpecSpinBox.value(), self.widget.upperSpecSpinBox.value()+1))
        )
        self.widget.spectraTableView.selectionModel().selectionChanged.connect(
            self.loadEvents
        )

    def loadEvents(self, item):
        if self.widget.spectraTableView.selectionModel().hasSelection():
            if len(item.indexes()):
                index = item.indexes()[0]
                spec = self.widget.spectraTableView.model().data(index, role=Qt.DisplayRole)
                self.widget.eventTableView.makeModel(
                    "output.nxs", str(spec)
                )

    def toggleUseAllPulses(self, state):
        self.widget.extrapolationModeComboBox.setEnabled(not state)

    def run(self):
        pass