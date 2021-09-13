from PyQt5.QtCore import QAbstractTableModel, QVariant, Qt
from PyQt5.QtWidgets import (
    QDoubleSpinBox,
    QItemDelegate,
    QSpinBox,
    QTableView,
    QTableWidget,
)


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
        value = editor.value()
        model.setData(index, value, Qt.EditRole)


class GroupingParameterModel(GudPyTableModel):

    def __init__(self, data, headers, parent):
        super(GroupingParameterModel, self).__init__(
            data, headers, parent
        )

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


class BeamProfileModel(GudPyTableModel):
    pass


class BeamProfileDelegate(GudPyDelegate):
    pass


class BeamProfileTable(QTableWidget):

    def __init__(self, parent):
        self.parent = parent
        super(BeamProfileTable, self).__init__(parent=parent)

    def makeModel(self, data):
        data = [
            *data,
            *[
                0 for _ in range(50 - len(data))
            ]
        ]  # pad or maybe not? since 0 is a valid value?
        self.setModel(BeamProfileModel(data, [], self.parent))
        self.setItemDelegate(BeamProfileDelegate())
