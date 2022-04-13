from gudpy.gui.widgets.dialogs.iteration_dialog import IterationDialog
from gudpy.core.thickness_iterator import ThicknessIterator
from gudpy.core.enums import Geometry
from gudpy.core import config


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
