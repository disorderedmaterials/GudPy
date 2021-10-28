from PySide6.QtGui import Qt
from PySide6.QtWidgets import QDoubleSpinBox, QTableView
from src.gui.widgets.tables.gudpy_tables import GudPyDelegate, GudPyTableModel


class ExponentialModel(GudPyTableModel):
    """
    Class to represent a ExponentialModel. Inherits GudPyTableModel.

    ...

    Methods
    -------
    columnCount(parent)
        Returns the number of columns in the model.
    setData(index, value, role)
        Sets data in the model.
    insertRow(data)
        Inserts a row of data into the model.
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
        super(ExponentialModel, self).__init__(data, headers, parent)

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
            Number of columns in the model - this is always 2.
        """
        return 2

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
        col = index.column()
        mutable = list(self._data[row])
        mutable[col] = value
        if role == Qt.EditRole:
            self._data[row] = tuple(mutable)

    def insertRow(self):
        """
        Inserts a row of data into the model.
        The data is always by default 0., 0.
        A row is only inserted if there are less than 5 rows.
        Calls super().insertRow().
        """
        if self.rowCount(self) < 5:
            super(ExponentialModel, self).insertRow((0., 0.))


class ExponentialDelegate(GudPyDelegate):
    """
    Class to represent a ExponentialDelegate. Inherits GudPyDelegate.

    ...

    Methods
    -------
    createEditor(parent, option, index)
        Creates an editor.
    """

    def createEditor(self, parent, option, index):
        """
        Creates an editor, which is a QDoubleSpinBox.
        Parameters
        ----------
        parent : QWidget
            Parent widget.
        option : QStyleOptionViewItem
            Option.
        index : QModelIndex
            Index in to create editor at.
        Returns
        -------
        QDoubleSpinBox
            The created editor.
        """
        editor = QDoubleSpinBox(parent)
        editor.setMinimum(0)
        editor.setMaximum(100)
        return editor


class ExponentialTable(QTableView):
    """
    Class to represent a ExponentialTable. Inherits QTableView.

    ...
    Attributes
    ----------
    parent : QWidget
        Parent widget.
    Methods
    -------
    makeModel(data)
        Creates the model using the data.
    insertRow()
        Inserts a row into the model.
    removeRow(rows)
        Removes selected rows from the model.
    """

    def __init__(self, parent):
        """
        Constructs all the necessary attributes
        for the ExponentialTable object.
        Calls super().__init__.
        Parameters
        ----------
        parent : QWidget
            Parent widget.
        """
        self.parent = parent
        super(ExponentialTable, self).__init__(parent=parent)

    def makeModel(self, data):
        """
        Makes the model and the delegate based on the data.
        Parameters
        ----------
        data : list
            Data for model to use.
        """
        self.setModel(
            ExponentialModel(data, ["Amplitude", "Decay [1/A]"], self.parent)
        )
        self.setItemDelegate(ExponentialDelegate())

    def insertRow(self):
        """
        Inserts a row into the model.
        """
        self.model().insertRow()

    def removeRow(self, rows):
        """
        Removes rows from the model.
        Parameters
        ----------
        rows : QModelIndexList
            Rows to be removed.
        """
        for _row in rows:
            self.model().removeRow(_row.row())