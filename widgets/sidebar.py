from PyQt5 import QtGui
from PyQt5.QtWidgets import QPushButton, QTabWidget, QVBoxLayout, QWidget



class  GudPySiderbar(QWidget):

    def __init__(self, parent, tabs):
        
        self.parent = parent
        self.buttons = []
        super().__init__(self.parent)

        for tab in tabs:
            self.buttons.append(QPushButton(tab, self))
        
        self.layout = QVBoxLayout(self)
        for button in self.buttons:
            self.layout.addWidget(button)
        self.setLayout(self.layout)
