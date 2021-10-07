from PySide6.QtGui import QAction
from PySide6.QtWidgets import QMainWindow, QTextEdit


class ViewInput(QMainWindow):
    def __init__(self, gudrunFile, parent=None):
        self.gudrunFile = gudrunFile
        self.parent = parent
        super(ViewInput, self).__init__(self.parent)
        self.setGeometry(
            0, 0,
            self.parent.size().width() // 2, self.parent.size().height() // 2
        )

        self.initComponents()
        self.show()

    def initComponents(self):

        self.textEdit = QTextEdit(self)
        self.textEdit.setText(str(self.gudrunFile))
        self.textEdit.setGeometry(
            0, 0,
            self.size().width(), self.size().height())

        menuBar = self.menuBar()
        menuBar.setNativeMenuBar(False)
        saveAction = QAction("Save and Close", menuBar)
        menuBar.addAction(saveAction)
        saveAction.triggered.connect(self.save)

    def save(self):

        with open(self.gudrunFile.path, "w", encoding="utf-8") as fp:
            fp.write(self.textEdit.toPlainText())
        self.parent.updateFromFile()
