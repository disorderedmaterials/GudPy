from src.gui.widgets.dialogs.iteration_dialog import IterationDialog
from src.gudrun_classes.radius_iterator import RadiusIterator
from src.gudrun_classes.enums import Geometry
from src.gudrun_classes import config


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
