from PySide6.QtCore import QModelIndex, Qt
from PySide6.QtGui import QAction, QCursor
from PySide6.QtWidgets import (
    QLineEdit, QMainWindow, QMenu, QSpinBox, QTableView
)
from gui.widgets.tables.gudpy_tables import GudPyTableModel, GudPyDelegate
from gui.widgets.core.exponential_spinbox import ExponentialSpinBox

from core.modulation_excitation import Period, Pulse

class PulseTableModel(GudPyTableModel):
    def __init__(self, data, headers, parent):
        super(PulseTableModel, self).__init__(data, headers, parent)
        self.attrs = {0: "label", 1: "periodOffset", 2: "duration"}

    def columnCount(self, parent):
        return 3

    def setData(self, index, value, role):
        row = index.row()
        col = index.column()
        if role == Qt.EditRole:
            self._data[row].__dict__[self.attrs[col]] = value
            self.dataChanged.emit(index, index)

    def insertRow(self):
        """
        Inserts a row of data into the model.
        The data is always by default "", 0, 0
        Calls super().insertRow().
        """
        self.beginInsertRows(
            QModelIndex(), self.rowCount(self), self.rowCount(self)
        )
        self._data.append(Pulse())
        self.endInsertRows()

    def data(self, index, role):
        row = index.row()
        col = index.column()
        if role == role & (Qt.DisplayRole | Qt.EditRole):
            return self._data[row].__dict__[self.attrs[col]]


class PulseDelegate(GudPyDelegate):
    def createEditor(self, parent, option, index):
        col = index.column()
        if col == 0:
            editor = QLineEdit(parent)
        elif col == 1:
            editor = ExponentialSpinBox(parent)
        else:
            editor = ExponentialSpinBox(parent)
        return editor

    def setEditorData(self, editor, index):
        value = index.model().data(index, Qt.EditRole)
        if value:
            if index.column() != 0:
                editor.setValue(value)
            else:
                editor.setText(value)

    def setModelData(self, editor, model, index):
        if index.column() != 0:
            editor.interpretText()
            try:
                value = editor.value()
                model.setData(index, value, Qt.EditRole)
            except Exception:
                model.setData(index, 0, Qt.EditRole)
        else:
            value = editor.text()
            model.setData(index, value, Qt.EditRole)


class PulseTable(QTableView):

    def __init__(self, parent):
        """
        Constructs all the necessary attributes
        for the CompositionTable object.
        Calls super().__init__.
        Parameters
        ----------
        parent : QWidget
            Parent widget.
        """
        self.parent = parent
        self.pulses = []
        self.parentObject = None
        super(PulseTable, self).__init__(parent=parent)

    def makeModel(self, data, parentObject):
        """
        Makes the model and the delegate based on the data.
        Collects all compositions.
        Parameters
        ----------
        data : list
            Data for model to use.
        """
        self.setModel(
            PulseTableModel(
                data, ["Label", "Period Offset", "Duration"], self.parent
            )
        )
        self.parentObject = parentObject
        self.setItemDelegate(PulseDelegate())

    def insertRow(self):
        self.model().insertRow()

    def removeRow(self, rows):
        for _row in rows:
            self.model().removeRow(_row.row())