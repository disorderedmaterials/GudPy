from PySide6 import QtWidgets


class SampleWidget(QtWidgets.QWidget):
    def __init__(self, parent, sample):
        super().__init__(parent)
        self.sample = sample
        self.initUI()

    def initUI(self):
        layout = QtWidgets.QGridLayout()

        self.sampleNameLabel = QtWidgets.QLabel(self.sample.name, self)
        layout.addWidget(self.sampleNameLabel, 0, 0)

        self.checkBox = QtWidgets.QCheckBox("Optimise", self)
        self.checkBox.setChecked(False)
        layout.addWidget(self.checkBox, 0, 1)

        self.lineEdit = QtWidgets.QLineEdit(self)
        layout.addWidget(self.lineEdit, 0, 2)

        self.browseButton = QtWidgets.QPushButton("Browse", self)
        self.browseButton.clicked.connect(self.browseFiles)
        layout.addWidget(self.browseButton, 0, 3)

        self.setLayout(layout)

    def browseFiles(self):
        filedialog = QtWidgets.QFileDialog()
        filepath, _ = filedialog.getOpenFileName()
        if filepath:
            self.lineEdit.setText(filepath)


class OptimiseExponents(QtWidgets.QGroupBox):
    def __init__(self, parent=None):
        super().__init__(parent, title="Optimise Exponential Subtractions")
        self.exponentialLayout = QtWidgets.QVBoxLayout()

        self.chooseIterations = QtWidgets.QHBoxLayout()
        self.iterationsSpinbox = QtWidgets.QSpinBox()
        self.chooseIterations.addWidget(
            QtWidgets.QLabel("Number of iterations"))
        self.chooseIterations.addWidget(self.iterationsSpinbox)

        self.runButton = QtWidgets.QPushButton("Run")

        self.setLayout(self.exponentialLayout)


class OptimiseTab(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._parent = parent
        self.mainLayout = QtWidgets.QVBoxLayout()

        self.sampleGroupBox = QtWidgets.QGroupBox(
            title="Sample Reference Files")
        self.sampleLayout = QtWidgets.QGridLayout()
        self.sampleGroupBox.setLayout(self.sampleLayout)

        self.optimiseOptionsLayout = QtWidgets.QHBoxLayout()
        self.optimiseExponents = OptimiseExponents(self)

        self.inelasticityGroupBox = QtWidgets.QGroupBox(
            title="Optimise Inelasticity Subtractions")
        self.inelasticityLayout = QtWidgets.QVBoxLayout()
        self.runInelasticityButton = QtWidgets.QPushButton("Run")
        self.inelasticityLayout.addWidget(self.runInelasticityButton)
        self.inelasticityGroupBox.setLayout(self.inelasticityLayout)

        self.mainLayout.addWidget(self.sampleGroupBox)

        self.optimiseOptionsLayout.addWidget(self.exponentialGroupBox)
        self.optimiseOptionsLayout.addWidget(self.inelasticityGroupBox)
        self.mainLayout.addItem(self.optimiseOptionsLayout)

        # self.mainLayout.addItem(QtWidgets.QSpacerItem(
        #    20, 40, QtWidgets.QSizePolicy.Minimum,
        #    QtWidgets.QSizePolicy.Expanding))
        self.setLayout(self.mainLayout)

    def setSamples(self, samples):
        for i, sample in enumerate(samples):
            samplewidget = SampleWidget(self, sample)
            self.sampleLayout.addWidget(samplewidget.sampleNameLabel, i, 0)
            self.sampleLayout.addWidget(samplewidget.checkBox, i, 1)
            self.sampleLayout.addWidget(samplewidget.lineEdit, i, 2)
            self.sampleLayout.addWidget(samplewidget.browseButton, i, 3)

        if not self._parent.widgetsRefreshing:
            self._parent.setModified()
