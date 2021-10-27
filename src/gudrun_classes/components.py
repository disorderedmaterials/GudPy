
class Component():

    def __init__(self, name):
        self.elements = []
        self.name = name
    
    def addElement(self, element):
        self.elements.append(element)

class Components():
    
    def __init__(self):
        self.components = []
    
    def addComponent(self, component):
        self.components.append(component)