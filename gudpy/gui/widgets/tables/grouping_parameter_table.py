from PySide6.QtCore import Qt
from PySide6.QtWidgets import QTableView, QSpinBox, QDoubleSpinBox

from gudpy.gui.widgets.tables.gudpy_tables import GudPyTableModel, GudPyDelegate


class GroupingParameterModel(GudPyTableModel):
    """
    Class to represent a GroupingParameterModel. Inherits GudPyTableModel.

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
        super(GroupingParameterModel, self).__init__(data, headers, parent)

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
            Number of columns in the model - this is always 4.
        """
        return 4

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
        The data is always by default 0, 0.0, 0.0, 0.0.
        Calls super().insertRow().
        """
        return super(GroupingParameterModel, self).insertRow((0, 0., 0., 0.))


class GroupingParameterDelegate(GudPyDelegate):
    """
    Class to represent a GroupingParameterDelegate. Inherits GudPyDelegate.

    ...

    Methods
    -------
    createEditor(parent, option, index)
        Creates an editor.
    """
    def createEditor(self, parent, option, index):
        """
        Creates an editor, which can be a QSpinBox or QDoubleSpinBox.
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
        QSpinBox | QDoubleSpinBox
            The created editor.
        """
        editor = (
            QSpinBox(parent) if index.column() == 0 else QDoubleSpinBox(parent)
        )
        editor.setMinimum(0)
        editor.setMaximum(100)
        return editor


class GroupingParameterTable(QTableView):
    """
    Class to represent a GroupingParameterTable. Inherits QTableView.

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
        for the GroupingParameterTable object.
        Calls super().__init__.
        Parameters
        ----------
        parent : QWidget
            Parent widget.
        """
        self.parent = parent
        super(GroupingParameterTable, self).__init__(parent=parent)

    def makeModel(self, data):
        """
        Makes the model and the delegate based on the data.
        Parameters
        ----------
        data : list
            Data for model to use.
        """
        self.setModel(
            GroupingParameterModel(
                data,
                ["Group", "XMin", "XMax", "Background Factor"],
                self.parent,
            )
        )
        self.setItemDelegate(GroupingParameterDelegate())

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
