from PyQt5.QtWidgets import QComboBox, QLabel, QLineEdit

def makeLabelComboBoxPair(parent, text, value, values, y, x):
    label = QLabel(parent)
    label.setText(text)
    label.setGeometry(x, y, parent.childWidth, parent.childHeight)
    label.adjustSize()
    combo = QComboBox(parent)
    combo.addItems(values)
    combo.setCurrentIndex(value)
    combo.setGeometry(x + label.size().width()+5, y, parent.childWidth, parent.childHeight//2)
    combo.adjustSize()
    return label, combo

def makeLabelTextPair(parent, text, value, y, x, isIterable=False):
    label = QLabel(parent)
    label.setText(text)
    label.setGeometry(x, y, parent.childWidth, parent.childHeight)
    label.adjustSize()
    if not isIterable:
        text = QLineEdit(parent)
        text.setText(str(value))
        text.setGeometry(x + label.size().width()+5, y, parent.childWidth, parent.childHeight//2)
        text.adjustSize()
        return label, text
    else:
        prev_size = label.size()
        texts = []
        for val in value:
            text = QLineEdit(parent)
            text.setText(str(val))
            text.setGeometry(x + prev_size.width()+5, y, parent.childWidth, parent.childHeight//2)
            text.adjustSize()
            prev_size+=text.size()
            texts.append(text)
        return label, texts