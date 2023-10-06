from gui.widgets.dialogs.iteration_dialog import IterationDialog
from core.iterators.tweak_factor_iterator import TweakFactorIterator


class TweakFactorIterationDialog(IterationDialog):

    def iterate(self):
        self.iterator = TweakFactorIterator(self.gudrunFile)
        self.enqueueTasks()
        self.text = "Iterate by Tweak Factor"
        self.widget.close()
