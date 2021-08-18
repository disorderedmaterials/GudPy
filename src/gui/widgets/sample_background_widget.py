from PyQt5.QtWidgets import QWidget
from PyQt5 import uic
import os

class SampleBackgroundWidget(QWidget):
    def __init__(self, sampleBackground, parent=None):
        self.sampleBackground = sampleBackground
        self.parent = parent

        super(SampleBackgroundWidget, self).__init__(self.parent)
        self.initComponents()
    
    def initComponents(self):
        current_dir = os.path.dirname(os.path.realpath(__file__))
        uifile = os.path.join(current_dir, "ui_files/sampleBackgroundWidget.ui")
        uic.loadUi(uifile, self)

        self.dataFilesList.addItems([df for df in self.sampleBackground.dataFiles.dataFiles])