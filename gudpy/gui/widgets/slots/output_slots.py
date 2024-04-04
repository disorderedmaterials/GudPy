class OutputSlots():

    def __init__(self, widget, parent):
        self.widget = widget
        self.parent = parent

    def setOutputStream(self, stdout):
        self.widget.outputTextEdit.append(
            "".join(stdout.split("\n"))
        )

    def setOutput(self, output, task, gudrunParams=None, keyMap=None):
        if not gudrunParams:
            gudrunParams = self.parent.data.gudrunParams
        self.output = output
        self.task = task
        self.widget.outputTree.buildTree(
            gudrunParams, output, self, keyMap=keyMap
        )
        self.widget.outputTextEdit.verticalScrollBar().setValue(
            self.widget.outputTextEdit.verticalScrollBar(
            ).maximum()
        )
