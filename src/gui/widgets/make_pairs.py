from PyQt5.QtWidgets import QComboBox, QLabel, QLineEdit

<<<<<<< HEAD

=======
>>>>>>> Separated pair making functions from InstrumentPane widget.
def makeLabelComboBoxPair(parent, text, value, values, y, x):
    label = QLabel(parent)
    label.setText(text)
    label.setGeometry(x, y, parent.childWidth, parent.childHeight)
    label.adjustSize()
    combo = QComboBox(parent)
    combo.addItems(values)
    combo.setCurrentIndex(value)
<<<<<<< HEAD
    combo.setGeometry(
        x + label.size().width()+5,
        y, parent.childWidth,
        parent.childHeight//2
    )
    combo.adjustSize()
    return label, combo


=======
    combo.setGeometry(x + label.size().width()+5, y, parent.childWidth, parent.childHeight//2)
    combo.adjustSize()
    return label, combo

>>>>>>> Separated pair making functions from InstrumentPane widget.
def makeLabelTextPair(parent, text, value, y, x, isIterable=False):
    label = QLabel(parent)
    label.setText(text)
    label.setGeometry(x, y, parent.childWidth, parent.childHeight)
    label.adjustSize()
    if not isIterable:
        text = QLineEdit(parent)
        text.setText(str(value))
<<<<<<< HEAD
        text.setGeometry(
            x + label.size().width()+5,
            y, parent.childWidth,
            parent.childHeight//2
        )
=======
        text.setGeometry(x + label.size().width()+5, y, parent.childWidth, parent.childHeight//2)
>>>>>>> Separated pair making functions from InstrumentPane widget.
        text.adjustSize()
        return label, text
    else:
        prev_size = label.size()
        texts = []
        for val in value:
            text = QLineEdit(parent)
            text.setText(str(val))
<<<<<<< HEAD
            text.setGeometry(
                x + prev_size.width() + 5,
                y, parent.childWidth,
                parent.childHeight//2
            )
            text.adjustSize()
            prev_size += text.size()
            texts.append(text)
        return label, texts
=======
            text.setGeometry(x + prev_size.width()+5, y, parent.childWidth, parent.childHeight//2)
            text.adjustSize()
            prev_size+=text.size()
            texts.append(text)
        return label, texts
>>>>>>> Separated pair making functions from InstrumentPane widget.
