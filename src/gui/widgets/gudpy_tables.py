from PyQt5.QtCore import QAbstractTableModel, QVariant, Qt
from PyQt5.QtWidgets import (
    QDoubleSpinBox,
    QItemDelegate,
    QSpinBox,
    QStyledItemDelegate,
    QTableView,
    QTableWidget,
)


class GroupingParameterModel(QAbstractTableModel):

    def __init__(self, data, headers, parent):
        super(GroupingParameterModel, self).__init__(parent=parent)
        self._data = data
        self.headers = headers
        
    def rowCount(self, parent):
        return len(self._data)
    
    def columnCount(self, parent):
        return len(self._data[0]) if self.data else 0
    
    def data(self, index, role):
        row = index.row()
        col = index.column()
        return self._data[row][col] if (role == Qt.DisplayRole & Qt.EditRole) else None

    def headerData(self, section, orientation, role):
        return self.headers[section] if orientation == Qt.Horizontal and role == Qt.DisplayRole else QVariant()

    def flags(self, parent):
        return Qt.ItemIsEnabled | Qt.ItemIsEditable | Qt.ItemIsSelectable


class GroupingParameterDelegate(QItemDelegate):

    def createEditor(self, parent, option, index):
        editor = QSpinBox(parent) if index.column() == 0 else QDoubleSpinBox(parent)
        editor.setMinimum(0)
        editor.setMaximum(100)
        return editor

    def setEditorData(self, editor, index):
        value = index.model().data(index, Qt.EditRole)
        editor.setValue(value)

    def setModelData(self, editor, model, index):
        editor.interpretText()
        value = editor.value()
        model.setData(index, value, Qt.EditRole)

class GroupingParameterTable(QTableView):

    def __init__(self, parent):
        self.parent = parent
        super(GroupingParameterTable, self).__init__(parent=parent)

    def makeModel(self, data):
        data = [*data, *[(0, 0.0, 0.0, 0.0) for _ in range(10 - len(data))]] # pad
        self.setModel(GroupingParameterModel(data, ["Group", "XMin", "XMax", "Background Factor"], self.parent))
        self.setItemDelegate(GroupingParameterDelegate())    


class BeamProfileTable(QTableWidget):
    pass