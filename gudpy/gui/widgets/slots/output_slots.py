from PySide6.QtCore import (
    QAbstractItemModel,
    QModelIndex,
    Qt
)
from PySide6.QtWidgets import QTreeView


class OutputSlots():
    def __init__(self, widget, parent):
        self.widget = widget
        self.parent = parent

    def setOutputStream(self, stdout):
        self.widget.outputTextEdit.append(
            "".join(stdout.split("\n"))
        )

    def setScroll(self):
        self.widget.outputTextEdit.verticalScrollBar().setValue(
            self.widget.outputTextEdit.verticalScrollBar(
            ).maximum()
        )

    def setOutput(self, output, task, gudrunFile):
        if not gudrunFile:
            gudrunFile = self.parent.gudrunFile
        self.output = output
        self.task = task
        self.widget.outputTree.buildTree(
            gudrunFile, output, self
        )
        self.setScroll()


class OutputNode:
    def __init__(self, name, data: str) -> None:
        self._name = name
        self._data = data
        self._parent = None
        self._children: list[OutputNode] = []
        self._row = 0

    def name(self):
        return self._name

    def data(self):
        return self._data

    def parent(self):
        return self._parent

    def row(self):
        return self._row

    def columnCount(self):
        return 1

    def childCount(self):
        return len(self._children)

    def child(self, row):
        if row >= 0 and row < self.childCount():
            return self._children[row]

    def addChild(self, child):
        child._parent = self
        child._row = len(self._children)
        self._children.append(child)


class OutputTreeModel(QAbstractItemModel):
    def __init__(self, processName, parent=None):
        super().__init__(parent)
        self.processName = processName
        self._root = OutputNode(processName, "")

    def setOutput(self, output, gudrunFile):
        self.beginResetModel()
        if isinstance(output, dict):
            self._setupDictData(output, gudrunFile)
        else:
            self._setupSingleData(self._root, output, gudrunFile)
        self.endResetModel()

    def addChild(self, parent, node):
        self.beginInsertRows(
            self.createIndex(parent.childCount() + 1, 0, node),
            parent.childCount(),
            parent.childCount())
        parent.addChild(node)
        self.endInsertRows()

    def splitOutput(self, outputLines, marker):
        splitOutput = [[]]
        currentIndex = 0
        for line in outputLines:
            if line.strip() == f"gudrun_dcs> Got to: {marker}":
                splitOutput.append([])
                currentIndex += 1
            splitOutput[currentIndex].append(line)
        return splitOutput

    def _setupSingleData(self, root, output, gudrunFile):
        root._data = output
        outputlines = output.splitlines(keepends=True)
        # Indexes for each sample background
        samples = [s for sb in gudrunFile.sampleBackgrounds
                   for s in sb.samples if s.runThisSample]

        sampleBgOutputs = self.splitOutput(
            outputlines, "SAMPLE BACKGROUND")

        self.addChild(root, OutputNode(
            "General", "".join(sampleBgOutputs[0])))
        sampleBgOutputs.pop(0)

        for sbg, sbgOutput in zip(
                gudrunFile.sampleBackgrounds, sampleBgOutputs):
            sampleOutputs = self.splitOutput(sbgOutput, "SAMPLE")

            sbgNode = OutputNode(
                "Sample Background", "".join(sampleOutputs[0]))
            sampleOutputs.pop(0)

            samples = [s for s in sbg.samples if s.runThisSample]

            for sample, sampleOutput in zip(samples, sampleOutputs):
                self.addChild(sbgNode, OutputNode(
                    sample.name, "".join(sampleOutput)))
            self.addChild(root, sbgNode)

    def _setupDictData(self, output, gudrunFile):
        for key, value in output:
            iterationOutput = OutputNode(key, value)
            self.addChild(self._root, iterationOutput)
            self._setupSingleData(iterationOutput, value, gudrunFile)

    def index(self, row, column, parent=QModelIndex()):
        if not self.hasIndex(row, column, parent):
            return QModelIndex()
        if not parent.isValid():
            parentNode = self._root
        else:
            parentNode = parent.internalPointer()
        child = parentNode.child(row)
        if child:
            return self.createIndex(row, column, child)
        return QModelIndex()

    def parent(self, index):
        if not index.isValid():
            return QModelIndex()
        child = index.internalPointer()
        parentNode = child.parent()
        if parentNode == self._root or not parentNode:
            return QModelIndex()
        return self.createIndex(parentNode.row(), 0, parentNode)

    def rowCount(self, index):
        if index.isValid():
            return index.internalPointer().childCount()
        return self._root.childCount()

    def columnCount(self, parent=QModelIndex()):
        return 1

    def data(self, index, role=Qt.DisplayRole):
        if index.isValid() and role == Qt.DisplayRole:
            return index.internalPointer().name()
        return None


class OutputTreeView(QTreeView):
    def __init__(self, parent):
        super().__init__(parent)
        self.model_ = None

    def buildTree(self, gudrunFile, output, parent):
        self.parent = parent
        self.model_ = OutputTreeModel(
            "Gudrun", parent=self
        )
        self.setModel(self.model_)

        self.model().setOutput(output, gudrunFile)

        self.setCurrentIndex(self.model().index(0, 0))
        self.setHeaderHidden(True)
        self.expandAll()

    def currentChanged(self, current, previous):
        if current.internalPointer():
            self.parent.widget.outputTextEdit.setText(
                current.internalPointer().data()
            )
        return super().currentChanged(current, previous)
