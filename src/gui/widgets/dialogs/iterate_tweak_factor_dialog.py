from src.gui.widgets.dialogs.iteration_dialog import IterationDialog
from src.gudrun_classes.tweak_factor_iterator import TweakFactorIterator


class TweakFactorIterationDialog(IterationDialog):

    def iterate(self):
        self.iterator = TweakFactorIterator(self.gudrunFile)
        self.enqueueTasks()
        self.text = "Iterate by Tweak Factor"
        self.widget.close()
