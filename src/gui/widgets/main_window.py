from os import write
from PyQt5.QtCore import QWaitCondition, left, right
from gudrun_classes.gudrun_file import GudrunFile, PurgeFile
from PyQt5.QtWidgets import QAction, QHBoxLayout, QMainWindow, QMenu, QMenuBar, QPushButton, QTabWidget, QVBoxLayout, QWidget, QTreeView
from PyQt5.QtGui import QResizeEvent, QStandardItemModel, QStandardItem
from widgets.gudpy_tree import GudPyTreeView

class GudPyMainWindow(QMainWindow):
    def __init__(self):
        super(GudPyMainWindow, self).__init__()

        self.setGeometry(0, 0, 800, 600)
        self.setMinimumHeight(800)
        self.setMinimumWidth(600)
        self.setWindowTitle("GudPy")
        self.show()
        self.initComponents()

    def initComponents(self):
        self.gudrunFile = GudrunFile("tests/TestData/NIMROD-water/water.txt")
        self.objectTree = GudPyTreeView(self, self.gudrunFile)
        # self.model = QStandardItemModel()
        # parentItem = self.model.invisibleRootItem()
        # instrumentItem = QStandardItem("Instrument")
        # parentItem.appendRow(instrumentItem)
        # beamItem = QStandardItem("Beam")
        # parentItem.appendRow(beamItem)
        # normalistionItem = QStandardItem("Normalisation")
        # parentItem.appendRow(normalistionItem)
        #
        # for sampleBackground in self.gudrunFile.sampleBackgrounds:
        #     sampleBackgroundItem = QStandardItem("Sample Background")
        #     parentItem.appendRow(sampleBackgroundItem)
        #
        #     for sample in sampleBackground.samples:
        #         sampleItem = QStandardItem(sample.name)
        #         sampleBackgroundItem.appendRow(sampleItem)
        #
        #         for container in sample.containers:
        #             containerItem = QStandardItem(container.name)
        #             sampleItem.appendRow(containerItem)
        #
        #
        #
        # self.objectTree = QTreeView(self)
        # self.objectTree.setModel(self.model)
        # self.objectTree.setHeaderHidden(True)
        leftLayout = QVBoxLayout()
        leftLayout.addWidget(self.objectTree)
        leftLayout.addStretch(5)
        leftWidget = QWidget()
        leftWidget.setLayout(leftLayout)

        centralWidget = QTabWidget()
        mainLayout = QHBoxLayout()
        mainLayout.addWidget(leftWidget)
        mainLayout.addWidget(centralWidget)
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
        # viewInputFile.triggered.connect(lambda : GudrunFileTextArea()

        self.setMenuBar(menuBar)


    def resizeEvent(self, a0: QResizeEvent) -> None:

        super().resizeEvent(a0)
        # for child in self.findChildren((GudrunFileTextArea, InstrumentPane, BeamPane)):
        #     child.updateArea()
