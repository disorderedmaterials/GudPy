from PyQt5.QtWidgets import QWidget

class GudPyWidget(QWidget):

    def __init__(self, object, parent):

        self.object = object
        self.parent = parent
        self.widgetMap = {}

        super(GudPyWidget, self).__init__(self.parent)


    def save(self):

        for widget, key in self.widgetMap.items():

            if isinstance(widget, QLineEdit):
                value = widget.text()
            self.object.__dict__[key] = value
