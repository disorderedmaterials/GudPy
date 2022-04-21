from PySide6.QtCharts import QChart, QLineSeries
from PySide6.QtCore import QPointF


class SpectraChart(QChart):

    def __init__(self):
        super().__init__()
        self.legend().setVisible(False)

    def setTimeBoundaries(self, start, end):
        self.start = start
        self.end = end

    def setSpectra(self, spec, pulses):
        self.spec = spec
        self.pulses = pulses
        self.plot()

    def plot(self):
        for pulse in self.pulses:
            print(pulse)
            series = QLineSeries(self)
            series.append(QPointF(pulse, 1.0))
            self.addSeries(series)

        self.createDefaultAxes()
        self.axisY().setRange(0, 1)
        self.axisX().setRange(self.start, self.end)
        self.axisX().setTitleText("Pulse time")