import enum
from os import closerange
from src.gudrun_classes.sample_background import SampleBackground
from src.gudrun_classes.sample import Sample
from src.gui.widgets.gudpy_tables import GudPyTableModel
from PyQt5.QtGui import QMoveEvent, QStandardItemModel, QStandardItem
from PyQt5.QtWidgets import QTreeView
from PyQt5.QtCore import QAbstractItemModel, QModelIndex, QPersistentModelIndex, QVariant, Qt

class GudPyNode():
    """
    Class to represent a GudPyNode. To be used in a QTreeView.

    ...

    Attributes
    ----------
    _data : list
        Data for node to contain,
    parent : GudPyNode
        Parent node.
    children : GudPyNode[]
        List of child nodes.
    Methods
    -------
    appendChild(node)
        Appends a child node to the current node.
    child(row)
        Returns child at specified row.
    childCount()
        Returns number of child nodes.
    columnCount()
        Returns number of columns.
    data(column)
        Returns data at specified column.
    parent()
        Returns parent node.
    row()
        Returns row of node.
    """
    def __init__(self, data, parent):
        """
        Constructs all the necessary attributes for the GudPyNode object.
        Parameters
        ----------
        _data : list
            Data for node to contain,
        parent : GudPyNode
            Parent node.
        """
        self._data = data
        self._parent = parent
        self.children = []

    def appendChild(self, node):
        """
        Appends a child node to the current node.
        Parameters
        ----------
        node : GudPyNode
            Parent node.
        """
        self.children.append(node)

    def child(self, row):
        """
        Returns child at specified row.
        Parameters
        ----------
        row : int
            Row number.
        Returns
        -------
        GudPyNode
            Child node.
        """
        return self.children[row]

    def childCount(self):
        """
        Returns number of child nodes.
        Returns
        -------
        int
            Number of child nodes
        """
        return len(self.children)

    def columnCount(self):
        """
        Returns the number of columns.
        Returns
        -------
        int
            Number of columns - this is always 1.
        """
        return 1

    def data(self, column):
        """
        Returns the data at a given column.
        Parameters
        ----------
        column : int
            Column to return data from.
        Returns
        -------
        QVariant
            Data at given column.
        """
        return QVariant(self._data) if self._data and not column else QVariant()

    def parent(self):
        """
        Returns parent node.
        Returns
        -------
        GudPyNode
            Parent node
        """
        return self._parent

    def row(self):
        """
        Returns row of node.
        Returns
        -------
        int
            Row number
        """
        return self._parent.children.index(self) if self._parent else 0

class GudPyTreeModel(QAbstractItemModel):
    def __init__(self,parent,gudrunFile) :
        super(GudPyTreeModel,self).__init__(parent)
        self.gudrunFile = gudrunFile
        self._data = ["Instrument", "Beam", "Normalisation"]
        self.dataReferences = [self.gudrunFile.instrument, self.gudrunFile.beam, self.gudrunFile.normalisation]
        for sampleBackground in self.gudrunFile.sampleBackgrounds:
            self._data.append([])
            self.dataReferences.append([])
            for sample in sampleBackground.samples:
                self._data[-1].append([sample.name, []])
                self.dataReferences[-1].append([sample, []])
                for container in sample.containers:
                    self._data[-1][-1][-1].append(container.name)
                    self.dataReferences[-1][-1].append(container)
        self.hasInit = False
        self.checkStates = {}
        self.root = GudPyNode(None, None)
        self.parents = {0 : self.root}
        self.makeModel(self.root, self._data)

    def makeModel(self, root, data):
        for el in data:
            if not isinstance(el, list):
                item = GudPyNode(el, root)
                root.appendChild(item)
        for el in data:
            if isinstance(el, list):
                if not root.parent():
                    item = GudPyNode("Sample Background", root)
                    root.appendChild(item)
                    self.makeModel(item, el)
                elif root.parent() and not root.parent().parent():
                    item = GudPyNode(el[0], root)
                    root.appendChild(item)
                    self.makeModel(item, el[1:])
                else:
                    item = GudPyNode(el[0], root)
                    root.appendChild(item)
                    self.makeModel(item, el[1:])

    def rowCount(self, parent = QModelIndex()):
        return self.root.childCount() if not parent.isValid() else parent.internalPointer().childCount()

    def columnCount(self, parent):
        return 1

    def checkState(self, index):
        return self.checkStates[index] if index in self.checkStates.keys() else Qt.Unchecked

    def data(self, index, role):
        if not index.isValid():
            return QVariant()
        if role == Qt.CheckStateRole and self.isSample(index):
            return self.checkState(QPersistentModelIndex(index))
        return index.internalPointer().data(index.column()) if role == Qt.DisplayRole else QVariant()
        
    def headerData(self, column, orientation, role):
        return QVariant()

    def index(self, row, column, parent):
        if not self.hasIndex(row, column, parent):
            return QModelIndex()
        child = self.root.child(row) if not parent.isValid() else parent.internalPointer().child(row)
        return self.createIndex(row, column, child) if child else QModelIndex()

    def parent(self, index):
        if not index.isValid():
            return QModelIndex()
        child = index.internalPointer()
        if not child:
            return QModelIndex()
        parent = child.parent()
        return QModelIndex() if parent == self.root else self.createIndex(parent.row(), 0, parent)

    def flags(self, index):
        flags = super(GudPyTreeModel, self).flags(index)
        if self.isSample(index):
            flags |= Qt.ItemIsUserCheckable | Qt.ItemIsEditable
        return flags
    
    def setData(self, index, value, role):
        if index.isValid() and role == Qt.CheckStateRole and self.isSample(index):
            # if not self.hasInit:
            #     self.checkStates[QPersistentModelIndex(index)] = Qt.Checked if 
            self.checkStates[QPersistentModelIndex(index)] = value
            return True

    def isSample(self, index):
        self.included(index)
        return self.parent(index).isValid() and not self.parent(self.parent(index)).isValid()

    # def included(self, index):
    #     print(index.row(), index.column())

class GudPyTreeView(QTreeView):
    """
    Custom QTreeView View class for GudPy objects. Inherits QTreeView.

    ...

    Attributes
    ----------
    gudrunFile : GudrunFile
        GudrunFile object to build the tree from.
    parent : QWidget
        Parent widget.
    model : QStandardItemModel
        Model to be used for the tree view.
    sibling : QStackedWidget
        Sibling widget to communicate signals and slots to/from.
    Methods
    -------
    buildTree(gudrunFile, sibling)
        Builds the tree view from the gudrunFile, pairing
        the modelIndexes with pages of the sibling QStackedWidget.
    makeModel()
        Creates the model for the tree view from the GudrunFile.
    click(modelIndex)
        Slot method for clicked signal on GudPyTreeView.
    siblings(modelIndex)
        Helper method that returns a list
        of all siblings associated with a QModelIndex.
    children(modelIndex)
        Helper method that returns a list of
        all children associated with a QModelIndex.
    absoluteIndex(modelIndex)
        Returns the 'absolute' index of a QModelIndex object.
    depth(modelIndex, depth)
        Recursive method for calulcating the
        depth in the tree of a QModelIndex object.
    """

    def __init__(self, parent):
        """
        Parameters
        ----------
        parent : QWidget
            Parent widget.
        """
        super(GudPyTreeView, self).__init__(parent)

    def buildTree(self, gudrunFile, sibling):
        """
        Constructs all the necessary attributes for the GudPyTreeView object.
        Calls the makeModel method,
        to create a QStandardItemModel for the tree view.
        Parameters
        ----------
        gudrunFile : GudrunFile
            GudrunFile object to create the tree from.
        sibling : QStackedWidget
            Sibling widget to communicate signals and slots to/from.
        """
        self.gudrunFile = gudrunFile
        self.sibling = sibling
        self.makeModel()
        # self.setModel(self.model)
        self.setHeaderHidden(True)
        self.clicked.connect(self.click)

    def makeModel(self):
        """
        Creates the QStandardItemModel to be used for the GudPyTreeView.
        The model is constructed from the GudrunFile.
        """
        # model = GudPyTreeModel(self.gudrunFile, self)
        self.setModel(GudPyTreeModel(self, self.gudrunFile))
        # print(self.model().rowCount(QModelIndex()))
        return
        # Create root.
        root = self.model.invisibleroot()

        # Add QStandardItems for the Instrument,
        # Beam and Normalisation objects.

        instrumentItem = GudPyItem("Instrument")
        beamItem = GudPyItem("Beam")
        normalistionItem = GudPyItem("Normalisation")
        root.appendRow(instrumentItem)
        root.appendRow(beamItem)
        root.appendRow(normalistionItem)

        # Iterate through SampleBackgrounds
        # belonging to the GudrunFile.
        # Add QStandardItems, in order,
        # for all SampleBackgrounds, Samples and Containers.
        for i, sampleBackground in enumerate(
            self.gudrunFile.sampleBackgrounds
        ):
            sampleBackgroundItem = SampleBackgroundItem(sampleBackground)
            root.appendRow(sampleBackgroundItem)
            for sample in sampleBackground.samples:
                sampleItem = SampleItem(sample)
                sampleBackgroundItem.appendRow(sampleItem)
                for container in sample.containers:
                    containerItem = ContainerItem(container)
                    sampleItem.appendRow(containerItem)

    def click(self, modelIndex):
        """
        Slot method for clicked signal of GudPyTreeView.
        Sets the current index of the sibling QStackedWidget
        to the absolute index of the modelIndex.
        Parameters
        ----------
        modelIndex : QModelIndex
            QModelIndex of the QStandardItem that was clicked in the tree view.
        """
        self.sibling.setCurrentIndex(self.absoluteIndex(modelIndex))

    def siblings(self, modelIndex):
        """
        Helper method that returns all siblings associated with a QModelIndex.
        Iterates over all siblings, checking if they share the same parent.
        Parameters
        ----------
        modelIndex : QModelIndex
            Input modelIndex, to find siblings from.
        Returns
        -------
        list
            QModelIndexes that are siblings of the input modelIndex.
        """
        s = []
        sibling = modelIndex.sibling(0, 0)
        i = 0
        while sibling.row() != -1:
            if modelIndex.parent() == sibling.parent():
                s.append(sibling)
            i += 1
            sibling = modelIndex.sibling(i, 0)
        return s

    def children(self, modelIndex):
        """
        Helper method that returns all children associated with a QModelIndex.
        Iterates over all children,
        checking if their parent is the input modelIndex.
        Parameters
        ----------
        modelIndex : QModelIndex
            Input modelIndex, to find children from.
        Returns
        -------
        list
            QModelIndexes that are children of the input modelIndex.
        """
        c = []
        child = modelIndex.child(0, 0)
        i = 0
        while child.row() != -1:
            if child.parent() == modelIndex:
                c.append(child)
            i += 1
            child = modelIndex.child(i, 0)
        return c

    def absoluteIndex(self, modelIndex):
        """
        Helper method that returns the 'absolute'
        index of a QModelIndex object.
        Absolute index is calculated by determining
        the index of the QModelIndex
        in a flattened model.
        Parameters
        ----------
        modelIndex : QModelIndex
            QModelIndex of which to find the absolute index.
        Returns
        -------
        int
            Absolute index of input modelIndex.
        """
        index = 1
        if modelIndex.parent().row() == -1:
            return modelIndex.row()
        else:
            siblings = self.siblings(modelIndex)
            for sibling in siblings:
                if sibling.row() < modelIndex.row():
                    index += 1 + len(self.children(sibling))
            index += self.absoluteIndex(modelIndex.parent())
        return index

    def depth(self, modelIndex, depth):
        """
        Recursive helper method that returns the
        'depth' of a QModelIndex object.
        This is calculated by recursing up,
        and incrementing the depth, the tree view,
        until no more parents exist.
        Parameters
        ----------
        modelIndex : QModelIndex
            QModelIndex of which to find the depth.
        Returns
        -------
        int
            Depth of input modelIndex.
        """
        row = modelIndex.parent().row()
        if row < 0:
            return depth
        return self.depth(modelIndex.parent(), depth + 1)
