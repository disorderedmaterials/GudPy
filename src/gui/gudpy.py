from PyQt5.QtWidgets import QApplication
import sys

from src.gui.widgets.main_window import GudPyMainWindow


class GudPy(QApplication):
    def __init__(self, args):

        super(GudPy, self).__init__(args)
        self.initComponents()
        self.gudrunFile = None
        sys.exit(self.exec_())

    def initComponents(self):

        self.mainWindow = GudPyMainWindow()


def main(argv):
    GudPy(argv)


if __name__ == "__main__":
    main(sys.argv)
