from queue import Queue
from copy import deepcopy

from src.gui.widgets.dialogs.iteration_dialog import IterationDialog
from src.gudrun_classes.composition_iterator import CompositionIterator, calculateTotalMolecules

class CompositionIterationDialog(IterationDialog):
    
    def iterate(self):
        self.iterator = CompositionIterator(self.gudrunFile)
        self.queue = Queue()
        for sampleBackground in self.gudrunFile.sampleBackgrounds:
            for sample in sampleBackground.samples:
                if sample.runThisSample:
                    if [
                        wc for wc in sample.composition.weightedComponents
                        if self.components[0].eq(wc.component)
                    ]:
                        sb = deepcopy(sampleBackground)
                        sb.samples = [deepcopy(sample)]
                        if len(self.iterator.components) == 1:
                            self.queue.put(
                                (
                                    (
                                        [1e-2, self.iterator.ratio, 10],
                                        0,
                                        self.numberIterations,
                                        self.rtol
                                    ),
                                    {
                                        "args": (
                                            self.gudrunFile,
                                            sb,
                                            self.iterator.components
                                        )
                                    },
                                    sample
                                )
                            )
                        elif len(self.iterator.components) == 2:
                            self.queue.put(
                                (
                                    (
                                        [1e-2, self.iterator.ratio, 10],
                                        0,
                                        self.numberIterations,
                                        self.rtol
                                    ),
                                    {
                                        "args": (
                                            self.gudrunFile,
                                            sb,
                                            self.iterator.components,
                                            calculateTotalMolecules(
                                                self.iterator.components,
                                                sample
                                            )
                                        )
                                    },
                                    sample
                                )
                            )
        self.text = "Iterate by Composition"
        self.widget.close()