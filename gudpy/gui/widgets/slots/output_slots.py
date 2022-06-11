class OutputSlots():

    def __init__(self, widget, parent):
        self.widget = widget
        self.parent = parent

    def setOutput(self, output, gudrunFile, task):
        self.output = output
        self.task = task
        self.widget.outputTree.buildTree(output, gudrunFile, self)
