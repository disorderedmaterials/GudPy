from gudpy.gui.widgets.dialogs.iteration_dialog import IterationDialog
from gudpy.core.radius_iterator import RadiusIterator
from gudpy.core.enums import Geometry
from gudpy.core import config


class RadiusIterationDialog(IterationDialog):

    def initComponents(self):
        super().initComponents()
        self.widget.iterateButton.setEnabled(
            config.geometry == Geometry.CYLINDRICAL
        )

    def iterate(self):
        self.iterator = RadiusIterator(self.gudrunFile)
        self.enqueueTasks()
        self.text = "Iterate by Radius"
        self.widget.close()
