
from PySide6.QtCore import QAbstractItemModel, QModelIndex, Qt

class PulseComboBoxModel(QAbstractItemModel):
    
    def __init__(self, pulses, parent):
        super(PulseComboBoxModel, self).__init__(parent=parent)
        self.pulses = pulses
    
    def index(self, row, column, parent=QModelIndex()):

        if not self.hasIndex(row, column, parent):
            return QModelIndex()
        else:
            return self.createIndex(row, column, parent)

    def parent(self, index):
        return QModelIndex()
    
    def rowCount(self, parent=QModelIndex()):
        return len(self.pulses)
    
    def columnCount(self, parent=QModelIndex()):
        return 1
    
    def data(self, index, role):
        if role == Qt.DisplayRole:
            return self.pulses[index.row()].label