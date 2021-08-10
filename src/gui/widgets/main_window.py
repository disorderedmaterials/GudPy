from widgets.instrument_pane import InstrumentPane
from PyQt5.QtWidgets import QMainWindow, QPushButton
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

    def showInstrumentPane(self):
        if self.instrumentPane.isVisible():
            self.instrumentPane.hide()
            self.instrumentButton.setStyleSheet("")
        else:
            self.instrumentPane.show()
            self.instrumentButton.setStyleSheet("background-color : grey")

    def initComponents(self):
        self.textArea = GudrunFileTextArea(self, 1, 0.3)
        self.gudrunFile = self.textArea.getGudrunFile()
        self.instrumentPane = InstrumentPane(
            self.gudrunFile.instrument, self, 0, 200, 1, 0.5
        )
        if self.gudrunFile:
            self.instrumentButton = QPushButton(self)
            self.instrumentButton.setGeometry(0, 0, 200, 50)
            self.instrumentButton.setText("INSTRUMENT")
            self.instrumentButton.show()
            self.instrumentButton.clicked.connect(self.showInstrumentPane)
            self.beamButton = QPushButton(self)
            self.beamButton.setGeometry(0, 50, 200, 50)
            self.beamButton.setText("BEAM")
            self.beamButton.show()
            self.normalisationButton = QPushButton(self)
            self.normalisationButton.setGeometry(0, 100, 200, 50)
            self.normalisationButton.setText("NORMALISATION")
            self.normalisationButton.show()
            y = 150
            self.sampleBackgroundButtons = {}
            self.sampleButtons = {}
            self.containerButtons = {}
            sampleBackgrounds = self.gudrunFile.sampleBackgrounds
            for i, sampleBackground in enumerate(sampleBackgrounds):
                sampleBackgroundButton = QPushButton(self)
                sampleBackgroundButton.setGeometry(0, y, 200, 50)
                sampleBackgroundButton.setText("SAMPLE BACKGROUND")
                sampleBackgroundButton.show()
                self.sampleBackgroundButtons[sampleBackgroundButton] = (
                    [i, self.gudrunFile.sampleBackgrounds[i]]
                )
                y += 50
                for j, sample in enumerate(sampleBackground.samples):
                    sampleButton = QPushButton(self)
                    sampleButton.setGeometry(0, y, 200, 50)
                    sampleButton.setText(sample.name)
                    sampleButton.show()
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
                    y += 50
                    for k, container in enumerate(sample.containers):
                        containerButton = QPushButton(self)
                        containerButton.setGeometry(0, y, 200, 50)
                        containerButton.setText(container.name)
                        containerButton.show()
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
                        y += 50

    def resizeEvent(self, a0: QResizeEvent) -> None:

        super().resizeEvent(a0)
        for child in self.findChildren((GudrunFileTextArea, InstrumentPane)):
            child.updateArea()
