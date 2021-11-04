from PySide6.QtCore import (
    QModelIndex, QPersistentModelIndex, QAbstractItemModel, Qt
)
from PySide6.QtWidgets import QListView
from src.gudrun_classes.composition import Component
from src.gudrun_classes.element import Element
from src.gui.widgets.tables.composition_table import CompositionDelegate


class ComponentsModel(QAbstractItemModel):
    """
    Class to represent a CompositionModel. Inherits QAbstractItemModel.

    ...

    Attributes
    ----------
    components : Components
        Components object associated with model.
    persistentIndexes : dict
        Dict of QPersistentIndexes,
        key is a GudPy object, value is a QPersistentIndex.
    Methods
    -------
    index(row, column, parent):
        Returns index associated with given row, column and parent.
    parent(index)
        Returns parent of a given index.
    findParent(item)
        Finds the parent of a given Element.
    data(index, role)
        Returns the data at a given index.
    setData(index, value, role)
        Sets data at a given index.
    rowCount(parent)
        Returns the row count of an index.
    columnCount(parent)
        Returns the column count of an index.
    flags(index)
        Returns flags associated with a given index.
    insertRow(obj, parent)
        Insert a row containing an object to a parent index.
    removeRow(index)
        Remove a row from an index.
    """
    def __init__(self, parent, components):
        """
        Constructs all the necessary attributes for the ComponentsModel object.
        Calls super()._init__ which calls the dunder init method
        from QAbstractItemModel.
        Parameters
        ----------
        parent : QWidget
            Parent widget.
        components : Components
            Components object to create model from.
        """
        super(ComponentsModel, self).__init__(parent)
        self.components = components
        self.persistentIndexes = {}

    def index(self, row, column, parent=QModelIndex()):
        """
        Returns index associated with given row, column and parent.
        If no such index is possible, then an invalid QModelIndex
        is returned.
        Creates a QPersistentModelIndex and adds it to the dict,
        to keep the internal pointer of the QModelIndex in
        reference.
        Parameters
        ----------
        row : int
            Row number.
        column : int
            Column number.
        parent, optional: QModelIndex
            Parent index.
        Returns
        -------
        QModelIndex
            The index created.
        """
        if not self.hasIndex(row, column, parent):
            return QModelIndex()
        elif not parent.isValid():
            obj = self.components.components[row]
            col = 0
        else:
            obj = self.components.components[parent.row()].elements[row]
            col = column
        index = self.createIndex(row, col, obj)
        self.persistentIndexes[obj] = QPersistentModelIndex(index)
        return index

    def parent(self, index):
        """
        Returns parent of a given index.
        If the index is invalid, then an invalid QModelIndex is returned.
        Parent is decided on by checking the data type of the internal pointer
        of the index.
        Parameters
        ----------
        index : QModelIndex
            Index to find parent index of.
        Returns
        -------
        QModelIndex
            Parent index.
        """
        if not index.isValid():
            return QModelIndex()
        elif isinstance(index.internalPointer(), Component):
            return QModelIndex()
        elif isinstance(index.internalPointer(), Element):
            parent = self.findParent(index.internalPointer())
            return QModelIndex(self.persistentIndexes[parent])
        else:
            return QModelIndex()

    def findParent(self, item):
        """
        Finds the parent of a given Element.
        Parameters
        ----------
        item : Element
            Object to find parent of.
        Returns
        -------
        Component
            Parent object.
        """
        for i, component in enumerate(self.components.components):
            if item in component.elements:
                return self.components.components[i]

    def setData(self, index, value, role):
        """
        Sets data at a given index, if the index is valid.
        Only used for assigning CheckStates to samples.
        Parameters
        ----------
        index : QModelIndex
            Index to set data at.
        value : QVariant
            Value to assign to data.
        role : int
            Role.
        Returns
        -------
        bool
            Success / Failure.
        """
        if not index.isValid():
            return False
        elif role == Qt.EditRole:
            if not index.parent().isValid():
                self.components.components[index.row()].name = value
                self.components.components[index.row()].nameChanged()
                self.dataChanged.emit(index, index)
            else:
                if index.column() == 0:
                    self.components.components[
                        index.parent().row()
                    ].elements[index.row()].atomicSymbol = value
                elif index.column() == 1:
                    self.components.components[
                        index.parent().row()
                    ].elements[index.row()].massNo = value
                elif index.column() == 2:
                    self.components.components[
                        index.parent().row()
                    ].elements[index.row()].abundance = value
            return True

    def data(self, index, role):
        """
        Returns the data at a given index.
        If the index is invalid, or the role is not
        Qt.EditRole | Qt.DisplayRole, then an empty
        QVariant is returned.
        Otherwise returns check state of index, or a QVariant constructed
        from its name.
        Parameters
        ----------
        index : QModelIndex
            Index to extract data from.
        role : int
            Role.
        Returns
        -------
        QVariant | QCheckState
            Data at index.
        """
        if not index.isValid():
            return None
        obj = index.internalPointer()
        if role == Qt.DisplayRole or role == Qt.EditRole:
            if isinstance(obj, Component):
                return index.internalPointer().name
            elif isinstance(obj, Element):
                if index.column() == 0:
                    return obj.atomicSymbol
                elif index.column() == 1:
                    return obj.massNo
                elif index.column() == 2:
                    return obj.abundance
        else:
            return None

    def rowCount(self, parent=QModelIndex()):
        """
        Returns the row count of a given parent index.
        The row count returned depends on the data type of the parent.
        Parameters
        ----------
        parent : QModelIndex
            Parent index to retrieve row count from.
        Returns
        -------
        int
            Row count.
        """
        if not parent.isValid():
            return len(self.components.components)
        elif parent.isValid():
            if len(self.components.components):
                return len(self.components.components[parent.row()].elements)
            else:
                return 0
        else:
            return 0

    def columnCount(self, parent=QModelIndex()):
        """
        Returns the column count of an index.
        Parameters
        ----------
        parent : QModelIndex
            Parent index to retrieve column row count from.
        Returns
        -------
        int
            Column count. This is always 1.
        """
        if not parent.isValid():
            return 1
        else:
            return 3

    def flags(self, index):
        """
        Returns flags associated with a given index.
        Parameters
        ----------
        index : QModelIndex
            Index to retreive flags from.
        Returns
        -------
        int
            Flags.
        """
        flags = super(ComponentsModel, self).flags(index)
        flags |= Qt.ItemIsEditable
        return flags

    def insertRow(self, obj, parent):
        """
        Insert a row containing an object to a parent index.
        Parameters
        ----------
        obj : Component | Element
            Object to be inserted.
        parent : QModelIndex
            Parent index to append to.
        """
        parentObj = parent.internalPointer()
        if isinstance(parentObj, Component):
            setter = self.components.components[parent.row()].addElement
        else:
            setter = self.components.addComponent
        start = end = self.rowCount(parent)
        self.beginInsertRows(parent, start, end)
        setter(obj)
        self.endInsertRows()
        return self.index(start, 0, parent)

    def removeRow(self, index):
        """
        Remove a row from an index.
        Parameters
        ----------
        index : QModelIndex
            Index to remove.
        """
        parent = index.parent()
        obj = index.internalPointer()

        if isinstance(obj, Component):
            remove = self.components.components.remove
        elif isinstance(obj, Element):
            remove = self.components.components[parent.row()].elements.remove
        else:
            return False

        invalidated = []
        if isinstance(obj, Element):
            for otherObj in self.persistentIndexes.keys():
                if isinstance(otherObj, Element):
                    invalidated.append(otherObj)
        elif isinstance(obj, Component):
            for otherObj in self.persistentIndexes.keys():
                if self.findParent(otherObj) == obj:
                    invalidated.append(otherObj)
        for index_ in invalidated:
            del self.persistentIndexes[index_]

        start = end = index.row()
        self.beginRemoveRows(parent, start, end)
        self.persistentIndexes.pop(obj)
        remove(obj)
        self.endRemoveRows()

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
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return ["Atomic Symbol", "Mass No.", "Abundance"][section]


class ComponentsList(QListView):
    """
    Class to represent a ComponentsList. Inherits QTableView.

    ...
    Attributes
    ----------
    sibling : QTableView
        Sibling table.
    Methods
    -------
    makeModel(data)
        Creates the model using the data.
    handleSelectionChanged(item)
        Handles change in selection in the model.
    insertComponent()
        Inserts a row into the model.
    removeComponent(rows)
        Removes selected rows from the model.
    """
    def __init__(self, parent):
        """
        Constructs all the necessary attributes
        for the ComponentsList object.
        Calls super().__init__.
        Parameters
        ----------
        parent : QWidget
            Parent widget.
        """
        super(ComponentsList, self).__init__(parent=parent)

    def makeModel(self, data, sibling):
        """
        Makes the model and the delegate based on the data.
        Collects all compositions.
        Parameters
        ----------
        data : list
            Data for model to use.
        """
        self.sibling = sibling
        model = ComponentsModel(self.parent(), data)
        self.setModel(model)
        self.sibling.setModel(model)
        self.sibling.setItemDelegate(CompositionDelegate())
        self.selectionModel().selectionChanged.connect(
            self.handleSelectionChanged
        )
        self.setCurrentIndex(
            self.model().index(0, 0)
        )

    def handleSelectionChanged(self, item):
        """
        Handles selection change in the model.
        """
        if self.selectionModel().hasSelection():
            index = item.indexes()[0]
            self.sibling.setRootIndex(index)

    def insertComponent(self):
        """
        Inserts a row into the model.
        """
        new = self.model().insertRow(Component("Component"), QModelIndex())
        self.setCurrentIndex(new)

    def removeComponent(self):
        """
        Removes rows from the model.
        """
        self.model().removeRow(self.currentIndex())
