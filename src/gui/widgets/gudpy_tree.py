from PyQt5.QtWidgets import QTreeView
from PyQt5.QtCore import (
    QAbstractItemModel,
    QModelIndex,
    QPersistentModelIndex,
    QVariant,
    Qt
)

from src.gudrun_classes.gudrun_file import GudrunFile
from src.gudrun_classes.instrument import Instrument
from src.gudrun_classes.beam import Beam
from src.gudrun_classes.normalisation import Normalisation
from src.gudrun_classes.sample import Sample
from src.gudrun_classes.sample_background import SampleBackground
from src.gudrun_classes.container import Container

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
        self.persistentIndexes = {}


    def index(self, row, column, parent=QModelIndex()):
        if not self.hasIndex(row, column, parent):
            return QModelIndex()
        elif not parent.isValid():
            if row == 0:
                obj = self.gudrunFile.instrument
            elif row == 1:
                obj = self.gudrunFile.beam
            elif row == 2:
                obj = self.gudrunFile.normalisation
            else:
                obj = self.gudrunFile.sampleBackgrounds[row-3]
        elif parent.isValid() and not parent.parent().isValid():
            obj = self.gudrunFile.sampleBackgrounds[parent.row()-3].samples[row]
        elif parent.isValid() and parent.parent().isValid() and isinstance(parent.internalPointer(), Sample):
            obj = self.gudrunFile.sampleBackgrounds[parent.parent().row()-3].samples[parent.row()].containers[row]
        else:
            return QModelIndex()
        index = self.createIndex(row, 0, obj)    
        self.persistentIndexes[obj] = QPersistentModelIndex(index)
        return index

    def parent(self, index):
        if not index.isValid():
            return QModelIndex()
        elif isinstance(index.internalPointer(), (Instrument, Beam, Normalisation, SampleBackground)):
            parent = index.internalPointer()
        elif isinstance(index.internalPointer(), (Sample, Container)):
            parent = self.findParent(index.internalPointer())
            print(type(parent))
            print(self.persistentIndexes[parent])
        else:
            return QModelIndex()
        return QModelIndex(self.persistentIndexes[parent])
    
    def findParent(self, item):
        for i, sampleBackground in enumerate(self.gudrunFile.sampleBackgrounds):
            if isinstance(item, Sample):
                if item in sampleBackground.samples:
                    return self.gudrunFile.sampleBackgrounds[i]
            elif isinstance(item, Container):
                for j, sample in enumerate(sampleBackground.samples):
                    if item in sample.containers:
                        return self.gudrunFile.sampleBackgrounds[i].samples[j]


    def data(self, index, role):
        print(type(index.internalPointer()))
        if not index.isValid():
            return QVariant()
        elif isinstance(index.internalPointer(), (Instrument, Beam, Normalisation, SampleBackground)):
            dic = {0:"Instrument",1:"Beam",2:"Normalisation", 3:"Sample Background"}
            return QVariant(dic[index.row()]) if role == Qt.DisplayRole or role == Qt.EditRole else QVariant()
        elif isinstance(index.internalPointer(), (Sample, Container)):
            return QVariant(index.internalPointer().name)
    def rowCount(self, parent=QModelIndex()):
        if not parent.isValid():
            return 3 + len(self.gudrunFile.sampleBackgrounds)
        elif isinstance(parent.internalPointer(), (Instrument, Beam, Normalisation)):
            return 0
        elif isinstance(parent.internalPointer(), SampleBackground):
            return len(parent.internalPointer().samples)
        elif isinstance(parent.internalPointer(), Sample):
            return len(parent.internalPointer().containers)
        else:
            return 0

    def columnCount(self, parent=QModelIndex()):
        return 1

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
