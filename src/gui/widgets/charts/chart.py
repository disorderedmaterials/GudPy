from PySide6.QtCharts import QChart, QLegend, QLegendMarker, QLineSeries
from PySide6.QtCore import QObject, Qt
from PySide6.QtGui import QPen
from src.gudrun_classes.sample import Sample
from src.gudrun_classes.container import Container
from src.gui.widgets.charts.sample_plot_config import SamplePlotConfig
from src.gui.widgets.charts.plot_modes import PlotModes

class GudPyChart(QChart):
    
    def __init__(self, gudrunFile, parent=None):

        super().__init__(parent)
        self.inputDir = gudrunFile.instrument.GudrunInputFileDir

        self.legend().setMarkerShape(QLegend.MarkerShapeFromSeries)
        self.legend().setAlignment(Qt.AlignRight)
        self.samples = []
        self.containers = []

    def connectMarkers(self):
        for marker in self.legend().markers():
            marker.clicked.connect(self.handleMarkerClicked)

    def disconnectMarkers(self):
        for marker in self.legend().markers():
            try:
                marker.clicked.disconnect(self.handleMarkerClicked)
            except RuntimeError:
                continue

    def handleMarkerClicked(self):
        marker = QObject.sender(self)
        if marker.type() == QLegendMarker.LegendMarkerTypeXY:
            marker.series().setVisible(not marker.series().isVisible())
            marker.setVisible(True)
            self.updateMarkerOpacity(marker)

    def updateMarkerOpacity(self, marker):
        alpha = 1.0 if marker.series().isVisible() else 0.5

        brush = marker.labelBrush()
        color = brush.color()
        color.setAlphaF(alpha)
        brush.setColor(color)
        marker.setLabelBrush(brush)

        brush = marker.brush()
        color = brush.color()
        color.setAlphaF(alpha)
        brush.setColor(color)
        marker.setBrush(brush)

        pen = marker.pen()
        color = pen.color()
        color.setAlphaF(alpha)
        pen.setColor(color)
        marker.setPen(pen)

    def addSamples(self, samples):
        for sample in samples:
            self.addSample(sample)

    def addSample(self, sample):
        self.samples.append(sample)

    def plot(self, plotMode=None):
        if plotMode:
            self.plotMode = plotMode

        self.removeAllSeries()
        for axis in self.axes():
            self.removeAxis(axis)

        plotsDCS = plotMode in [PlotModes.SF, PlotModes.SF_MDCS01, PlotModes.SF_CANS, PlotModes.SF_MDCS01_CANS]
        plotsSamples = plotMode in [PlotModes.SF, PlotModes.SF_MDCS01, PlotModes.SF_MINT01, PlotModes.RDF]
        plotsContainers = plotMode in [PlotModes.SF_CANS, PlotModes.SF_MINT01_CANS, PlotModes.SF_MDCS01_CANS, PlotModes.RDF_CANS]
        print(plotMode, plotsContainers)
        for sample in self.samples:
            plotConfig = SamplePlotConfig(sample, self.inputDir, self)
            for series in plotConfig.plotData(plotMode):
                if isinstance(sample, Sample) and plotsSamples:
                    self.addSeries(series)
                elif isinstance(sample, Container) and plotsContainers:
                    self.addSeries(series)
            if plotsDCS:
                pen = QPen(plotConfig.dcsSeries.pen())
                pen.setStyle(Qt.PenStyle.DashLine)
                pen.setWidth(2)
                pen.setColor(plotConfig.mdcs01Series.color())
                plotConfig.dcsSeries.setPen(pen)

        # Label axes
        if self.plotMode in [
            PlotModes.SF, PlotModes.SF_MINT01,
            PlotModes.SF_MDCS01, PlotModes.SF_CANS,
            PlotModes.SF_MINT01_CANS, PlotModes.SF_MDCS01_CANS
        ]:
            XLabel = "Q, 1\u212b"
            YLabel = "DCS, barns/sr/atom"
        elif self.plotMode in [
            PlotModes.RDF, PlotModes.RDF_CANS
        ]:
            XLabel = "r, \u212b"
            YLabel = "G(r)"
        self.createDefaultAxes()
        if self.series():
            self.axisX().setTitleText(XLabel)
            self.axisY().setTitleText(YLabel)
        self.connectMarkers()
    
    # def hasData(self, obj):
    #     series = SamplePlotConfig(obj, self.inputDir, self).series()
    #     print(sum([s.count() for s in series]))
    #     return sum([s.count() for s in series])