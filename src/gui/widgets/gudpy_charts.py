from PySide6.QtCharts import QChart, QLineSeries
from enum import Enum
import os


class PlotModes(Enum):
    STRUCTURE_FACTOR = 0
    RADIAL_DISTRIBUTION_FUNCTIONS = 1


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
            self, dataFileType, inputDir, sample=None,
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
        inputDir : str
            Input directory used.
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
            self.plotSample(sample, plotMode, dataFileType, inputDir)
        elif samples:
            self.plotSamples(samples, plotMode, dataFileType, inputDir)

    def plotSample(self, sample, plotMode, dataFileType, inputDir):
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
            if not os.path.exists(mintFile):
                mintFile = os.path.join(inputDir, mintFile)
            if not os.path.exists(mdcsFile):
                mdcsFile = os.path.join(inputDir, mdcsFile)

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

        elif plotMode == PlotModes.RADIAL_DISTRIBUTION_FUNCTIONS:
            # Set the title.
            self.setTitle("Radial Distribution Functions")

            # Get the mint01 and mdcs01 filenames.
            mdorFile = (
                sample.dataFiles.dataFiles[0].replace(dataFileType, "mdor")
            )
            mgorFile = (
                sample.dataFiles.dataFiles[0].replace(dataFileType, "mgor")
            )
            if not os.path.exists(mdorFile):
                mintFile = os.path.join(inputDir, mdorFile)
            if not os.path.exists(mgorFile):
                mdcsFile = os.path.join(inputDir, mgorFile)

            # Instantiate the series'.
            mdorSeries = QLineSeries()
            # Set the name of the series.
            mdorSeries.setName(f"{sample.name} mdor")

            mgorSeries = QLineSeries()
            # Set the name of the series.
            mgorSeries.setName(f"{sample.name} mgor")

            if os.path.exists(mdorFile):
                # Open it.
                with open(mdorFile, "r", encoding="utf-8") as f:
                    for data in f.readlines():

                        # Ignore commented lines.
                        if data[0] == "#":
                            continue

                        # Extract x,y, err.
                        x, y, _err, *__ = data.split()

                        # Append the data to the series.
                        mdorSeries.append(float(x), float(y))
            # Add the series to the chart.
            self.addSeries(mdorSeries)

            if os.path.exists(mgorFile):
                # Open it.
                with open(mgorFile, "r", encoding="utf-8") as f:
                    for data in f.readlines():

                        # Ignore commented lines.
                        if data[0] == "#":
                            continue

                        # Extract x,y, err.
                        x, y, _err, *__ = data.split()

                        # Append the data to the series.
                        mgorSeries.append(float(x), float(y))
            # Add the series to the chart.
            self.addSeries(mgorSeries)

        self.createDefaultAxes()

    def plotSamples(self, samples, plotMode, dataFileType, inputDir):
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
                self.plotSample(sample, plotMode, dataFileType, inputDir)
        elif plotMode == PlotModes.RADIAL_DISTRIBUTION_FUNCTIONS:
            # Set the title.
            self.setTitle("Radial Distribution Functions")
            for sample in samples:
                self.plotSample(sample, plotMode, dataFileType, inputDir)
