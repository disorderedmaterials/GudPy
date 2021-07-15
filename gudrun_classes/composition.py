from inspect import cleandoc


class Composition:
    def __init__(self, elements, type_):
        self.elements = elements
        # print(elements)
        self.type_ = type_
        self.str = [str(el) +'        ' + type_ + ' atomic composition' for el in self.elements]

    
    def __str__(self):
        string = ''
        for element in self.elements:
            string+=( '{}        {} atomic composition'.format(str(element), self.type_))
            string+='\n'
        # for element in self.elements:
        #     string+=cleandoc("""{}       {} atomic composition""".format(
        #                                                 str(element),
        #                                                 self.type_
        #     ))
        # return '\n'.join(self.str)                               
        # return cleandoc(string)
        # string =''
        # for element in self.elements:
        #     string+= '{}        {} atomic composition'.format(str(element), self.type_)
        #     string+='\n'
        # print(cleandoc(string))
        return cleandoc(string)

        # return ('\n'.join([str(x) for x in self.elements]))
        # return ('\n'.join(self.str))