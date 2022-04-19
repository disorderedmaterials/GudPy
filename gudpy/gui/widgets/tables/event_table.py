from PySide6.QtCore import Qt
from PySide6.QtWidgets import QTableView
from src.gui.widgets.tables.gudpy_tables import GudPyTableModel


class EventModel(GudPyTableModel):
    """
    Class to represent a EventModel. Inherits GudPyTableModel.

    ...

    Methods
    -------
    columnCount(parent)
        Returns the number of columns in the model.
    headerData(section, orientation, role)
        Stub method.
    setData(index, value, role)
        Sets data in the model.
    data(index, role)
        Returns data at a given index
    """
    def __init__(self, data, headers, parent):
        """
        Calls super().__init__ on the passed parameters.
        Parameters
        ----------
        data : list
            Data for model to use.
        headers: str[]
            Column headers for table.
        parent : QWidget
            Parent widget.
        """
        super(EventModel, self).__init__(data, headers, parent)

    def columnCount(self, parent):
        """
        Returns the number of columns in the model.
        Parameters
        ----------
        parent : QWidget
            Parent widget.
        Returns
        -------
        int
            Number of columns in the model - this is always 1.
        """
        return 1

    def headerData(self, section, orientation, role):
        """
        There are no headers, so this always returns nothing.
        Returns
        -------
        None
        """
        pass

    def setData(self, index, value, role):
        """
        Sets data in the model.
        Parameters
        ----------
        index : QModelIndex
            Index to set data at.
        value : any
            Value to set data to.
        role : int
            Role.
        """
        row = index.row()
        if role == Qt.EditRole:
            self._data[row] = value
            self.dataChanged.emit(index, index)

    def data(self, index, role):
        """
        Returns the data at a given index.
        Parameters
        ----------
        index : QModelIndex
            Index to return data from.
        role : int
            Role
        Returns
        -------
        float
            Data at given index.
        """
        row = index.row()
        if role == role & (Qt.DisplayRole | Qt.EditRole):
            return self._data[row]


class EventTable(QTableView):
    """
    Class to represent a EventTable. Inherits QTableView.

    ...
    Attributes
    ----------
    parent : QWidget
        Parent widget.
    Methods
    -------
    makeModel(data)
        Creates the model using the data.
    """
    def __init__(self, parent):
        """
        Constructs all the necessary attributes
        for the BeamProfileTable object.
        Calls super().__init__
        which calls the dunder init method from GudPyTableModel.
        Parameters
        ----------
        parent : QWidget
            Parent widget.
        """
        self.parent = parent
        super(EventTable, self).__init__(parent=parent)

    def makeModel(self, data):
        """
        Makes the model and the delegate based on the data.
        Parameters
        ----------
        data : list
            Data for model to use.
        """
        self.setModel(EventModel(data, ["Event"], self.parent))
