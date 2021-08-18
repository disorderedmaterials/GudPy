from PyQt5.QtCore import QAbstractItemModel, QModelIndex
from gudrun_classes.gudrun_file import GudrunFile, PurgeFile
from PyQt5.QtWidgets import QAction, QHBoxLayout, QMainWindow, QMenu, QStackedWidget,QTabWidget, QVBoxLayout, QWidget
from PyQt5.QtGui import QResizeEvent
from widgets.gudpy_tree import GudPyTreeView
from widgets.view_input import ViewInput
from widgets.sample_widget import SampleWidget
from widgets.instrument_widget import InstrumentWidget
from widgets.beam_widget import BeamWidget
from widgets.sample_background_widget import SampleBackgroundWidget
from widgets.container_widget import ContainerWidget
from widgets.normalisation_widget import NormalisationWidget

class GudPyMainWindow(QMainWindow):
    def __init__(self):
        super(GudPyMainWindow, self).__init__()

        self.setGeometry(0, 0, 1366, 768)
        self.setMinimumHeight(1366)
        self.setMinimumWidth(768)
        self.setWindowTitle("GudPy")
        self.show()
        self.initComponents()

    def initComponents(self):
        self.gudrunFile = GudrunFile("tests/TestData/NIMROD-water/water.txt")
        self.objectTree = GudPyTreeView(self, self.gudrunFile)

        leftLayout = QVBoxLayout()
        leftLayout.addWidget(self.objectTree)
        leftLayout.addStretch(5)
        leftWidget = QWidget()
        # leftWidget.setMaximumSize(self.size().width()*0.2, self.size().height()*0.3)
        leftWidget.setLayout(leftLayout)
        # centralWidget = InstrumentWidget(self.gudrunFile.instrument, self)
        self.stack = QStackedWidget(self)
        instrumentWidget = InstrumentWidget(self.gudrunFile.instrument, self)
        beamWidget = BeamWidget(self.gudrunFile.beam, self)
        normalisationWidget = NormalisationWidget(self.gudrunFile.normalisation, self)
        self.stack.addWidget(instrumentWidget)
        self.stack.addWidget(beamWidget)
        self.stack.addWidget(normalisationWidget)

        for sampleBackground in self.gudrunFile.sampleBackgrounds:
            sampleBackgroundWidget = SampleBackgroundWidget(sampleBackground, self)
            self.stack.addWidget(sampleBackgroundWidget)

            for sample in sampleBackground.samples:
                sampleWidget = SampleWidget(sample, self)
                self.stack.addWidget(sampleWidget)

                for container in sample.containers:
                    containerWidget = ContainerWidget(container, self)
                    self.stack.addWidget(containerWidget)


        mainLayout = QHBoxLayout()
        mainLayout.addWidget(leftWidget, 20)
        mainLayout.addWidget(self.stack, 80)
        mainWidget = QWidget()
        mainWidget.setLayout(mainLayout)
        self.setCentralWidget(mainWidget)

        menuBar = self.menuBar()
        menuBar.setNativeMenuBar(False)
        runMenu = QMenu("&Run", menuBar)
        writePurgeFile = QAction("Write Purge File", runMenu)
        runPurge = QAction("Run Purge", runMenu)
        runGudrun = QAction("Run Gudrun", runMenu)
        iterateGudrun = QAction("Iterate Gudrun", runMenu)
        runMenu.addAction(writePurgeFile)
        runMenu.addAction(runPurge)
        runMenu.addAction(runGudrun)
        runMenu.addAction(iterateGudrun)
        writePurgeFile.triggered.connect(lambda : PurgeFile(self.gudrunFile).write_out())
        runPurge.triggered.connect(lambda : PurgeFile(self.gudrunFile).purge())
        runGudrun.triggered.connect(lambda : self.gudrunFile.dcs())
        menuBar.addMenu(runMenu)

        loadMenu = QMenu("&Load", menuBar)
        loadFile = QAction("Load Input File", loadMenu)
        loadConfiguration = QAction("Load Configuration", loadMenu)
        loadMenu.addAction(loadFile)
        loadMenu.addAction(loadConfiguration)
        menuBar.addMenu(loadMenu)

        plotMenu = QMenu("&Plot", menuBar)
        menuBar.addMenu(plotMenu)

        viewMenu = QMenu("&View", menuBar)
        viewInputFile = QAction("View input file", viewMenu)
        viewMenu.addAction(viewInputFile)
        viewInputFile.triggered.connect(lambda : ViewInput(self.gudrunFile, parent=self))
        menuBar.addMenu(viewMenu)

        self.setMenuBar(menuBar)

    def updateFromFile(self):
        self.initComponents()

    def resizeEvent(self, a0: QResizeEvent) -> None:

        super().resizeEvent(a0)
        # for child in self.findChildren((GudrunFileTextArea, InstrumentPane, BeamPane)):
        #     child.updateArea()
