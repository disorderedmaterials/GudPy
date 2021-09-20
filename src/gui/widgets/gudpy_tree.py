from PyQt5.QtWidgets import QTreeView
from PyQt5.QtCore import (
    QAbstractItemModel,
    QModelIndex,
    QPersistentModelIndex,
    QVariant,
    Qt
)


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
    objectData()
        Returns the object associated with the data.
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
        if isinstance(self._data, str):
            return QVariant(self._data)
        return (
            QVariant(self._data[0])
            if self._data and not column
            else QVariant()
        )

    def objectData(self):
        """
        Returns the object associated with the data. Only works for samples.
        Returns
        -------
        Sample
            Sample object.
        """
        return self._data[1]

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
    """
    Class to represent a GudPyTreeModel. To be used with a GudyTree object.
    Inherits QAbstractTreeModel.

    ...

    Attributes
    ----------
    gudrunFile : GudrunFile
        GudrunFile object associated with the model.
    _data : list
        Data for the model to use.
    checkStates : dict
        Dictionary to manage check states.
    root : GudPyNode
        Root node of the tree.
    Methods
    -------
    makeModel(root, data)
        Creates the internal tree data structure.
    rowCount(parent)
        Returns the row count of an index.
    columnCount(parent)
        Returns the column count of an index.
    checkState(index)
        Returns the check state of a given index.
    data(index, role)
        Returns the data at a given index.
    objectData(index)
        Returns the object associated with a given index.
    headerData(column, orientation, role)
        Stub method.
    index(row, column, parent)
        Returns index associated with given row, column and parent.
    parent(index)
        Returns parent of a given index.
    flags(index)
        Returns flags associated with a given index.
    setData(index, value, role)
        Sets data at a given index.
    isSample(index)
        Returns whether a given index is associated with a sample.
    included(index)
        Returns whether a given index of a sample is to be ran.
    """

    def __init__(self, parent, gudrunFile):
        """
        Constructs all the necessary attributes for the GudPyTreeModel object.
        Creates the tree data stucture in list format, and then using nodes
        by calling makeModel(root, data).
        Calls super()._init__ which calls the dunder init method
        from QAbstractItemModel.
        Parameters
        ----------
        parent : QWidget
            Parent widget.
        gudrunFile : GudrunFile
            GudrunFile object for model to use.
        """
        super(GudPyTreeModel, self).__init__(parent)
        self.gudrunFile = gudrunFile

        # Form a heirarchical list from the gudrunFile.
        self._data = ["Instrument", "Beam", "Normalisation"]
        for sampleBackground in self.gudrunFile.sampleBackgrounds:
            self._data.append([])
            for sample in sampleBackground.samples:
                # For samples, include a tuple (name, object)
                self._data[-1].append([(sample.name, sample), []])
                for container in sample.containers:
                    self._data[-1][-1][-1].append(container.name)

        # Set the root node.
        self.root = GudPyNode(None, None)
        # Make the model!
        self.makeModel(self.root, self._data)

    def makeModel(self, root, data):
        """
        Recursive method that creates the internal tree data structure.
        Elements which are strings are simply appended to the root.
        Elements which are lists are appended as subtrees to the root.
        Parameters
        ----------
        root : GudPyNode
            Root node of tree.
        data : list
            Data to form tree from.
        """
        for element in data:
            # String instances are appended as children to the root.
            if isinstance(element, str):
                item = GudPyNode(element, root)
                root.appendChild(item)
            elif isinstance(element, list):
                # If there is no parent node, but the element is a list,
                # then it must be a sample background.
                if not root.parent():
                    item = GudPyNode("Sample Background", root)
                    root.appendChild(item)
                    # Append a child tree to the root.
                    # This tree consists of samples/containers.
                    self.makeModel(item, element)
                # If there is a parent node, but no grandparent,
                # and the element is a list, then it must be a
                # sample.
                elif root.parent() and not root.parent().parent():
                    item = GudPyNode(element[0], root)
                    root.appendChild(item)
                    # Append a child tree to the root.
                    # This tree consists of containers.
                    self.makeModel(item, element[1:])
                # If there is a parent and grandparent node,
                # then it must be a container.
                else:
                    item = GudPyNode(element[0], root)
                    # Append a leaf node to the tree.
                    root.appendChild(item)
                    # Append the other containers to the same root.
                    self.makeModel(root, element[1:])

    def rowCount(self, parent=QModelIndex()):
        """
        Returns the row count.
        Parameters
        ----------
        parent : QModelIndex, optional
            Parent index.
        Returns
        int
            Row count
        """
        return (
            self.root.childCount()
            if not parent.isValid()
            else parent.internalPointer().childCount()
        )

    def columnCount(self, parent):
        """
        Returns the number of columns in the model.
        Parameters
        ----------
        parent : QModelIndex
            Parent index.
        Returns
        -------
        int
            Column count - this is always 1.
        """
        return 1

    def checkState(self, index):
        """
        Returns the check state of a given index.
        Parameters
        ----------
        index : QModelIndex
            Index to return check state from.
        Returns
        -------
        QCheckState
            The check state of the index.
        """
        return Qt.Checked if self.included(index) else Qt.Unchecked

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
        QVariant | QCheckState
            Data at given index.
        """
        if not index.isValid():
            return QVariant()
        if role == Qt.CheckStateRole and self.isSample(index):
            return self.checkState(QPersistentModelIndex(index))
        return (
            index.internalPointer().data(index.column())
            if role == Qt.DisplayRole
            else QVariant()
        )

    def objectData(self, index):
        """
        Returns the object associated with a given index.
        Parameters
        ----------
        index : QModelIndex
            Index to retrieve object data from.
        Returns
        -------
        Sample
            Sample object associated with index.
        """
        return index.internalPointer().objectData()

    def headerData(self, column, orientation, role):
        """
        There are no headers, so this always returns nothing.
        Returns
        -------
        None
        """
        pass

    def index(self, row, column, parent):
        """
        Returns index associated with given row, column and parent.
        Parameters
        ----------
        row : int
            Row number.
        column : int
            Column number
        parent : QModelIndex
            Parent index.
        Returns
        QModelIndex
            QModelIndex created, if possible, otherwise empty QModelIndex.
        """
        if not self.hasIndex(row, column, parent):
            return QModelIndex()
        child = (
            self.root.child(row)
            if not parent.isValid()
            else
            parent.internalPointer().child(row)
        )
        return self.createIndex(row, column, child) if child else QModelIndex()

    def parent(self, index):
        """
        Returns parent of a given index.
        Parameters
        ----------
        index : QModelIndex
            Index to return parent from.
        Returns
        -------
        QModelIndex
            Parent index if there is any, otherwise empty QModelIndex
        """
        if not index.isValid():
            return QModelIndex()
        child = index.internalPointer()
        if not child:
            return QModelIndex()
        parent = child.parent()
        return (
            QModelIndex()
            if parent == self.root
            else
            self.createIndex(parent.row(), 0, parent)
        )

    def flags(self, index):
        """
        Returns flags associated with a given index.
        Returns default flags if index is associated with a sample,
        otherwise appends sample-specific flags.
        Parameters
        ----------
        index : QModelIndex
            Index to return flags from.
        Returns
        -------
        int
            Flags.
        """
        flags = super(GudPyTreeModel, self).flags(index)
        if self.isSample(index):
            flags |= Qt.ItemIsUserCheckable | Qt.ItemIsEditable
        return flags

    def setData(self, index, value, role):
        """
        Sets data at a given index.
        Parameters
        ----------
        index : QModelIndex
            Index to set data at.
        value : any
            Value to set data at index.
        role : int
            Role.
        Returns
        bool
            Was data successfully set or not?
        """
        if (
            index.isValid()
            and role == Qt.CheckStateRole
            and self.isSample(index)
        ):
            self.objectData(QModelIndex(index)).runThisSample = (
                True if value == Qt.Checked
                else False
            )
            return True
        return False

    def isSample(self, index):
        """
        Returns whether a given index is associated with a sample.
        Parameters
        index : QModelIndex
            Index to check if sample is associated with.
        Returns
        bool
            Is the index associated with a sample or not?
        """
        return (
            self.parent(index).isValid()
            and not self.parent(self.parent(index)).isValid()
        )

    def included(self, index):
        """
        Returns whether a given index of a sample is to be ran.
        Parameters
        index : QModelIndex
            Index to check if the sample associated with it is to be ran.
        Returns
        bool
            Is the sample to be run or not?
        """
        return self.objectData(QModelIndex(index)).runThisSample


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
        self.setModel(GudPyTreeModel(self, self.gudrunFile))

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
