from gui.widgets.dialogs.iteration_dialog import IterationDialog
from core.wavelength_subtraction_iterator import (
    WavelengthSubtractionIterator
)


class WavelengthInelasticitySubtractionsIterationDialog(IterationDialog):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.iterator = WavelengthSubtractionIterator(self.gudrunFile)

    def iterate(self):
        self.numberIterations *= 2
        self.enqueueTasks()
        self.text = "Inelasticity subtractions"
        self.widget.close()
