from copy import deepcopy
from PySide6.QtWidgets import QTreeView
from PySide6.QtCore import (
    QAbstractItemModel,
    QModelIndex,
    QPersistentModelIndex,
    Qt
)

from core.gudpy_data import GudrunParameters
from core.instrument import Instrument
from core.sample import Sample


class OutputTreeModel(QAbstractItemModel):

    def __init__(self, output, gudrunParams, keyMap=None, parent=None):
        super().__init__(parent)
        if isinstance(output, str):
            output = {0: output}
        self.keyMap = keyMap
        self.output = output
        self.params = gudrunParams
        self.map = {}
        self.refs = []
        self.data_ = {}

        for idx, key in enumerate(output.keys()):
            self.data_[idx] = {
                "name": key,
                "outputs": []
            }

        self.persistentIndexes = {}
        self.setupData()

    def setupData(self):
        for idx, [name, output] in enumerate(self.output.items()):
            gf = deepcopy(self.params)
            gf.name = name
            gf.output = output
            self.refs.append(gf)
            # Indexes for each sample background
            offsets = [
                n for n, l in
                enumerate(output.splitlines(keepends=True))
                if "Got to: SAMPLE BACKGROUND" in l
            ]

            if not offsets:
                i = deepcopy(self.params.instrument)
                i.output = output
                i.name = "General"
                self.data_[idx]["outputs"].append(i)
                return

            sbindicies = []
            for i in range(len(offsets) - 1):
                sbindicies.append([offsets[i], offsets[i + 1] - 1])

            sbindicies.append(
                [
                    offsets[-1], len(output.splitlines(keepends=True))
                ]
            )

            instrument = deepcopy(self.params.instrument)
            instrument.output = "".join(
                output.splitlines(keepends=True)
                [0: sbindicies[0][0]]
            )
            instrument.name = "General"
            self.data_[idx]["outputs"].append(instrument)
            prev = None
            for start, end in sbindicies:
                splicedOutput = (
                    output.splitlines(keepends=True)[start:end]
                )
                indices = [
                    n for n, l in
                    enumerate(splicedOutput) if "Got to: SAMPLE" in l
                ][1:]
                for sample, index in zip(
                    [
                        s for sb in
                        self.params.sampleBackgrounds
                        for s in sb.samples
                        if s.runThisSample
                    ], indices
                ):
                    s = deepcopy(sample)
                    s.output = index + start

                    # If iterator output
                    if len(self.data_.keys()) != 1:
                        if prev:
                            prev.output = "".join(
                                output.splitlines(keepends=True)
                                [prev.output:index + start - 1]
                            )

                    prev = s
                    self.data_[idx]["outputs"].append(s)
                if prev:
                    prev.output = "".join(
                        output.splitlines(keepends=True)
                        [prev.output:end]
                    )

    def index(self, row, column, parent=QModelIndex()):
        # Check for invalid index.
        if not self.hasIndex(row, column, parent):
            return QModelIndex()
        elif not parent.isValid():
            if len(self.data_.keys()) == 1:
                obj = self.data_[0]["outputs"][row]
            elif len(self.data_.keys()) > 1:
                try:
                    obj = self.refs[row]
                except IndexError:
                    return QModelIndex()
            else:
                return QModelIndex()
        elif parent.isValid():
            obj = self.data_[
                self.refs.index(
                    parent.internalPointer())]["outputs"][row]
        index = self.createIndex(row, 0, obj)
        self.persistentIndexes[obj] = QPersistentModelIndex(index)
        return index

    def findParent(self, obj):
        for parent, items in self.data_.items():
            if obj in items["outputs"]:
                return self.refs[parent]

    def parent(self, index):
        if not index.isValid():
            return QModelIndex()
        if isinstance(index.internalPointer(), GudrunParameters):
            return QModelIndex()
        elif isinstance(index.internalPointer(), (Instrument, Sample)):
            if len(self.data_.keys()) > 1:
                parent = self.findParent(index.internalPointer())
                return QModelIndex(self.persistentIndexes[parent])
            else:
                return QModelIndex()
        else:
            return QModelIndex()

    def rowCount(self, parent=QModelIndex()):
        if not parent.isValid():
            if len(self.data_.keys()) == 1:
                # get length of first value
                return len(self.data_[0]["outputs"])
            elif len(self.data_.keys()) > 1:
                return len(self.data_.keys())
            else:
                return 0
        parentObj = parent.internalPointer()
        if isinstance(parentObj, GudrunParameters):
            return len(
                self.data_[
                    self.refs.index(
                        parent.internalPointer())]["outputs"]
            )
        else:
            return 0

    def columnCount(self, parent=QModelIndex()):
        return 1

    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid():
            return None
        if role == Qt.DisplayRole or role == Qt.EditRole:
            obj = index.internalPointer()
            if isinstance(obj, GudrunParameters):
                if self.keyMap:
                    return self.keyMap[obj.name]
                else:
                    return obj.name
            elif isinstance(obj, (Instrument, Sample)):
                return obj.name
        else:
            return None


class OutputTreeView(QTreeView):

    def __init__(self, parent):
        super().__init__(parent)

    def buildTree(self, params, output, parent, keyMap=None):
        self.params = params
        self.output = output
        self.parent = parent
        self.keyMap = keyMap
        self.makeModel()
        self.setCurrentIndex(self.model().index(0, 0))
        self.setHeaderHidden(True)
        self.expandAll()

    def makeModel(self):
        self.model_ = OutputTreeModel(
            self.output, self.params,
            keyMap=self.keyMap, parent=self
        )
        self.setModel(self.model_)

    def currentChanged(self, current, previous):
        if current.internalPointer():
            self.parent.widget.outputTextEdit.setText(
                current.internalPointer().output
            )
        return super().currentChanged(current, previous)
