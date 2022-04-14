from gui.widgets.dialogs.iteration_dialog import IterationDialog
from core.wavelength_subtraction_iterator import (
    WavelengthSubtractionIterator
)


class WavelengthInelasticitySubtractionsIterationDialog(IterationDialog):

    def iterate(self):
        self.iterator = WavelengthSubtractionIterator(self.gudrunFile)
        self.enqueueTasks()
        self.enqueueTasks()
        self.text = "Inelasticity subtractions"
        self.widget.close()
