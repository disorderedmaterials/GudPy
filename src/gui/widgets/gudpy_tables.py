from PyQt5.QtCore import QAbstractTableModel, QModelIndex, QVariant, Qt
from PyQt5.QtWidgets import (
    QDoubleSpinBox,
    QItemDelegate,
    QSpinBox,
    QTableView,
    QTableWidget,
)
import numpy as np


class GudPyTableModel(QAbstractTableModel):

    def __init__(self, data, headers, parent):
        super(GudPyTableModel, self).__init__(parent=parent)
        self._data = data
        self.headers = headers

    def rowCount(self, parent):
        return len(self._data) if self._data else 0

    def columnCount(self, parent):
        return len(self._data[0]) if self._data else 0

    def setData(self, index, value, role):
        row = index.row()
        col = index.column()
        if role == Qt.EditRole:
            self._data[row][col] = value

    def data(self, index, role):
        row = index.row()
        col = index.column()
        return (
            self._data[row][col]
            if (role == Qt.DisplayRole & Qt.EditRole)
            else None
        )

    def headerData(self, section, orientation, role):
        return (
            self.headers[section]
            if (
                orientation == Qt.Horizontal
                and role == Qt.DisplayRole
            )
            else QVariant()
        )

    def insertRow(self):
        self.beginInsertRows(QModelIndex(), self.rowCount(self), self.rowCount(self))
        self._data.append((0, 0., 0., 0.))
        self.endInsertRows()
            
    def removeRow(self, index):
        self.beginRemoveRows(QModelIndex(), index, index)
        self._data.pop(index)
        self.endRemoveRows()

    def flags(self, parent):
        return Qt.ItemIsEnabled | Qt.ItemIsEditable | Qt.ItemIsSelectable


class GudPyDelegate(QItemDelegate):

    def createEditor(self, parent, option, index):
        return super(GudPyDelegate, self).createEditor(parent, option, index)

    def setEditorData(self, editor, index):
        value = index.model().data(index, Qt.EditRole)
        if value:
            editor.setValue(value)

    def setModelData(self, editor, model, index):
        editor.interpretText()
        try:
            value = editor.value()
            model.setData(index, value, Qt.EditRole)
        except:
            model.setData(index, 0, Qt.EditRole)

class GroupingParameterModel(GudPyTableModel):

    def __init__(self, data, headers, parent):
        super(GroupingParameterModel, self).__init__(
            data, headers, parent
        )

    def columnCount(self, parent):
        return 4

    def setData(self, index, value, role):
        row = index.row()
        col = index.column()
        mutable = list(self._data[row])
        mutable[col] = value
        if role == Qt.EditRole:
            self._data[row] = tuple(mutable)


class GroupingParameterDelegate(GudPyDelegate):

    def createEditor(self, parent, option, index):
        editor = (
            QSpinBox(parent)
            if index.column() == 0
            else QDoubleSpinBox(parent)
        )
        editor.setMinimum(0)
        editor.setMaximum(100)
        return editor


class GroupingParameterTable(QTableView):

    def __init__(self, parent):
        self.parent = parent
        super(GroupingParameterTable, self).__init__(parent=parent)

    def makeModel(self, data):
        self.setModel(
            GroupingParameterModel(
                data,
                ["Group", "XMin", "XMax", "Background Factor"],
                self.parent
            )
        )
        self.setItemDelegate(GroupingParameterDelegate())

    def insertRow(self):
        self.model().insertRow()

    def removeRow(self, rows):
        for _row in rows:
            self.model().removeRow(_row.row())

class BeamProfileModel(GudPyTableModel):

    def __init__(self, data, headers, parent):
        super(BeamProfileModel, self).__init__(
            data, headers, parent
        )

    def columnCount(self, parent):
        return 5

    def headerData(self, section, orientation, role):
        pass

    def setData(self, index, value, role):
        row = index.row()
        if role == Qt.EditRole:
            self._data[row] = value

    def data(self, index, role):
        row = index.row()
        return (
            self._data[row]
            if (role == Qt.DisplayRole & Qt.EditRole)
            else None
        )


class BeamProfileDelegate(GudPyDelegate):

    def createEditor(self, parent, option, index):
        editor = QDoubleSpinBox(parent)
        editor.setMinimum(0)
        editor.setMaximum(1)
        editor.setSingleStep(0.01)
        return editor


class BeamProfileTable(QTableView):

    def __init__(self, parent):
        self.parent = parent
        super(BeamProfileTable, self).__init__(parent=parent)

    def makeModel(self, data):
        self.setModel(BeamProfileModel(data, [], self.parent))
        self.setItemDelegate(BeamProfileDelegate())

    def insertRow(self):
        self.model().insertRow()

    def removeRow(self, rows):
        for _row in rows:
            self.model().removeRow(_row.row())