from gui.widgets.dialogs.iteration_dialog import IterationDialog
from core.tweak_factor_iterator import TweakFactorIterator


class TweakFactorIterationDialog(IterationDialog):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.iterator = TweakFactorIterator(self.gudrunFile)

    def iterate(self):
        self.enqueueTasks()
        self.text = "Iterate by Tweak Factor"
        self.widget.close()
