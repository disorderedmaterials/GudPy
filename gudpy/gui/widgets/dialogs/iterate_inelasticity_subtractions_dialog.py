from gui.widgets.dialogs.iteration_dialog import IterationDialog
from core.iterators.wavelength_subtraction_iterator import (
    WavelengthSubtractionIterator
)


class WavelengthInelasticitySubtractionsIterationDialog(IterationDialog):

    def iterate(self):
        self.iterator = WavelengthSubtractionIterator(self.gudrunFile)
        self.numberIterations *= 2
        self.enqueueTasks()
        self.text = "Inelasticity subtractions"
        self.widget.close()
