from PySide6.QtCharts import QChart, QLineSeries, QDateTimeAxis, QValueAxis
from PySide6.QtCore import QPointF, Qt


class SpectraChart(QChart):

    def __init__(self):
        super().__init__()
        self.legend().setVisible(False)
        
        self.axisX_ = QDateTimeAxis(self)
        self.axisX_.setTitleText("Pulse Time")
        self.addAxis(self.axisX_, Qt.AlignBottom)

        self.axisY_ = QValueAxis(self)
        self.axisY_.setRange(0, 1)
        self.addAxis(self.axisY_, Qt.AlignLeft)
    
    def setTimeBoundaries(self, start, end):
        self.start = start
        self.end = end

        self.axisX().setRange(start, end)
    
    def plot(self, pulses):

        for pulse in pulses:
            series = QLineSeries(self)
            series.append(self.start.toMSecsSinceEpoch() + pulse*1000, 0.)
            series.append(self.start.toMSecsSinceEpoch() + pulse*1000, 0.25)
            series.append(self.start.toMSecsSinceEpoch() + pulse*1000, 0.50)
            series.append(self.start.toMSecsSinceEpoch() + pulse*1000, 0.75)
            series.append(self.start.toMSecsSinceEpoch() + pulse*1000, 1.0)
            self.addSeries(series)
            series.attachAxis(self.axisX())
            series.attachAxis(self.axisY())
