
import os

from gui.widgets.charts.sample_plot_data import (
    DCSLevel, Mdcs01Plot,
    Mdor01Plot, Mgor01Plot, Mint01Plot
)
from gui.widgets.charts.enums import PlotModes


class SamplePlotConfig():
    """
    Class for managing configurations of sample plots.
    This is used to determine which datasets etc, pertaining to a specific sample,
    should be shown.

    ...

    Attributes
    ----------
    sample : Sample
        Reference Sample object.
    inputDir : str
        Input file directory.
    parent : Any
        Parent object.
    
    Methods
    -------
    constructDataSets(offsetX, offsetY)
        Loads datasets and constructs series.
    series()
        Returns all of the series.
    SF()
        Returns series that should be shown by `SF`.
    SF_MINT01()
        Returns series that should be shown by `SF_MINT01`.
    SF_MDCS01()
        Returns series that should be shown by `SF_MDCS01`.
    RDF()
        Returns series that should be shown by `RDF`.
    plotData(plotMode)
        Returns series that should be plotted by a given plotMode.
    """

    def __init__(self, sample, inputDir, offsetX, offsetY, parent):
        """
        Constructs all the necessary attributes for the SamplePlotConfig object.

        Parameters
        ----------
        sample : Sample
            Reference Sample object.
        inputDir : str
            Input file directory.
        offsetX : float
            X-Offset for data.
        offsetY : float
            Y-Offset for data.
        parent : Any
            Parent object.
        """
        self.sample = sample
        self.inputDir = inputDir
        self.parent = parent

        # Construct the datasets.
        self.constructDataSets(offsetX, offsetY)

    def constructDataSets(self, offsetX, offsetY):
        """
        This is the core function of the configuration, it is called every time
        a configuration is initialised.
        Reads data in from the input directory, and then constructs the relevant
        data sets from that.

        Parameters
        ----------
        offsetX : float
            X-Offset for data.
        offsetY : float
            Y-Offset for data.
        """

        # Ensure that there are actually some data files.
        if len(self.sample.dataFiles):

            # Base file path.
            baseFile = self.sample.dataFiles[0]
            ext = os.path.splitext(self.sample.dataFiles[0])[-1]

            # mint01 dataset.
            mintPath = baseFile.replace(ext, ".mint01")
            hasMintData = False

            if os.path.exists(mintPath):
                hasMintData = True
            elif os.path.exists(os.path.join(self.inputDir, mintPath)):
                mintPath = os.path.join(self.inputDir, mintPath)
                hasMintData = True

            self.mint01DataSet = Mint01Plot(mintPath, hasMintData)
            self.mint01Series = self.mint01DataSet.toLineSeries(
                self.parent, offsetX, offsetY
            )
            if self.mint01Series:
                self.mint01Series.setName(f"{self.sample.name} mint01")

            # mdcs01 dataset.
            mdcsPath = baseFile.replace(ext, ".mdcs01")
            hasMdcsData = False

            if os.path.exists(mdcsPath):
                hasMdcsData = True
            elif os.path.exists(os.path.join(self.inputDir, mdcsPath)):
                mdcsPath = os.path.join(self.inputDir, mdcsPath)
                hasMdcsData = True

            self.mdcs01DataSet = Mdcs01Plot(mdcsPath, hasMdcsData)
            self.mdcs01Series = self.mdcs01DataSet.toLineSeries(
                self.parent, offsetX, offsetY
            )
            if self.mdcs01Series:
                self.mdcs01Series.setName(f"{self.sample.name} mdcs01")

            # gud data, for dcs level.
            gudPath = baseFile.replace(ext, ".gud")
            hasDCSData = False

            if os.path.exists(gudPath):
                hasDCSData = True
            elif os.path.exists(os.path.join(self.inputDir, gudPath)):
                gudPath = os.path.join(self.inputDir, gudPath)
                hasDCSData = True

            self.dcsLevel = DCSLevel(gudPath, hasDCSData)
            if hasMdcsData:
                self.dcsLevel.extend(
                    [p.x() for p in self.mdcs01Series.points()]
                )
            self.dcsSeries = self.dcsLevel.toLineSeries(self.parent)
            if self.dcsSeries:
                self.dcsSeries.setName(
                    f"{self.sample.name} Expected DCS level"
                )

            # mdor01 dataset.
            mdorPath = baseFile.replace(ext, ".mdor01")
            hasMdorData = False

            if os.path.exists(mdorPath):
                hasMdorData = True
            elif os.path.exists(os.path.join(self.inputDir, mdorPath)):
                mdorPath = os.path.join(self.inputDir, mdorPath)
                hasMdorData = True

            self.mdor01DataSet = Mdor01Plot(mdorPath, hasMdorData)
            self.mdor01Series = self.mdor01DataSet.toLineSeries(
                self.parent, offsetX, offsetY
            )
            if self.mdor01Series:
                self.mdor01Series.setName(f"{self.sample.name} mdor01")

            # mgor01 dataset.
            mgorPath = baseFile.replace(ext, ".mgor01")
            hasMgorData = False

            if os.path.exists(mgorPath):
                hasMgorData = True
            elif os.path.exists(os.path.join(self.inputDir, mgorPath)):
                mgorPath = os.path.join(self.inputDir, mgorPath)
                hasMgorData = True

            self.mgor01DataSet = Mgor01Plot(mgorPath, hasMgorData)
            self.mgor01Series = self.mgor01DataSet.toLineSeries(
                self.parent, offsetX, offsetY
            )
            if self.mgor01Series:
                self.mgor01Series.setName(f"{self.sample.name} mgor01")

    # return all series
    def series(self):
        """
        Returns all of the series.

        Returns
        -------
        QLineSeries[] : series
        """
        return [
            self.mint01Series,
            self.mdcs01Series,
            self.dcsSeries,
            self.mdor01Series,
            self.mgor01Series
        ]

    def SF(self):
        """
        Returns series that should be shown by `SF`.

        Returns
        -------
        QLineSeries[] : series
        """
        return [
            self.mint01Series,
            self.mdcs01Series,
            self.dcsSeries
        ]

    def SF_MINT01(self):
        """
        Returns series that should be shown by `SF_MINT01`.

        Returns
        -------
        QLineSeries[] : series
        """
        return [
            self.mint01Series
        ]

    def SF_MDCS01(self):
        """
        Returns series that should be shown by `SF_MDCS01`.

        Returns
        -------
        QLineSeries[] : series
        """
        return [
            self.mdcs01Series,
            self.dcsSeries
        ]

    def RDF(self):
        """
        Returns series that should be shown by `RDF`.

        Returns
        -------
        QLineSeries[] : series
        """
        return [
            self.mdor01Series,
            self.mgor01Series
        ]

    def plotData(self, plotMode):
        """
        Returns series that should be plotted by a given plotMode.

        Returns
        -------
        QLineSeries[] : series
        """
        if len(self.sample.dataFiles):
            return {
                PlotModes.SF: self.SF,
                PlotModes.SF_MINT01: self.SF_MINT01,
                PlotModes.SF_MDCS01: self.SF_MDCS01,
                PlotModes.RDF: self.RDF,
                PlotModes.SF_CANS: self.SF,
                PlotModes.SF_MINT01_CANS: self.SF_MINT01,
                PlotModes.SF_MDCS01_CANS: self.SF_MDCS01,
                PlotModes.RDF_CANS: self.RDF
            }[plotMode]()
        else:
            return []
