from PyQt5.QtWidgets import QWidget
from PyQt5 import uic
import os

class NormalisationWidget(QWidget):
    def __init__(self, normalisation, parent=None):
        self.normalisation = normalisation
        self.parent = parent

        super(NormalisationWidget, self).__init__(self.parent)
        self.initComponents()
    
    def initComponents(self):
        current_dir = os.path.dirname(os.path.realpath(__file__))
        uifile = os.path.join(current_dir, "ui_files/normalisationWidget.ui")
        uic.loadUi(uifile, self)
