from PySide6.QtCore import QModelIndex, Qt
from PySide6.QtWidgets import QComboBox, QTableView
from src.gudrun_classes import config
from src.gudrun_classes.composition import WeightedComponent
from src.gui.widgets.exponential_spinbox import ExponentialSpinBox
from src.gui.widgets.tables.gudpy_tables import GudPyDelegate, GudPyTableModel


class RatioCompositionModel(GudPyTableModel):
    """
    Class to represent a RatioCompositionModel. Inherits GudPyTableModel.

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
        super(RatioCompositionModel, self).__init__(
            data, headers, parent
        )

    def rowCount(self, parent):
        return len(self._data)

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
        if role == Qt.EditRole:
            if col == 0:
                self._data[row].component = value
            elif col == 1:
                self._data[row].ratio = value
            self.dataChanged.emit(index, index)

    def insertRow(self, weightedComponent):
        """
        Inserts a row of data into the model.
        """
        self.beginInsertRows(
            QModelIndex(), self.rowCount(self), self.rowCount(self)
        )
        self._data.append(
            weightedComponent
        )
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
            if col == 0:
                return self._data[row].component.name
            elif col == 1:
                return self._data[row].ratio


class RatioCompositionDelegate(GudPyDelegate):
    """
    Class to represent a RatioCompositionDelegate. Inherits GudPyDelegate.

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

    def __init__(self):
        super(RatioCompositionDelegate, self).__init__()
        self.components = config.components

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
            editor = QComboBox(parent)
            for component in self.components.components:
                editor.addItem(component.name, component)
        elif col == 1:
            editor = ExponentialSpinBox(parent)
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
        if index.column() == 1:
            editor.setValue(value)
        elif index.column() == 0:
            for i, component in enumerate(self.components.components):
                if component.name == value:
                    editor.setCurrentIndex(i)

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
        if index.column() == 0:
            model.setData(index, editor.currentData(), Qt.EditRole)
        else:
            try:
                value = editor.value()
                model.setData(index, value, Qt.EditRole)
            except Exception:
                model.setData(index, 0., Qt.EditRole)


class RatioCompositionTable(QTableView):
    """
    Class to represent a RatioCompositionTable. Inherits QTableView.

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
    farmCompositions()
        Collect compositions from normalisation, all samples and containers.
    copyFrom(composition)
        Create a new model from a given composition.
    showContextMenu(event)
        Creates context menu.
    mousePressEvent(event)
        Handles mouse presses.
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
        super(RatioCompositionTable, self).__init__(parent=parent)

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
            RatioCompositionModel(
                data, ["Component", "Ratio"], self.parent
            )
        )
        self.setItemDelegate(
            RatioCompositionDelegate()
        )

    def insertRow(self):
        """
        Inserts a row into the model.
        """
        if len(config.components.components):
            self.model().insertRow(
                WeightedComponent(config.components.components[0], 0.)
            )

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
