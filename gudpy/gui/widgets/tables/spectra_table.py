from PySide6.QtCore import Qt
from PySide6.QtWidgets import QTableView
from src.gui.widgets.tables.gudpy_tables import GudPyTableModel
import h5py as h5

class SpectraModel(GudPyTableModel):
    """
    Class to represent a SpectraModel. Inherits GudPyTableModel.

    ...

    Methods
    -------
    columnCount(parent)
        Returns the number of columns in the model.
    headerData(section, orientation, role)
        Stub method.
    setData(index, value, role)
        Sets data in the model.
    data(index, role)
        Returns data at a given index
    """
    def __init__(self, h5path, headers, parent):
        """
        Calls super().__init__ on the passed parameters.
        Parameters
        ----------
        h5path : str
            Path to hdf5 file.
        headers: str[]
            Column headers for table.
        parent : QWidget
            Parent widget.
        """
        data = []
        with h5.File(h5path) as fp:
            data = fp["/raw_data_1/detector_1/spectrum_index"][()][:].tolist()
        super(SpectraModel, self).__init__(data, headers, parent)

    def columnCount(self, parent):
        """
        Returns the number of columns in the model.
        Parameters
        ----------
        parent : QWidget
            Parent widget.
        Returns
        -------
        int
            Number of columns in the model - this is always 1.
        """
        return 1

    def headerData(self, section, orientation, role):
        """
        There are no headers, so this always returns nothing.
        Returns
        -------
        None
        """
        pass


    def data(self, index, role):
        """
        Returns the data at a given index.
        Parameters
        ----------
        index : QModelIndex
            Index to return data from.
        role : int
            Role
        Returns
        -------
        float
            Data at given index.
        """
        row = index.row()
        if role == role & (Qt.DisplayRole | Qt.EditRole):
            return self._data[row]

    def flags(self, parent):
        return super().flags(parent) & ~Qt.ItemIsEditable

class SpectraTable(QTableView):
    """
    Class to represent a SpectraTable. Inherits QTableView.

    ...
    Attributes
    ----------
    parent : QWidget
        Parent widget.
    Methods
    -------
    makeModel(data)
        Creates the model using the data.
    """
    def __init__(self, parent):
        """
        Constructs all the necessary attributes
        for the BeamProfileTable object.
        Calls super().__init__
        which calls the dunder init method from GudPyTableModel.
        Parameters
        ----------
        parent : QWidget
            Parent widget.
        """
        self.parent = parent
        super(SpectraTable, self).__init__(parent=parent)

    def makeModel(self, h5path):
        """
        Makes the model and the delegate based on the data.
        Parameters
        ----------
        h5path : str
            Path to hdf5 file.
        """
        self.setModel(SpectraModel(h5path, ["Spectra"], self.parent))
