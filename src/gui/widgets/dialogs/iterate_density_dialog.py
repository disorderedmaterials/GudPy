from src.gui.widgets.dialogs.iteration_dialog import IterationDialog
from src.gudrun_classes.density_iterator import DensityIterator

class DensityIterationDialog(IterationDialog):
    
    def iterate(self):
        self.iterator = DensityIterator(self.gudrunFile)
        self.enqueueTasks()
        self.text = "Iterate by Density"
        self.widget.close()