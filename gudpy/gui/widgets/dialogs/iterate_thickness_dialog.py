from gui.widgets.dialogs.iteration_dialog import IterationDialog
from core.thickness_iterator import ThicknessIterator
from core.enums import Geometry
from core import config


class ThicknessIterationDialog(IterationDialog):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.iterator = ThicknessIterator(self.gudrunFile)

    def initComponents(self):
        super().initComponents()
        self.widget.iterateButton.setEnabled(
            config.geometry == Geometry.FLATPLATE
        )

    def iterate(self):
        self.enqueueTasks()
        self.text = "Iterate by Thickness"
        self.widget.close()
