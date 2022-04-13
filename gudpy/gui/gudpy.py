import sys
from PySide6.QtWidgets import QApplication

from gudpy.gui.widgets.core.main_window import GudPyMainWindow


class GudPy(QApplication):
    def __init__(self, args):
        sys.hookedFrom = self
        super(GudPy, self).__init__(args)
        self.initComponents()
        self.gudrunFile = None
        sys.exit(self.exec_())

    def initComponents(self):

        self.mainWindow = GudPyMainWindow()

    def onException(self, cls, exception, traceback):
        self.mainWindow.onException(cls, exception, traceback)


def main(argv):
    GudPy(argv)


def excepthook(cls, exception, traceback):
    sys.hookedFrom.onException(cls, exception, traceback)


if __name__ == "__main__":
    main(sys.argv)
