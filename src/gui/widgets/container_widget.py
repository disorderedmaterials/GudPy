from PyQt5.QtWidgets import QWidget
from PyQt5 import uic
import os

class ContainerWidget(QWidget):
    def __init__(self, container, parent=None):
        self.container = container
        self.parent = parent

        super(ContainerWidget, self).__init__(self.parent)
        self.initComponents()
    
    def initComponents(self):
        current_dir = os.path.dirname(os.path.realpath(__file__))
        uifile = os.path.join(current_dir, "ui_files/containerWidget.ui")
        uic.loadUi(uifile, self)
