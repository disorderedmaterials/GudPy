from PySide6.QtCore import QAbstractTableModel, QModelIndex, Qt
from PySide6.QtWidgets import QItemDelegate


class GudPyTableModel(QAbstractTableModel):
    """
    Class to represent a GudPyTableModel. Inherits QAbstractTableModel.

    ...

    Attributes
    ----------
    _data : list
        Data for model to use.
    headers : str[]
        Column headers for table.
    Methods
    -------
    rowCount(parent)
        Returns the number of rows in the model.
    columnCount(parent)
        Returns the number of columns in the model.
    setData(index, value, role)
        Sets dat ain the model.
    data(index, role)
        Returns data at a specific index.
    headerData(section, orientation, role)
        Returns header for a given section.
    insertRow(data)
        Inserts a row of data into the model.
    removeRow(index)
        Removes a row from the model at a given index.
    flags(parent)
        Returns the flags of the model.
    """
    def __init__(self, data, headers, parent):
        """
        Constructs all the necessary attributes for the GudPyTable object.
        Calls super().__init__
        which calls the dunder init method from QAbstractTableModel.
        Parameters
        ----------
        data : list
            Data for model to use.
        headers: str[]
            Column headers for table.
        parent : QWidget
            Parent widget.
        """
        super(GudPyTableModel, self).__init__(parent=parent)
        self._data = data
        self.headers = headers

    def rowCount(self, parent):
        """
        Returns the number of rows in the model.
        Parameters
        ----------
        parent : QWidget
            Parent widget.
        Returns
        -------
        int
            Number of rows
        """
        return len(self._data) if self._data else 0

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
            Number of columns
        """
        return len(self._data[0]) if self._data else 0

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
        if role == Qt.EditRole:
            self._data[row][col] = value

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
        any
            Data at given index.
        """
        row = index.row()
        col = index.column()
        if role == role & (Qt.DisplayRole | Qt.EditRole):
            return self._data[row][col]

    def headerData(self, section, orientation, role):
        """
        Returns the column header for a given section.
        Parameters
        ----------
        section : int
            Column index.
        orientation : int
            Type of orientation (Horizontal/Vertical)
        role : int
            Role
        Returns
        -------
        str | QVariant
            column header | empty QVariant.
        """
        return (
            self.headers[section]
            if (orientation == Qt.Horizontal and role == Qt.DisplayRole)
            else None
        )

    def insertRow(self, data):
        """
        Inserts a row of data into the model.
        Parameters
        ----------
        data : any
            Data to insert.
        """
        self.beginInsertRows(
            QModelIndex(), self.rowCount(self), self.rowCount(self)
        )
        self._data.append(data)
        self.endInsertRows()

    def removeRow(self, index):
        """
        Remove a row at a given index.
        Parameters
        ----------
        index : int
            Index to remove at.
        """
        self.beginRemoveRows(QModelIndex(), index, index)
        self._data.pop(index)
        self.endRemoveRows()

    def flags(self, parent):
        """
        Returns flags of model.
        Parameters
        ----------
        parent : QWidget
            Parent widget.
        Returns
        -------
        int
            Flags
        """
        return Qt.ItemIsEnabled | Qt.ItemIsEditable | Qt.ItemIsSelectable


class GudPyDelegate(QItemDelegate):
    """
    Class to represent a GudPyDelegate. Inherits QItemDelegate.

    ...

    Methods
    -------
    createEditor(parent, option, index)
        Creates an editor.
    setEditorData(editor, index)
        Sets data at a specific index inside the editor.
    setModelData(editor, model, index)
        Sets data at a specific index inside the model.
    """
    def createEditor(self, parent, option, index):
        """
        Calls super().createEditor on the passed parameters.
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
        QWidget
            The created editor.
        """
        return super(GudPyDelegate, self).createEditor(parent, option, index)

    def setEditorData(self, editor, index):
        """
        Sets data at a specific index inside the editor.
        Parameters
        ----------
        editor : QWidget
            The editor widet.
        index : QModelIndex
            Index in the model to set data at.
        """
        value = index.model().data(index, Qt.EditRole)
        if value:
            editor.setValue(value)

    def setModelData(self, editor, model, index):
        """
        Sets data at a specific index inside the model.
        Parameters
        ----------
        editor : QWidget
            The editor widet.
        model : GudPyTableModel
            Model to set data inside.
        index : QModelIndex
            Index in the model to set data at.
        """
        editor.interpretText()
        try:
            value = editor.value()
            model.setData(index, value, Qt.EditRole)
        except Exception:
            model.setData(index, 0, Qt.EditRole)
