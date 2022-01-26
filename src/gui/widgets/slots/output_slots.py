from collections import OrderedDict
from PySide6.QtCore import QModelIndex


class OutputSlots():


    def __init__(self, widget, parent):
        self.widget = widget
        self.parent = parent
        self.setupOutputSlots()

    def setOutput(self, output, task):
        self.output = output
        self.task = task
        self.constructOutputMap()

    def constructOutputMap(self):
        self.fmtMap = OrderedDict()

        if self.task == "gudrun_dcs":

            offsets = [
                n for n, l in
                enumerate(self.output.splitlines(keepends=True))
                if "Got to: SAMPLE BACKGROUND" in l
            ]
            
            if not offsets:
                self.fmtMap["General"] = [0, len(self.output.splitlines(keepends=True))]
                return

            sbindicies = []
            for i in range(len(offsets)-1):
                sbindicies.append([offsets[i], offsets[i+1]-1])

            sbindicies.append([offsets[-1], len(self.output.splitlines(keepends=True))])

            self.fmtMap["General"] = [0, sbindicies[0][0]]

            for sampleBackground, (start, end) in zip(
                self.parent.gudrunFile.sampleBackgrounds, sbindicies
            ):
                splicedOutput = self.output.splitlines(keepends=True)[start:end]
                indices = [
                    n for n, l in
                    enumerate(splicedOutput) if "Got to: SAMPLE" in l
                ][1:]
                for sample, index in zip(
                    [
                        s for sb in self.parent.gudrunFile.sampleBackgrounds
                        for s in sb.samples
                        if s.runThisSample
                    ], indices
                ):
                    if not [k for k in self.fmtMap.keys() if k!="General"]:
                        self.fmtMap[sample.name] = [index+start]
                    else:
                        self.fmtMap[
                            next(reversed(self.fmtMap))
                        ].append(index+start-1)
                        self.fmtMap[sample.name] = [index+start]
                if len(sampleBackground.samples):
                    self.fmtMap[next(reversed(self.fmtMap))].append(end)
        else:
            self.fmtMap["purge_det"] = [0, len(self.output.splitlines(keepends=True))]

        self.widget.outputFocusList.clear()
        self.widget.outputFocusList.addItems(list(self.fmtMap.keys()))
        self.widget.outputFocusList.setCurrentRow(0)


    def setupOutputSlots(self):
        self.widget.outputFocusList.currentRowChanged.connect(self.giveFocus)

    def giveFocus(self, index):
        if index != -1:
            key = self.widget.outputFocusList.currentItem().text()
            start, end = self.fmtMap[key]
            self.widget.outputTextEdit.setText(
                "\n".join(self.output.splitlines(keepends=True)[start:end])
            )

            
