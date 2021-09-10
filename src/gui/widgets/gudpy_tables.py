from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QDoubleSpinBox,
    QItemDelegate,
    QSpinBox,
    QTableWidget,
)

class DoubleSpinBoxDelegate(QItemDelegate):

    def __init__(self, parent, range):

        self.min, self.max = range
        super().__init__(parent=parent)

    def createEditor(self, parent, option, index):
        editor = QDoubleSpinBox(parent)
        editor.setFrame(False)
        editor.setMinimum(self.min)
        editor.setMaximum(self.max)

        return editor

    def setEditorData(self, spinBox, index):
        value = index.model().data(index, Qt.EditRole)

        spinBox.setValue(value)

    def setModelData(self, spinBox, model, index):
        spinBox.interpretText()
        value = spinBox.value()

        model.setData(index, value, Qt.EditRole)

class GroupingParameterTable(QTableWidget):

    def __init__(self, parent):

        super(GroupingParameterTable, self).__init__(parent=parent)
        self.initComponents()

    def initComponents(self):
        self.setItemDelegate(DoubleSpinBoxDelegate(self, (0, 10)))
