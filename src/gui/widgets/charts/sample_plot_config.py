
import os

from src.gui.widgets.charts.sample_plot_data import DCSLevel, Mdcs01Plot, Mdor01Plot, Mgor01Plot, Mint01Plot
from src.gui.widgets.charts.plot_modes import PlotModes


class SamplePlotConfig():

    def __init__(self, sample, inputDir, parent):
        self.sample = sample
        self.inputDir = inputDir
        self.parent = parent
        self.constructDataSets()

    def constructDataSets(self):
        if len(self.sample.dataFiles.dataFiles):

            baseFile = self.sample.dataFiles.dataFiles[0]
            ext = os.path.splitext(self.sample.dataFiles.dataFiles[0])[1]

            # mint01 dataset.
            mintPath = baseFile.replace(ext, ".mint01")
            hasMintData = False

            if os.path.exists(mintPath):
                hasMintData = True
            elif os.path.exists(os.path.join(self.inputDir, mintPath)):
                mintPath = os.path.join(self.inputDir, mintPath)
                hasMintData = True

            self.mint01DataSet = Mint01Plot(mintPath, hasMintData)
            self.mint01Series = self.mint01DataSet.toLineSeries(self.parent)
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
            self.mdcs01Series = self.mdcs01DataSet.toLineSeries(self.parent)
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
            self.dcsLevel.extend([p.x() for p in self.mdcs01Series.points()])
            self.dcsSeries = self.dcsLevel.toLineSeries(self.parent)
            self.dcsSeries.setName(f"{self.sample.name} Expected DCS level")

            # mdor01 dataset.
            mdorPath = baseFile.replace(ext, ".mdor01")
            hasMdorData = False

            if os.path.exists(mdorPath):
                hasMdorData = True
            elif os.path.exists(os.path.join(self.inputDir, mdorPath)):
                mdorPath = os.path.join(self.inputDir, mdorPath)
                hasMdorData = True

            self.mdor01DataSet = Mdor01Plot(mdorPath, hasMdorData)
            self.mdor01Series = self.mdor01DataSet.toLineSeries(self.parent)
            self.mdor01Series.setName(f"{self.sample.name} mdor01")

            # mgor01 dataset.
            mgorPath = baseFile.replace(ext, ".mgor01")
            hasMgorData = False

            if os.path.exists(mdorPath):
                hasMgorData = True
            elif os.path.exists(os.path.join(self.inputDir, mgorPath)):
                mdorPath = os.path.join(self.inputDir, mgorPath)
                hasMgorData = True

            self.mgor01DataSet = Mgor01Plot(mgorPath, hasMgorData)
            self.mgor01Series = self.mgor01DataSet.toLineSeries(self.parent)
            self.mgor01Series.setName(f"{self.sample.name} mgor01")

    # return all series
    def series(self):
        return [
            self.mint01Series,
            self.mdcs01Series,
            self.dcsSeries,
            self.mdor01Series,
            self.mgor01Series
        ]
    
    def SF(self):
        return [
            self.mint01Series,
            self.mdcs01Series,
            self.dcsSeries
        ]
    
    def SF_MINT01(self):
        return [
            self.mint01Series
        ]
    
    def SF_MDCS01(self):
        return [
            self.mdcs01Series,
            self.dcsSeries
        ]

    def RDF(self):
        return [
            self.mdor01Series,
            self.mgor01Series
        ]
    
    def plotData(self, plotMode):

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
