from PySide6.QtCore import QPoint
from PySide6.QtGui import QSyntaxHighlighter, QTextCharFormat, QTextCursor
from PySide6.QtWidgets import QScrollBar, QPlainTextEdit
from collections import OrderedDict


class VerticalScrollBar(QScrollBar):

    def __init__(self, parent):
        super().__init__(parent)

        self.sliderMoved.connect(
            self.parent().refocus
        )


class Highlighter(QSyntaxHighlighter):
    def __init__(self, parent):
        super().__init__(parent)
        self.highlighted = {}

    def highlightLine(self, line, fmt):
        self.highlighted[line] = fmt
        self.rehighlightBlock(
            self.document().findBlockByLineNumber(
                line
            )
        )

    def clearHighlight(self):
        self.highlighted = {}
        self.rehighlight()

    def highlightBlock(self, text):
        fmt = self.highlighted.get(self.currentBlock().blockNumber())
        self.setFormat(0, len(text), fmt if fmt else QTextCharFormat())


class OutputTextEdit(QPlainTextEdit):

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.verticalScrollBar_ = VerticalScrollBar(self)
        self.setVerticalScrollBar(self.verticalScrollBar_)

    def setOutput(self, output, widget, sampleBackgrounds):
        self.appendPlainText(output)
        self.highlighter = Highlighter(self.document())
        self.buildFmtMap(sampleBackgrounds)
        for sample in [
            s.name for sb in sampleBackgrounds
            for s in sb.samples if s.runThisSample
        ]:
            widget.outputFocusComboBox.addItem(sample)

        widget.outputFocusComboBox.currentTextChanged.connect(
            self.focusChanged
        )

        widget.outputFocusComboBox.setCurrentIndex(
            widget.outputFocusComboBox.count()-1
        )

        self.widget = widget

    def buildFmtMap(self, sampleBackgrounds):
        self.fmtMap = OrderedDict()

        output = self.toPlainText()
        offsets = [
            n for n, l in
            enumerate(output.splitlines(keepends=True))
            if "Got to: SAMPLE BACKGROUND" in l
        ]
        sbindicies = []
        for i in range(len(offsets)-1):
            sbindicies.append([offsets[i], offsets[i+1]-1])

        sbindicies.append([offsets[-1], len(output.splitlines(keepends=True))])
        for sampleBackground, (start, end) in zip(
            sampleBackgrounds, sbindicies
        ):
            splicedOutput = output.splitlines(keepends=True)[start:end]
            indices = [
                n for n, l in
                enumerate(splicedOutput) if "Got to: SAMPLE" in l
            ][1:]
            for sample, index in zip(
                [
                    s for sb in sampleBackgrounds
                    for s in sb.samples
                    if s.runThisSample
                ], indices
            ):
                if not self.fmtMap.keys():
                    self.fmtMap[sample.name] = [index+start]
                else:
                    self.fmtMap[
                        next(reversed(self.fmtMap))
                    ].append(index+start-1)
                    self.fmtMap[sample.name] = [index+start]
            if len(sampleBackground.samples):
                self.fmtMap[next(reversed(self.fmtMap))].append(end)

    def focusChanged(self, sample):
        start, end = self.fmtMap[sample]
        self.highlight(start, end)
        cursor = QTextCursor(self.document().findBlockByLineNumber(start-1))
        self.setTextCursor(cursor)
        self.ensureCursorVisible()

    def highlight(self, start, end):
        fmt = QTextCharFormat()
        fmt.setBackground(self.palette().highlight().color())
        self.highlighter.clearHighlight()
        for n in range(start, end):
            self.highlighter.highlightLine(n, fmt)

    def refocus(self):
        focusedSample = self.focusedSample()
        if focusedSample != self.widget.outputFocusComboBox.currentText():
            start, end = self.fmtMap[focusedSample]
            self.highlight(start, end)
            self.blockSignals(True)
            self.widget.outputFocusComboBox.setCurrentText(focusedSample)
            self.blockSignals(False)

    def wheelEvent(self, e):
        self.refocus()
        return super().wheelEvent(e)

    def focusedSample(self):
        cursor = self.cursorForPosition(QPoint(0, 0))
        start = cursor.blockNumber()
        br = QPoint(self.viewport().width()-1, self.viewport().height()-1)
        end = self.cursorForPosition(br).position()
        cursor.setPosition(end, QTextCursor.KeepAnchor)
        end = cursor.blockNumber()

        currentStart = None
        for sample, (start_, end_) in self.fmtMap.items():
            if currentStart is None:
                currentStart = start_
                ret = sample
            elif abs(start-start_) < abs(start-currentStart):
                currentStart = start_
                ret = sample
        return ret
