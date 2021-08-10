from PyQt5.QtWidgets import QWidget

from scripts.utils import spacify, numifyBool
from widgets.make_pairs import makeLabelTextPair, makeLabelComboBoxPair

class BeamPane(QWidget):

    def __init__(self, beam, parent, x, y, relHeight, relWidth):
        self.beam = beam
        self.parent = parent
        self.x = x
        self.y = y
        self.relHeight = relHeight
        self.relWidth = relWidth
        super(BeamPane, self).__init__(parent)
        self.setGeometry(
            y,
            0,
            int(self.parent.size().width() * self.relWidth),
            int(self.parent.size().height() * self.relHeight),
        )
        self.childWidth = (self.parent.size().width()*self.relWidth) // 5
        self.childHeight =  (self.parent.size().height() * self.relHeight) // 20
        self.initComponents()

    def initComponents(self):
    	pass
        
        
        
    def updateArea(self):

        self.setGeometry(
            self.y,
            0,
            int(self.parent.size().width() * self.relWidth),
            int(self.parent.size().height() * self.relHeight),
        )
