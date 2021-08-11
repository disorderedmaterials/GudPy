from PyQt5.QtCore import QWaitCondition, left, right
from gudrun_classes.gudrun_file import GudrunFile
from widgets.instrument_pane import InstrumentPane
from widgets.beam_pane import BeamPane
from PyQt5.QtWidgets import QHBoxLayout, QMainWindow, QPushButton, QTabWidget, QVBoxLayout, QWidget
from PyQt5.QtGui import QResizeEvent
from widgets.gudrun_file_text_area import GudrunFileTextArea


class GudPyMainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setGeometry(0, 0, 800, 600)
        self.setMinimumHeight(800)
        self.setMinimumWidth(600)
        self.setWindowTitle("GudPy")
        self.show()
        self.initComponents()

    def initComponents(self):

        rightWidget = GudrunFileTextArea(self, 1, 0.2)
        self.gudrunFile = rightWidget.getGudrunFile()


        self.instrumentButton = QPushButton("INSTRUMENT", self)
        self.beamButton = QPushButton("BEAM", self)
        self.normalisationButton = QPushButton("NORMALISATION", self)

        leftLayout = QVBoxLayout()
        leftLayout.addWidget(self.instrumentButton)
        leftLayout.addWidget(self.beamButton)
        leftLayout.addWidget(self.normalisationButton)
        leftLayout.addStretch(5)
        leftLayout.setSpacing(20)

        if self.gudrunFile:
            self.sampleBackgroundButtons = {}
            self.sampleButtons = {}
            self.containerButtons = {}
            sampleBackgrounds = self.gudrunFile.sampleBackgrounds

            leftLayout = QVBoxLayout()

            for i, sampleBackground in enumerate(sampleBackgrounds):
                sampleBackgroundButton = QPushButton("SAMPLE BACKGROUND", self)
                self.sampleBackgroundButtons[sampleBackgroundButton] = (
                    [i, self.gudrunFile.sampleBackgrounds[i]]
                )
                leftLayout.addWidget(sampleBackgroundButton)
                for j, sample in enumerate(sampleBackground.samples):
                    sampleButton = QPushButton(sample.name, self)
                    leftLayout.addWidget(sampleButton)
                    if sample.runThisSample:
                        sampleButton.setStyleSheet("background-color : green")
                    else:
                        sampleButton.setStyleSheet("background-color : red")

                    self.sampleButtons[sampleButton] = (
                        [
                            i,
                            j,
                            self.gudrunFile.sampleBackgrounds[i].samples[j]
                        ]
                    )
                    for k, container in enumerate(sample.containers):
                        containerButton = QPushButton(container.name, self)
                        leftLayout.addWidget(containerButton)
                        self.containerButtons[containerButton] = (
                            [
                                i,
                                j,
                                k,
                                (
                                    self.gudrunFile.sampleBackgrounds[i]
                                    .samples[j].
                                    containers[k]
                                )
                            ]
                        )

        leftWidget = QWidget()
        leftWidget.setLayout(leftLayout)

        centralWidget = QTabWidget()



        mainLayout = QHBoxLayout()
        mainLayout.addWidget(leftWidget)
        mainLayout.addWidget(centralWidget)
        mainLayout.addWidget(rightWidget)
        mainWidget = QWidget()
        mainWidget.setLayout(mainLayout)
        self.setCentralWidget(mainWidget)

    def resizeEvent(self, a0: QResizeEvent) -> None:

        super().resizeEvent(a0)
        for child in self.findChildren((GudrunFileTextArea, InstrumentPane, BeamPane)):
            child.updateArea()
