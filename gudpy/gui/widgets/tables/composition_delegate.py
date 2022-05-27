from PySide6.QtWidgets import QLineEdit, QComboBox
from PySide6.QtCore import Qt
from core.isotopes import Sears91
from gui.widgets.core.exponential_spinbox import ExponentialSpinBox
from gui.widgets.tables.gudpy_tables import GudPyDelegate


class CompositionDelegate(GudPyDelegate):
    """
    Class to represent a CompositionDelegate. Inherits GudPyDelegate.

    ...

    Methods
    -------
    createEditor(parent, option, index)
        Creates an editor.
    setEditorData(editor, index)
        Sets data at a specific index inside the editor.
    setModelData(editor, model, index)
        Sets data at a specific index inside the model.
    """

    def createEditor(self, parent, option, index):
        """
        Creates an editor, and returns it.
        Parameters
        ----------
        parent : QWidget
            Parent widget.
        option : QStyleOptionViewItem
            Option.
        index : QModelIndex
            Index in to create editor at.
        Returns
        -------
        QLineEdit | QSpinBox | QDoubleSpinBox
            The created editor.
        """
        col = index.column()
        if col == 0:
            editor = QLineEdit(parent)
        elif col == 1:
            editor = QComboBox(parent)
            sears91 = Sears91()
            element = index.model().data(
                index.model().index(index.row(), 0, index.parent()),
                Qt.EditRole
            )
            isotope = index.model().data(
                index.model().index(index.row(), 1, index.parent()),
                Qt.EditRole
            )
            for isotope_ in sears91.isotopes(element):
                editor.addItem(
                    sears91.isotope(isotope_),
                    sears91.mass(isotope_)
                )
            editor.setCurrentText(isotope)
        else:
            editor = ExponentialSpinBox(parent)
        return editor

    def setEditorData(self, editor, index):
        """
        Sets data at a specific index inside the editor.
        Parameters
        ----------
        editor : QWidget
            The editor widet.
        index : QModelIndex
            Index in the model to set data at.
        """
        value = index.model().data(index, Qt.EditRole)
        if index.column() == 0:
            sears91 = Sears91()
            if sears91.isIsotope(value, 0):
                editor.setText(value)
        elif index.column() == 2:
            editor.setValue(value)

    def setModelData(self, editor, model, index):
        """
        Sets data at a specific index inside the model.
        Parameters
        ----------
        editor : QWidget
            The editor widet.
        model : GudPyTableModel
            Model to set data inside.
        index : QModelIndex
            Index in the model to set data at.
        """
        if index.column() == 0:
            value = editor.text()
        elif index.column() == 1:
            value = editor.currentData()
        elif index.column() == 2:
            try:
                editor.interpretText()
                value = editor.value()
            except Exception:
                value = 0
        model.setData(index, value, Qt.EditRole)
