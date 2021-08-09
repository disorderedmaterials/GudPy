from widgets.text_area import TextArea
from PyQt5.QtWidgets import (
    QFileDialog,
    QMessageBox,
)
from gudrun_classes.gudrun_file import GudrunFile

class GudrunFileTextArea(TextArea):
    def __init__(self, parent, relHeight, relWidth):
        super().__init__(parent, relHeight, relWidth)
        self.setReadOnly(True)

    def updateArea(self):

        super().updateArea()
        self.setGeometry(
            int(self.parent.size().width() * (1 - self.relWidth)),
            0,
            int(self.parent.size().width() * self.relWidth),
            int(self.parent.size().height() * self.relHeight),
        )
    
    def getGudrunFile(self):
        filename = QFileDialog.getOpenFileName(
            self, "Choose GudPy file for gudrun_dcs"
        )

        if filename[0]:
            with open(filename[0], "r") as f:
                self.setText(f.read())

        try:
            self.gudrunFile = GudrunFile(filename[0])
            return self.gudrunFile
        except ValueError as e:
            self.msgBox = QMessageBox(self)
            self.msgBox.setText(str(e))
            self.msgBox.exec()
            return None
