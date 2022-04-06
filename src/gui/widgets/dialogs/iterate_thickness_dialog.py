from src.gui.widgets.dialogs.iteration_dialog import IterationDialog
from src.gudrun_classes.thickness_iterator import ThicknessIterator
from src.gudrun_classes.enums import Geometry
from src.gudrun_classes import config


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
