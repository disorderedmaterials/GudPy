from PyQt5.QtGui import QCursor
from PyQt5.QtWidgets import QAction, QMenu, QTreeView
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
from src.gudrun_classes.config import NUM_GUDPY_CORE_OBJECTS


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
    index(row, column, parent)
        Returns index associated with given row, column and parent.
    parent(index)
        Returns parent of a given index.
    findParent(item)
        Finds the parent of a given Sample or Container.
    data(index, role)
        Returns the data at a given index.
    setData(index, value, role)
        Sets data at a given index.
    checkState(index)
        Returns the check state of a given index.
    rowCount(parent)
        Returns the row count of an index.
    columnCount(parent)
        Returns the column count of an index.
    flags(index)
        Returns flags associated with a given index.
    isSample(index)
        Returns whether a given index is associated with a sample.
    isIncluded(index)
        Returns whether a given index of a sample is to be ran.
    insertRow(obj, parent)
        Insert a row containing an object to a parent index.
    removeRow(index)
        Remove a row from an index.
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
                obj = self.gudrunFile.sampleBackgrounds[
                    row-NUM_GUDPY_CORE_OBJECTS
                ]
        elif parent.isValid() and not parent.parent().isValid():
            # Valid parent and invalid grandparent, means that the index
            # corresponds to a sample.
            obj = (
                self.gudrunFile.sampleBackgrounds[
                    parent.row()-NUM_GUDPY_CORE_OBJECTS
                ]
                .samples[row]
            )
        elif parent.isValid() and parent.parent().isValid():
            # Valid parent and grandparent means that the index
            # corresponds to a container.
            obj = (
                self.gudrunFile.sampleBackgrounds[
                    parent.parent().row()-NUM_GUDPY_CORE_OBJECTS
                ].samples[parent.row()].containers[row]
            )
        else:
            # Otherwise we return an invalid index.
            return QModelIndex()
        # Create the index and add a QPersistentModelIndex
        # constructed from the index, to the dict.
        index = self.createIndex(row, 0, obj)
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
                return QVariant(
                    dic[
                        index.row() if index.row() <= NUM_GUDPY_CORE_OBJECTS
                        else NUM_GUDPY_CORE_OBJECTS
                    ]
                )
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
            return (
                NUM_GUDPY_CORE_OBJECTS
                + len(self.gudrunFile.sampleBackgrounds)
            )
        elif parent.isValid() and not parent.parent().isValid():
            # If the parent is valid, but the grandparent is invalid
            # Return the number of samples of the sample background.
            if (
                parent.row() >= NUM_GUDPY_CORE_OBJECTS
                and len(self.gudrunFile.sampleBackgrounds)
            ):
                return len(
                    self.gudrunFile.sampleBackgrounds[
                        parent.row()-NUM_GUDPY_CORE_OBJECTS
                    ].samples
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
            return len(
                self.gudrunFile.sampleBackgrounds[
                    parent.parent().row()-NUM_GUDPY_CORE_OBJECTS
                ].samples[parent.row()].containers
            )
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

    def insertRow(self, obj, parent):
        """
        Insert a row containing an object to a parent index.
        Parameters
        ----------
        obj : SampleBackground | Sample | Container
            Object to be inserted.
        parent : QModelIndex
            Parent index to append to.
        """
        # Get the parent object.
        parentObj = parent.internalPointer()

        # Dict for deciding if the object has a valid parent.
        validParents = {
            SampleBackground: not isinstance(parentObj, SampleBackground),
            Sample: isinstance(parentObj, SampleBackground),
            Container: isinstance(parentObj, Sample)
        }

        # Dict for deciding if the parent object is actually a sibling.
        validSiblings = {
            SampleBackground: isinstance(parentObj, SampleBackground),
            Sample: isinstance(parentObj, Sample),
            Container: isinstance(parentObj, Container)
        }

        if validParents[type(obj)]:
            # We are appending
            if isinstance(obj, SampleBackground):
                # SampleBackground is top level, so the parent is the root.
                parent = QModelIndex()
                setter = self.gudrunFile.sampleBackgrounds.append
            if isinstance(obj, Sample):
                targetIndex = parent.row()-NUM_GUDPY_CORE_OBJECTS
                setter = (
                    self.gudrunFile.sampleBackgrounds[targetIndex]
                    .samples.append
                )
            elif isinstance(obj, Container):
                targetIndex = parent.parent().row()-NUM_GUDPY_CORE_OBJECTS
                setter = (
                    self.gudrunFile.sampleBackgrounds[targetIndex]
                    .samples[parent.row()].containers.append
                )
            # Since we are only inserting one row, start = end.
            start = end = self.rowCount(parent)
            # Begin inserting rows.
            self.beginInsertRows(parent, start, end)
            # Call the setter.
            setter(obj)
            # End inserting rows.
            self.endInsertRows()
        elif validSiblings[type(obj)]:
            # We are inserting.
            if isinstance(obj, SampleBackground):
                index = self.gudrunFile.sampleBackgrounds.index(parentObj)
                # SampleBackground is top level, so the parent is the root.
                parent = QModelIndex()
                setter = self.gudrunFile.sampleBackgrounds.insert
            elif isinstance(obj, Sample):
                targetIndex = parent.parent().row()-NUM_GUDPY_CORE_OBJECTS
                index = (
                    self.gudrunFile.sampleBackgrounds[targetIndex]
                    .samples.index(parentObj)
                )
                setter = (
                    self.gudrunFile.sampleBackgrounds[targetIndex]
                    .samples.insert
                )
            elif isinstance(obj, Container):
                targetIndex = (
                    parent.parent().parent().row()-NUM_GUDPY_CORE_OBJECTS
                )
                index = (
                    self.gudrunFile.sampleBackgrounds[targetIndex].
                    samples[parent.parent().row()].containers.index(parentObj)
                )
                setter = (
                    self.gudrunFile.sampleBackgrounds[targetIndex].
                    samples[parent.parent().row()].containers.insert
                )
            # Again, start = end.
            start = end = self.rowCount(parent.parent())
            # Begin inserting rows.
            self.beginInsertRows(parent.parent(), start, end)
            # Call the setter.
            # index+1 to insert after the current index.
            setter(index+1, obj)
            # End inserting rows.
            self.endInsertRows()

    def removeRow(self, index):
        """
        Remove a row from an index.
        Parameters
        ----------
        index : QModelIndex
            Index to remove.
        """
        # Get the parent index.
        parent = index.parent()
        # Get the object associated with the current index.
        obj = index.internalPointer()
        # Decide on the remove function.
        if isinstance(obj, SampleBackground):
            remove = self.gudrunFile.sampleBackgrounds.remove
        elif isinstance(obj, Sample):
            targetIndex = parent.row()-NUM_GUDPY_CORE_OBJECTS
            remove = (
                self.gudrunFile.sampleBackgrounds[targetIndex].samples.remove
            )
        elif isinstance(obj, Container):
            targetIndex = parent.parent().row()-NUM_GUDPY_CORE_OBJECTS
            remove = (
                self.gudrunFile.sampleBackgrounds[targetIndex]
                .samples[parent.row()].containers.remove
            )
        invalidated = []

        # Remove QPersistendIndexes from the dict that become invalidated
        # by removing the current index.
        if isinstance(obj, Sample):
            for otherObj in self.persistentIndexes.keys():
                if isinstance(otherObj, Sample):
                    if self.findParent(otherObj) == parent.internalPointer():
                        invalidated.append(otherObj)
            for otherObj in self.persistentIndexes.keys():
                if isinstance(otherObj, Container):
                    if self.findParent(otherObj) in invalidated:
                        invalidated.append(otherObj)
                        print("appended")

        elif isinstance(obj, Container):
            for otherObj in self.persistentIndexes.keys():
                if isinstance(otherObj, Container):
                    if self.findParent(otherObj) == parent.internalPointer():
                        invalidated.append(otherObj)
        for index_ in invalidated:
            del self.persistentIndexes[index_]
        start = end = index.row()
        # Begin inserting rows.
        self.beginRemoveRows(parent, start, end)
        # Pop the object from the dict.
        self.persistentIndexes.pop(obj)
        # Remove the row.
        remove(obj)
        # End inserting rows.
        self.endRemoveRows()


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
    currentObject()
        Returns the object associated with the current index.
    insertRow(obj)
        Inserts an object into the current row in the model.
    removeRow()
        Removes the current index from the model.
    insertSampleBackground_(sampleBackground)
        Inserts a SampleBackground into the GudrunFile.
    insertSample_(sample)
        Inserts a Sample into the GudrunFile.
    insertContainer_(container)
        Inserts a Container into the GudrunFile.
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
        indexMap = {
            Instrument: (0, None),
            Beam: (1, None),
            Normalisation: (2, None),
            SampleBackground: (3, self.sibling.widget(3).setSampleBackground),
            Sample: (4, self.sibling.widget(4).setSample),
            Container: (5, self.sibling.widget(5).setContainer)
        }
        index, setter = indexMap[type(modelIndex.internalPointer())]
        self.sibling.setCurrentIndex(index)
        if setter:
            setter(modelIndex.internalPointer())

    def currentObject(self):
        """
        Returns the object associated with the current index.
        Returns
        -------
        Instrument | Beam | Normalisation |
        SampleBackground | Sample | Container
            Object associated with the current index.
        """
        return self.currentIndex().internalPointer()

    def insertRow(self, obj):
        """
        Inserts an object into the current row in the model.
        Parameters
        ----------
        obj : SampleBackground | Sample | Container
            Object to be inserted.
        """
        self.model().insertRow(obj, self.currentIndex())

    def removeRow(self):
        """
        Removes the current index from the model.
        """
        self.model().removeRow(self.currentIndex())

    def contextMenuEvent(self, event):
        """
        Creates context menu, so that on right clicking the table,
        the user is able to perform menu actions.
        Parameters
        ----------
        event : QMouseEvent
            The event that triggers the context menu.
        """
        self.menu = QMenu(self)
        editMenu = self.menu.addMenu("Edit")
        insertSampleBackground = QAction("Insert Sample Background", editMenu)
        insertSampleBackground.triggered.connect(
            self.insertSampleBackground
        )
        editMenu.addAction(insertSampleBackground)
        if isinstance(self.currentObject(), SampleBackground):
            insertSample = QAction("Insert Sample", editMenu)
            insertSample.triggered.connect(
                self.insertSample
            )
            editMenu.addAction(insertSample)
        elif isinstance(self.currentObject(), Sample):
            insertContainer = QAction("Insert Container", editMenu)
            insertContainer.triggered.connect(
                self.insertContainer
            )
            editMenu.addAction(insertContainer)

        self.menu.popup(QCursor.pos())

    def insertSampleBackground(self, sampleBackground=None):
        """
        Inserts a SampleBackground into the GudrunFile.
        Inserts it into the tree.
        Parameters
        ----------
        sampleBackground : SampleBackground, optional
            SampleBackground object to insert.
        """
        if not sampleBackground:
            sampleBackground = SampleBackground()
        self.insertRow(sampleBackground)

    def insertSample(self, sample=None):
        """
        Inserts a Sample into the GudrunFile.
        Inserts it into the tree.
        Parameters
        ----------
        sample : Sample, optional
            Sample object to insert.
        """
        if not sample:
            sample = Sample()
            sample.name = "SAMPLE"  # for now, give a default name.
        self.insertRow(sample)

    def insertContainer(self, container=None):
        """
        Inserts a Container into the GudrunFile.
        Inserts it into the tree.
        Parameters
        ----------
        container : Container, optional
            Container object to insert.
        """
        if not container:
            container = Container()
            container.name = "CONTAINER"  # for now, give a default name.
        self.insertRow(container)
    
