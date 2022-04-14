

class Pulse():

    def __init__(self, label="", periodOffset=0.0, duration=0.0):
        self.label = label
        self.periodOffset = periodOffset
        self.duration = duration

class Period():

    def __init__(self):
        self.duration = 0.
        self.pulses = []

class ModulationExcitation():

    def __init__(self, gudrunFile):
        self.gudrunFile = gudrunFile
        self.period = Period()
