class OutputSlots():

    def __init__(self, widget, parent):
        self.widget = widget
        self.parent = parent

    def setOutput(self, output, task):
        self.output = output
        self.task = task
        self.widget.outputTree.buildTree(self.parent.gudrunFile, output, self)
