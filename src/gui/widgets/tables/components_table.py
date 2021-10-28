from PySide6.QtCore import (
    QModelIndex, QPersistentModelIndex, QAbstractItemModel, Qt
)
from PySide6.QtWidgets import QListView
from src.gudrun_classes.components import Component
from src.gudrun_classes.element import Element
from src.gui.widgets.tables.composition_table import CompositionDelegate


class ComponentsModel(QAbstractItemModel):

    def __init__(self, parent, components):
        super(ComponentsModel, self).__init__(parent)
        self.components = components
        self.persistentIndexes = {}

    def index(self, row, column, parent=QModelIndex()):

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
        for i, component in enumerate(self.components.components):
            if item in component.elements:
                return self.components.components[i]

    def setData(self, index, value, role):
        if not index.isValid():
            return False
        elif role == Qt.EditRole:
            if not index.parent().isValid():
                self.components.components[index.row()].name = value
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
        if not parent.isValid():
            return 1
        else:
            return 3

    def flags(self, index):
        flags = super(ComponentsModel, self).flags(index)
        flags |= Qt.ItemIsEditable
        return flags

    def insertRow(self, obj, parent):
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
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return ["Atomic Symbol", "Mass No.", "Abundance"][section]


class ComponentsList(QListView):

    def __init__(self, parent):
        super(ComponentsList, self).__init__(parent=parent)

    def makeModel(self, data, sibling):
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
        if self.selectionModel().hasSelection():
            index = item.indexes()[0]
            self.sibling.setRootIndex(index)

    def insertComponent(self):
        new = self.model().insertRow(Component("Component"), QModelIndex())
        self.setCurrentIndex(new)

    def removeComponent(self):
        self.model().removeRow(self.currentIndex())
