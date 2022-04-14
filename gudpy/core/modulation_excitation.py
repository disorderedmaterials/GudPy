

class Pulse():

    def __init__(self, periodOffset, label, duration):
        self.periodOffset = periodOffset
        self.label = label
        self.duration = duration

class Period():

    def __init__(self):
        self.duration = 0.
        self.pulses = []

class ModulationExcitation():

    def __init__(self, gudrunFile):
        self.gudrunFile = gudrunFile
        self.period = Period()
        