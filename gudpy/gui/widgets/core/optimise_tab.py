from PySide6 import QtWidgets, QtCore
import os
import copy


class SampleWidget(QtWidgets.QWidget):
    refDataSet = QtCore.Signal(int)

    def __init__(self, parent, sample):
        super().__init__(parent)
        self._parent = parent
        self.sample = sample
        self.runSample: bool = False
        self.initUI()

    def initUI(self):
        layout = QtWidgets.QGridLayout()

        self.sampleNameLabel = QtWidgets.QLabel(self.sample.name, self)
        layout.addWidget(self.sampleNameLabel, 0, 0)

        self.checkBox = QtWidgets.QCheckBox("Optimise", self)
        self.checkBox.setChecked(False)
        self.checkBox.stateChanged.connect(self.checkChanged)
        layout.addWidget(self.checkBox, 0, 1)

        self.lineEdit = QtWidgets.QLineEdit(self)
        self.lineEdit.editingFinished.connect(self.checkFile)
        if self.sample.referenceDataFile:
            self.lineEdit.setText(self.sample.referenceDataFile)
            self.checkBox.setChecked(True)
            self.runSample = True
        layout.addWidget(self.lineEdit, 0, 2)

        self.browseButton = QtWidgets.QPushButton("Browse", self)
        self.browseButton.clicked.connect(self.browseFiles)
        layout.addWidget(self.browseButton, 0, 3)

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
            self.lineEdit.setStyleSheet("color: red;")
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
        return len(self.samples)

    def columnCount(self, parent: QtCore.QModelIndex) -> int:
        return len(self.headings)

    def headerData(self, section: int, orientation: QtCore.Qt.Orientation,
                   role: int = ...) -> QtWidgets:
        if role == QtCore.Qt.DisplayRole:
            if orientation == QtCore.Qt.Horizontal:
                return self.headings[section]
            else:
                return ""

    def setSamples(self, samples):
        self.samples = samples
        self.initSamples = []
        for s in samples:
            self.initSamples.append(copy.deepcopy(s))
        bottomRight = self.createIndex(len(self.samples), len(self.headings))
        self.dataChanged.emit(self.createIndex(0, 0), bottomRight)


class OptimiseExponents(QtWidgets.QGroupBox):
    class OptimiseExponentsResultsModel(OptimiseResultsModel):
        def __init__(self, limitSpinBox):
            super().__init__(("Sample", "Initial MSE", "Final MSE",
                             "Optimum Parameters"))
            self.limitSpinBox = limitSpinBox

        def data(self, index: QtCore.QModelIndex, role: int):
            if role == QtCore.Qt.DisplayRole:
                if index.column() == 0:
                    return self.samples[index.row()].name
                if index.column() == 1:
                    if not self.initSamples[index.row()].mse(
                            self.limitSpinBox.value()):
                        return "-"
                    return str(round(self.initSamples[index.row()].mse(
                        self.limitSpinBox.value()), 5))
                if index.column() == 2:
                    if not self.samples[index.row()].mse(
                            self.limitSpinBox.value()):
                        return "-"
                    return str(round(self.samples[index.row()].mse(
                        self.limitSpinBox.value()), 5))
                if index.column() == 3:
                    rounded = ""
                    for set in self.samples[index.row()].exponentialValues:
                        roundedSet = [round(v, 3) for v in set]
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
        self.resultsTable.verticalHeader().hide()
        self.resultsTable.horizontalHeader().setSectionResizeMode(
            QtWidgets.QHeaderView.ResizeMode.Stretch
        )
        self.resultsTable.setSizePolicy(
            QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Preferred)
        self.resultsLayout.addWidget(self.resultsTable)

        self.buttonLayout = QtWidgets.QHBoxLayout()
        self.runOptimiseExponents = QtWidgets.QPushButton("Run")
        self.exportDataButton = QtWidgets.QPushButton("Export Data")
        self.exportDataButton.setEnabled(False)
        self.buttonLayout.addWidget(self.runOptimiseExponents)
        self.buttonLayout.addItem(QtWidgets.QSpacerItem(
            0, 0, QtWidgets.QSizePolicy.Expanding,
            QtWidgets.QSizePolicy.Minimum))
        self.buttonLayout.addWidget(self.exportDataButton)
        self.resultsLayout.addItem(self.buttonLayout)
        self.optionsLayout.addItem(self.resultsLayout)

        self.optionsLayout.addItem(self.options)

        self.exponentialLayout.addItem(self.optionsLayout)

        self.setLayout(self.exponentialLayout)

    def setSamples(self, samples):
        self.resultsModel.setSamples(samples)


class OptimiseInelasticity(QtWidgets.QGroupBox):
    class OptimiseInelasticityResultsModel(OptimiseResultsModel):
        def __init__(self):
            super().__init__(("Sample", "Initial MSE",
                              "Final MSE", "Optimum iterations"))

        def data(self, index: QtCore.QModelIndex, role: int):
            if role == QtCore.Qt.DisplayRole:
                if index.column() == 0:
                    return self.samples[index.row()].name
                if index.column() == 1:
                    if not self.initSamples[index.row()].mse():
                        return "-"
                    return str(round(self.initSamples[index.row()].mse(), 5))
                if index.column() == 2:
                    return "e"
                if index.column() == 3:
                    return "F"

    def __init__(self, parent=None):
        super().__init__(parent, title="Optimise Inelasticity Subtractions")
        self._parent = parent
        self.inelasticityLayout = QtWidgets.QVBoxLayout()

        self.resultsLayout = QtWidgets.QHBoxLayout()

        self.resultsTable = QtWidgets.QTableView()
        self.resultsModel = self.OptimiseInelasticityResultsModel()
        self.resultsTable.setModel(self.resultsModel)
        self.resultsTable.horizontalHeader().setSectionResizeMode(
            QtWidgets.QHeaderView.ResizeMode.ResizeToContents
        )
        self.resultsTable.verticalHeader().hide()
        self.resultsTable.setSizePolicy(
            QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        self.resultsLayout.addWidget(self.resultsTable)

        self.inelasticityLayout.addItem(self.resultsLayout)

        self.buttonLayout = QtWidgets.QHBoxLayout()
        self.runInelasticityButton = QtWidgets.QPushButton("Run")
        self.exportDataButton = QtWidgets.QPushButton("Export Data")
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


class OptimiseTab(QtWidgets.QWidget):
    runOptimise = QtCore.Signal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._parent = parent
        self.samples = []
        self.sampleWidgets = []
        self.mainLayout = QtWidgets.QVBoxLayout()

        self.sampleGroupBox = QtWidgets.QGroupBox(
            title="Sample Reference Files")
        self.sampleLayout = QtWidgets.QGridLayout()
        self.sampleGroupBox.setLayout(self.sampleLayout)

        self.optimiseOptionsLayout = QtWidgets.QVBoxLayout()
        self.exponentialGroupBox = OptimiseExponents(self)
        self.exponentialGroupBox.runOptimiseExponents.clicked.connect(
            self.validateRun
        )

        self.mainLayout.addWidget(self.sampleGroupBox)

        self.inelasticityGroupBox = OptimiseInelasticity(self._parent)

        self.optimiseOptionsLayout.addWidget(self.exponentialGroupBox)
        self.optimiseOptionsLayout.addItem(
            QtWidgets.QSpacerItem(
                0, 20, QtWidgets.QSizePolicy.Expanding,
                QtWidgets.QSizePolicy.Preferred)
        )
        self.optimiseOptionsLayout.addWidget(self.inelasticityGroupBox)
        self.mainLayout.addItem(self.optimiseOptionsLayout)

        self.setLayout(self.mainLayout)

    def setSamples(self, samples):
        self.samples = samples
        self.inelasticityGroupBox.setSamples(samples)
        self.exponentialGroupBox.setSamples(samples)

        for i, sample in enumerate(samples):
            samplewidget = SampleWidget(self._parent, sample)
            samplewidget.refDataSet.connect(
                lambda: (
                    self.exponentialGroupBox.resultsModel.setSamples(
                        self.samples)))
            samplewidget.refDataSet.connect(
                lambda: (
                    self.inelasticityGroupBox.resultsModel.setSamples(
                        self.samples)))
            self.sampleWidgets.append(samplewidget)
            self.sampleLayout.addWidget(samplewidget.sampleNameLabel, i, 0)
            self.sampleLayout.addWidget(samplewidget.checkBox, i, 1)
            self.sampleLayout.addWidget(samplewidget.lineEdit, i, 2)
            self.sampleLayout.addWidget(samplewidget.browseButton, i, 3)

        if not self._parent.widgetsRefreshing:
            self._parent.setModified()

    def validateRun(self):
        for sw in self.sampleWidgets:
            if sw.runSample:
                if not sw.sample.referenceDataFile:
                    self._parent.sendError(
                        f"Reference data not provided for {sw.sample.name}"
                    )
                    return
        self.runOptimise.emit(1)
