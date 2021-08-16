from PyQt5.QtWidgets import QWidget
from PyQt5 import uic
import os

class BeamWidget(QWidget):
    def __init__(self, instrument, parent=None):
        self.instrument = instrument
        self.parent = parent

        super(BeamWidget, self).__init__(self.parent)
        self.initComponents()
    
    def initComponents(self):
        current_dir = os.path.dirname(os.path.realpath(__file__))
        uifile = os.path.join(current_dir, "ui_files/beamWidget.ui")
        uic.loadUi(uifile, self)