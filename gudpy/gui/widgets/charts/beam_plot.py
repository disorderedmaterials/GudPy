from PySide6.QtCharts import QAreaSeries, QChart, QLineSeries
from PySide6.QtCore import QPoint, QPointF


class BeamChart(QChart):
    """
    Plots the beam profile. Inherits QChart.

    Methods
    -------
    setBeam(beam)
        Sets the beam.
    plot()
        Updates the plot.
    """

    def __init__(self):
        """
        Constructs all the necessary attributes for the BeamChart object.
        """
        super(BeamChart, self).__init__()

        # Show the chart legend.
        self.legend().setVisible(False)
        
        # Initialise the series.
        self.areaSeries = QAreaSeries(self)
        self.addSeries(self.areaSeries)

    def setBeam(self, beam):
        """
        Sets the beam object.

        Parameters
        ----------
        beam : Beam
            Beam to set.
        """
        self.beam = beam

    def plot(self):
        """
        Updates the plot using the current beam.
        """

        # Upper series of the area series.
        self.upperSeries = QLineSeries(self)

        # Intensity values.
        intensities = [
            QPointF(float(x+1), float(y))
            for x, y in enumerate(self.beam.beamProfileValues)
        ]
        self.upperSeries.append(intensities)

        # Lower series of the area series.
        self.lowerSeries = QLineSeries(self)
        self.lowerSeries.append([QPoint(p.x(), 0) for p in intensities])

        # Construct area series.
        self.areaSeries.setUpperSeries(self.upperSeries)
        self.areaSeries.setLowerSeries(self.lowerSeries)

        # Axis and titles.
        self.createDefaultAxes()
        self.axisY().setTitleText("Intensity")
        self.axisY().setRange(0, 2)
        self.axisY().setTickCount(5)
        self.axisX().setRange(
            min([p.x() for p in intensities])-1,
            max([p.x() for p in intensities])+1
        )
        self.axisX().setTitleText("Beam X, cm")
