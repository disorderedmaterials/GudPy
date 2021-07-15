import sys, os
from PyQt5 import QtCore, QtGui
sys.path.insert(1, os.path.join(sys.path[0], '../scripts'))
sys.path.insert(2, os.path.join(sys.path[0], '../gudrun_classes'))
sys.path.insert(3, os.path.join(sys.path[0], '../widgets'))

from PyQt5.QtWidgets import QApplication, QFileDialog, QHBoxLayout, QTextEdit, QWidget
from main_window import GudPyMainWindow
from gudrun_file_text_area import GudrunFileTextArea
from sidebar import GudPySiderbar

from gudrun_file import GudrunFile



class GudPy(QApplication):
    
    def __init__(self, args):

        super(GudPy, self).__init__(args)
        self.initComponents()
        self.gudrunFile = None
        sys.exit(self.exec_())

    def initComponents(self):
        
        self.mainWindow = GudPyMainWindow()
        self.textArea = GudrunFileTextArea(self.mainWindow, 1, 0.3)
        self.textArea.setGeometry(int(self.mainWindow.size().width()-(0.3*self.mainWindow.size().width())), 0, 
                                        int(self.mainWindow.size().height()), int(0.3*self.mainWindow.size().width()))


        filename = QFileDialog.getOpenFileName(self.mainWindow, 'Choose GudPy file for gudrun_dcs')
        if filename[0]:
            with open(filename[0], 'r') as f:
                self.textArea.setText(f.read())
        self.gudrunFile = GudrunFile(filename[0])



        # self.sidebar = GudPySiderbar(self.mainWindow, tabs)
        # self.mainWindow.setCentralWidget(self.sidebar)

        # self.layout = QHBoxLayout()
        # self.layout.addWidget(self.sidebar)
        # self.layout.setStretch(0,40)
        # self.mainWidget = QWidget()
        # self.mainWidget.setLayout(self.layout)
        # self.mainWindow.setMenuWidget(self.mainWidget)



if __name__ == '__main__':
    GudPy(sys.argv)