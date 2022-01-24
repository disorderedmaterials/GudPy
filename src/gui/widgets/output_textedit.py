from PySide6.QtWidgets import QTextEdit, QScrollBar, QStyleOptionSlider, QStyle, QLabel, QToolTip
from PySide6.QtGui import QPainter, QRegion, QColor, QPen
from PySide6.QtCore import Qt, QRect
from numpy import indices, maximum
from time import sleep
from src.scripts.utils import nthreplace

class ScrollBarWithBookMarks(QScrollBar):

    def __init__(self, parent=None):
        self.callout = None
        super().__init__(parent=parent)
        self.parent = parent
        self.indices = {}

    def addBookmark(self, key):
        index = self.value()
        lower = index - 10
        upper = index + 10
        if lower < self.minimum():
            lower = self.minimum()
        if upper > self.maximum():
            upper = self.maximum()
        self.indices[key] = (lower, upper)
        # self.indices.append((lower, upper, key))

    def overlayRect(self):
        opt = QStyleOptionSlider()
        self.initStyleOption(opt)
        return self.style().subControlRect(
            QStyle.CC_ScrollBar, opt, QStyle.SC_ScrollBarGroove, self
        )

    def scrollRect(self):
        opt = QStyleOptionSlider()
        self.initStyleOption(opt)
        return self.style().subControlRect(QStyle.CC_ScrollBar, opt,
                                         QStyle.SC_ScrollBarSlider, self)


    def paintEvent(self, event):
        super().paintEvent(event)
        self.rects = {}
        p = QPainter(self)
        opt = QStyleOptionSlider()
        self.initStyleOption(opt)
        gr = self.style().subControlRect(QStyle.CC_ScrollBar, opt,
                                         QStyle.SC_ScrollBarGroove, self)
        sr = self.style().subControlRect(QStyle.CC_ScrollBar, opt,
                                         QStyle.SC_ScrollBarSlider, self)
        p.setClipRegion(QRegion(gr) -QRegion(sr),
                        Qt.IntersectClip)
        x, y, w, h = gr.getRect()
        c = QColor("green")
        p.setBrush(c)
        c.setAlphaF(0.3)
        p.setPen(QPen(c, 2.0))
        yscale = 1.0 / self.parent.document().size().height()
        for key, value in self.indices.items():
            start, end = value
            rect = QRect(x, y + h * start * yscale - 0.5,
                                  w, h * (end - start) * yscale + 1)
            self.rects[rect] = key
        p.drawRects(list(self.rects.keys()))
        p.end()

    def mouseMoveEvent(self, event):
        for rect in self.rects.keys():
            if rect.contains(event.pos()):
                QToolTip.showText(event.globalPos(), self.rects[rect], self.parentWidget())
        return super().mouseMoveEvent(event)
    
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            moved = False
            for rect in self.rects.keys():
                if rect.contains(event.pos()):
                    lower, upper = self.indices[self.rects[rect]]
                    pos = (lower + upper) //2
                    self.setSliderPosition(
                        pos
                    )
                    print("moving!")
                    moved = True
                    break
            if not moved:
                super().mousePressEvent(event)
        return super().mousePressEvent(event)

class OutputTextEdit(QTextEdit):

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setVerticalScrollBar(ScrollBarWithBookMarks(self))

    def setOutput(self, output, sampleBackgrounds):
        self.verticalScrollBar().indices = {}
        anchors, markup = self.createBookmarks(self.toHtml(output), sampleBackgrounds)
        self.setHtml(markup)
        for anchor in anchors:
            self.scrollToAnchor(anchor)
            sleep(1)
            self.verticalScrollBar().addBookmark(anchor)

        self.verticalScrollBar().setValue(self.verticalScrollBar().maximum())

    def toHtml(self, output):
        output = output.replace("\n", "<br/>")
        return f"<html><p>{output}</p></html>"
    
    def createBookmarks(self, output, sampleBackgrounds):
        anchors = []

        # output = nthreplace(output, "Got to: SAMPLE", f"<a name=\"{sampleBackgrounds[0].samples[0].name}\">Got to: SAMPLE</a>", 1)
        # anchors.append(sampleBackgrounds[0].samples[0].name)

        # output = nthreplace(output, "Got to: SAMPLE", f"<a name=\"{sampleBackgrounds[0].samples[1].name}\">Got to: SAMPLE</a>", 2)
        # anchors.append(sampleBackgrounds[0].samples[1].name)

        # output = nthreplace(output, "Got to: SAMPLE", f"<a name=\"{sampleBackgrounds[0].samples[2].name}\">Got to: SAMPLE</a>", 3)
        # anchors.append(sampleBackgrounds[0].samples[2].name)
        
        # output = nthreplace(output, "Got to: SAMPLE", f"<a name=\"{sampleBackgrounds[0].samples[3].name}\">Got to: SAMPLE</a>", 4)
        # anchors.append(sampleBackgrounds[0].samples[3].name)

        for i, sampleBackground in enumerate(sampleBackgrounds):
            for j, sample in enumerate([s for s in sampleBackground.samples if s.runThisSample]):
                output = nthreplace(output, "Got to: SAMPLE", f"<a name=\"{sample.name}\">Got to: SAMPLE</a>", i+j+1)
                anchors.append(sample.name)
        
        return anchors, output