from PySide6.QtCore import QObject, Signal

from src.gudrun_classes.sample import Sample

class Worker(QObject):
    finished = Signal(Sample, float)
    started = Signal(Sample)
    def work(self, func, cost, args, kwargs):
        self.started.emit(Sample)
        ratio = func(cost, *args, **kwargs)
        self.finished.emit(Sample, ratio)