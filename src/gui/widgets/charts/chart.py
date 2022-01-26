from PySide6.QtCharts import QChart, QLegend, QLegendMarker, QLogValueAxis
from PySide6.QtCore import QObject, Qt
from PySide6.QtGui import QPen
from src.gudrun_classes.sample import Sample
from src.gudrun_classes.container import Container
from src.gui.widgets.charts.sample_plot_config import SamplePlotConfig
from src.gui.widgets.charts.enums import PlotModes, SeriesTypes
from src.gui.widgets.charts.enums import Axes


class GudPyChart(QChart):

    def __init__(self, gudrunFile, parent=None):

        super().__init__(parent)
        self.inputDir = gudrunFile.instrument.GudrunInputFileDir

        self.legend().setMarkerShape(QLegend.MarkerShapeFromSeries)
        self.legend().setAlignment(Qt.AlignRight)
        self.samples = []
        self.configs = {}

        self.logarithmicA = False
        self.logarithmicX = False
        self.logarithmicY = False
        self.logarithmicXAxis = QLogValueAxis(self)
        self.logarithmicXAxis.setBase(10.0)
        self.logarithmicYAxis = QLogValueAxis(self)
        self.logarithmicYAxis.setBase(10.0)

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

    def removeAllSeries(self):
        for series in self.series():
            self.removeSeries(series)

    def plot(self, plotMode=None):
        if plotMode:
            self.plotMode = plotMode

        self.removeAllSeries()
        for axis in self.axes():
            self.removeAxis(axis)

        plotsDCS = self.plotMode in [
            PlotModes.SF_MDCS01,
            PlotModes.SF_MDCS01_CANS
        ]
        plotsSamples = self.plotMode in [
            PlotModes.SF_MDCS01,
            PlotModes.SF_MINT01, PlotModes.RDF
        ]
        plotsContainers = self.plotMode in [
            PlotModes.SF_MINT01_CANS,
            PlotModes.SF_MDCS01_CANS, PlotModes.RDF_CANS
        ]
        for sample in self.samples:
            if sample in self.configs.keys():
                plotConfig = self.configs[sample]
            else:
                plotConfig = SamplePlotConfig(sample, self.inputDir, self)
                self.configs[sample] = plotConfig
            for series in plotConfig.plotData(self.plotMode):
                if series:
                    if isinstance(sample, Sample) and plotsSamples:
                        self.addSeries(series)
                    elif isinstance(sample, Container) and plotsContainers:
                        self.addSeries(series)
                    if not series.points():
                        series.hide()
            if (
                len(sample.dataFiles.dataFiles)
                and plotsDCS and
                plotConfig.mdcs01Series
            ):
                pen = QPen(plotConfig.dcsSeries.pen())
                pen.setStyle(Qt.PenStyle.DashLine)
                pen.setWidth(2)
                pen.setColor(plotConfig.mdcs01Series.color())
                plotConfig.dcsSeries.setPen(pen)

        # Label axes
        if self.plotMode in [
           PlotModes.SF_MINT01,
            PlotModes.SF_MDCS01,
            PlotModes.SF_MINT01_CANS, PlotModes.SF_MDCS01_CANS
        ]:
            XLabel = "Q, 1\u212b"
            YLabel = "DCS, barns/sr/atom"
        elif self.plotMode in [
            PlotModes.RDF, PlotModes.RDF_CANS
        ]:
            XLabel = "r, \u212b"
            YLabel = "G(r)"
        if self.series():
            self.createDefaultAxes()
            self.axisX().setTitleText(XLabel)
            self.axisY().setTitleText(YLabel)

            if self.logarithmicX or self.logarithmicA:
                self.removeAxis(self.axisX())
                self.addAxis(self.logarithmicXAxis, Qt.AlignBottom)
                for series in self.series():
                    series.attachAxis(self.logarithmicXAxis)

            if self.logarithmicY or self.logarithmicA:
                self.addAxis(self.logarithmicYAxis, Qt.AlignLeft)
                self.removeAxis(self.axisY())
                for series in self.series():
                    series.attachAxis(self.logarithmicYAxis)

        self.connectMarkers()

    def toggleVisible(self, seriesType):
        """
        Toggles visibility of a given series, or set of series'.
        Parameters
        ----------
        series : dict | QLineSeries
            Series(') to toggle visibility on.
        """
        targetAttr = (
            {
                SeriesTypes.MINT01: "mint01Series",
                SeriesTypes.MDCS01: "mdcs01Series",
                SeriesTypes.DCSLEVEL: "dcsSeries",
                SeriesTypes.MGOR01: "mgor01Series",
                SeriesTypes.MDOR01: "mdor01Series"
            }[seriesType]
        )

        for sample in self.samples:
            if self.configs[sample].__dict__[targetAttr]:
                self.configs[sample].__dict__[targetAttr].setVisible(
                    not self.configs[sample].__dict__[targetAttr].isVisible()
                )

    def isVisible(self, seriesType):
        """
        Method for determining if a given series or set of series' is visible.
        Parameters
        ----------
        series : dict | QLineSeries
            Series(') to check visibility of.
        """
        # If it's a dict, assume that if any value (series)
        # is visible, then they all should be.
        targetAttr = (
            {
                SeriesTypes.MINT01: "mint01Series",
                SeriesTypes.MDCS01: "mdcs01Series",
                SeriesTypes.DCSLEVEL: "dcsSeries",
                SeriesTypes.MGOR01: "mgor01Series",
                SeriesTypes.MDOR01: "mdor01Series"
            }[seriesType]
        )

        return any(
            [
                self.configs[sample].__dict__[targetAttr].isVisible()
                for sample in self.samples
                if self.configs[sample].__dict__[targetAttr]
            ]
        )

    def isSampleVisible(self, sample):

        if self.plotMode in [PlotModes.SF_MINT01, PlotModes.SF_MINT01_CANS]:
            return self.configs[sample].mint01Series.isVisible()
        elif self.plotMode in [PlotModes.SF_MDCS01, PlotModes.SF_MDCS01_CANS]:
            return (
                self.configs[sample].mdcs01Series.isVisible()
                | self.configs[sample].dcsSeries.isVisible()
            )
        elif self.plotMode in [PlotModes.RDF, PlotModes.RDF_CANS]:
            return (
                self.configs[sample].mdor01Series.isVisible()
                | self.configs[sample].mgor01Series.isVisible()
            )

    def toggleSampleVisibility(self, state, sample):
        self.configs[sample].mint01Series.setVisible(state)
        self.configs[sample].mdcs01Series.setVisible(state)
        self.configs[sample].dcsSeries.setVisible(state)
        self.configs[sample].mdor01Series.setVisible(state)
        self.configs[sample].mgor01Series.setVisible(state)

    def toggleLogarithmicAxis(self, axis):
        if axis == Axes.A:
            self.logarithmicA = not self.logarithmicA
            self.logarithmicX = self.logarithmicA
            self.logarithmicY = self.logarithmicA
        elif axis == Axes.X:
            self.logarithmicX = not self.logarithmicX
            self.logarithmicA = self.logarithmicX and self.logarithmicY
        elif axis == Axes.Y:
            self.logarithmicY = not self.logarithmicY
            self.logarithmicA = self.logarithmicX and self.logarithmicY

        self.plot()
