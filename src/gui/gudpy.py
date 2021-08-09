from ..gudrun_classes.gudrun_file import GudrunFile
from .widgets.gudrun_file_text_area import GudrunFileTextArea
from .widgets.main_window import GudPyMainWindow
from PyQt5.QtWidgets import (
    QApplication,
    QFileDialog,
    QMessageBox,
)
import pathmagic
import sys

from gudrun_classes.gudrun_file import GudrunFile
from widgets.gudrun_file_text_area import GudrunFileTextArea
from widgets.main_window import GudPyMainWindow

class GudPy(QApplication):

    def __init__(self, args):

        super(GudPy, self).__init__(args)
        self.initComponents()
        self.gudrunFile = None
        sys.exit(self.exec_())

    def initComponents(self):

        self.mainWindow = GudPyMainWindow()
        self.textArea = GudrunFileTextArea(self.mainWindow, 1, 0.3)

        filename = QFileDialog.getOpenFileName(
            self.mainWindow, "Choose GudPy file for gudrun_dcs"
        )
        if filename[0]:
            with open(filename[0], "r") as f:
                self.textArea.setText(f.read())
        sys.path.append(filename[0])
        try:
            self.gudrunFile = GudrunFile(filename[0])
        except ValueError as e:
            self.msgBox = QMessageBox(self.mainWindow)
            self.msgBox.setText(str(e))
            self.msgBox.exec()

def main(argv):
    print(sys.path)
    GudPy(argv)


if __name__ == "__main__":
    main(sys.argv)
