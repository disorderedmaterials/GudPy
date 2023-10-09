from gui.widgets.dialogs.iteration_dialog import IterationDialog
from core.iterators import (
    InelasticitySubtractionIterator
)


class InelasticityIterationDialog(IterationDialog):

    def iterate(self):
        self.iterator = InelasticitySubtractionIterator(self.gudrunFile)
        self.numberIterations *= 2
        self.enqueueTasks()
        self.text = "Inelasticity subtractions"
        self.widget.close()
