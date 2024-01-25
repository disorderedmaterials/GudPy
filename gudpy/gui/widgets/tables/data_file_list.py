from PySide6.QtCore import QModelIndex, QStringListModel
from PySide6.QtWidgets import QListView


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
        self.setCurrentIndex(
            self.model().index(self.model().rowCount(QModelIndex())-1, 0)
        )

    def duplicate(self):
        if self.currentIndex().isValid():
            self.insertRow(self.model().data(self.currentIndex()))

    def removeItem(self):
        """
        Removes rows from the model.
        """
        if self.currentIndex().isValid():
            for index in self.selectedIndexes():
                self.model().removeRow(index.row())
