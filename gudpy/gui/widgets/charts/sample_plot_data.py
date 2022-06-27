from abc import abstractmethod
from PySide6.QtCharts import QLineSeries
from PySide6.QtCore import QPoint, QPointF

from core.gud_file import GudFile


class Point():
    """
    Wrapper class for representing a point, with error.

    ...

    Attributes
    ----------
    x : int | float
        X value.
    y : int | float
        Y value.
    err : int | float
        Error.
    
    Methods
    -------
    toQPointF()
        Returns the internal point as a QPointF.
    toQPoint()
        Returns the internal point as a QPoint.
    """

    def __init__(self, x, y, err):
        """
        Constructs all the necessary attributes for the Point object.

        Parameters
        ----------
        x : int | float
            X value.
        y : int | float
            Y value.
        err : int | float
            Error.
        """
        self.x = x
        self.y = y
        self.err = err

    def toQPointF(self):
        """
        Returns the internal point as a QPointF.

        Returns
        -------
        QPointF : casted point.
        """
        return QPointF(self.x, self.y)

    def toQPoint(self):
        """
        Returns the internal point as a QPoint.

        Returns
        -------
        QPoint : casted point.
        """
        return QPoint(self.x, self.y)


class GudPyPlot():
    """
    Class for wrapping datasets as Qt-style plots.
    In effect, this provides an interface between the data
    and the GudPy plotting functionality.

    ...

    Attributes
    ----------
    path : str
        Path to dataset.
    dataSet : None | Point[]
        Internal dataset.
    
    Methods
    -------
    constructDataSet(path)
        Reads a dataset from a path, and constructs a plottable dataset.
    toQPointList()
        Casts the dataset to a list of QPoints.
    toQPointFList()
        Casts the dataset to a list of QPointFs.
    toLineSeries(parent, offsetX, offsetY)
        Constructs a line series from the dataset.
    """

    def __init__(self, path, exists):
        """
        Constructs all the necessary attributes for the GudPyPlot object.

        Parameters
        ----------
        path : str
            Path to dataset.
        exists : bool
            Whether the path actually exists or not.
        """
        if not exists:
            self.dataSet = None
        else:
            self.dataSet = self.constructDataSet(path)

    @abstractmethod
    def constructDataSet(self, path):
        """
        Reads a dataset from a path and then constructs a plottable dataset.
        This is always called when initialising a GudPyPlot object,
        as long as the path exists.

        Parameters
        ----------
        path : str
            Path to dataset.
        
        Returns
        -------
        dataSet : QPoint[]
        """
        dataSet = []
        with open(path, "r", encoding="utf-8") as fp:
            for dataLine in fp.readlines():

                # Ignore commented lines.
                if dataLine[0] == "#":
                    continue

                # Extract x, y, error
                x, y, err, *__ = [float(n) for n in dataLine.split()]

                # Cast to point and append to dataset.
                dataSet.append(Point(x, y, err))

        return dataSet

    def toQPointList(self):
        """
        Casts the dataset to a list of QPoints.

        Returns
        -------
        QPoint[] : casted dataset.
        """
        return [x.toQPoint() for x in self.dataSet] if self.dataSet else None

    def toQPointFList(self):
        """
        Casts the dataset to a list of QPointFs.

        Returns
        -------
        QPointF[] : casted dataset.
        """
        return [x.toQPointF() for x in self.dataSet] if self.dataSet else None

    def toLineSeries(self, parent, offsetX, offsetY):
        """
        Constructs a line series from the dataset.

        Parameters
        ----------
        parent : Any
            Parent object for the resultant line series.
        offsetX : float
            Offset for X values.
        offsetY : float
            Offset for Y values.
        
        Returns
        -------
        QLineSeries : constructed line series.
        """
        # Create line series.
        self.series = QLineSeries(parent)
        
        # Cast points to QPointF
        points = self.toQPointFList()
        if points:
            # Apply offset to points.
            points = [
                QPointF(p.x() + offsetX, p.y() + offsetY)
                for p in points
            ]
            # Add points to series.
            self.series.append(points)
        return self.series


class Mint01Plot(GudPyPlot):
    """
    Class for representing a Mint01 plot.
    Inherits GudPyPlot.

    ...

    Attributes
    ----------
    XLabel : str
        Label for X-Axis.
    YLabel : str
        Label for Y-Axis.
    """

    def __init__(self, path, exists):
        """
        Constructs all the necessary attributes for the Mint01Plot object.

        Parameters
        ----------
        path : str
            Path to dataset.
        exists : bool
            Whether the path actually exists or not.
        """
        self.path = path

        # Set labels.
        self.XLabel = "Q, 1\u212b"
        self.YLabel = "DCS, barns/sr/atom"
        super(Mint01Plot, self).__init__(path, exists)


class Mdcs01Plot(GudPyPlot):
    """
    Class for representing a Mdcs01 plot.
    Inherits GudPyPlot.

    ...

    Attributes
    ----------
    XLabel : str
        Label for X-Axis.
    YLabel : str
        Label for Y-Axis.
    """

    def __init__(self, path, exists):
        """
        Constructs all the necessary attributes for the Mdcs01Plot object.

        Parameters
        ----------
        path : str
            Path to dataset.
        exists : bool
            Whether the path actually exists or not.
        """
        self.path = path

        # Set labels.
        self.XLabel = "Q, 1\u212b"
        self.YLabel = "DCS, barns/sr/atom"
        super(Mdcs01Plot, self).__init__(path, exists)


class Mdor01Plot(GudPyPlot):
    """
    Class for representing a Mdor01 plot.
    Inherits GudPyPlot.

    ...

    Attributes
    ----------
    XLabel : str
        Label for X-Axis.
    YLabel : str
        Label for Y-Axis.
    """

    def __init__(self, path, exists):
        """
        Constructs all the necessary attributes for the Mdor01Plot object.

        Parameters
        ----------
        path : str
            Path to dataset.
        exists : bool
            Whether the path actually exists or not.
        """
        self.path = path

        # Set labels.
        self.XLabel = "r, \u212b"
        self.YLabel = "G(r)"
        super(Mdor01Plot, self).__init__(path, exists)


class Mgor01Plot(GudPyPlot):
    """
    Class for representing a Mgor01 plot.
    Inherits GudPyPlot.

    ...

    Attributes
    ----------
    XLabel : str
        Label for X-Axis.
    YLabel : str
        Label for Y-Axis.
    """

    def __init__(self, path, exists):
        """
        Constructs all the necessary attributes for the Mgor01Plot object.

        Parameters
        ----------
        path : str
            Path to dataset.
        exists : bool
            Whether the path actually exists or not.
        """
        self.path = path

        # Set labels.
        self.XLabel = "r, \u212b"
        self.YLabel = "G(r)"
        super(Mgor01Plot, self).__init__(path, exists)


class DCSLevel:
    """
    Class for wrapping the DCS level into a Qt-style plot.
    Provides an interface between the GudFile and the GudPy
    plotting functionality.

    ...

    Attributes
    ----------
    path : str
        Path to dataset.
    dcsLevel : float
        DCS level.
    data : QPointF[]
        Extended DCS level.
    visible : bool
        Should this be visible?
    
    Methods
    -------
    extractDCSLevel(path)
        Extract the DCS level from the given path.
    extend(xAxis)
        Extrapolate the DCS level, to extend the entire xAxis.
    toLineSeries(parent)
        Construct a line series from the data.
    """

    def __init__(self, path, exists):
        """
        Constructs all the necessary attributes for the GudPyPlot object.

        Parameters
        ----------
        path : str
            Path to dataset.
        exists : bool
            Whether the path actually exists or not.
        """
        self.path = path
        if not exists:
            self.dcsLevel = None
            self.data = []
        else:
            self.dcsLevel = self.extractDCSLevel(path)
            self.data = []
        self.visible = True

    @abstractmethod
    def extractDCSLevel(self, path):
        """
        Reads the given path in as a GudFile, and extracts the DCS level.

        Parameters
        ----------
        path : str
            Path to read from.
        
        Returns
        -------
        float : expected DCS level.
        """
        gudFile = GudFile(path)
        return gudFile.expectedDCS

    def extend(self, xAxis):
        """
        Extrapolate the DCS level, to extend the entire xAxis.

        Parameters
        ----------
        xAxis : float[]
            X-Axis values to extrapolate until.
        """
        if self.dcsLevel:
            self.data = [QPointF(x, self.dcsLevel) for x in xAxis]

    def toLineSeries(self, parent):
        """
        Construct a line series from the data.

        Parameters
        ----------
        parent : Any
            Parent object for the resultant line series.
        
        Returns
        -------
        QLineSeries : constructed line series.
        """
        self.series = QLineSeries(parent)
        if self.data:
            self.series.append(self.data)
        return self.series
