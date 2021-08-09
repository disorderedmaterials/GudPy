from ..gudrun_classes.gudrun_file import GudrunFile
from .widgets.gudrun_file_text_area import GudrunFileTextArea
from .widgets.main_window import GudPyMainWindow
from PyQt5.QtWidgets import (
    QApplication,
    QFileDialog,
    QMessageBox,
)
import pathmagic  # noqa: F401
import sys

from widgets.main_window import GudPyMainWindow

class GudPy(QApplication):

    def __init__(self, args):

        super(GudPy, self).__init__(args)
        self.initComponents()
        self.gudrunFile = None
        sys.exit(self.exec_())

    def initComponents(self):

        self.mainWindow = GudPyMainWindow()

def main(argv):
    print(sys.path)
    GudPy(argv)


if __name__ == "__main__":
    main(sys.argv)
