from src.gui.widgets.dialogs.iteration_dialog import IterationDialog
from src.gudrun_classes.radius_iterator import RadiusIterator

class RadiusIterationDialog(IterationDialog):

    def iterate(self):
        self.iterator = RadiusIterator(self.gudrunFile)
        self.enqueueTasks()
        self.text = "Iterate by Radius"
        self.widget.close()