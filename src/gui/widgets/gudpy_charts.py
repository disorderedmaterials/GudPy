import sys
from PySide6.QtCharts import QChart, QChartView, QLineSeries
from PySide6.QtCore import QPointF
from PySide6.QtGui import QPainter
from PySide6.QtWidgets import QApplication, QMainWindow
from enum import Enum
import os

class PlotModes(Enum):
    STRUCTURE_FACTOR = 0

class GudPyChart(QChart):

    def __init__(self, dataFileType, sample=None, samples=[], plotMode=PlotModes.STRUCTURE_FACTOR):
        super(GudPyChart, self).__init__()
        self.plottable = False
        if sample:
            self.plotSample(sample, plotMode, dataFileType)
        elif samples:
            self.plotSamples(samples, plotMode, dataFileType)


    def plotSample(self, sample, plotMode, dataFileType):
        if plotMode == PlotModes.STRUCTURE_FACTOR:
            self.setTitle("Structure Factor")

            mintFile = os.path.join(os.getcwd(), sample.dataFiles.dataFiles[0].replace(dataFileType, "mint01"))
            mdcsFile = os.path.join(os.getcwd(), sample.dataFiles.dataFiles[0].replace(dataFileType, "mdcs01"))
         
            mintSeries = QLineSeries()
            mdcsSeries = QLineSeries()

            if sample.topHatW:
                if os.path.exists(mintFile):
                    mintData = open(mintFile, "r", encoding="utf-8").readlines()[14:]
                    for item in mintData:
                        x, y, err, *_ = item.split()
                        mintSeries.append(float(x), float(y))
                    mintSeries.setName(f"{sample.name} mint01")
                    self.addSeries(mintSeries)

            if os.path.exists(mdcsFile):
                mdcsData = open(mdcsFile, "r", encoding="utf-8").readlines()[14:]
                for item in mdcsData:
                    x, y, err, *_ = item.split()
                    mdcsSeries.append(float(x), float(y))
                mdcsSeries.setName(f"{sample.name} mdcs01")
                self.addSeries(mdcsSeries)
                self.plottable = True

        self.createDefaultAxes()

    def plotSamples(self, samples, plotMode, dataFileType):
        if plotMode == PlotModes.STRUCTURE_FACTOR:
            self.setTitle("Structure Factor")    

            for sample in samples:
                self.plotSample(sample, plotMode, dataFileType)

