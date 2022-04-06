import os
from queue import Queue
import sys

from PySide6.QtWidgets import QDialog
from PySide6.QtCore import QFile
from PySide6.QtUiTools import QUiLoader

class IterationDialog():

    def __init__(self, name, gudrunFile, parent):
        super(IterationDialog, self).__init__(parent=parent)
        self.gudrunFile = gudrunFile
        self.name = name
        self.numberIterations = 1
        self.loadUI()
        self.initComponents()

    def initComponents(self):
        self.widget.numberIterationsSpinBox.valueChanged.connect(
            self.numberIterationsChanged
        )

        self.widget.iterateButton.clicked.connect(
            self.iterate
        )

    def loadUI(self):
        """
        Loads the UI file for the IterationDialog object.
        """
        if hasattr(sys, '_MEIPASS'):
            uifile = QFile(
                os.path.join(
                    sys._MEIPASS, "ui_files", f"{self.name}.ui"
                )
            )
        else:
            current_dir = os.path.dirname(os.path.realpath(__file__))
            uifile = QFile(
                os.path.join(
                    current_dir, "..", "ui_files", f"{self.name}.ui"
                )
            )
        loader = QUiLoader()
        self.widget = loader.load(uifile)
    
    def iterate(self):
        pass

    def numberIterationsChanged(self, value):
        pass
    
    def enqueueTasks(self):
        self.queue = Queue()
        for _ in range(self.numberIterations):
            self.queue.put(
                self.gudrunFile.dcs(
                    path=os.path.join(
                        self.gudrunFile.instrument.GudrunInputFileDir,
                        "gudpy.txt"
                    ), headless=False)
            )