from inspect import cleandoc


class Composition:
    def __init__(self, elements, type_):
        self.elements = elements
        self.type_ = type_
        self.str = [
            str(el) + "        " + type_ + " atomic composition"
            for el in self.elements
        ]

    def __str__(self):
        string = ""
        for element in self.elements:
            string += "{}        {} atomic composition".format(
                str(element), self.type_
            )
            string += "\n"
        return cleandoc(string)
