import os
import sys
from PySide6.QtCore import QFile
from PySide6.QtUiTools import QUiLoader
from PySide6.QtWidgets import QDialog


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
        self.purge_det = self.gudrunFile.purge(
            headless=False,
            standardDeviation=(
                self.stdDeviationsAcceptanceOffset,
                self.stdsAroundMeanDeviation
            ),
            ignoreBad=self.ignoreBad,
            excludeSampleAndCan=self.excludeSampleAndCan
        )
        self.widget.close()

    def cancel(self):
        self.cancelled = True
        self.widget.close()

    def handleStdDeviationsAcceptanceOffsetChanged(self, value):
        self.stdDeviationsAcceptanceOffset = value

    def handleStdsAroundMeanDeviationChanged(self, value):
        self.stdsAroundMeanDeviation = value

    def ignoreBadChanged(self, state):
        self.ignoreBad = bool(state)

    def excludeSampleAndCanChanged(self, state):
        self.excludeSampleAndCan = state

    def initComponents(self):
        """
        Loads the UI file for the IterationDialog object.
        """
        if hasattr(sys, '_MEIPASS'):
            uifile = QFile(
                os.path.join(
                    sys._MEIPASS, "ui_files", "purgeDialog.ui"
                )
            )
        else:
            current_dir = os.path.dirname(os.path.realpath(__file__))
            uifile = QFile(
                os.path.join(
                    current_dir, "..", "ui_files", "purgeDialog.ui"
                )
            )
        loader = QUiLoader()
        self.widget = loader.load(uifile)
        self.widget.buttonBox.accepted.connect(
            self.purge
        )
        self.widget.buttonBox.rejected.connect(
            self.cancel
        )
        self.widget.stdDeviationsSpinBox.valueChanged.connect(
            self.handleStdDeviationsAcceptanceOffsetChanged
        )
        self.widget.rangeAroundMeanSpinBox.valueChanged.connect(
            self.handleStdsAroundMeanDeviationChanged
        )
        self.widget.ignoreBadCheckBox.toggled.connect(
            self.ignoreBadChanged
        )
        self.widget.excludeSampleAndCanCheckBox.toggled.connect(
            self.excludeSampleAndCanChanged
        )
