from PyQt5.QtWidgets import QComboBox, QLineEdit, QWidget

class GudPyWidget(QWidget):

    def __init__(self, object, parent):

        self.object = object
        self.parent = parent
        self.widgetMap = {}

        super(GudPyWidget, self).__init__(self.parent)


    def save(self, widget, value):
        key = self.widgetMap[widget]
        if isinstance(key, tuple):
            key, index = key
            print(key, index)
            print(f"Previous value: {self.object.__dict__[key][index]}")
            self.object.__dict__[key][index] = value
            print(f"New value: {self.object.__dict__[key][index]}")        
        else:    
            print(f"Previous value: {self.object.__dict__[key]}")
            self.object.__dict__[key] = value
            print(f"New value: {self.object.__dict__[key]}")