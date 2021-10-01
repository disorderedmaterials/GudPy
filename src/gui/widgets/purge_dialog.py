from PyQt5.QtWidgets import QDialog
from PyQt5 import uic
import os
from src.gudrun_classes.purge_file import PurgeFile


class PurgeDialog(QDialog):
    """
    Class to represent the PurgeDialog. Inherits QDialog.
    This is the dialog window opened when a user wishes to run purge_det.

    ...

    Attributes
    ----------
    gudrunFile : GudrunFile
        GudrunFile object currently associated with the application.
    Methods
    -------
    initComponents()
        Loads the UI file for the IterationDialog
    """
    def __init__(self, gudrunFile, parent):
        super(PurgeDialog, self).__init__(parent=parent)
        self.gudrunFile = gudrunFile
        self.stdDeviationsAcceptanceOffset = 10
        self.stdsAroundMeanDeviation = 10
        self.excludeSampleAndCan = True
        self.ignoreBad = True
        self.purge_det = None
        self.cancelled = False
        self.initComponents()
        self.setModal(True)

    def purge(self):    
        """
        Purge with the specified configuration.
        Called when an accepted signal is emmited from the buttonBox.
        """
        self.purge_det = self.gudrunFile.purge(headless=False, standardDeviation=(self.stdDeviationsAcceptanceOffset, self.stdsAroundMeanDeviation), ignoreBad=self.ignoreBad, excludeSampleAndCan=self.excludeSampleAndCan)
        self.close()
    
    def cancel(self):
        self.cancelled = True
        self.close()

    def handleStdDeviationsAcceptanceOffsetChanged(self, value):
        self.stdDeviationsAcceptanceOffset = value

    def handleStdsAroundMeanDeviationChanged(self, value):
        self.stdsAroundMeanDeviation = value

    def ignoreBadChanged(self, state):
        self.ignoreBad = state

    def initComponents(self):
        """
        Loads the UI file for the IterationDialog object.
        """
        current_dir = os.path.dirname(os.path.realpath(__file__))
        uifile = os.path.join(current_dir, "ui_files/purgeDialog.ui")
        uic.loadUi(uifile, self)
        self.buttonBox.accepted.connect(
            self.purge
        )
        self.buttonBox.rejected.connect(
            self.cancel
        )
        self.stdDeviationsSpinBox.valueChanged.connect(
            self.handleStdDeviationsAcceptanceOffsetChanged
        )
        self.rangeAroundMeanSpinBox.valueChanged.connect(
            self.handleStdsAroundMeanDeviationChanged
        )
        self.ignoreBadCheckBox.toggled.connect(
            self.ignoreBadChanged
        )