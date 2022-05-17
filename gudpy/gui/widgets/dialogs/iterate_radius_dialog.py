from gui.widgets.dialogs.iteration_dialog import IterationDialog
from core.radius_iterator import RadiusIterator
from core.enums import Geometry
from core import config


class RadiusIterationDialog(IterationDialog):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.iterator = RadiusIterator(self.gudrunFile)
        self.iterator.setTargetRadius("inner")

    def initComponents(self):
        super().initComponents()
        self.widget.iterateButton.setEnabled(
            config.geometry == Geometry.CYLINDRICAL
        )

    def iterate(self):
        self.enqueueTasks()
        self.text = "Iterate by Radius"
        self.widget.close()
