

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
                        return
                    dataSet.append(Point(x, y, err))
                else:
                    x, y = splitLine
                    if lim and x > lim:
                        return
                    dataSet.append(Point(x, y))

        return dataSet


def calcError(d1: DataSet, d2: DataSet) -> DataSet:
    err = DataSet("", exists=False)
    err.dataSet = []
    for p1, p2 in zip(d1.dataSet, d2.dataSet):
        errPoint = p1.x - p2.x
        err.dataSet.append(Point(p1.x, errPoint, 0))
    return err


def meanSquaredError(d1: DataSet, d2: DataSet) -> float:
    # for p1, p2 in zip(d1.dataSet, d2.dataSet):
    # print(p1.y, p2.y)
    # print((p1.y - p2.y)**2)

    return sum((p1.y - p2.y)**2
               for p1, p2 in zip(d1.dataSet, d2.dataSet)
               ) / len(d1.dataSet)
