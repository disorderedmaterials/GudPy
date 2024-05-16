import sys
from PySide6.QtWidgets import QApplication

from gui.widgets.core.control import GudPyController


class GudPy(QApplication):
    def __init__(self, args):
        sys.hookedFrom = self
        super(GudPy, self).__init__(args)
        self.gudpy = GudPyController()
        self.aboutToQuit.connect(self.gudpy.cleanup)
        sys.exit(self.exec())

    def onException(self, cls, exception, traceback):
        self.gudpy.onException(cls, exception, traceback)


def gui(argv):
    GudPy(argv)


def excepthook(cls, exception, traceback):
    sys.hookedFrom.onException(cls, exception, traceback)


if __name__ == '__main__':
    gui(sys.argv)
