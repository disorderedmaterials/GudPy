from PySide6 import QtWidgets, QtCore
import os
import shutil

from core import utils
import core.optimise as opt


class SampleWidget(QtWidgets.QWidget):
    refDataSet = QtCore.Signal(int)

    def __init__(self, parent, sample):
        super().__init__(parent)
        self._parent = parent
        self.sample = sample
        self.runSample: bool = False
        self.initUI()

    def initUI(self):
        layout = QtWidgets.QHBoxLayout()

        self.sampleNameLabel = QtWidgets.QLabel(self.sample.name, self)
        layout.addWidget(self.sampleNameLabel)

        self.checkBox = QtWidgets.QCheckBox("Optimise", self)
        self.checkBox.setChecked(False)
        self.checkBox.stateChanged.connect(self.checkChanged)
        layout.addWidget(self.checkBox)

        self.lineEdit = QtWidgets.QLineEdit(self)
        self.lineEdit.editingFinished.connect(self.checkFile)
        if self.sample.referenceDataFile:
            self.lineEdit.setText(self.sample.referenceDataFile)
            self.checkBox.setChecked(True)
            self.runSample = True
        layout.addWidget(self.lineEdit)

        self.browseButton = QtWidgets.QPushButton("Browse", self)
        self.browseButton.clicked.connect(self.browseFiles)
        layout.addWidget(self.browseButton)
        self.setLayout(layout)

    def checkChanged(self):
        self.runSample = self.checkBox.isChecked()

    def browseFiles(self):
        filepath, _ = QtWidgets.QFileDialog.getOpenFileName(
            self,
            "Select reference data (.r)",
            filter="*.r")
        if filepath:
            self.lineEdit.setText(filepath)
        self.checkFile()

    def checkFile(self):
        if not os.path.exists(self.lineEdit.text()):
            if self.runSample:
                self.sampleNameLabel.setStyleSheet("color: darkRed;")
            else:
                self.sampleNameLabel.setStyleSheet("")
            self.sample.referenceDataFile = ""
        else:
            self.lineEdit.setStyleSheet("")
            self.sample.referenceDataFile = self.lineEdit.text()
            self.refDataSet.emit(1)


class OptimiseResultsModel(QtCore.QAbstractTableModel):
    def __init__(self, headings):
        super().__init__()
        self.samples = []
        self.initSamples = []
        self.headings = headings
        self.dataFn = None

    def rowCount(
            self, parent: QtCore.QModelIndex) -> int:
        return len(self.initSamples)

    def columnCount(self, parent: QtCore.QModelIndex) -> int:
        return len(self.headings)

    def headerData(self, section: int, orientation: QtCore.Qt.Orientation,
                   role: int = ...) -> QtWidgets:
        if role == QtCore.Qt.DisplayRole:
            if orientation == QtCore.Qt.Horizontal:
                return self.headings[section]
            else:
                return ""

    def setSamples(self, initSamples):
        self.initSamples = initSamples
        bottomRight = self.createIndex(len(self.samples), len(self.headings))
        self.dataChanged.emit(self.createIndex(0, 0), bottomRight)

    def setResults(self, resultSamples):
        self.samples = []
        for s in self.initSamples:
            for rs in resultSamples:
                if rs.name == s.name:
                    self.samples.append(rs)

    def refresh(self):
        bottomRight = self.createIndex(len(self.samples), len(self.headings))
        self.dataChanged.emit(self.createIndex(0, 0), bottomRight)

    def round(self, val, precision):
        try:
            return round(val, precision)
        except TypeError:
            return "-"


class OptimiseExponents(QtWidgets.QGroupBox):
    class OptimiseExponentsResultsModel(OptimiseResultsModel):
        def __init__(self, limitSpinBox):
            super().__init__(("Sample", "Initial MSE", "Final MSE",
                             "Optimum Parameters"))
            self.limitSpinBox = limitSpinBox

        def data(self, index: QtCore.QModelIndex, role: int):
            if role == QtCore.Qt.DisplayRole:
                if index.column() == 0:
                    return self.initSamples[index.row()].name
                if index.column() == 1:
                    if not self.initSamples[index.row()].mse(
                            self.limitSpinBox.value()):
                        return "-"
                    return str(self.round(self.initSamples[index.row()].mse(
                        self.limitSpinBox.value()), 5))
                if index.column() == 2:
                    if not self.samples:
                        return "-"
                    if not self.samples[index.row()].mse(
                            self.limitSpinBox.value()):
                        return "-"
                    return str(self.round(self.samples[index.row()].mse(
                        self.limitSpinBox.value()), 5))
                if index.column() == 3:
                    rounded = ""
                    samples = (self.samples if self.samples
                               else self.initSamples)
                    for set in samples[index.row()].exponentialValues:
                        roundedSet = [self.round(v, 3) for v in set]
                        if rounded:
                            rounded += ", "
                        rounded += str(roundedSet)
                    return rounded

    def __init__(self, parent=None):
        super().__init__(parent, title="Optimise Exponential Subtractions")
        self.exponentialLayout = QtWidgets.QVBoxLayout()

        self.optionsLayout = QtWidgets.QHBoxLayout()
        self.options = QtWidgets.QVBoxLayout()

        self.nIterationsSpinBox = QtWidgets.QSpinBox()
        self.nIterationsSpinBox.setValue(15)
        self.nIterationsSpinBox.setMinimum(10)
        self.nIterationsSpinBox.setSizePolicy(
            QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        self.nIterationsSpinBox.setMinimumWidth(100)

        self.options.addWidget(QtWidgets.QLabel(text="Iterations"))
        self.options.addWidget(self.nIterationsSpinBox)

        self.limitSpinBox = QtWidgets.QDoubleSpinBox()
        self.limitSpinBox.setValue(0.5)
        self.limitSpinBox.setSizePolicy(
            QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        self.nIterationsSpinBox.setMinimumWidth(100)

        self.options.addWidget(QtWidgets.QLabel(text="Q Limit"))
        self.options.addWidget(self.limitSpinBox)
        self.options.addItem(QtWidgets.QSpacerItem(
            0, 0, QtWidgets.QSizePolicy.Minimum,
            QtWidgets.QSizePolicy.Expanding))
        self.options.setContentsMargins(10, 0, 0, 0)

        self.resultsLayout = QtWidgets.QVBoxLayout()

        self.resultsTable = QtWidgets.QTableView()
        self.resultsModel = self.OptimiseExponentsResultsModel(
            self.limitSpinBox)
        self.resultsTable.setModel(self.resultsModel)
        self.resultsModel.dataChanged.connect(self.resultsTable.update)
        self.resultsTable.verticalHeader().hide()
        self.resultsTable.horizontalHeader().setSectionResizeMode(
            QtWidgets.QHeaderView.ResizeMode.Stretch
        )
        self.resultsTable.setSizePolicy(
            QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Preferred)
        self.resultsLayout.addWidget(self.resultsTable)

        self.buttonLayout = QtWidgets.QHBoxLayout()
        self.runOptimiseExponents = QtWidgets.QPushButton("Run")

        self.setParamsButton = QtWidgets.QPushButton("Set new parameters")
        self.setParamsButton.setEnabled(False)

        self.exportDataButton = QtWidgets.QPushButton("Export Data")
        self.exportDataButton.setEnabled(False)
        self.exportDataButton.clicked.connect(self.exportData)

        self.buttonLayout.addWidget(self.runOptimiseExponents)
        self.buttonLayout.addItem(QtWidgets.QSpacerItem(
            0, 0, QtWidgets.QSizePolicy.Expanding,
            QtWidgets.QSizePolicy.Minimum))
        self.buttonLayout.addWidget(self.setParamsButton)
        self.buttonLayout.addWidget(self.exportDataButton)
        self.resultsLayout.addItem(self.buttonLayout)
        self.optionsLayout.addItem(self.resultsLayout)

        self.optionsLayout.addItem(self.options)

        self.exponentialLayout.addItem(self.optionsLayout)

        self.setLayout(self.exponentialLayout)

    def setSamples(self, samples):
        self.resultsModel.setSamples(samples)
        self.resultsModel.refresh()

    def setResults(self, resultSamples):
        self.resultsModel.setResults(resultSamples)
        self.resultsModel.refresh()
        self.setParamsButton.setEnabled(True)
        self.exportDataButton.setEnabled(True)

    def setParameters(self, gudrunFile):
        for optSample in self.resultsModel.samples:
            for sample in gudrunFile.samples():
                if optSample.name == sample.name:
                    sample.exponentialValues = optSample.exponentialValues
        message = QtWidgets.QMessageBox()
        message.setWindowTitle("GudPy Info")
        message.setText(
            "New parameters applied to the samples. " +
            "Run Gudrun to apply the changes.")
        message.exec()

    def exportData(self):
        dirname, _ = QtWidgets.QFileDialog.getSaveFileName(
            caption="Export mint files to...",
        )
        if not dirname:
            return False
        utils.makeDir(dirname)
        for sample in self.resultsModel.samples:
            mintFile = sample.dataFiles[0].mintFile
            shutil.copyfile(mintFile, os.path.join(
                dirname, os.path.basename(mintFile)))


class OptimiseInelasticity(QtWidgets.QGroupBox):
    class OptimiseInelasticityResultsModel(OptimiseResultsModel):
        def __init__(self):
            super().__init__(("Sample", "Initial MSE",
                              "Final MSE", "Optimum iterations"))
            self.results = {}

        def data(self, index: QtCore.QModelIndex, role: int):
            if role == QtCore.Qt.DisplayRole:
                sample = self.initSamples[index.row()]
                if index.column() == 0:
                    return sample.name
                if index.column() == 1:
                    if not sample.mse():
                        return "-"
                    return str(self.round(sample.mse(), 5))
                if index.column() == 2:
                    if not self.results.get(sample.name, None):
                        if not sample.mse():
                            return "-"
                        return str(self.round(sample.mse(), 5))
                    bestSamp = self.results[sample.name]["bestSample"]
                    return str(self.round(bestSamp.mse(), 5))
                if index.column() == 3:
                    if not self.results.get(sample.name, None):
                        return "-"

                    return (self.results[
                        self.samples[index.row()].name]["bestIt"]
                        if self.results else "-")

    def __init__(self, parent=None):
        super().__init__(parent, title="Optimise Inelasticity Subtractions")
        self._parent = parent
        self.results = {}
        self.inelasticityLayout = QtWidgets.QVBoxLayout()

        self.resultsLayout = QtWidgets.QHBoxLayout()

        self.resultsTable = QtWidgets.QTableView()

        self.resultsModel = self.OptimiseInelasticityResultsModel()
        self.resultsTable.setModel(self.resultsModel)
        self.resultsModel.dataChanged.connect(self.resultsTable.update)
        self.resultsTable.horizontalHeader().setSectionResizeMode(
            QtWidgets.QHeaderView.ResizeMode.ResizeToContents
        )
        self.resultsTable.verticalHeader().hide()
        self.resultsTable.horizontalHeader().setSectionResizeMode(
            QtWidgets.QHeaderView.ResizeMode.Stretch
        )
        self.resultsTable.setSizePolicy(
            QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        self.resultsLayout.addWidget(self.resultsTable)
        self.inelasticityLayout.addItem(self.resultsLayout)

        self.buttonLayout = QtWidgets.QHBoxLayout()
        self.runInelasticityButton = QtWidgets.QPushButton("Run")
        self.exportDataButton = QtWidgets.QPushButton("Export Data")
        self.exportDataButton.clicked.connect(self.exportData)
        self.exportDataButton.setEnabled(False)
        self.buttonLayout.addWidget(self.runInelasticityButton)
        self.buttonLayout.addItem(QtWidgets.QSpacerItem(
            0, 0, QtWidgets.QSizePolicy.Expanding,
            QtWidgets.QSizePolicy.Minimum))
        self.buttonLayout.addWidget(self.exportDataButton)

        self.inelasticityLayout.addItem(self.buttonLayout)
        self.setLayout(self.inelasticityLayout)

    def setSamples(self, samples):
        self.resultsModel.setSamples(samples)
        self.resultsModel.refresh()

    def setResults(self, resultSamples, results: dict):
        self.resultsModel.setResults(resultSamples)
        self.resultsModel.results = results
        self.resultsModel.refresh()
        self.exportDataButton.setEnabled(True)

    def exportData(self):
        dirname, _ = QtWidgets.QFileDialog.getSaveFileName(
            caption="Export mint files to...",
        )
        if not dirname:
            return False
        utils.makeDir(dirname)

        for sample in self.resultsModel.samples:
            mintFile = None
            optSample = self.results.get(sample.name, None)
            if not optSample:
                mintFile = sample.dataFiles[0].mintFile
            else:
                mintFile = optSample["bestSample"].mintFile
            shutil.copyfile(mintFile, os.path.join(
                dirname, os.path.basename(mintFile)))


class OptimiseTab(QtWidgets.QWidget):
    runOptimiseExponents = QtCore.Signal(int)
    runOptimiseInelasticity = QtCore.Signal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._parent = parent
        self.samples = []
        self.sampleWidgets = {}
        self.mainLayout = QtWidgets.QVBoxLayout()

        self.sampleGroupBox = QtWidgets.QGroupBox(
            title="Sample Reference Files")
        self.sampleLayout = QtWidgets.QVBoxLayout()
        self.sampleLayout.setSpacing(1)
        self.sampleGroupBox.setLayout(self.sampleLayout)

        self.optimiseOptionsLayout = QtWidgets.QVBoxLayout()
        self.exponentialGroupBox = OptimiseExponents(self)
        self.exponentialGroupBox.runOptimiseExponents.clicked.connect(
            self.handleOptimiseExponentsButton
        )

        self.mainLayout.addWidget(self.sampleGroupBox)

        self.inelasticityGroupBox = OptimiseInelasticity(self._parent)
        self.inelasticityGroupBox.runInelasticityButton.clicked.connect(
            self.handleOptimiseInelasticityButton
        )

        self.optimiseOptionsLayout.addWidget(self.exponentialGroupBox)
        self.optimiseOptionsLayout.addItem(
            QtWidgets.QSpacerItem(
                0, 20, QtWidgets.QSizePolicy.Expanding,
                QtWidgets.QSizePolicy.Preferred)
        )
        self.optimiseOptionsLayout.addWidget(self.inelasticityGroupBox)
        self.mainLayout.addItem(self.optimiseOptionsLayout)

        self.setLayout(self.mainLayout)

    def refreshWidgets(self):
        self.exponentialGroupBox.resultsModel.refresh()
        self.inelasticityGroupBox.resultsModel.refresh()

    def setSamples(self, samples):
        self.inelasticityGroupBox.setSamples(samples)
        self.exponentialGroupBox.setSamples(samples)

        if samples == self.samples:
            return

        self.samples = samples

        while self.sampleLayout.count():
            item = self.sampleLayout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()

        for sample in samples:
            sampleWidget = self.sampleWidgets.get(sample.name)
            if not sampleWidget:
                sampleWidget = SampleWidget(self._parent, sample)
                sampleWidget.refDataSet.connect(
                    lambda: (
                        self.exponentialGroupBox.resultsModel.setSamples(
                            self.samples)))
                sampleWidget.refDataSet.connect(
                    lambda: (
                        self.inelasticityGroupBox.resultsModel.setSamples(
                            self.samples)))
            self.sampleWidgets[sample.name] = sampleWidget
            self.sampleLayout.addWidget(sampleWidget)

        for sname in self.sampleWidgets.keys():
            if sname not in [s.name for s in samples]:
                self.sampleWidgets.pop(sname, None)

        if not self._parent.widgetsRefreshing:
            self._parent.setModified()

    def setResults(self, samples, optimiser):
        self.exponentialGroupBox.setResults(samples)

        if isinstance(optimiser, opt.InelasticityOptimisation):
            self.inelasticityGroupBox.setResults(samples, optimiser.results)

        if not self._parent.widgetsRefreshing:
            self._parent.setModified()

    def validateRun(self):
        sampleSelected = False
        for sw in self.sampleWidgets.values():
            if sw.runSample:
                sampleSelected = True
                if not sw.sample.referenceDataFile:
                    self._parent.sendError(
                        f"Reference data not provided for {sw.sample.name}"
                    )
                    return False
                if (not sw.sample.dataFiles or
                        not sw.sample.dataFiles[0].mintFile):
                    self._parent.sendError(
                        "Please run Gudrun before optimising."
                    )
                    return False
        if not sampleSelected:
            self._parent.sendError(
                "No samples selected"
            )
            return False
        return True

    def handleOptimiseExponentsButton(self):
        if self.validateRun():
            self.runOptimiseExponents.emit(1)

    def handleOptimiseInelasticityButton(self):
        if self.validateRun():
            self.runOptimiseInelasticity.emit(1)
