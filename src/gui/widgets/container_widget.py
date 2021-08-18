from PyQt5.QtWidgets import QWidget
from PyQt5 import uic
import os

class ContainerWidget(QWidget):
    """
    Class to represent a ContainerWidget. Inherits QWidget.

    ...

    Attributes
    ----------
    container : Container
        Container object belonging to the GudrunFile.
    parent : QWidget
        Parent widget.
    Methods
    -------
    initComponents()
        Loads UI file, and then populates data from the Container.
    """
    def __init__(self, container, parent=None):
        """
        Constructs all the necessary attributes for the ContainerWidget object.
        Calls the initComponents method, to load the UI file and populate data.
        Parameters
        ----------
        container : Container
            Container object belonging to the GudrunFile.
        parent : QWidget
            Parent widget.
        """
        self.container = container
        self.parent = parent

        super(ContainerWidget, self).__init__(self.parent)
        self.initComponents()
    
    def initComponents(self):
        """
        Loads the UI file for the ContainerWidget object,
        and then populates the child widgets with their
        corresponding data from the attributes of the Container object.
        ----------
        container : Container
            Container object belonging to the GudrunFile.
        parent : QWidget
            Parent widget.
        """

        # Get the current directory that we are residing in.
        current_dir = os.path.dirname(os.path.realpath(__file__))
        # Join the current directory with the relative path of the UI file.
        uifile = os.path.join(current_dir, "ui_files/containerWidget.ui")
        
        # Use pyuic to load to the UI file into the ContainerWidget.
        uic.loadUi(uifile, self)
