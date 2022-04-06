from src.gui.widgets.dialogs.iteration_dialog import IterationDialog
from src.gudrun_classes.thickness_iterator import ThicknessIterator

class ThicknessIterationDialog(IterationDialog):

    def iterate(self):
        self.iterator = ThicknessIterator(self.gudrunFile)
        self.enqueueTasks()
        self.text = "Iterate by Thickness"
        self.widget.close()