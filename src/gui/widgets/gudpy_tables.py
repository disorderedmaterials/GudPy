from PyQt5.QtCore import QAbstractTableModel, QModelIndex, QVariant, Qt
from PyQt5.QtWidgets import (
    QDoubleSpinBox,
    QItemDelegate,
    QLineEdit,
    QSpinBox,
    QTableView,
    QMenu,
    QAction
)
from PyQt5.QtGui import QCursor

from src.gudrun_classes.element import Element
from src.gui.widgets.main_window import GudPyMainWindow

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
            else QVariant()
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


class BeamProfileModel(GudPyTableModel):
    """
    Class to represent a BeamProfileModel. Inherits GudPyTableModel.

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
        super(BeamProfileModel, self).__init__(data, headers, parent)

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
            Number of columns in the model - this is always 5.
        """
        return 5

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

    def insertRow(self):
        """
        Inserts a row of data into the model.
        The data is always by default 0.0.
        Calls super().insertRow().
        """
        return super(BeamProfileModel, self).insertRow(0.)


class BeamProfileDelegate(GudPyDelegate):
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
        Creates an editor, and returns it.
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
        editor.setMaximum(1)
        editor.setSingleStep(0.01)
        return editor


class BeamProfileTable(QTableView):
    """
    Class to represent a BeamProfileTable. Inherits QTableView.

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
        for the BeamProfileTable object.
        Calls super().__init__
        which calls the dunder init method from GudPyTableModel.
        Parameters
        ----------
        parent : QWidget
            Parent widget.
        """
        self.parent = parent
        super(BeamProfileTable, self).__init__(parent=parent)

    def makeModel(self, data):
        """
        Makes the model and the delegate based on the data.
        Parameters
        ----------
        data : list
            Data for model to use.
        """
        self.setModel(BeamProfileModel(data, [], self.parent))
        self.setItemDelegate(BeamProfileDelegate())

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


class CompositionModel(GudPyTableModel):
    """
    Class to represent a CompositionModel. Inherits GudPyTableModel.

    ...

    Methods
    -------
    columnCount(parent)
        Returns the number of columns in the model.
    setData(index, value, role)
        Sets data in the model.
    insertRow(data)
        Inserts a row of data into the model.
    data(index, role)
        Returns data at a specific index.
    """
    def __init__(self, data, headers, parent):
        """
        Calls super().__init__ on the passed parameters.
        Sets up attrs dict.
        Parameters
        ----------
        data : list
            Data for model to use.
        headers: str[]
            Column headers for table.
        parent : QWidget
            Parent widget.
        """
        super(CompositionModel, self).__init__(data, headers, parent)
        self.attrs = {0: "atomicSymbol", 1: "massNo", 2: "abundance"}

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
            Number of columns in the model - this is always 3.
        """
        return 3

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
            self._data[row].__dict__[self.attrs[col]] = value

    def insertRow(self):
        """
        Inserts a row of data into the model.
        The data is always by default "", 0, 0
        Calls super().insertRow().
        """
        self.beginInsertRows(
            QModelIndex(), self.rowCount(self), self.rowCount(self)
        )
        self._data.append(Element("", 0, 0))
        self.endInsertRows()

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
        tuple
            str, float, float
            Element attributes.
        """
        row = index.row()
        col = index.column()
        if role == role & (Qt.DisplayRole | Qt.EditRole):
            return self._data[row].__dict__[self.attrs[col]]


class CompositionDelegate(GudPyDelegate):
    """
    Class to represent a CompositionDelegate. Inherits GudPyDelegate.

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
        Creates an editor, and returns it.
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
        QLineEdit | QSpinBox | QDoubleSpinBox
            The created editor.
        """
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
            if index.column() != 0:
                editor.setValue(value)
            else:
                editor.setText(value)

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


class CompositionTable(QTableView):
    """
    Class to represent a CompositionTable. Inherits QTableView.

    ...
    Attributes
    ----------
    parent : QWidget
        Parent widget.
    compositions : Composition[]
        List of all compositions.
    Methods
    -------
    makeModel(data)
        Creates the model using the data.
    insertRow()
        Inserts a row into the model.
    removeRow(rows)
        Removes selected rows from the model.
    farmCompositions()
        Collect compositions from normalisation, all samples and containers.
    copyFrom(composition)
        Create a new model from a given composition.
    contextMenuEvent(event)
        Creates context menu.
    """
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
        self.compositions = []
        super(CompositionTable, self).__init__(parent=parent)

    def makeModel(self, data):
        """
        Makes the model and the delegate based on the data.
        Collects all compositions.
        Parameters
        ----------
        data : list
            Data for model to use.
        """
        self.setModel(
            CompositionModel(
                data, ["Element", "Mass No", "Abundance"], self.parent
            )
        )
        self.setItemDelegate(CompositionDelegate())
        self.farmCompositions()

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

    def farmCompositions(self):
        """
        Seeks up the widget heirarchy, and then collects all compositions.
        """
        ancestor = self.parent
        while not isinstance(ancestor, GudPyMainWindow):
            ancestor = ancestor.parent
            if callable(ancestor):
                ancestor = ancestor()
        self.compositions.clear()
        self.compositions = [
                (
                    "Normalisation",
                    ancestor.gudrunFile.normalisation.composition
                )
            ]
        for sampleBackground in ancestor.gudrunFile.sampleBackgrounds:
            for sample in sampleBackground.samples:
                self.compositions.append((sample.name, sample.composition))
                for container in sample.containers:
                    self.compositions.append(
                        (container.name, container.composition)
                    )

    def copyFrom(self, composition):
        """
        Create a new model from a given composition,
        and replaces the current model with it.
        Parameters
        ----------
        composition : Composition
            Composition object to copy elements from.
        """
        self.makeModel(composition.elements)

    def contextMenuEvent(self, event):
        """
        Creates context menu, so that on right clicking the table,
        the user is able to copy compositions in.
        Parameters
        ----------
        event : QMouseEvent
            The event that triggers the context menu.
        """
        self.menu = QMenu(self)
        copyMenu = self.menu.addMenu("Copy from")
        for composition in self.compositions:
            action = QAction(f"{composition[0]}", copyMenu)
            action.triggered.connect(
                lambda _, comp=composition[1]: self.copyFrom(comp)
            )
            copyMenu.addAction(action)
        self.menu.popup(QCursor.pos())


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


class ResonanceModel(GudPyTableModel):
    """
    Class to represent a ResonanceModel. Inherits GudPyTableModel.

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
        super(ResonanceModel, self).__init__(data, headers, parent)

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
            super(ResonanceModel, self).insertRow((0., 0.))


class ResonanceDelegate(GudPyDelegate):
    """
    Class to represent a ResonanceDelegate. Inherits GudPyDelegate.

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


class ResonanceTable(QTableView):
    """
    Class to represent a ResonanceTable. Inherits QTableView.

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
        for the ResonanceTable object.
        Calls super().__init__.
        Parameters
        ----------
        parent : QWidget
            Parent widget.
        """
        self.parent = parent
        super(ResonanceTable, self).__init__(parent=parent)

    def makeModel(self, data):
        """
        Makes the model and the delegate based on the data.
        Parameters
        ----------
        data : list
            Data for model to use.
        """
        self.setModel(
            ResonanceModel(
                data, ["Wavelength min", "Wavelength max"], self.parent
            )
        )
        self.setItemDelegate(ResonanceDelegate())

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
