import os
from PySide6.QtCore import QFile
from PySide6.QtWidgets import QDialog
from PySide6.QtUiTools import QUiLoader
import sys


class ViewOutputDialog(QDialog):
    """
    Class to represent the ViewOutputDialog. Inherits QDialog.
    This is the dialog window opened when a user wishes to
    view the output of the previously ran proc (purge_det/gudrun_dcs)

    ...

    Attributes
    ----------
    title : str
        The title for the window to use.
    content : str
        Content to be displayed.
    Methods
    -------
    initComponents():
        Loads the UI file for the ViewOutputDialog
    """
    def __init__(self, title, content, parent):
        super(ViewOutputDialog, self).__init__(parent=parent)
        self.title = title
        self.content = content
        self.initComponents()


    def initComponents(self):
        """
        Loads the UI file for the ViewOutputDialog object.
        """
        if hasattr(sys, '_MEIPASS'):
            uifile = QFile(
                os.path.join(
                    sys._MEIPASS, "ui_files", "viewOutputDialog.ui"
                )
            )
        else:
            current_dir = os.path.dirname(os.path.realpath(__file__))
            uifile = QFile(
                os.path.join(
                    current_dir, "..", "ui_files", "viewOutputDialog.ui"
                )
            )
        loader = QUiLoader()
        self.widget = loader.load(uifile)
        self.widget.setWindowTitle(self.title)
        self.widget.contentTextEdit.setText(self.content)
