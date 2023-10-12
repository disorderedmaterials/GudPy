from gui.widgets.dialogs.iteration_dialog import IterationDialog
from core.iterators.thickness_iterator import ThicknessIterator
from core.enums import Geometry
from core import config


class ThicknessIterationDialog(IterationDialog):

    def initComponents(self):
        super().initComponents()
        self.widget.iterateButton.setEnabled(
            config.geometry == Geometry.FLATPLATE
        )

    def iterate(self):
        self.iterator = ThicknessIterator(self.gudrunFile)
        self.enqueueTasks()
        self.text = "Iterate by Thickness"
        self.widget.close()
