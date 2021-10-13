from PySide6.QtCharts import QChart, QLineSeries
from enum import Enum
import os


class PlotModes(Enum):
    STRUCTURE_FACTOR = 0


class GudPyChart(QChart):
    """
    Class to represent plots in GudPy. Inherits QChart.

    ...

    Methods
    -------
    plotSample(sample, plotMode, dataFileType):
        Plots a single sample.
    plotSamples(samples, plotMode, dataFileType):
        Plots a list of samples.
    """
    def __init__(
            self, dataFileType, sample=None,
            samples=[], plotMode=PlotModes.STRUCTURE_FACTOR
    ):
        """
        Constructs all the necessary attributes for the GudPyChart object.
        Calls super()._init__ which calls the dunder init method
        from QChart.
        Parameters
        ----------
        dataFileType : str
            Data file type used throughout the input file.
        sample : Sample, optional
            Sample to create plot from.
        samples : Sample[], optional
            Samples to create plots from.
        plotMode : PlotModes, optional
            Mode to use for plotting.
        """
        super(GudPyChart, self).__init__()

        # Call plotting function.
        if sample:
            self.plotSample(sample, plotMode, dataFileType)
        elif samples:
            self.plotSamples(samples, plotMode, dataFileType)

    def plotSample(self, sample, plotMode, dataFileType):
        """
        Plots a single sample, with a given plotting mode.
        Parameters
        ----------
        sample : Sample
            Sample to create plot from.
        plotMode : PlotModes
            Mode to use for plotting.
        dataFileType : str
            Data file type used throughout the input file.
        """

        # If the plotting mode is Structure Factor.
        if plotMode == PlotModes.STRUCTURE_FACTOR:

            # Set the title.
            self.setTitle("Structure Factor")

            # Get the mint01 and mdcs01 filenames.
            mintFile = (
                sample.dataFiles.dataFiles[0].replace(dataFileType, "mint01")
            )
            mdcsFile = (
                sample.dataFiles.dataFiles[0].replace(dataFileType, "mdcs01")
            )

            # Instantiate the series'.
            mintSeries = QLineSeries()
            # Set the name of the series.
            mintSeries.setName(f"{sample.name} mint01")
            mdcsSeries = QLineSeries()
            # Set the name of the series.
            mdcsSeries.setName(f"{sample.name} mdcs01")
            # mint01 files are only present if a positive top hat
            # width is used.
            if sample.topHatW:
                # Check the file exists.
                if os.path.exists(mintFile):
                    # Open it.
                    with open(mintFile, "r", encoding="utf-8") as f:
                        for data in f.readlines():

                            # Ignore commented lines.
                            if data[0] == "#":
                                continue

                            # Extract x,y, err.
                            x, y, _err, *__ = data.split()

                            # Append the data to the series.
                            mintSeries.append(float(x), float(y))
                    # Add the series to the chart.
                    self.addSeries(mintSeries)

            # Check the file exists.
            if os.path.exists(mdcsFile):
                # Open it.
                with open(mdcsFile, "r", encoding="utf-8") as f:
                    for data in f.readlines():

                        # Ignore commented lines.
                        if data[0] == "#":
                            continue

                        # Extract x,y, err.
                        x, y, _err, *__ = data.split()

                        # Append the data to the series.
                        mdcsSeries.append(float(x), float(y))
            # Add the series to the chart.
            self.addSeries(mdcsSeries)

        self.createDefaultAxes()

    def plotSamples(self, samples, plotMode, dataFileType):
        """
        Plots a list of samples, with a given plotting mode.
        Parameters
        ----------
        samples : Sample[]
            Samples to create plot from.
        plotMode : PlotModes
            Mode to use for plotting.
        dataFileType : str
            Data file type used throughout the input file.
        """
        # If the plotting mode is Structure Factor.
        if plotMode == PlotModes.STRUCTURE_FACTOR:

            # Set the title.
            self.setTitle("Structure Factor")

            # Iterate through samples adding them to the plot.
            for sample in samples:
                self.plotSample(sample, plotMode, dataFileType)
