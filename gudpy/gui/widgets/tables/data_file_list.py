from PySide6.QtCore import Qt, QModelIndex, QAbstractItemModel, QStringListModel
from PySide6.QtWidgets import QTableView, QDoubleSpinBox, QListView
import os
from gui.widgets.tables.gudpy_tables import GudPyTableModel, GudPyDelegate

class DataFilesList(QListView):

    def __init__(self, parent):
        self.parent = parent
        super(DataFilesList, self).__init__(parent=parent)

    def makeModel(self, data):
        """
        Makes the model and the delegate based on the data.
        Parameters
        ----------
        data : list
            Data for model to use.
        """
        self.setModel(QStringListModel(data, self.parent))

    def insertRow(self, item):
        """
        Inserts a row into the model.
        """
        self.model().insertRows(self.model().rowCount(QModelIndex()), 1)
        self.model().setData(
            self.model().index(self.model().rowCount(QModelIndex()) - 1),
            item
        )


    def removeItem(self):
        """
        Removes rows from the model.
        """
        self.model().removeRow(self.currentIndex().row())
