from PySide6 import QtWidgets, QtCore
import os


class SampleWidget(QtWidgets.QWidget):
    def __init__(self, parent, sample):
        super().__init__(parent)
        self.sample = sample
        self.runSample: bool = True
        self.initUI()

    def initUI(self):
        layout = QtWidgets.QGridLayout()

        self.sampleNameLabel = QtWidgets.QLabel(self.sample.name, self)
        layout.addWidget(self.sampleNameLabel, 0, 0)

        self.checkBox = QtWidgets.QCheckBox("Optimise", self)
        self.checkBox.setChecked(True)
        self.checkBox.stateChanged.connect(self.checkChanged)
        layout.addWidget(self.checkBox, 0, 1)

        self.lineEdit = QtWidgets.QLineEdit(self)
        self.lineEdit.editingFinished.connect(self.checkFile)
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
            print("TEXT ", self.lineEdit.text())
            self.sample.referenceDataFile = self.lineEdit.text()


class OptimiseResultsModel(QtCore.QAbstractTableModel):
    def __init__(self, headings):
        super().__init__()
        self.samples = []
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
        bottomRight = self.createIndex(len(self.samples), len(self.headings))
        self.dataChanged.emit(self.createIndex(0, 0), bottomRight)


class OptimiseExponents(QtWidgets.QGroupBox):
    class OptimiseExponentsResultsModel(OptimiseResultsModel):
        def __init__(self):
            super().__init__(("Sample", "Initial MSE", "Final MSE",
                             "Optimim Paramaters"))

        def data(self, index: QtCore.QModelIndex, role: int):
            if role == QtCore.Qt.DisplayRole:
                if index.column() == 0:
                    return self.samples[index.row()].name
                if index.column() == 1:
                    return self.samples[index.row()].mse
                if index.column() == 2:
                    return "e"
                if index.column() == 3:
                    return "F"

    def __init__(self, parent=None):
        super().__init__(parent, title="Optimise Exponential Subtractions")
        self.exponentialLayout = QtWidgets.QVBoxLayout()

        self.chooseIterations = QtWidgets.QHBoxLayout()
        self.iterationsSpinbox = QtWidgets.QSpinBox()
        self.chooseIterations.addWidget(
            QtWidgets.QLabel("Number of iterations"))
        self.chooseIterations.addWidget(self.iterationsSpinbox)

        self.optionsLayout = QtWidgets.QHBoxLayout()
        self.resultsLayout = QtWidgets.QVBoxLayout()

        self.resultsTable = QtWidgets.QTableView()
        self.resultsModel = self.OptimiseExponentsResultsModel()

        self.resultsTable.setModel(self.resultsModel)
        self.resultsTable.verticalHeader().hide()
        self.resultsTable.horizontalHeader().setSectionResizeMode(
            QtWidgets.QHeaderView.ResizeMode.ResizeToContents
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

        self.options = QtWidgets.QVBoxLayout()

        self.nIterationsSpinBox = QtWidgets.QSpinBox()
        self.nIterationsSpinBox.setValue(15)
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
                    return self.samples[index.row()].mse
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
    def __init__(self, parent=None):
        super().__init__(parent)
        self._parent = parent
        self.sampleWidgets = []
        self.mainLayout = QtWidgets.QVBoxLayout()

        self.sampleGroupBox = QtWidgets.QGroupBox(
            title="Sample Reference Files")
        self.sampleLayout = QtWidgets.QGridLayout()
        self.sampleGroupBox.setLayout(self.sampleLayout)

        self.optimiseOptionsLayout = QtWidgets.QHBoxLayout()
        self.exponentialGroupBox = OptimiseExponents(self)

        self.mainLayout.addWidget(self.sampleGroupBox)

        self.inelasticityGroupBox = OptimiseInelasticity(self._parent)

        self.optimiseOptionsLayout.addWidget(self.exponentialGroupBox)
        self.optimiseOptionsLayout.addWidget(self.inelasticityGroupBox)
        self.mainLayout.addItem(self.optimiseOptionsLayout)

        self.setLayout(self.mainLayout)

    def setSamples(self, samples):
        self.inelasticityGroupBox.setSamples(samples)
        self.exponentialGroupBox.setSamples(samples)

        for i, sample in enumerate(samples):
            samplewidget = SampleWidget(self, sample)
            self.sampleWidgets.append(samplewidget)
            self.sampleLayout.addWidget(samplewidget.sampleNameLabel, i, 0)
            self.sampleLayout.addWidget(samplewidget.checkBox, i, 1)
            self.sampleLayout.addWidget(samplewidget.lineEdit, i, 2)
            self.sampleLayout.addWidget(samplewidget.browseButton, i, 3)

        if not self._parent.widgetsRefreshing:
            self._parent.setModified()
