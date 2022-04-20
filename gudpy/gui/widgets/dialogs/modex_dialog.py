import os
import sys
import subprocess

from PySide6.QtWidgets import QDialog
from PySide6.QtCore import QFile, Qt
from PySide6.QtUiTools import QUiLoader

from src.scripts.utils import resolve
from src.gudrun_classes import config


SUFFIX = ".exe" if os.name == "nt" else ""

class ModexDialog(QDialog):

    def __init__(self, gudrunFile, parent, spectraRange):
        super(ModexDialog, self).__init__(parent=parent)
        self.gudrunFile = gudrunFile
        self.spectraRange = spectraRange
        self.loadUI()
        self.initComponents()
        # if hasattr(sys, '_MEIPASS'):
        #     partition_events = os.path.join(sys._MEIPASS, f"partition_events{SUFFIX}")
        # else:
        #     partition_events = resolve(
        #         os.path.join(
        #             config.__rootdir__, "bin"
        #         ), f"partition_events{SUFFIX}"
        #     )
        # subprocess.run(
        #     [
        #         partition_events,
        #         os.path.join(
        #             self.gudrunFile.instrument.dataFileDir,
        #             self.gudrunFile.sampleBackgrounds[0].samples[0].dataFiles.dataFiles[0]
        #         )
        #     ]
        # )

    def initComponents(self):
        self.widget.spectraTableView.makeModel(
            list(range(self.spectraRange[0], self.spectraRange[1]+1))
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