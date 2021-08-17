from PyQt5.QtWidgets import (
    QApplication,
    QFileDialog,
    QMessageBox,
)
import sys
import os

print(sys.path)
from ..gudrun_classes.gudrun_file import GudrunFile
from .widgets.gudrun_file_text_area import GudrunFileTextArea
from .widgets.main_window import GudPyMainWindow

class GudPy(QApplication):
    def __init__(self, args):

        super(GudPy, self).__init__(args)
        self.initComponents()
        self.gudrunFile = None
        sys.exit(self.exec_())

    def initComponents(self):

        self.mainWindow = GudPyMainWindow()
        self.textArea = GudrunFileTextArea(self.mainWindow, 1, 0.3)
        self.textArea.setGeometry(
            int(
                self.mainWindow.size().width()
                - (0.3 * self.mainWindow.size().width())
            ),
            0,
            int(self.mainWindow.size().height()),
            int(0.3 * self.mainWindow.size().width()),
        )

        filename = QFileDialog.getOpenFileName(
            self.mainWindow, "Choose GudPy file for gudrun_dcs"
        )
        if filename[0]:
            with open(filename[0], "r") as f:
                self.textArea.setText(f.read())
        sys.path.append(filename[0])
        self.gudrunFile = GudrunFile(filename[0])
        result = self.gudrunFile.dcs()
        self.msg = QMessageBox(self.mainWindow)
        self.msg.setWindowTitle("Result")
        self.msg.setText(result.stdout)
        self.msg.exec_()
        # self.sidebar = GudPySiderbar(self.mainWindow, tabs)
        # self.mainWindow.setCentralWidget(self.sidebar)

        # self.layout = QHBoxLayout()
        # self.layout.addWidget(self.sidebar)
        # self.layout.setStretch(0,40)
        # self.mainWidget = QWidget()
        # self.mainWidget.setLayout(self.layout)
        # self.mainWindow.setMenuWidget(self.mainWidget)


if __name__ == "__main__":
    main(sys.argv)

def main(argv):
    print(sys.path)
    GudPy(argv)
