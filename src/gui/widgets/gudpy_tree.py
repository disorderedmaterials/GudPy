from PyQt5.QtWidgets import QTreeView
from PyQt5.QtCore import (
    QAbstractItemModel,
    QModelIndex,
    QPersistentModelIndex,
    QVariant,
    Qt
)


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
        if not parent.isValid():
            return 3 + len(self.gudrunFile.sampleBackgrounds)
        elif parent.isValid() and not parent.parent().isValid():
            if parent.row() >=3 and parent.row() < (3 + len(self.gudrunFile.sampleBackgrounds)):
                return len(self.gudrunFile.sampleBackgrounds[parent.row()-3].samples)
            else:
                return 0
        elif parent.isValid() and parent.parent().isValid():
            # print(parent.parent().row())
            # print(parent.row())
            # print(self.data(parent, Qt.DisplayRole).value())
            return len(self.gudrunFile.sampleBackgrounds[parent.parent().row()-3].samples[parent.row()].containers)
        else:
            return 0
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
            Column count - this is always 3.
        """
        return 1
        # if parent.isValid():
        #     return 3
        # else:
        #     return 1
        # return 1
        # if not parent.isValid():
        #     return 1
        # return 0
        # if not parent.isValid():
        #     return 1
        # elif parent.isValid() and not parent.parent().isValid():
        #     return 4
        # elif parent.isValid() and parent.parent().isValid():
        #     return 1

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
        elif not index.parent().isValid():
            dic = {0:"Instrument",1:"Beam",2:"Normalisation", 3:"Sample Background"}
            return QVariant(dic[index.row()]) if role == Qt.DisplayRole or role == Qt.EditRole else QVariant()
        elif index.parent().isValid() and not index.parent().parent().isValid():
            return QVariant(self.gudrunFile.sampleBackgrounds[index.parent().row()-3].samples[index.row()].name) if role == Qt.DisplayRole or role == Qt.EditRole else QVariant()
        elif index.parent().isValid() and index.parent().parent().isValid():
            return QVariant(self.gudrunFile.sampleBackgrounds[index.parent().parent().row()-3].samples[index.parent().row()].containers[index.row()]) if role == Qt.DisplayRole or role == Qt.EditRole else QVariant()
        else:
            return QVariant()

    def flags(self, index):
        flags = super(GudPyTreeModel, self).flags(index)
        # if self.isSample(index):
        #     flags |= Qt.ItemIsUserCheckable | Qt.ItemIsEditable
        return flags

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
        if not parent.isValid():
            child = 0
        # elif parent.internalId() > 0xffffffff or parent.internalId() == 0:
        #     child = parent.row() + 1
        # elif parent.parent().internalId() > 0xffffffff or parent.parent().internalId() == 0:
        #     child = parent.parent().row() + 1
        elif parent.isValid() and not parent.parent().isValid():
            child = parent.row() + 1
        elif parent.isValid() and parent.parent().isValid():
            child = parent.parent().row() + 1
        else:
            return QModelIndex()
        return self.createIndex(row, 0, child)

    def parent(self, index):
        """
        Returns parent of a given index.
        Parameters
        ----------
        index : QModelIndex
            Index to return parent from.
        Returns
        -------
        QModelIndexx§
            Parent index if there is any, otherwise empty QModelIndex
        """
        # child = index.internalPointer()
        # parent = child.parentItem()
        # if parent == 
        internalID = index.internalId()
        if internalID > 0xffffffff or internalID == 0: return QModelIndex()
        # # if internalID >= 3 + len(self.gudrunFile.sampleBackgrounds):
        # #     internalID = 0
        #     # return self.createIndex(1, 0, 0)
        return self.createIndex(internalID-1, 0, 0)
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
    
    def isContainer(self, index):
        return (
            self.parent(index).isValid()
            and self.parent(self.parent(index)).isValid()
        )


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
        self.model_ = GudPyTreeModel(self, self.gudrunFile)
        self.setModel(self.model_)

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
