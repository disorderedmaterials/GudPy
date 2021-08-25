from PyQt5.QtWidgets import QWidget

class GudPyWidget(QWidget):

    def __init__(self, object, parent):

        self.object = object
        self.parent = parent
        self.widgetMap = {}

        super(GudPyWidget, self).__init__(self.parent)


    def save(self, widget, value):
        self.object[self.widgetMap[widget]] = value