from gui.widgets.dialogs.iteration_dialog import IterationDialog
from core.density_iterator import DensityIterator


class DensityIterationDialog(IterationDialog):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.iterator = DensityIterator(self.gudrunFile)

    def iterate(self):
        self.enqueueTasks()
        self.text = "Iterate by Density"
        self.widget.close()
