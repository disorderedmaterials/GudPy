import numpy


class Point():
    def __init__(self, x, y, err=0.0):
        self.x = x
        self.y = y
        self.err = err


class DataSet():
    # mint01 / mdcs01 / mdor01 / mgor01 / dcs
    def __init__(self, path, exists, lim=None):
        if not exists:
            self.dataSet = None
        else:
            self.dataSet = self.constructDataSet(path, lim)

    def constructDataSet(self, path, lim=None):
        dataSet = []
        with open(path, "r", encoding="utf-8") as fp:
            for dataLine in fp.readlines():

                # Ignore commented lines.
                if dataLine[0] == "#":
                    continue

                splitLine = [float(n) for n in dataLine.split()]
                if len(splitLine) > 2:
                    x, y, err, *__ = splitLine
                    if lim and x > lim:
                        return dataSet
                    dataSet.append(Point(x, y, err))
                else:
                    x, y = splitLine
                    if lim and x > lim:
                        return dataSet
                    dataSet.append(Point(x, y))

        return dataSet


class NpDataSet():
    # mint01 / mdcs01 / mdor01 / mgor01 / dcs
    def __init__(self, path, lim=None):
        self.LIMIT = lim
        self.x = []
        self.y = []

        with open(path, "r", encoding="utf-8") as fp:
            for dataLine in fp.readlines():

                # Ignore commented lines.
                if dataLine[0] == "#":
                    continue

                splitLine = [float(n) for n in dataLine.split()]
                x, y, *__ = splitLine
                if lim and x > lim:
                    break
                self.x.append(x)
                self.y.append(y)

        if not self.LIMIT:
            self.LIMIT = self.x[-1]

        self.x = numpy.array(self.x)
        self.y = numpy.array(self.y)

        self.interpolate()

    def interpolate(self):
        xnew = numpy.round(numpy.arange(0, self.LIMIT, 0.015), 4)
        ynew = numpy.interp(xnew, self.x, self.y)
        self.x = xnew
        self.y = ynew


def meanSquaredError(d1: NpDataSet, d2: NpDataSet) -> float:
    return sum((y1 - y2)**2
               for y1, y2 in zip(d1.y, d2.y)
               ) / len(d1.y)
