import sys
from PySide6.QtCharts import QChart, QChartView, QLineSeries
from PySide6.QtCore import QPointF
from PySide6.QtGui import QPainter
from PySide6.QtWidgets import QApplication, QMainWindow


class GudPyChartAppTest(QMainWindow):
    def __init__(self):
        super().__init__()
    
    def makeChart(self, path):

        if path.endswith("mint01"):
            self.series = QLineSeries()
            data = open(
                path, "r", encoding="utf-8"
                ).readlines()[14:]
            for item in data:
                x, y, err, *_ = item.split()
                print(float(x), float(y))
                self.series.append(float(x), float(y))
            self.chart = QChart()
            self.chart.legend().hide()
            self.chart.addSeries(self.series)
            self.chart.createDefaultAxes()
            self.chart.setTitle("Mint 01 Example")

            self._chart_view = QChartView(self.chart)
            self._chart_view.setRenderHint(QPainter.Antialiasing)
            self._chart_view.setRubberBand(QChartView.HorizontalRubberBand)
            self.setCentralWidget(self._chart_view)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = GudPyChartAppTest()
    window.makeChart("C:/Users/axe43977/Desktop/gudpy/tests/TestData/water-ref/plain/NIMROD00016608_H2O_in_N9.mint01")
    window.show()
    window.resize(440, 300)
    sys.exit(app.exec())
