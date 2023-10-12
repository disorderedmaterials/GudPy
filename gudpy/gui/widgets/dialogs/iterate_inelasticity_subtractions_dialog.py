import os
from queue import Queue
from gui.widgets.dialogs.iteration_dialog import IterationDialog
from core.iterators.wavelength_subtraction_iterator import (
    WavelengthSubtractionIterator
)


class WavelengthInelasticitySubtractionsIterationDialog(IterationDialog):

    def iterate(self):
        self.iterator = WavelengthSubtractionIterator(self.gudrunFile)
        self.enqueueTasks()
        self.text = "Inelasticity subtractions"
        self.widget.close()

    def enqueueTasks(self):
        self.queue = Queue()
        for _ in range((self.numberIterations * 2)):
            self.queue.put(
                self.iterator.gudrunFile.dcs(
                    path=os.path.join(
                        self.gudrunFile.instrument.GudrunInputFileDir,
                        "gudpy.txt"
                    ), headless=False)
            )
