from text_area import TextArea


class GudrunFileTextArea(TextArea):
    def __init__(self, parent, relHeight, relWidth):
        super().__init__(parent, relHeight, relWidth)
        self.setReadOnly(True)

    def updateArea(self):

        super().updateArea()
        self.setGeometry(
            int(self.parent.size().width() * (1 - self.relWidth)),
            0,
            int(self.parent.size().width() * self.relWidth),
            int(self.parent.size().height() * self.relHeight),
        )
