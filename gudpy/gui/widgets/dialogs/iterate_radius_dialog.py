from gui.widgets.dialogs.iteration_dialog import IterationDialog
from core.radius_iterator import RadiusIterator
from core.enums import Geometry
from core import config


class RadiusIterationDialog(IterationDialog):

    def initComponents(self):
        super().initComponents()
        self.widget.iterateButton.setEnabled(
            config.geometry == Geometry.CYLINDRICAL
        )

    def iterate(self):
        self.iterator = RadiusIterator(self.gudrunFile)
        self.iterator.setTargetRadius("inner")
        self.enqueueTasks()
        self.text = "Iterate by Radius"
        self.widget.close()
