from PyQt5.QtWidgets import QComboBox, QLineEdit, QWidget

class GudPyWidget(QWidget):

    def __init__(self, object, parent):

        self.object = object
        self.parent = parent
        self.widgetMap = {}

        super(GudPyWidget, self).__init__(self.parent)


    def save(self, widget, value):
        print(f"Previous value: {self.object.__dict__[self.widgetMap[widget]]}")
        self.object.__dict__[self.widgetMap[widget]] = value
        print(f"New value: {self.object.__dict__[self.widgetMap[widget]]}")

    def setUpSignals(self):
        for widget in self.widgetMap.keys():
            if isinstance(widget, QLineEdit):
                widget.textChanged.connect(lambda text : self.save(widget, text))