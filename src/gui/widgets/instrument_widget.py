from PyQt5.QtWidgets import QWidget
from PyQt5 import uic
import os

class InstrumentWidget(QWidget):
    def __init__(self, sample, parent=None):
        self.sample = sample
        self.parent = parent

        super(InstrumentWidget, self).__init__(self.parent)
        self.initComponents()
    
    def initComponents(self):
        current_dir = os.path.dirname(os.path.realpath(__file__))
        uifile = os.path.join(current_dir, "ui_files/instrumentWidget.ui")
        uic.loadUi(uifile, self)