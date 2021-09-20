from PyQt5.QtWidgets import QTreeView
from PyQt5.QtCore import (
    QAbstractItemModel,
    QModelIndex,
    QPersistentModelIndex,
    QVariant,
    Qt
)
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
    persistentIndexes : dict
        Dict of QPersistentIndexes,
        key is a GudPy object, value is a QPersistentIndex.
    Methods
    -------
    rowCount(parent)
        Returns the row count of an index.
    columnCount(parent)
        Returns the column count of an index.
    checkState(index)
        Returns the check state of a given index.
    data(index, role)
        Returns the data at a given index.
    index(row, column, parent)
        Returns index associated with given row, column and parent.
    parent(index)
        Returns parent of a given index.
    findParent(item)
        Finds the parent of a given Sample or Container.
    flags(index)
        Returns flags associated with a given index.
    setData(index, value, role)
        Sets data at a given index.
    isSample(index)
        Returns whether a given index is associated with a sample.
    isIncluded(index)
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
        # Check for invalid index.
        if not self.hasIndex(row, column, parent):
            return QModelIndex()
        elif not parent.isValid():
            # Invalid parent means we are at the top level.
            rows = {
                0: self.gudrunFile.instrument, 1: self.gudrunFile.beam,
                2: self.gudrunFile.normalisation
            }
            # Instrument | Beam | Normalisation
            if row in rows.keys():
                obj = rows[row]
            else:
                obj = self.gudrunFile.sampleBackgrounds[row-3]
        elif parent.isValid() and not parent.parent().isValid():
            # Valid parent and invalid grandparent, means that the index
            # corresponds to a sample.
            obj = (
                self.gudrunFile.sampleBackgrounds[parent.row()-3]
                .samples[row]
            )
        elif parent.isValid() and parent.parent().isValid():
            # Valid parent and grandparent means that the index
            # corresponds to a container.
            obj = (
                self.gudrunFile.sampleBackgrounds[parent.parent().row()-3]
                .samples[parent.row()].containers[row]
            )
        else:
            # Otherwise we return an invalid index.
            return QModelIndex()
        # Check that we don't already have the index in reference.
        if obj not in self.persistentIndexes.keys():
            # Create the index and add a QPersistentModelIndex
            # constructed from the index, to the dict.
            index = self.createIndex(row, 0, obj)
            self.persistentIndexes[obj] = QPersistentModelIndex(index)
            return index
        else:
            return QModelIndex(self.persistentIndexes[obj])

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
        if isinstance(
            index.internalPointer(),
            (Instrument, Beam, Normalisation, SampleBackground)
        ):
            return QModelIndex()
        elif isinstance(index.internalPointer(), Sample):
            parent = self.findParent(index.internalPointer())
            return QModelIndex(self.persistentIndexes[parent])
        elif isinstance(index.internalPointer(), Container):
            parent = self.findParent(index.internalPointer())
            return QModelIndex(self.persistentIndexes[parent])
        else:
            return QModelIndex()

    def findParent(self, item):
        """
        Finds the parent of a given Sample or Container.
        Parameters
        ----------
        item : Sample | Container
            Object to find parent of.
        Returns
        -------
        SampleBackground | Sample
            Parent object.
        """
        for i, sampleBackground in enumerate(
            self.gudrunFile.sampleBackgrounds
        ):
            if isinstance(item, Sample):
                if item in sampleBackground.samples:
                    return self.gudrunFile.sampleBackgrounds[i]
            elif isinstance(item, Container):
                for j, sample in enumerate(sampleBackground.samples):
                    if item in sample.containers:
                        return self.gudrunFile.sampleBackgrounds[i].samples[j]

    def data(self, index, role):
        """
        Returns the data at a given index.
        If the index is invalid, or the role is not
        Qt.EditRole | Qt.DisplayRole | Qt.CheckStateRole, then an empty
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
            return QVariant()
        if role == Qt.DisplayRole or role == Qt.EditRole:
            if isinstance(
                index.internalPointer(),
                (Instrument, Beam, Normalisation, SampleBackground)
            ):
                dic = {
                    0: "Instrument", 1: "Beam",
                    2: "Normalisation", 3: "Sample Background"
                }
                return QVariant(dic[index.row()])
            elif isinstance(index.internalPointer(), (Sample, Container)):
                return QVariant(index.internalPointer().name)
        elif role == Qt.CheckStateRole and self.isSample(index):
            return self.checkState(index)
        else:
            return QVariant()

    def setData(self, index, value, role):
        """
        Sets data at a given index, if the index is valid.
        Only used for assigning CheckStates to samples.
        Parameters
        ----------
        index : QModelIndex
            Index to set data at.
        value : QCheckState
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
        elif role == Qt.CheckStateRole and self.isSample(index):
            if value == Qt.Checked:
                index.internalPointer().runThisSample = True
            else:
                index.internalPointer().runThisSample = False
            return True
        else:
            return False

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
            Check state.
        """
        return Qt.Checked if self.isIncluded(index) else Qt.Unchecked

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
        # If the parent is invalid, then it is a top level node.
        if not parent.isValid():
            # Instrument + Beam + Normalisation + N SampleBackgrounds
            return 3 + len(self.gudrunFile.sampleBackgrounds)
        elif parent.isValid() and not parent.parent().isValid():
            # If the parent is valid, but the grandparent is invalid
            # Return the number of samples of the sample background.
            if parent.row() >= 3:
                return len(
                    self.gudrunFile.sampleBackgrounds[parent.row()-3].samples
                )
            else:
                return 0
        elif (
            parent.isValid()
            and parent.parent().isValid()
            and not parent.parent().parent().isValid()
        ):
            # If it is a leaf, then return the number of
            # containers for the sample.
            if parent.parent().row() >= 3:
                return len(
                    self.gudrunFile.sampleBackgrounds[parent.parent().row()-3]
                    .samples[parent.row()].containers
                )
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
        return 1

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
        flags = super(GudPyTreeModel, self).flags(index)
        # If is is a sample, make append checkable flag.
        if self.isSample(index):
            flags |= Qt.ItemIsUserCheckable
        return flags

    def isSample(self, index):
        """
        Returns whether a given index is associated with a sample.
        Parameters
        ----------
        index : QModelIndex
            Index to check if sample is associated with.
        Returns
        -------
        bool
            Is it a sample or not?
        """
        return isinstance(index.parent().internalPointer(), SampleBackground)

    def isIncluded(self, index):
        """
        Returns whether a given index of a sample is to be ran.
        Parameters
        ----------
        index : QModelIndex
            Index to check if the associated sample is to be included or not.
        Returns
        -------
        bool
            Is it to be included?
        """
        return self.isSample(index) and index.internalPointer().runThisSample


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
