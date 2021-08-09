from PyQt5.QtWidgets import QTextEdit


class TextArea(QTextEdit):
    def __init__(self, parent, relHeight, relWidth):
        self.parent = parent
        self.relHeight = relHeight
        self.relWidth = relWidth

        super().__init__(self.parent)

        self.setFixedHeight(self.relHeight * self.parent.size().height())
        self.setFixedWidth(self.relWidth * self.parent.size().width())
        self.setGeometry(
            int(
                self.parent.size().width()
                - (0.3 * self.parent.size().width())
            ),
            0,
            int(self.parent.size().height()),
            int(0.3 * self.parent.size().width()),
        )
        self.show()

    def updateArea(self):

        self.setFixedHeight(self.relHeight * self.parent.size().height())
        self.setFixedWidth(self.relWidth * self.parent.size().width())
