from unittest import TestCase

from PySide6.QtCore import QModelIndex, Qt
from src.gudrun_classes.element import Element

from src.gui.widgets.gudpy_tables import (
    BeamProfileModel,
    CompositionModel,
    ExponentialModel,
    GroupingParameterModel,
    GudPyTableModel,
    ResonanceModel,
)


class TestModels(TestCase):
    def testGudPyTableModel(self):

        model = GudPyTableModel([["test"]], ["test"], None)

        self.assertEqual(model._data, [["test"]])
        self.assertEqual(model.headers, ["test"])

        self.assertEqual(model.parent(), None)
        self.assertEqual(model.rowCount(QModelIndex()), 1)
        self.assertEqual(model.columnCount(QModelIndex()), 1)

        self.assertEqual(model.data(QModelIndex(), Qt.EditRole), "test")
        self.assertEqual(
            model.headerData(0, Qt.Horizontal, Qt.DisplayRole), "test"
        )

        self.assertEqual(
            model.flags(QModelIndex()),
            Qt.ItemIsEnabled | Qt.ItemIsEditable | Qt.ItemIsSelectable,
        )

        model.insertRow(["test2"])
        self.assertEqual(model._data, [["test"], ["test2"]])
        self.assertEqual(model.rowCount(QModelIndex()), 2)
        self.assertEqual(
            model.data(model.index(1, 0, QModelIndex()), Qt.EditRole), "test2"
        )

        model.removeRow(1)
        self.assertEqual(model.rowCount(QModelIndex()), 1)

        model.removeRow(0)
        self.assertEqual(model.rowCount(QModelIndex()), 0)

    def testGroupingParameterModel(self):

        model = GroupingParameterModel(
            [[0, 0.0, 0.0, 0.0]],
            ["Group", "XMin", "XMax", "Background Factor"],
            None,
        )

        self.assertEqual(model._data, [[0, 0.0, 0.0, 0.0]])
        self.assertEqual(
            model.headers, ["Group", "XMin", "XMax", "Background Factor"]
        )
        self.assertEqual(model.parent(), None)
        self.assertEqual(model.rowCount(QModelIndex()), 1)
        self.assertEqual(model.columnCount(QModelIndex()), 4)

        self.assertEqual(
            model.data(model.index(0, 0, QModelIndex()), Qt.EditRole), 0
        )
        self.assertEqual(
            model.data(model.index(0, 1, QModelIndex()), Qt.EditRole), 0.0
        )
        self.assertEqual(
            model.data(model.index(0, 2, QModelIndex()), Qt.EditRole), 0.0
        )
        self.assertEqual(
            model.data(model.index(0, 3, QModelIndex()), Qt.EditRole), 0.0
        )

        self.assertEqual(
            model.headerData(0, Qt.Horizontal, Qt.DisplayRole), "Group"
        )
        self.assertEqual(
            model.headerData(1, Qt.Horizontal, Qt.DisplayRole), "XMin"
        )
        self.assertEqual(
            model.headerData(2, Qt.Horizontal, Qt.DisplayRole), "XMax"
        )
        self.assertEqual(
            model.headerData(3, Qt.Horizontal, Qt.DisplayRole),
            "Background Factor",
        )

        model.insertRow()
        self.assertEqual(
            model.data(model.index(1, 0, QModelIndex()), Qt.EditRole), 0
        )
        self.assertEqual(
            model.data(model.index(1, 1, QModelIndex()), Qt.EditRole), 0.0
        )
        self.assertEqual(
            model.data(model.index(1, 2, QModelIndex()), Qt.EditRole), 0.0
        )
        self.assertEqual(
            model.data(model.index(1, 3, QModelIndex()), Qt.EditRole), 0.0
        )

        model.setData(model.index(0, 3, QModelIndex()), 1.0, Qt.EditRole)
        self.assertEqual(
            model.data(model.index(0, 3, QModelIndex()), Qt.EditRole), 1.0
        )

    def testBeamProfileModel(self):

        model = BeamProfileModel([0.0], [], None)

        self.assertEqual(model._data, [0.0])
        self.assertEqual(model.headers, [])
        self.assertEqual(model.parent(), None)
        self.assertEqual(model.rowCount(QModelIndex()), 1)
        self.assertEqual(model.columnCount(QModelIndex()), 1)

        self.assertEqual(
            model.data(model.index(0, 0, QModelIndex()), Qt.EditRole), 0.0
        )
        self.assertEqual(
            model.headerData(0, Qt.Horizontal, Qt.DisplayRole), None
        )

        model.insertRow()
        self.assertEqual(
            model.data(model.index(1, 0, QModelIndex()), Qt.EditRole), 0.0
        )

        model.setData(model.index(0, 0, QModelIndex()), 0.5, Qt.EditRole)
        self.assertEqual(
            model.data(model.index(0, 0, QModelIndex()), Qt.EditRole), 0.5
        )

    def testCompositionModel(self):

        elementA = Element("V", 0, 1.0)
        model = CompositionModel(
            [elementA], ["Element", "Mass No", "Abundance"], None
        )

        self.assertEqual(model._data, [elementA])
        self.assertEqual(model.headers, ["Element", "Mass No", "Abundance"])
        self.assertEqual(model.parent(), None)
        self.assertEqual(model.rowCount(QModelIndex()), 1)
        self.assertEqual(model.columnCount(QModelIndex()), 3)

        self.assertEqual(
            model.data(model.index(0, 0, QModelIndex()), Qt.EditRole), "V"
        )
        self.assertEqual(
            model.data(model.index(0, 1, QModelIndex()), Qt.EditRole), 0
        )
        self.assertEqual(
            model.data(model.index(0, 2, QModelIndex()), Qt.EditRole), 1.0
        )

        self.assertEqual(
            model.headerData(0, Qt.Horizontal, Qt.DisplayRole), "Element"
        )
        self.assertEqual(
            model.headerData(1, Qt.Horizontal, Qt.DisplayRole), "Mass No"
        )
        self.assertEqual(
            model.headerData(2, Qt.Horizontal, Qt.DisplayRole), "Abundance"
        )

        model.insertRow()
        self.assertEqual(
            model.data(model.index(1, 0, QModelIndex()), Qt.EditRole), ""
        )
        self.assertEqual(
            model.data(model.index(1, 1, QModelIndex()), Qt.EditRole), 0
        )
        self.assertEqual(
            model.data(model.index(1, 2, QModelIndex()), Qt.EditRole), 0.0
        )

        model.setData(model.index(1, 0, QModelIndex()), "Ti", Qt.EditRole)
        model.setData(model.index(1, 1, QModelIndex()), 0, Qt.EditRole)
        model.setData(model.index(1, 2, QModelIndex()), 7.16, Qt.EditRole)
        self.assertEqual(
            model.data(model.index(1, 0, QModelIndex()), Qt.EditRole), "Ti"
        )
        self.assertEqual(
            model.data(model.index(1, 1, QModelIndex()), Qt.EditRole), 0
        )
        self.assertEqual(
            model.data(model.index(1, 2, QModelIndex()), Qt.EditRole), 7.16
        )

    def testExponentialModel(self):

        model = ExponentialModel([[0, 1.5]], ["Amplitude", "Decay 1/A"], None)

        self.assertEqual(model._data, [[0, 1.5]])
        self.assertEqual(model.headers, ["Amplitude", "Decay 1/A"])
        self.assertEqual(model.parent(), None)
        self.assertEqual(model.rowCount(QModelIndex()), 1)
        self.assertEqual(model.columnCount(QModelIndex()), 2)

        self.assertEqual(
            model.data(model.index(0, 0, QModelIndex()), Qt.EditRole), 0
        )
        self.assertEqual(
            model.data(model.index(0, 1, QModelIndex()), Qt.EditRole), 1.5
        )
        self.assertEqual(
            model.headerData(0, Qt.Horizontal, Qt.DisplayRole), "Amplitude"
        )
        self.assertEqual(
            model.headerData(1, Qt.Horizontal, Qt.DisplayRole), "Decay 1/A"
        )

        model.insertRow()
        self.assertEqual(
            model.data(model.index(1, 0, QModelIndex()), Qt.EditRole), 0.0
        )
        self.assertEqual(
            model.data(model.index(1, 1, QModelIndex()), Qt.EditRole), 0.0
        )

        model.setData(model.index(0, 0, QModelIndex()), 0.5, Qt.EditRole)
        self.assertEqual(
            model.data(model.index(0, 0, QModelIndex()), Qt.EditRole), 0.5
        )
        model.setData(model.index(0, 1, QModelIndex()), 1.85, Qt.EditRole)
        self.assertEqual(
            model.data(model.index(0, 1, QModelIndex()), Qt.EditRole), 1.85
        )

    def testResonanceModel(self):

        model = ResonanceModel(
            [[0.0, 1.0]], ["Wavelength min", "Wavelength max"], None
        )

        self.assertEqual(model._data, [[0.0, 1.0]])
        self.assertEqual(model.headers, ["Wavelength min", "Wavelength max"])
        self.assertEqual(model.parent(), None)
        self.assertEqual(model.rowCount(QModelIndex()), 1)
        self.assertEqual(model.columnCount(QModelIndex()), 2)

        self.assertEqual(
            model.data(model.index(0, 0, QModelIndex()), Qt.EditRole), 0.0
        )
        self.assertEqual(
            model.data(model.index(0, 1, QModelIndex()), Qt.EditRole), 1.0
        )
        self.assertEqual(
            model.headerData(0, Qt.Horizontal, Qt.DisplayRole),
            "Wavelength min",
        )
        self.assertEqual(
            model.headerData(1, Qt.Horizontal, Qt.DisplayRole),
            "Wavelength max",
        )

        model.insertRow()
        self.assertEqual(
            model.data(model.index(1, 0, QModelIndex()), Qt.EditRole), 0.0
        )
        self.assertEqual(
            model.data(model.index(1, 1, QModelIndex()), Qt.EditRole), 0.0
        )

        model.setData(model.index(0, 0, QModelIndex()), 0.8, Qt.EditRole)
        self.assertEqual(
            model.data(model.index(0, 0, QModelIndex()), Qt.EditRole), 0.8
        )
        model.setData(model.index(0, 1, QModelIndex()), 2.0, Qt.EditRole)
        self.assertEqual(
            model.data(model.index(0, 1, QModelIndex()), Qt.EditRole), 2.0
        )
