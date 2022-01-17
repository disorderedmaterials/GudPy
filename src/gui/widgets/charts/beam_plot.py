

from PySide6.QtCharts import QAreaSeries, QChart, QLineSeries
from PySide6.QtCore import QPoint, QPointF


class BeamChart(QChart):

    def __init__(self):
        super().__init__()
        self.legend().setVisible(False)

    def setBeam(self, beam):
        self.beam = beam

    def plot(self):

        self.upperSeries = QLineSeries(self)
        intensities = [
            QPointF(float(x+1), float(y))
            for x, y in enumerate(self.beam.beamProfileValues)
        ]
        self.upperSeries.append(intensities)
        self.lowerSeries = QLineSeries(self)
        self.lowerSeries.append([QPoint(p.x(), 0) for p in intensities])
        self.intensitySeries = QAreaSeries(self.upperSeries, self.lowerSeries)
        self.addSeries(self.intensitySeries)
        self.createDefaultAxes()
        self.axisY().setTitleText("Intensity")
        self.axisY().setRange(0, 2)
        self.axisY().setTickCount(5)
        self.axisX().setRange(
            min([p.x() for p in intensities])-1,
            max([p.x() for p in intensities])+1
        )
        self.axisX().hide()
