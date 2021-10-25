from unittest import TestCase

from PySide6.QtCore import QKeyCombination, QModelIndex, Qt

from src.gui.widgets.gudpy_tables import GudPyTableModel

class TestModels(TestCase):

    def testGudPyTableModel(self):

        model = GudPyTableModel([["test"]], ["test"], None)

        self.assertEqual([["test"]], model._data)
        self.assertEqual(["test"], model.headers)

        self.assertEqual(None, model.parent())
        self.assertEqual(model.rowCount(QModelIndex()), 1)
        self.assertEqual(model.columnCount(QModelIndex()), 1)

        self.assertEqual(model.data(QModelIndex(), Qt.EditRole), "test")
        self.assertEqual(model.headerData(0, Qt.Horizontal, Qt.DisplayRole), "test")

        self.assertEqual(model.flags(QModelIndex()), Qt.ItemIsEnabled | Qt.ItemIsEditable | Qt.ItemIsSelectable)

        model.insertRow(["test2"])
        self.assertEqual([["test"], ["test2"]], model._data)
        self.assertEqual(model.rowCount(QModelIndex()), 2)
        self.assertEqual(model.data(model.index(1, 0, QModelIndex()), Qt.EditRole), "test2")

        model.removeRow(1)
        self.assertEqual(model.rowCount(QModelIndex()), 1)

        model.removeRow(0)
        self.assertEqual(model.rowCount(QModelIndex()), 0)
    
    def testGroupingParameterModel(self):
        pass

    def testBeamProfileModel(self):
        pass
    
    def testCompositionModel(self):
        pass

    def testExponentialModel(self):
        pass

    def testResonanceModel(self):
        pass
