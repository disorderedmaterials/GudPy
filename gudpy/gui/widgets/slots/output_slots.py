class OutputSlots():

    def __init__(self, widget, parent):
        self.widget = widget
        self.parent = parent

    def setOutput(self, output, task, gudrunFile=None, keyMap=None):
        if not gudrunFile:
            gudrunFile = self.parent.gudrunFile
        self.output = output
        self.task = task
        self.widget.outputTree.buildTree(gudrunFile, output, self, keyMap=keyMap)