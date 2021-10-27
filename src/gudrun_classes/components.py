
class Component():

    def __init__(self, name):
        self.elements = []
        self.name = name
        self.ratio = 1.
    
    def addElement(self, element):
        self.elements.append(element)
    
    def setRatio(self, ratio):
        self.ratio = ratio

class Components():
    
    def __init__(self):
        self.components = []
    
    def addComponent(self, component):
        self.components.append(component)