from abc import abstractmethod


class Point():
    def __init__(self, x, y, err):
        self.x = x
        self.y = y
        self.err = err


class DataSet():
    # mint01 / mdcs01 / mdor01 / mgor01 / dcs
    def __init__(self, path, exists):
        if not exists:
            self.dataSet = None
        else:
            self.dataSet = self.constructDataSet(path)

    @abstractmethod
    def constructDataSet(self, path):
        dataSet = []
        with open(path, "r", encoding="utf-8") as fp:
            for dataLine in fp.readlines():

                # Ignore commented lines.
                if dataLine[0] == "#":
                    continue

                x, y, err, *__ = [float(n) for n in dataLine.split()]
                dataSet.append(Point(x, y, err))
        return dataSet


def calcError(d1: DataSet, d2: DataSet) -> DataSet:
    err = DataSet("", exists=False)
    err.dataSet = []
    for p1, p2 in zip(d1.dataSet, d2.dataSet):
        errPoint = p1.x - p2.x
        err.dataSet.append(Point(p1.x, errPoint, 0))
    return err
