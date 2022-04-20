import os
import sys
import h5py as h5

from PySide6.QtWidgets import QDialog
from PySide6.QtCore import QFile
from PySide6.QtUiTools import QUiLoader


class SpectraSelectionDialog(QDialog):

    def __init__(self, gudrunFile, parent):
        super(SpectraSelectionDialog, self).__init__(parent=parent)
        self.gudrunFile = gudrunFile
        self.cancelled = False
        self.lowSpec = 0
        self.highSpec = 0
        self.loadUI()
        self.initComponents()

    def initComponents(self):
        with h5.File(self.gudrunfile.sampleBackgrounds[0].samples[0].dataFiles.dataFiles[0]) as fp:
            spectra = fp["/raw_data_1/detector_1/spectrum_index"][()][:].tolist()
            self.widget.lowerSpecSpinBox.setRange(min(spectra), max(spectra))

    def cancel(self):
        self.cancelled = True
        self.widget.close()

    def loadUI(self):
        """
        Loads the UI file for the SpectraSelectionDialog object.
        """
        if hasattr(sys, '_MEIPASS'):
            uifile = QFile(
                os.path.join(
                    sys._MEIPASS, "ui_files", "spectraSelectionDialog.ui"
                )
            )
        else:
            current_dir = os.path.dirname(os.path.realpath(__file__))
            uifile = QFile(
                os.path.join(
                    current_dir, "..", "ui_files", "spectraSelectionDialog.ui"
                )
            )
        loader = QUiLoader()
        self.widget = loader.load(uifile)
        self.widget.buttonBox.accepted.connect(
            self.widget.close
        )
        self.widget.buttonBox.rejected.connect(
            self.cancel
        )