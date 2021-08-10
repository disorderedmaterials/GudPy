from PyQt5.QtWidgets import QComboBox, QLabel, QLineEdit

<<<<<<< HEAD
<<<<<<< HEAD

=======
>>>>>>> Separated pair making functions from InstrumentPane widget.
=======

>>>>>>> Refactor for PEP8 conformance.
def makeLabelComboBoxPair(parent, text, value, values, y, x):
    label = QLabel(parent)
    label.setText(text)
    label.setGeometry(x, y, parent.childWidth, parent.childHeight)
    label.adjustSize()
    combo = QComboBox(parent)
    combo.addItems(values)
    combo.setCurrentIndex(value)
<<<<<<< HEAD
<<<<<<< HEAD
=======
>>>>>>> Refactor for PEP8 conformance.
    combo.setGeometry(
        x + label.size().width()+5,
        y, parent.childWidth,
        parent.childHeight//2
    )
<<<<<<< HEAD
    combo.adjustSize()
    return label, combo


=======
    combo.setGeometry(x + label.size().width()+5, y, parent.childWidth, parent.childHeight//2)
    combo.adjustSize()
    return label, combo

>>>>>>> Separated pair making functions from InstrumentPane widget.
=======
    combo.adjustSize()
    return label, combo


>>>>>>> Refactor for PEP8 conformance.
def makeLabelTextPair(parent, text, value, y, x, isIterable=False):
    label = QLabel(parent)
    label.setText(text)
    label.setGeometry(x, y, parent.childWidth, parent.childHeight)
    label.adjustSize()
    if not isIterable:
        text = QLineEdit(parent)
        text.setText(str(value))
<<<<<<< HEAD
<<<<<<< HEAD
=======
>>>>>>> Refactor for PEP8 conformance.
        text.setGeometry(
            x + label.size().width()+5,
            y, parent.childWidth,
            parent.childHeight//2
        )
<<<<<<< HEAD
=======
        text.setGeometry(x + label.size().width()+5, y, parent.childWidth, parent.childHeight//2)
>>>>>>> Separated pair making functions from InstrumentPane widget.
=======
>>>>>>> Refactor for PEP8 conformance.
        text.adjustSize()
        return label, text
    else:
        prev_size = label.size()
        texts = []
        for val in value:
            text = QLineEdit(parent)
            text.setText(str(val))
<<<<<<< HEAD
<<<<<<< HEAD
=======
>>>>>>> Refactor for PEP8 conformance.
            text.setGeometry(
                x + prev_size.width() + 5,
                y, parent.childWidth,
                parent.childHeight//2
            )
<<<<<<< HEAD
            text.adjustSize()
            prev_size += text.size()
            texts.append(text)
        return label, texts
=======
            text.setGeometry(x + prev_size.width()+5, y, parent.childWidth, parent.childHeight//2)
=======
>>>>>>> Refactor for PEP8 conformance.
            text.adjustSize()
            prev_size += text.size()
            texts.append(text)
        return label, texts
<<<<<<< HEAD
>>>>>>> Separated pair making functions from InstrumentPane widget.
=======
>>>>>>> Refactor for PEP8 conformance.
