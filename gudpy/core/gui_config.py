class GUIConfig():
    """
    A simple class for defining the GUI configuration.

    ...

    Attributes
    ----------
    useComponents : bool
        Should components be used?
    yamlignore : str{}
        Class attributes to ignore during yaml serialisation.        
    """
    def __init__(self):
        self.useComponents = False
        self.yamlignore = {
            "yamlignore"
        }
