class OutputSlots():

    def __init__(self, widget, parent):
        self.widget = widget
        self.parent = parent

    def setOutputStream(self, output):
        scrollValue = self.widget.outputTextEdit.verticalScrollBar().value()
        scrollBottom = scrollValue == (
            self.widget.outputTextEdit.verticalScrollBar().maximum()
        ) or scrollValue == 0

        self.widget.outputTextEdit.setText(
            output
        )

        if scrollBottom:
            self.widget.outputTextEdit.verticalScrollBar().setValue(
                self.widget.outputTextEdit.verticalScrollBar(
                ).maximum()
            )
        else:
            self.widget.outputTextEdit.verticalScrollBar().setValue(
                scrollValue
            )

    def setOutput(self, output, task, gudrunFile=None, keyMap=None):
        if not gudrunFile:
            gudrunFile = self.parent.gudrunFile
        self.output = output
        self.task = task
        self.widget.outputTree.buildTree(
            gudrunFile, output, self, keyMap=keyMap
        )
        self.widget.outputTextEdit.verticalScrollBar().setValue(
            self.widget.outputTextEdit.verticalScrollBar(
            ).maximum()
        )
