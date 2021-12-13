from PySide6.QtGui import QValidator
from PySide6.QtWidgets import QDoubleSpinBox
from PySide6.QtCore import Qt
import re


class ExponentialValidator(QValidator):
    """
    Class to represent an ExponentialValidator. Inherits QValidator.
    ...

    Attributes
    ----------
    regex : Pattern
        Regular expression pattern to validate against.
    symbols : str[]
        List of symbols.
    Methods
    -------
    valid(string):
        Returns whether a given string is valid or not.
    validate(string, position):
        Returns the state of a string at a given position.
    search(string):
        Searches the string using the regular expression.
    """
    def __init__(self):
        super(ExponentialValidator, self).__init__()
        # Regular expression that matches scientific notation.
        self.regex = re.compile(r"(([+-]?\d+(\.\d*)?|\.\d+)([eE][+-]?\d+)?)")
        # Symbols in scientific notation.
        self.symbols = ["e", ".", "+", "-"]

    def valid(self, string):
        """
        Returns whether a given string is valid or not.

        Parameters
        ----------
        string : str
            String to be checked.
        """
        match = self.regex.search(string)
        return match.group(0) == string if match else ""

    def validate(self, string, position):
        """
        Returns the state of a string at a given position.

        Parameters
        ----------
        string : str
            String to be checked.
        position : int
            Position in string to validate at.
        """
        if self.valid(string):
            return QValidator.State.Acceptable
        if not string:
            return QValidator.State.Intermediate
        if string[position-1] == "e" and len(string) == 1:
            return QValidator.State.Invalid
        if string[position-1] == "-" and len(string) == 1:
            return QValidator.State.Intermediate
        if string[position-1] in self.symbols:
            if string[position-1] in string[:position-1]:
                return QValidator.State.Invalid
            if (
                not string[position-2] == "e"
                and string[position-1] in self.symbols[2:]
            ):
                return QValidator.State.Invalid
            return QValidator.State.Intermediate
        return QValidator.State.Invalid

    def search(self, string):
        """
        Searches the string using the regular expression.

        Parameters
        ----------
        string : str
            String to be checked.
        Returns
        -------
        Match
        """
        return self.regex.search(string)


class ExponentialSpinBox(QDoubleSpinBox):
    """
    Class to represent an ExponentialSpinBox. Inherits QDoubleSpinBox.
    ...

    Attributes
    ----------
    validator : ExponentialValidator
        Validator to use for validation.
    Methods
    -------
    validate(text, position):
        Returns the state of a string at a given position.
    fixup(text):
        Changes text to ensure it is valid.
    valueFromText(text):
        Returns the float value.
    textFromValue(value):
        Returns the string representation.
    search(string):
        Searches the string using the validator.
    stepBy(steps):
        Steps the value in the spin box.
    """
    def __init__(self, parent):
        super(ExponentialSpinBox, self).__init__(parent=parent)
        self.validator = ExponentialValidator()
        self.setDecimals(16)
        self.editingFinished.connect(self.appendSuffix)

    def validate(self, text, position):
        """
        Returns the state of a string at a given position.

        Parameters
        ----------
        text : str
            String to validate.
        position : int
            Position to validate at.
        Returns
        -------
        QValidator.State
        """
        return self.validator.validate(text, position)

    def fixup(self, text):
        """
        Changes text to ensure it is valid.

        Parameters
        ----------
        text: str
            String to fixup.
        Returns
        -------
        str
        """
        match = self.validator.regex.search(text)
        return match.groups()[0] if match else ""

    def valueFromText(self, text):
        """
        Returns the float value.

        Parameters
        ----------
        text: str
            String to convert to float.
        Returns
        -------
        float
        """
        return float(text)

    def textFromValue(self, value):
        """
        Returns the string representation.

        Parameters
        ----------
        value: float
            Float to convert to string.
        Returns
        -------
        str
        """
        return str(value)

    def search(self, string):
        """
        Searches the string using the validator.

        Parameters
        ----------
        string : str
            String to search.
        Returns
        -------
        Match
        """
        return self.validator.search(string)

    def stepBy(self, steps):
        """
        Steps the value in the spin box.

        Parameters
        ----------
        steps : int
            Steps to take.
        """
        groups = [
            group for group in
            self.search(str(float(self.cleanText()))).groups()
        ]
        if groups[0] == self.cleanText():
            mantissa = float(groups[1]) + steps
        else:
            mantissa = float(groups[0]) + steps
        string = "{:g}".format(mantissa)
        if groups[-1]:
            string += groups[-1]
        if float(string) < self.minimum():
            string = str(self.minimum())
        elif float(string) > self.maximum():
            string = str(self.maximum())
        self.lineEdit().setText(string)

    def keyPressEvent(self, event):
        if event.key() == Qt.MouseButton.LeftButton:
            self.focusInEvent(event)
        return super().keyPressEvent(event)

    def removeSuffix(self):
        self.prevSuffix = self.suffix()
        self.setSuffix("")

    def appendSuffix(self):
        self.setSuffix(self.prevSuffix)
        self.clearFocus()

    def focusInEvent(self, event):
        self.removeSuffix()
        return super().focusInEvent(event)

    def focusOutEvent(self, event):
        self.appendSuffix()
        return super().focusOutEvent(event)
