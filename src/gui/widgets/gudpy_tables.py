from PyQt5.QtCore import QAbstractTableModel, QModelIndex, QVariant, Qt
from PyQt5.QtWidgets import (
    QDoubleSpinBox,
    QItemDelegate,
    QLineEdit,
    QSpinBox,
    QTableView,
)

from src.gudrun_classes.element import Element


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
        if role == role & (Qt.DisplayRole | Qt.EditRole):
            return self._data[row][col]

    def headerData(self, section, orientation, role):
        return (
            self.headers[section]
            if (orientation == Qt.Horizontal and role == Qt.DisplayRole)
            else QVariant()
        )

    def insertRow(self, data):
        self.beginInsertRows(
            QModelIndex(), self.rowCount(self), self.rowCount(self)
        )
        self._data.append(data)
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
            print(value)
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
        super(GroupingParameterModel, self).__init__(data, headers, parent)

    def columnCount(self, parent):
        return 4

    def setData(self, index, value, role):
        row = index.row()
        col = index.column()
        mutable = list(self._data[row])
        mutable[col] = value
        if role == Qt.EditRole:
            self._data[row] = tuple(mutable)

    def insertRow(self):
        return super(GroupingParameterModel, self).insertRow((0, 0., 0., 0.))

class GroupingParameterDelegate(GudPyDelegate):
    def createEditor(self, parent, option, index):
        editor = (
            QSpinBox(parent) if index.column() == 0 else QDoubleSpinBox(parent)
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
                self.parent,
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
        super(BeamProfileModel, self).__init__(data, headers, parent)

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
        if role == role & (Qt.DisplayRole | Qt.EditRole):
            return self._data[row]

    def insertRow(self):
        return super(BeamProfileModel, self).insertRow(0.)


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


class CompositionModel(GudPyTableModel):
    def __init__(self, data, headers, parent):
        super(CompositionModel, self).__init__(data, headers, parent)
        self.attrs = {0: "atomicSymbol", 1: "massNo", 2: "abundance"}

    def columnCount(self, parent):
        return 3

    def setData(self, index, value, role):
        row = index.row()
        col = index.column()
        if role == Qt.EditRole:
            self._data[row].__dict__[self.attrs[col]] = value

    def insertRow(self):
        self.beginInsertRows(
            QModelIndex(), self.rowCount(self), self.rowCount(self)
        )
        self._data.append(Element("", 0, 0))
        self.endInsertRows()

    def removeRow(self, index):
        self.beginRemoveRows(QModelIndex(), index, index)
        self._data.pop(index)
        self.endRemoveRows()

    def data(self, index, role):
        row = index.row()
        col = index.column()
        if role == role & (Qt.DisplayRole | Qt.EditRole):
            return self._data[row].__dict__[self.attrs[col]]


class CompositionDelegate(GudPyDelegate):
    def createEditor(self, parent, option, index):
        col = index.column()
        if col == 0:
            editor = QLineEdit(parent)
        elif col == 1:
            editor = QSpinBox(parent)
        else:
            editor = QDoubleSpinBox(parent)
            editor.setMinimum(0)
            editor.setMaximum(1)
            editor.setSingleStep(0.01)
        return editor

    def setModelData(self, editor, model, index):
        if index.column() != 0:
            editor.interpretText()
            try:
                value = editor.value()
                model.setData(index, value, Qt.EditRole)
            except:
                model.setData(index, 0, Qt.EditRole)
        else:
            value = editor.text()
            model.setData(index, value, Qt.EditRole)


class CompositionTable(QTableView):
    def __init__(self, parent):
        self.parent = parent
        super(CompositionTable, self).__init__(parent=parent)

    def makeModel(self, data):
        self.setModel(
            CompositionModel(
                data, ["Element", "Mass No", "Abundance"], self.parent
            )
        )
        self.setItemDelegate(CompositionDelegate())

    def insertRow(self):
        self.model().insertRow()

    def removeRow(self, rows):
        for _row in rows:
            self.model().removeRow(_row.row())


class ExponentialModel(GudPyTableModel):
    def __init__(self, data, headers, parent):
        super(ExponentialModel, self).__init__(data, headers, parent)

    def columnCount(self, parent):
        return 2

    def setData(self, index, value, role):
        row = index.row()
        col = index.column()
        mutable = list(self._data[row])
        mutable[col] = value
        if role == Qt.EditRole:
            self._data[row] = tuple(mutable)

    def insertRow(self):
        if self.rowCount(self) < 5:
            super(ResonanceModel, self).insertRow()


class ExponentialDelegate(GudPyDelegate):
    def createEditor(self, parent, option, index):
        editor = QDoubleSpinBox(parent)
        editor.setMinimum(0)
        editor.setMaximum(100)
        return editor


class ExponentialTable(QTableView):
    def __init__(self, parent):
        self.parent = parent
        super(ExponentialTable, self).__init__(parent=parent)

    def makeModel(self, data):
        self.setModel(
            ExponentialModel(data, ["Amplitudate", "Decay [1/A]"], self.parent)
        )
        self.setItemDelegate(ExponentialDelegate())

    def insertRow(self):
        self.model().insertRow()

    def removeRow(self, rows):
        for _row in rows:
            self.model().removeRow(_row.row())


class ResonanceModel(GudPyTableModel):
    def __init__(self, data, headers, parent):
        super(ResonanceModel, self).__init__(data, headers, parent)

    def columnCount(self, parent):
        return 2

    def setData(self, index, value, role):
        row = index.row()
        col = index.column()
        mutable = list(self._data[row])
        mutable[col] = value
        if role == Qt.EditRole:
            self._data[row] = tuple(mutable)

    def insertRow(self):
        if self.rowCount(self) < 5:
            super(ResonanceModel, self).insertRow()


class ResonanceDelegate(GudPyDelegate):
    def createEditor(self, parent, option, index):
        editor = QDoubleSpinBox(parent)
        editor.setMinimum(0)
        editor.setMaximum(100)
        return editor


class ResonanceTable(QTableView):
    def __init__(self, parent):
        self.parent = parent
        super(ResonanceTable, self).__init__(parent=parent)

    def makeModel(self, data):
        self.setModel(
            ResonanceModel(
                data, ["Wavelength min", "Wavelength max"], self.parent
            )
        )
        self.setItemDelegate(ResonanceDelegate())

    def insertRow(self):
        self.model().insertRow()

    def removeRow(self, rows):
        for _row in rows:
            self.model().removeRow(_row.row())
