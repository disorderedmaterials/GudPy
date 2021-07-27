from PyQt5.QtWidgets import QMainWindow, QTextEdit
from PyQt5.QtGui import QResizeEvent


class GudPyMainWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        self.setGeometry(0, 0, 800, 600)
        self.setMinimumHeight(800)
        self.setMinimumWidth(600)
        self.setWindowTitle("GudPy")
        self.show()

    def resizeEvent(self, a0: QResizeEvent) -> None:

        super().resizeEvent(a0)
        [textArea.updateArea() for textArea in self.findChildren(QTextEdit)]
