from PySide6.QtCharts import QChart, QLegend, QLegendMarker, QLogValueAxis
from PySide6.QtCore import QObject, Qt
from PySide6.QtGui import QPen
from PySide6.QtWidgets import QGraphicsTextItem

from core.sample import Sample
from core.container import Container
from gui.widgets.charts.sample_plot_config import SamplePlotConfig
from gui.widgets.charts.enums import PlotModes, SeriesTypes
from gui.widgets.charts.enums import Axes


class GudPyChart(QChart):
    """
    Core plotting functionality of GudPy. Inherits QChart.
    This is used for embedded plots throughout the GUI.

    Methods
    -------
    connectMarkers()
        Connects markers.
    disconnectMarkers()
        Disconnects markers.
    handleMarkerClicked()
        Handles a marker being clicked.
    updateMarkerOpacity(marker)
        Updates the opacity of the given marker.
    addSamples(samples)
        Adds samples to the plot.
    AddSample(sample)
        Adds a single sample to the plot.
    removeAllSeries()
        Removes all series from the plot.
    plot(plotMode=None)
        Plots the chart using plotMode.
    toggleVisible(seriesType)
        Toggles visibility of series of a specified type.
    isVisible(seriesType)
        Returns whether a given type of series is visible or not.
    isSampleVisible(sample)
        Returns whether a given sample is visible or not.
    toggleSampleVisibility(state, sample)
        Toggles the visibility of a given sample.
    toggleLogarithmicAxis(axis)
        Toggles logarithmic mode of `axis`.
    
    Attributes
    ----------
    inputDir : str
        Directory of input file.
    samples : Sample[]
        List of Sample objects being plotted.
    configs : {}
        Map of Samples to SamplePlotConfigs.
    logarithmicA : bool
        All axes logarithmic?
    logarithmicX : bool
        X-Axis logarithmic?
    logarithmicY : bool
        Y-Axis logarithmic?
    plotMode : PlotModes
        Mode for plotting.
    label : QGraphicsTextItem
        Label for mouse coordinates.
    """

    def __init__(self, gudrunFile, parent=None):
        """
        Constructs all the necessary attributes for the GudPyChart object.

        Parameters
        ----------
        gudrunFile : GudrunFile
            Reference GudrunFile object to create plot from.
        parent : Any | None, optional
            Parent object of chart.
        """
        super(GudPyChart, self).__init__(parent)
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

        self.plotMode = PlotModes.SF_MINT01

        # Set up label for mouse coordinates.
        self.label = QGraphicsTextItem("x=,y=", self)

    def connectMarkers(self):
        """
        Connects markers in the legend to the `handleMarkerClicked` slot.
        """
        for marker in self.legend().markers():
            marker.clicked.connect(self.handleMarkerClicked)

    def disconnectMarkers(self):
        """
        Disconnects markers in the legend from the `handleMarkerClicked` slot.
        """
        for marker in self.legend().markers():
            try:
                marker.clicked.disconnect(self.handleMarkerClicked)
            except RuntimeError:
                continue

    def handleMarkerClicked(self):
        """
        Slot for handling markers in the legend being clicked.
        Alters visibility of corresponding series, and opacity of
        marker.
        """
        # Get the sender object, i.e marker.
        marker = QObject.sender(self)
        # Double check type of marker.
        if marker.type() == QLegendMarker.LegendMarkerTypeXY:
            # Toggle the visibility of series.
            marker.series().setVisible(not marker.series().isVisible())
            # Ensure marker remains visible.
            marker.setVisible(True)
            # Update the opacity of the marker.
            self.updateMarkerOpacity(marker)

    def updateMarkerOpacity(self, marker):
        """
        Updates the opacity of a given marker.
        This opacity relates to the visibility of the
        corresponding series.

        Parameters
        ----------
        marker : QLegendMarker
            Marker to alter opacity.
        """

        # Determine alpha from series visibility.
        alpha = 1.0 if marker.series().isVisible() else 0.5

        # Update the opacities!

        brush = marker.labelBrush()
        color = brush.color()
        color.setAlphaF(alpha)
        brush.setColor(color)
        marker.setLabelBrush(brush)

        brush = marker.brush()
        color = brush.color()#
        color.setAlphaF(alpha)
        brush.setColor(color)
        marker.setBrush(brush)

        pen = marker.pen()
        color = pen.color()
        color.setAlphaF(alpha)
        pen.setColor(color)
        marker.setPen(pen)

    def addSamples(self, samples):
        """
        Adds a collection of samples to the plot.

        Parameters
        ----------
        samples : Sample[]
            List of Sample objects to add.
        """
        for sample in samples:
            self.addSample(sample)

    def addSample(self, sample):
        """
        Adds a samples to the plot.

        Parameters
        ----------
        sample : Sample
            Sample object to add.
        """
        self.samples.append(sample)

    def removeAllSeries(self):
        """
        Removes all series from the plot.
        """
        for series in self.series():
            self.removeSeries(series)

    def plot(self, plotMode=None):
        """
        Core functionality of the class.
        Plots samples using the given plotting mode.

        Parameters
        ----------
        plotMode : PlotModes | None
            Plotting mode to use.
        """

        # If a plot mode is given, then update the attribute.
        if plotMode:
            self.plotMode = plotMode

        # Remove all series from the plot.
        self.removeAllSeries()

        # Remove all axes.#
        for axis in self.axes():
            self.removeAxis(axis)

        # Determine whether to plot DCS level or not.
        plotsDCS = self.plotMode in [
            PlotModes.SF,
            PlotModes.SF_CANS,
            PlotModes.SF_MDCS01,
            PlotModes.SF_MDCS01_CANS
        ]

        # Determine whether to plot samples or not.
        plotsSamples = self.plotMode in [
            PlotModes.SF,
            PlotModes.SF_MDCS01,
            PlotModes.SF_MINT01, PlotModes.RDF
        ]

        # Determine whether to plot containers or not.
        plotsContainers = self.plotMode in [
            PlotModes.SF_CANS,
            PlotModes.SF_MINT01_CANS,
            PlotModes.SF_MDCS01_CANS, PlotModes.RDF_CANS
        ]

        # Iterate samples, adding them to the series.
        for sample in self.samples:
            # Determine minima.
            if self.series():
                pointsX = [
                    p.x()
                    for series in self.series()
                    for p in series.points()
                ]
                minX = 0 if sum(pointsX) == 0 else min(pointsX)
                pointsY = [
                    p.y()
                    for series in self.series()
                    for p in series.points()
                ]
                minY = 0 if sum(pointsY) == 0 else min(pointsY)
            else:
                minX = 0
                minY = 0
            # If plotting logarithmically, then apply offset.
            if self.logarithmicX or self.logarithmicA:
                offsetX = 1 + minX
            else:
                offsetX = 0
            if self.logarithmicY or self.logarithmicA:
                offsetY = 1 + minY
            else:
                offsetY = 0
            
            # Construct plotting configuration for the sample.
            plotConfig = SamplePlotConfig(
                sample, self.inputDir,
                offsetX,
                offsetY,
                self
            )
            # Add it to the map of configurations.
            self.configs[sample] = plotConfig

            # Iterate series in the configuration.
            for series in plotConfig.plotData(self.plotMode):
                if series:
                    # Add the relevant series to the plot.
                    if isinstance(sample, Sample) and plotsSamples:
                        self.addSeries(series)
                    elif isinstance(sample, Container) and plotsContainers:
                        self.addSeries(series)
                    # If the series is empty, hide it.
                    if not series.points():
                        series.hide()
            # Plot DCS level if necessary.
            if (
                len(sample.dataFiles)
                and plotsDCS and
                plotConfig.mdcs01Series
            ):
                # Use a dashed line.
                pen = QPen(plotConfig.dcsSeries.pen())
                pen.setStyle(Qt.PenStyle.DashLine)
                pen.setWidth(2)
                pen.setColor(plotConfig.mdcs01Series.color())
                plotConfig.dcsSeries.setPen(pen)

        # Label axes
        if self.plotMode in [
            PlotModes.SF,
            PlotModes.SF_MINT01,
            PlotModes.SF_MDCS01,
            PlotModes.SF_CANS,
            PlotModes.SF_MINT01_CANS, PlotModes.SF_MDCS01_CANS
        ]:
            XLabel = "Q, 1\u212b"
            YLabel = "DCS, barns/sr/atom"
        elif self.plotMode in [
            PlotModes.RDF, PlotModes.RDF_CANS
        ]:
            XLabel = "r, \u212b"
            YLabel = "G(r)"
        
        # As long as we have series in the plot, update the axes.
        if self.series():

            # Determine limits automatically.
            self.createDefaultAxes()

            # Update the axes labels.
            self.axisX().setTitleText(XLabel)
            self.axisY().setTitleText(YLabel)

            # If X-Axis needs to be logarithmic..
            if self.logarithmicX or self.logarithmicA:

                # Swap out the current X-Axis for a logarithmic axis.
                self.removeAxis(self.axisX())
                self.addAxis(self.logarithmicXAxis, Qt.AlignBottom)

                # Attach the series to the new X-Axis.
                for series in self.series():
                    series.attachAxis(self.logarithmicXAxis)

            # If Y-Axis needs to be logarithmic..
            if self.logarithmicY or self.logarithmicA:

                # Swap out the current Y-Axis for a logarithmic axis.
                self.removeAxis(self.axisY())
                self.addAxis(self.logarithmicYAxis, Qt.AlignLeft)

                # Attach the series to the new Y-Axis.
                for series in self.series():
                    series.attachAxis(self.logarithmicYAxis)

        # Connect the legend markers.
        self.connectMarkers()

    def toggleVisible(self, seriesType):
        """
        Toggles visibility of series of a specified type.

        Parameters
        ----------
        seriesType : SeriesTypes
            Target type to toggle visibility of.
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

        # Update visibility of relevant series.
        for sample in self.samples:
            if self.configs[sample].__dict__[targetAttr]:
                self.configs[sample].__dict__[targetAttr].setVisible(
                    not self.configs[sample].__dict__[targetAttr].isVisible()
                )

    def isVisible(self, seriesType):
        """
        Returns whether a given type of series is visible or not.

        Parameters
        ----------
        seriesType : SeriesTypes
            Target type to check visibility of.
        
        Returns
        -------
        bool : are any series of the specified type visible?
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

        # Determine if any of the series of the specified type are visible.
        return any(
            [
                self.configs[sample].__dict__[targetAttr].isVisible()
                for sample in self.samples
                if self.configs[sample].__dict__[targetAttr]
            ]
        )

    def isSampleVisible(self, sample):
        """
        Determine if given Sample is visible in the plot.

        Parameters
        ----------
        sample : Sample
            Sample object to check series visibility of.
        
        Returns
        -------
        bool : Are any of the sample's series visible?
        """

        # If only plotting mint01 series, then just check that.
        if self.plotMode in [PlotModes.SF_MINT01, PlotModes.SF_MINT01_CANS]:
            return self.configs[sample].mint01Series.isVisible()
        # If only plotting mdcs01 series, then just check that.
        elif self.plotMode in [PlotModes.SF_MDCS01, PlotModes.SF_MDCS01_CANS]:
            return (
                self.configs[sample].mdcs01Series.isVisible()
                | self.configs[sample].dcsSeries.isVisible()
            )
        # If checking SF, then check for both mint01 and mdcs01 visibility.
        elif self.plotMode in [PlotModes.SF, PlotModes.SF_CANS]:
            return (
                self.configs[sample].mint01Series.isVisible()
                | self.configs[sample].mdcs01Serie.isVisible()
                | self.configs[sample].dcsSeries.isVisible()
            )
        # If checking RDF, then check for both mdor01 and mgor01 visibility.
        elif self.plotMode in [PlotModes.RDF, PlotModes.RDF_CANS]:
            return (
                self.configs[sample].mdor01Series.isVisible()
                | self.configs[sample].mgor01Series.isVisible()
            )

    def toggleSampleVisibility(self, state, sample):
        """
        Toggles the visibility of a given sample.

        Parameters
        ----------
        state : bool
            Should sample be visible or not?
        sample : Sample
            Sample object to alter series visibility of.
        """
        self.configs[sample].mint01Series.setVisible(state)
        self.configs[sample].mdcs01Series.setVisible(state)
        self.configs[sample].dcsSeries.setVisible(state)
        self.configs[sample].mdor01Series.setVisible(state)
        self.configs[sample].mgor01Series.setVisible(state)

    def toggleLogarithmicAxis(self, axis):
        """
        Toggles using logarithmic axes or not.

        Parameters
        ----------
        axis : Axes
            Axes to be toggled.
        """
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

        # Re-plot.
        self.plot()
