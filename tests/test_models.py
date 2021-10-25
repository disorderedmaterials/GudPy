from unittest import TestCase

from PySide6.QtCore import QKeyCombination, QModelIndex, Qt

from src.gui.widgets.gudpy_tables import GroupingParameterModel, GudPyTableModel

class TestModels(TestCase):

    def testGudPyTableModel(self):

        model = GudPyTableModel([["test"]], ["test"], None)

        self.assertEqual(model._data, [["test"]])
        self.assertEqual(model.headers, ["test"])

        self.assertEqual(model.parent(), None)
        self.assertEqual(model.rowCount(QModelIndex()), 1)
        self.assertEqual(model.columnCount(QModelIndex()), 1)

        self.assertEqual(model.data(QModelIndex(), Qt.EditRole), "test")
        self.assertEqual(model.headerData(0, Qt.Horizontal, Qt.DisplayRole), "test")

        self.assertEqual(model.flags(QModelIndex()), Qt.ItemIsEnabled | Qt.ItemIsEditable | Qt.ItemIsSelectable)

        model.insertRow(["test2"])
        self.assertEqual(model._data, [["test"], ["test2"]])
        self.assertEqual(model.rowCount(QModelIndex()), 2)
        self.assertEqual(model.data(model.index(1, 0, QModelIndex()), Qt.EditRole), "test2")

        model.removeRow(1)
        self.assertEqual(model.rowCount(QModelIndex()), 1)

        model.removeRow(0)
        self.assertEqual(model.rowCount(QModelIndex()), 0)
    
    def testGroupingParameterModel(self):
        
        model = GroupingParameterModel([[0, 0., 0., 0.]], ["Group", "XMin", "XMax", "Background Factor"], None)

        self.assertEqual(model._data, [[0, 0., 0., 0.]])
        self.assertEqual(model.headers, ["Group", "XMin", "XMax", "Background Factor"])
        self.assertEqual(model.parent(), None)
        self.assertEqual(model.rowCount(QModelIndex()), 1)
        self.assertEqual(model.columnCount(QModelIndex()), 4)

        self.assertEqual(model.data(model.index(0, 0, QModelIndex()), Qt.EditRole), 0)
        self.assertEqual(model.data(model.index(0, 1, QModelIndex()), Qt.EditRole), 0.)
        self.assertEqual(model.data(model.index(0, 2, QModelIndex()), Qt.EditRole), 0.)
        self.assertEqual(model.data(model.index(0, 3, QModelIndex()), Qt.EditRole), 0.)

        self.assertEqual(model.headerData(0, Qt.Horizontal, Qt.DisplayRole), "Group")
        self.assertEqual(model.headerData(1, Qt.Horizontal, Qt.DisplayRole), "XMin")
        self.assertEqual(model.headerData(2, Qt.Horizontal, Qt.DisplayRole), "XMax")
        self.assertEqual(model.headerData(3, Qt.Horizontal, Qt.DisplayRole), "Background Factor")

        model.insertRow()
        self.assertEqual(model.data(model.index(1, 0, QModelIndex()), Qt.EditRole), 0)
        self.assertEqual(model.data(model.index(1, 1, QModelIndex()), Qt.EditRole), 0.)
        self.assertEqual(model.data(model.index(1, 2, QModelIndex()), Qt.EditRole), 0.)
        self.assertEqual(model.data(model.index(1, 3, QModelIndex()), Qt.EditRole), 0.)

        model.setData(model.index(0, 3, QModelIndex()), 1., Qt.EditRole)
        self.assertEqual(model.data(model.index(0, 3, QModelIndex()), Qt.EditRole), 1.)

    def testBeamProfileModel(self):
        pass
    
    def testCompositionModel(self):
        pass

    def testExponentialModel(self):
        pass

    def testResonanceModel(self):
        pass
