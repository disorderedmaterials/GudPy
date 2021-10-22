from PySide6.QtCharts import (
    QChart, QChartView, QLegend, QLineSeries, QLogValueAxis, QValueAxis
)
from PySide6.QtCore import QPointF, QRectF, Qt
from PySide6.QtGui import (
    QAction, QClipboard, QCursor, QKeySequence, QPainter, QPen, QShortcut
)
from enum import Enum
import os

from PySide6.QtWidgets import QApplication, QMenu, QSizePolicy

from src.gudrun_classes.gud_file import GudFile


class PlotModes(Enum):
    STRUCTURE_FACTOR = 0
    RADIAL_DISTRIBUTION_FUNCTIONS = 1


class GudPyChart(QChart):
    """
    Class to represent plots in GudPy. Inherits QChart.

    ...

    Attributes
    ----------
    dataFileType : str
        Data file type being used in the input file.
    inputDir : str
        Input directory.
    data : dict
        Dictionary of data for plotting.
    logarithmic : bool
        Are plots logarithmic?
    logarithmicXAxis : QLogValueAxis
        X-Axis to use for logarithmic plots.
    logarithmicYAxis : QLogValueAxis
        Y-Axis to use for logarithmic plots.
    seriesAVisible : bool
        Is the first series visible?
    seriesBVisible : bool
        Is the second series visible?
    Methods
    -------
    addSamples(samples):
        Adds the given samples to the chart.
    addSample(sample):
        Adds the given sample to the chart.
    plot(plotMode):
        Plots the data stored with the given plotmode.
    plotSample(sample):
        Plots the given sample on the chart.
    toggleLogarithmicAxes():
        Toggles logarithmic plotting.
    toggleVisible(series):
        Toggles visibility of a given series, or set of series'.
    isVisible(series):
        Method for determining if a given series or set of series' is visible.
    errorData():
        Method for constructing data for use in error bars.
    """
    def __init__(
            self, gudrunFile
    ):
        """
        Constructs all the necessary attributes for the GudPyChart object.
        Calls super()._init__ which calls the dunder init method
        from QChart.
        Parameters
        ----------
        gudrunFile : GudrunFile
            GudrunFile object that all data will be constructed from.
        """
        super(GudPyChart, self).__init__()

        self.dataFileType = gudrunFile.instrument.dataFileType
        self.inputDir = gudrunFile.instrument.GudrunInputFileDir

        self.data = {}
        self.logarithmic = False
        self.logarithmicXAxis = QLogValueAxis()
        self.logarithmicXAxis.setBase(10.0)
        self.logarithmicYAxis = QLogValueAxis()
        self.logarithmicYAxis.setBase(10.0)

        self.dcsAxis = QValueAxis()
        self.addAxis(self.dcsAxis, Qt.AlignRight)

        self.seriesAVisible = True
        self.seriesBVisible = True
        self.seriesCVisible = True

        self.legend().setMarkerShape(QLegend.MarkerShapeFromSeries)

    def addSamples(self, samples):
        """
        Adds the given samples to the chart.
        Parameters
        ----------
        samples : Sample[]
            List of samples to add.
        """
        for sample in samples:
            self.addSample(sample)

    def addSample(self, sample):
        """
        Adds the given sample to the chart.
        Parameters
        ----------
        sample : Sample
            Sample to be added.
        """

        # Add a new dictionary / empty the currently stored dictionary.
        self.data[sample] = {}

        # Get the mint01 and mdcs01 filenames.
        mintFile = (
            sample.dataFiles.dataFiles[0].replace(self.dataFileType, "mint01")
        )
        mdcsFile = (
            sample.dataFiles.dataFiles[0].replace(self.dataFileType, "mdcs01")
        )

        # Try and resolve paths.
        if not os.path.exists(mintFile):
            mintFile = os.path.join(self.inputDir, mintFile)
        if not os.path.exists(mdcsFile):
            mdcsFile = os.path.join(self.inputDir, mdcsFile)

        # Check the file exists.
        if os.path.exists(mintFile):
            mintData = []
            # Open it.
            with open(mintFile, "r", encoding="utf-8") as f:
                for data in f.readlines():

                    # Ignore commented lines.
                    if data[0] == "#":
                        continue

                    # Extract x,y, err.
                    x, y, err, *__ = [float(n) for n in data.split()]

                    mintData.append([x, y, err])
            self.data[sample]["mint01"] = mintData

        # Check the file exists.
        if os.path.exists(mdcsFile):
            mdcsData = []
            # Open it.
            with open(mdcsFile, "r", encoding="utf-8") as f:
                for data in f.readlines():

                    # Ignore commented lines.
                    if data[0] == "#":
                        continue

                    # Extract x,y, err.
                    x, y, err, *__ = [float(n) for n in data.split()]
                    mdcsData.append([x, y, err])
            self.data[sample]["mdcs01"] = mdcsData

        gudPath = sample.dataFiles.dataFiles[0].replace(
            self.dataFileType, "gud"
        )
        if not os.path.exists(gudPath):
            gudPath = os.path.join(self.inputDir, gudPath)

        if os.path.exists(gudPath) and "mdcs01" in self.data[sample].keys():
            dcsData = []
            gudFile = GudFile(gudPath)
            dcsLevel = gudFile.averageLevelMergedDCS
            for x, _, _ in self.data[sample]["mdcs01"]:
                dcsData.append((x, float(dcsLevel)))
            self.data[sample]["dcs"] = dcsData

        # Get the mint01 and mdcs01 filenames.
        mdorFile = (
            sample.dataFiles.dataFiles[0].replace(self.dataFileType, "mdor01")
        )
        mgorFile = (
            sample.dataFiles.dataFiles[0].replace(self.dataFileType, "mgor01")
        )

        # Try and resolve paths.
        if not os.path.exists(mdorFile):
            mdorFile = os.path.join(self.inputDir, mdorFile)
        if not os.path.exists(mgorFile):
            mgorFile = os.path.join(self.inputDir, mgorFile)

        if os.path.exists(mdorFile):
            mdorData = []
            # Open it.
            with open(mdorFile, "r", encoding="utf-8") as f:
                for data in f.readlines():

                    # Ignore commented lines.
                    if data[0] == "#":
                        continue

                    # Extract x,y, err.
                    x, y, err, *__ = [float(n) for n in data.split()]

                    # Append the data to the series.
                    mdorData.append([x, y, err])
            self.data[sample]["mdor01"] = mdorData

        if os.path.exists(mgorFile):
            mgorData = []
            # Open it.
            with open(mgorFile, "r", encoding="utf-8") as f:
                for data in f.readlines():

                    # Ignore commented lines.
                    if data[0] == "#":
                        continue

                    # Extract x,y, err.
                    x, y, err, *__ = [float(n) for n in data.split()]

                    # Append the data to the series.
                    mgorData.append([x, y, err])
            self.data[sample]["mgor01"] = mgorData

    def plot(self, plotMode=None):
        """
        Plots the data stored with the given plotmode.
        Parameters
        ----------
        plotMode : PlotMode, optional
            Plot mode to use.
        """

        # If a plotMode is defined, then set the class attribute to it.
        if plotMode:
            self.plotMode = plotMode

        # Clear the chart of all series' and axes.
        self.seriesA = {}
        self.seriesB = {}
        self.seriesC = {}

        self.removeAllSeries()
        for axis in self.axes():
            self.removeAxis(axis)

        # Plot all the samples stored.
        for sample in self.data.keys():
            self.plotSample(sample)

        # If it is a logarithmic plot, we need to define our own
        # QLogValueAxis, and attatch to our series'.
        # Otherwise create default ones.
        if self.logarithmic:
            self.addAxis(self.logarithmicXAxis, Qt.AlignBottom)
            self.addAxis(self.logarithmicYAxis, Qt.AlignLeft)
            for series in self.series():
                series.attachAxis(self.axisX())
                series.attachAxis(self.axisY())
        else:
            self.createDefaultAxes()

        # Ensure that visibility is persistent.
        if not self.seriesAVisible:
            for series in self.seriesA.values():
                series.setVisible(False)
        if not self.seriesBVisible:
            for series in self.seriesB.values():
                series.setVisible(False)
        if not self.seriesCVisible:
            for series in self.seriesC.values():
                series.setVisible(False)

    def plotSample(self, sample):
        """
        Plots the given sample on the chart.
        Parameters
        ----------
        sample : Sample
            Sample to plot.
        """

        # Decide on the offset.
        # Non-logarithmic = 0, logarithmic = 10.
        # Offset ensures that when plotting logarithmically,
        # that no undefined values are produced.
        offset = int(self.logarithmic)*10

        # If the plotting mode is Structure Factor.
        if self.plotMode == PlotModes.STRUCTURE_FACTOR:
            # Instantiate the series.
            mintSeries = QLineSeries()
            # Set the name of the series.
            mintSeries.setName(f"{sample.name} mint01")
            # Construct the series
            mintSeries.append(
                [
                    QPointF(x+offset, y+offset)
                    for x, y, _ in self.data[sample]["mint01"]
                ]
            )
            # Add the series to the chart.
            self.addSeries(mintSeries)
            # Keep the series.
            self.seriesA[sample] = mintSeries

            # Instantiate the series.
            mdcsSeries = QLineSeries()
            # Set the name of the series.
            mdcsSeries.setName(f"{sample.name} mdcs01")
            # Construct the series
            mdcsSeries.append(
                [
                    QPointF(x+offset, y+offset)
                    for x, y, _ in self.data[sample]["mdcs01"]
                ]
            )
            # Add the series to the chart.
            self.addSeries(mdcsSeries)
            # Keep the series.
            self.seriesB[sample] = mdcsSeries

            dcsSeries = QLineSeries()
            dcsSeries.setName(f"{sample.name} dcs level")
            dcsSeries.append(
                [
                    QPointF(x, y)
                    for x, y in self.data[sample]["dcs"]
                ]
            )
            pen = QPen(dcsSeries.pen())
            pen.setStyle(Qt.PenStyle.DashLine)
            pen.setColor(mdcsSeries.color())
            dcsSeries.setPen(pen)
            self.addSeries(dcsSeries)
            self.seriesC[sample] = dcsSeries

        # If the plotting mode is RDF.
        elif self.plotMode == PlotModes.RADIAL_DISTRIBUTION_FUNCTIONS:

            # Instantiate the series.
            mdorSeries = QLineSeries()
            # Set the name of the series.
            mdorSeries.setName(f"{sample.name} mdor01")
            # Construct the series
            mdorSeries.append(
                [
                    QPointF(x+offset, y+offset)
                    for x, y, _ in self.data[sample]["mdor01"]
                ]
            )
            # Add the series to the chart.
            self.addSeries(mdorSeries)
            # Keep the series.
            self.seriesA[sample] = mdorSeries

            # Instantiate the series.
            mgorSeries = QLineSeries()
            # Set the name of the series.
            mgorSeries.setName(f"{sample.name} mgor01")
            # Construct the series
            mgorSeries.append(
                [
                    QPointF(x+offset, y+offset)
                    for x, y, _ in self.data[sample]["mgor01"]
                ]
            )
            # Add the series to the chart.
            self.addSeries(mgorSeries)
            # Keep the series.
            self.seriesB[sample] = mgorSeries

    def toggleLogarithmicAxes(self):
        """
        Toggles logarithmic plotting.
        """
        # 'Flick' the logarithmic flag.
        self.logarithmic = not self.logarithmic
        # Replot.
        self.plot()

    def toggleVisible(self, series):
        """
        Toggles visibility of a given series, or set of series'.
        Parameters
        ----------
        series : dict | QLineSeries
            Series(') to toggle visibility on.
        """
        # If a dict is received
        if isinstance(series, dict):
            # 'Flick' the corresponding visibility flag.
            if series == self.seriesA:
                self.seriesAVisible = not self.seriesAVisible
            elif series == self.seriesB:
                self.seriesBVisible = not self.seriesBVisible
            elif series == self.seriesC:
                self.seriesCVisible = not self.seriesCVisible
            # Recurse, toggling visibility of values (series').
            for s in series.values():
                self.toggleVisible(s)
        else:
            # 'Flick' internal visibility flag of QLineSeries object.
            series.setVisible(not series.isVisible())

    def isVisible(self, series):
        """
        Method for determining if a given series or set of series' is visible.
        Parameters
        ----------
        series : dict | QLineSeries
            Series(') to check visibility of.
        """
        # If it's a dict, assume that if any value (series)
        # is visible, then they all should be.
        if isinstance(series, dict):
            return any([s.isVisible() for s in series.values()])
        else:
            return series.isVisible()

    def errorData(self):
        """
        Method for constructing data for use in error bars.
        Returns
        -------
        list
            List of tuples of points (x1, y1, x2, y2)
        """
        errorData = []
        if self.plotMode == PlotModes.STRUCTURE_FACTOR:
            for sample in self.data.keys():
                for x, y, err in self.data[sample]["mint01"]:
                    errorData.append((x, y-err, x, y+err))
                for x, y, err in self.data[sample]["mdcs01"]:
                    errorData.append((x, y-err, x, y+err))
        elif self.plotMode == PlotModes.RADIAL_DISTRIBUTION_FUNCTIONS:
            for sample in self.data.keys():
                for x, y, err in self.data[sample]["mdor01"]:
                    errorData.append((x, y-err, x, y+err))
                for x, y, err in self.data[sample]["mgor01"]:
                    errorData.append((x, y-err, x, y+err))
        return errorData


class GudPyChartView(QChartView):
    """
    Class to represent a GudPyChartView. Inherits QChartView.

    ...
    Attributes
    ----------
    chart : GudPyChart
        Chart to be shown in the view.
    Methods
    -------
    wheelEvent(event):
        Event handler for using the scroll wheel.
    toggleLogarithmicAxes():
        Toggles logarithmic axes in the chart.
    setupShortcuts():
        Sets up the keyboard shortcuts for the chart.
    """
    def __init__(self, parent):
        """
        Constructs all the necessary attributes for the GudPyChartView object.
        Calls super()._init__ which calls the dunder init method
        from QChartView.
        Parameters
        ----------
        parent : QWidget, optional
            Parent widget.
        """
        super(GudPyChartView, self).__init__(parent=parent)

        # Set size policy.
        self.setSizePolicy(
            QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
        )

        # Enable rectangualar rubber banding.
        self.setRubberBand(QChartView.RectangleRubberBand)

        # Enable Antialiasing.
        self.setRenderHint(QPainter.Antialiasing)

        # Setup keyboard shortcuts.
        self.setupShortcuts()

        self.clipboard = QClipboard(self.parent())

    def wheelEvent(self, event):
        """
        Event handler called when the scroll wheel is used.
        This event is overridden for zooming in/out.
        Parameters
        ----------
        event : QWheelEvent
            Event that triggered the function call.
        """
        # Decide on the zoom factor.
        # If y > 0, zoom in, if y < 0 zoom out.
        zoomFactor = 2.0 if event.angleDelta().y() > 0 else 0.5

        # Create QRect area to zoom in on.
        chartArea = self.chart().plotArea()
        left = chartArea.left()
        top = chartArea.top()
        width = chartArea.width() / zoomFactor
        height = chartArea.height() / zoomFactor
        zoomArea = QRectF(left, top, width, height)

        # Move the rectangle to the mouse position.
        mousePos = self.mapFromGlobal(QCursor.pos())
        zoomArea.moveCenter(mousePos)

        # Zoom in on the area.
        self.chart().zoomIn(zoomArea)

        # Scroll to match the zoom.
        delta = self.chart().plotArea().center() - mousePos
        self.chart().scroll(delta.x(), -delta.y())

        self.zoomArea = zoomArea
        self.scrolled = (delta.x(), -delta.y())

    def toggleLogarithmicAxes(self):
        """
        Toggles logarithmic axes in the chart.
        """
        self.chart().toggleLogarithmicAxes()

    def contextMenuEvent(self, event):
        """
        Creates context menu, so that on right clicking the chartview,
        the user is able to perform actions.
        Parameters
        ----------
        event : QMouseEvent
            The event that triggers the context menu.
        """
        self.menu = QMenu(self)
        if self.chart():
            resetAction = QAction("Reset zoom", self.menu)
            resetAction.triggered.connect(self.chart().zoomReset)
            self.menu.addAction(resetAction)
            toggleLogarithmicAction = QAction(
                "Toggle logarithmic axes", self.menu
            )
            toggleLogarithmicAction.setCheckable(True)
            toggleLogarithmicAction.setChecked(self.chart().logarithmic)
            toggleLogarithmicAction.triggered.connect(
                self.toggleLogarithmicAxes
            )
            self.menu.addAction(toggleLogarithmicAction)

            if self.chart().plotMode == PlotModes.STRUCTURE_FACTOR:
                showMint01Action = QAction("Show mint01 data", self.menu)
                showMint01Action.setCheckable(True)
                showMint01Action.setChecked(
                    self.chart().isVisible(self.chart().seriesA)
                )
                showMint01Action.triggered.connect(
                    lambda: self.chart().toggleVisible(
                        self.chart().seriesA
                    )
                )
                self.menu.addAction(showMint01Action)

                showMdcs01Action = QAction("Show mdcs01 data", self.menu)
                showMdcs01Action.setCheckable(True)
                showMdcs01Action.setChecked(
                    self.chart().isVisible(self.chart().seriesB)
                )
                showMdcs01Action.triggered.connect(
                    lambda: self.chart().toggleVisible(
                        self.chart().seriesB
                    )
                )
                self.menu.addAction(showMdcs01Action)

                showDCSLevelAction = QAction("Show dcs level", self.menu)
                showDCSLevelAction.setCheckable(True)
                showDCSLevelAction.setChecked(
                    self.chart().isVisible(self.chart().seriesC)
                )
                showDCSLevelAction.triggered.connect(
                    lambda: self.chart().toggleVisible(
                        self.chart().seriesC
                    )
                )
                self.menu.addAction(showDCSLevelAction)
            elif (
                self.chart().plotMode ==
                PlotModes.RADIAL_DISTRIBUTION_FUNCTIONS
            ):
                showMdor01Action = QAction("Show mdor01 data", self.menu)
                showMdor01Action.setCheckable(True)
                showMdor01Action.setChecked(
                    self.chart().isVisible(self.chart().seriesA)
                )
                showMdor01Action.triggered.connect(
                    lambda: self.chart().toggleVisible(
                        self.chart().seriesA
                    )
                )
                self.menu.addAction(showMdor01Action)

                showMgor01Action = QAction("Show mgor01 data", self.menu)
                showMgor01Action.setCheckable(True)
                showMgor01Action.setChecked(
                    self.chart().isVisible(self.chart().seriesB)
                )
                showMgor01Action.triggered.connect(
                    lambda: self.chart().toggleVisible(
                        self.chart().seriesB
                    )
                )
                self.menu.addAction(showMgor01Action)
        
        copyAction = QAction("Copy plot", self.menu)
        copyAction.triggered.connect(self.copyPlot)
        self.menu.addAction(copyAction)

        self.menu.popup(QCursor.pos())
    
    def copyPlot(self):
        pixMap = self.grab()
        self.clipboard.setPixmap(pixMap)

    def keyPressEvent(self, event):

        modifiers = QApplication.keyboardModifiers()
        if event.key() == Qt.Key_C and modifiers == Qt.ControlModifier:
            self.copyPlot()

    def setupShortcuts(self):
        """
        Sets up keyboard shortcuts for the Chart.
        """

        # TODO: Can we enable these shortcuts when hovering the Chart?
        # TODO: Instead of having to first click inside to get the context?

        # Keyboard shorcut 'L/l' for toggling logarithmic axes.
        self.toggleLogarithmicAxesShortcut = QShortcut(
            QKeySequence(Qt.Key_L), self
        )
        self.toggleLogarithmicAxesShortcut.setContext(Qt.WidgetShortcut)
        self.toggleLogarithmicAxesShortcut.activated.connect(
            self.toggleLogarithmicAxes
        )

        # Keyboard shortcut 'A/a' for showing the limits of the chart.
        # i.e. zooming out fully.
        self.showLimitsShortcut = QShortcut(QKeySequence(Qt.Key_A), self)
        self.showLimitsShortcut.setContext(Qt.WidgetShortcut)
        self.showLimitsShortcut.activated.connect(self.chart().zoomReset)
