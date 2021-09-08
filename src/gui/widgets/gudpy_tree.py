
from PyQt5.QtGui import QStandardItemModel, QStandardItem
from PyQt5.QtWidgets import QTreeView
from PyQt5.QtCore import Qt


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
    Methods
    -------
    makeModel()
        Creates the model for the tree view from the GudrunFile.
    click(modelIndex)
        Slot method for clicked signal on GudPyTreeView.
    siblings(modelIndex)
        Helper method that returns a list of all siblings associated with a QModelIndex.
    children(modelIndex)
        Helper method that returns a list of all children associated with a QModelIndex.
    absoluteIndex(modelIndex)
        Returns the 'absolute' index of a QModelIndex object.
    depth(modelIndex, depth)
        Recursive method for calulcating the depth in the tree of a QModelIndex object.
    """
    def __init__(self, parent, gudrunFile):
        """
        Constructs all the necessary attributes for the GudPyTreeView object.
        Calls the makeModel method, to create a QStandardItemModel for the tree view.
        Parameters
        ----------
        parent : QWidget
            Parent widget.
        gudrunFile : GudrunFile
            GudrunFile object to build the tree from.
        """
        super(GudPyTreeView, self).__init__(parent)

        self.gudrunFile = gudrunFile
        self.parent = parent

        self.model = QStandardItemModel()
        self.makeModel()
        self.setModel(self.model)
        self.setHeaderHidden(True)
        self.clicked.connect(self.click)

    def makeModel(self):
        """
        Creates the QStandardItemModel to be used for the GudPyTreeView.
        The model is constructed from the GudrunFile.
        """

        # Create root.
        root = self.model.invisibleRootItem()

        # Add QStandardItems for the Instrument, Beam and Normalisation objects.

        instrumentItem = QStandardItem("Instrument")
        instrumentItem.setEditable(False)
        beamItem = QStandardItem("Beam")
        beamItem.setEditable(False)
        normalistionItem = QStandardItem("Normalisation")
        normalistionItem.setEditable(False)
        root.appendRow(instrumentItem)
        root.appendRow(beamItem)
        root.appendRow(normalistionItem)

        # Iterate through SampleBackgrounds belonging to the GudrunFile.
        # Add QStandardItems, in order, for all SampleBackgrounds, Samples and Containers.
        for i, sampleBackground in enumerate(self.gudrunFile.sampleBackgrounds):
            sampleBackgroundItem = QStandardItem(f'Sample Background {i+1}')
            sampleBackgroundItem.setEditable(False)
            root.appendRow(sampleBackgroundItem)
            self.map[f'Sample Background {i+1}'] = Attribute(f'Sample Background {i+1}', sampleBackground, sampleBackground.__str__)
            for sample in sampleBackground.samples:
                sampleItem = QStandardItem(sample.name)
                sampleItem.setCheckable(True)
                sampleItem.setFlags(sampleItem.flags() | Qt.ItemIsUserCheckable)
                sampleItem.setCheckState(Qt.Checked if sample.include else Qt.Unchecked)
                sampleBackgroundItem.appendRow(sampleItem)
                for container in sample.containers:
                    containerItem = QStandardItem(container.name)
                    sampleItem.appendRow(containerItem)

    def click(self, modelIndex):
        """
        Slot method for clicked signal of GudPyTreeView.
        Sets the current index of the parent's QStackedWidget
        to the absolute index of the modelIndex.
        Parameters
        ----------
        modelIndex : QModelIndex
            QModelIndex of the QStandardItem that was clicked in the tree view.
        """
        self.parent.stack.setCurrentIndex(self.absoluteIndex(modelIndex))            


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
        sibling = modelIndex.sibling(0,0)
        i = 0
        while sibling.row() != -1:
            if modelIndex.parent() == sibling.parent():
                s.append(sibling)
            i+=1
            sibling = modelIndex.sibling(i,0)
        return s

    def children(self, modelIndex):
        """
        Helper method that returns all children associated with a QModelIndex.
        Iterates over all children, checking if their parent is the input modelIndex.
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
        child = modelIndex.child(0,0)
        i = 0
        while child.row() != -1:
            if child.parent() == modelIndex:
                c.append(child)
            i+=1
            child = modelIndex.child(i,0)
        return c


    def absoluteIndex(self, modelIndex):
        """
        Helper method that returns the 'absolute' index of a QModelIndex object.
        Absolute index is calculated by determining the index of the QModelIndex
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
                    index+=1+len(self.children(sibling))
            index+=self.absoluteIndex(modelIndex.parent())
        return index            

    def depth(self, modelIndex, depth):
        """
        Recursive helper method that returns the 'depth' of a QModelIndex object.
        This is calculated by recursing up, and incrementing the depth, the tree view,
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
        return self.depth(modelIndex.parent(), depth+1)