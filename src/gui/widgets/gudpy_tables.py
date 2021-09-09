from PyQt5.QtWidgets import (
    QDoubleSpinBox,
    QSpinBox,
    QTableWidget,
)
class GroupingParameterTable(QTableWidget):

    def __init__(self, parent):

        super(GroupingParameterTable, self).__init__(parent=parent)
        self.initComponents()
    
    def initComponents(self):

        self.setRowCount(10)
        self.setColumnCount(4)

        for i in range(self.rowCount()):
            for j in range(self.columnCount()):
                self.setCellWidget(i, j , QDoubleSpinBox(self))