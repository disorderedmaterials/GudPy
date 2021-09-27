from src.gudrun_classes.enums import (
    CrossSectionSource,
    Geometry,
    NormalisationType,
    OutputUnits,
    UnitsOfDensity,
)
from PyQt5.QtWidgets import QFileDialog, QWidget
from PyQt5 import uic
from PyQt5.QtCore import Qt
import os
from src.gudrun_classes import config


class SampleWidget(QWidget):
    """
    Class to represent a SampleWidget. Inherits QWidget.

    ...

    Attributes
    ----------
    sample : Sample
        Sample object belonging to the GudrunFile.
    parent : QWidget
        Parent widget.
    Methods
    -------
    loadUI()
        Loads the UI file for the SampleWidget object.
    setSample(sample)
        Gives the focus of the SampleWidget to the sample.
    initComponents()
        Loads UI file, and then populates data from the Sample.
    handlePeriodNoChanged(value)
        Slot for handling change in the period number.
    handleForceCorrectionsSwitched(state)
        Slot for handling switching forcing correction calculations on/off.
    handleGeometryChanged(index)
        Slot for handling change in the geometry.
    handleUpstreamThicknessChanged(value)
        Slot for handling change in the upstream thickness.
    handleDownstreamThicknessChanged(value)
        Slot for handling change in the downstream thickness.
    handleInnerRadiiChanged(value)
        Slot for handling change in the inner radii.
    handleOuterRadiiChanged(value)
        Slot for handling change to the outer radii.
    handleDensityChanged(value)
        Slot for handling change to the density.
    handleDensityUnitsChanged(index)
        Slot for handling change to the density units.
    handleTotalCrossSectionChanged(index)
        Slot for handling change in the total cross section source.
    handleTweakFactorChanged(value)
        Slot for handling change in the sample tweak factor.
    handleTopHatWidthChanged(value)
        Slot for handling change in the top had width for FT.
    handleMinChanged(value)
        Slot for handling change in the minimum radius for FT.
    handleMaxChanged(value)
        Slot for handling change in the maximum radius for FT.
    handleBroadeningFunctionChanged(value)
        Slot for handling change in g(r) broadening at r = 1A.
    handleBroadeningPowerChanged(value)
        Slot for handling change in the power for broadening.
    handleStepSizeChanged(value)
        Slot for handling change in the step size in radius for final g(r).
    handleSelfScatteringFileChanged(value)
        Slot for handling change in the file name for self scattering.
    handleNormaliseToChanged(index)
        Slot for handling change in the normalisation type.
    handleOutputUnitsChanged(index)
        Slot for handling change in the output units.
    handleAngleOfRotationChanged(value)
        Slot for handling change in the angle of rotation.
    handleSampleWidthChanged(value)
        Slot for handling change in the sample width.
    handleSampleHeightChanged(value)
        Slot for handling change in the sample height.
    handleCorrectionFactorChanged(value)
        Slot for handling change in the normalisation correction factor.
    handleScatteringFractionChanged(value)
        Slot for handling change in the environment scattering fraction.
    handleAttenuationCoefficientChanged(value)
        Slot for handling change in the environment attenuation coefficient.
    handleDataFilesAltered(item)
        Slot for handling changes to the data files list.
    handleDataFileInserted(item)
        Slot for handling insertion to the data files list.
    updateDataFilesList()
        Fills the data files list.
    addFiles(target, title, regex)
        Slot for adding files to a target list.
    removeFile(target, dataFiles)
        Slot for removing data files from a target list.
    updateCompositionTable()
        Fills the composition table.
    handleInsertElement()
        Slot for handling insertion to the composition table.
    handleRemoveElement()
        Slot for removing the selected element from the composition table.
    updateExponentialTable()
        Fills the exponential table.
    updateResonanceTable()
        Fills the resonance table.
    handleInsertExponentialValue()
        Slot for handling insertion to the exponential table.
    handleRemoveExponentialValue()
        Slot for handling removing values from the exponential table.
    handleInsertResonanceValue()
        Slot for handling insertion to the resonance table.
    handleRemoveResonanceValue()
        Slot for handling removing values from the resonance table.
    """

    def __init__(self, parent=None):
        """
        Constructs all the necessary attributes for the SampleWidget object.
        Parameters
        ----------
        parent : QWidget
            Parent widget.
        """
        self.parent = parent
        super(SampleWidget, self).__init__(parent=self.parent)
        self.loadUI()
        self.connectSlots()
    def setSample(self, sample):
        """
        Gives the focus of the SampleWidget to the sample.
        Calls the initComponents method, to load the UI file and populate data.
        Parameters
        ----------
        sample : Sample
            Sample object belonging to the GudrunFile.
        """
        self.sample = sample
        self.initComponents()

    def loadUI(self):
        """
        Loads the UI file for the SampleWidget object.
        """
        current_dir = os.path.dirname(os.path.realpath(__file__))
        uifile = os.path.join(current_dir, "ui_files/sampleWidget.ui")
        uic.loadUi(uifile, self)

    def handlePeriodNoChanged(self, value):
        """
        Slot for handling change in the period number.
        Called when a valueChanged signal is emitted,
        from the periodNoSpinBox.
        Alters the sample's period number as such.
        Parameters
        ----------
        value : float
            The new value of the periodNoSpinBox.
        """
        self.sample.periodNo = value
        if not self.widgetsRefreshing:
            self.parent.setModified()

    def handleForceCorrectionsSwitched(self, state):
        """
        Slot for handling switching forcing correction calculations on/off.
        Called when a stateChanged signal is emitted,
        from the forceCorrectionsCheckBox.
        Alters the sample's forcing calculations of
        corrections as such.
        Parameters
        ----------
        state : int
            The new state of the forceCorrectionsCheckBox (1: True, 0: False)
        """
        self.sample.forceCalculationOfCorrections = state
        if not self.widgetsRefreshing:
            self.parent.setModified()

    def handleGeometryChanged(self, index):
        """
        Slot for handling change in sample geometry.
        Called when a currentIndexChanged signal is emitted,
        from the geometryComboBox.
        Alters the sample geometry as such.
        Parameters
        ----------
        index : int
            The new current index of the geometryComboBox.
        """
        self.sample.geometry = self.geometryComboBox.itemData(index)
        self.geometryInfoStack.setCurrentIndex(self.sample.geometry.value)
        self.geometryInfoStack_.setCurrentIndex(self.sample.geometry.value)

    def handleUpstreamThicknessChanged(self, value):
        """
        Slot for handling change in the upstream thickness.
        Called when a valueChanged signal is emitted,
        from the upstreamSpinBox.
        Alters the sample's upstream thickness as such.
        Parameters
        ----------
        value : float
            The new value of the upstreamSpinBox.
        """
        self.sample.upstreamThickness = value
        if not self.widgetsRefreshing:
            self.parent.setModified()

    def handleDownstreamThicknessChanged(self, value):
        """
        Slot for handling change in the downstream thickness.
        Called when a valueChanged signal is emitted,
        from the downstreamSpinBox.
        Alters the sample's downstream thickness as such.
        Parameters
        ----------
        value : float
            The new value of the downstreamSpinBox.
        """
        self.sample.downstreamThickness = value
        if not self.widgetsRefreshing:
            self.parent.setModified()

    def handleInnerRadiiChanged(self, value):
        """
        Slot for handling change in the inner radii.
        Called when a valueChanged signal is emitted,
        from the innerRadiiSpinBox.
        Alters the sample's inner radius as such.
        Parameters
        ----------
        value : float
            The new value of the innerRadiiSpinBox.
        """
        self.sample.innerRadius = value
        if not self.widgetsRefreshing:
            self.parent.setModified()

    def handleOuterRadiiChanged(self, value):
        """
        Slot for handling change in the outer radii.
        Called when a valueChanged signal is emitted,
        from the outerRadiiSpinBox.
        Alters the sample's outer radius as such.
        Parameters
        ----------
        value : float
            The new value of the outerRadiiSpinBox.
        """
        self.sample.outerRadius = value
        if not self.widgetsRefreshing:
            self.parent.setModified()

    def handleDensityChanged(self, value):
        """
        Slot for handling change in density.
        Called when a valueChanged signal is emitted,
        from the densitySpinBox.
        Alters the sample density as such.
        Parameters
        ----------
        value : float
            The new current index of the densitySpinBox.
        """
        self.sample.density = value
        if not self.widgetsRefreshing:
            self.parent.setModified()

    def handleDensityUnitsChanged(self, index):
        """
        Slot for handling change in density units.
        Called when a currentIndexChanged signal is emitted,
        from the densityUnitsComboBox.
        Alters the sample density units as such.
        Parameters
        ----------
        index : int
            The new current index of the densityUnitsComboBox.
        """
        self.sample.densityUnits = self.densityUnitsComboBox.itemData(index)
        if not self.widgetsRefreshing:
            self.parent.setModified()

    def handleCrossSectionSourceChanged(self, index):
        """
        Slot for handling change in total cross section source.
        Called when a currentIndexChanged signal is emitted,
        from the totalCrossSectionComboBox.
        Alters the sample's total cross section source as such.
        Parameters
        ----------
        index : int
            The new current index of the totalCrossSectionComboBox.
        """
        self.sample.totalCrossSectionSource = (
            self.totalCrossSectionComboBox.itemData(index)
        )
        if not self.widgetsRefreshing:
            self.parent.setModified()

    def handleTweakFactorChanged(self, value):
        """
        Slot for handling change in the sample tweak factor.
        Called when a valueChanged signal is emitted,
        from the the tweakFactorSpinBox.
        Alters the sample's tweak factor as such.
        Parameters
        ----------
        value : float
            The new current value of the tweakFactorSpinBox.
        """
        self.sample.tweakFactor = value
        if not self.widgetsRefreshing:
            self.parent.setModified()

    def handleTopHatWidthChanged(self, value):
        """
        Slot for handling change in the top hat width.
        Called when a valueChanged signal is emitted,
        from the the topHatWidthSpinBox.
        Alters the sample's top hat width as such.
        Parameters
        ----------
        value : float
            The new current value of the topHatWidthSpinBox.
        """
        self.sample.topHatW = value
        if not self.widgetsRefreshing:
            self.parent.setModified()

    def handleMinChanged(self, value):
        """
        Slot for handling change in the minimum radius for FT.
        Called when a valueChanged signal is emitted,
        from the the minSpinBox.
        Alters the sample's minimum radius for FT as such.
        Parameters
        ----------
        value : float
            The new current value of the minSpinBox.
        """
        self.sample.minRadFT = value
        if not self.widgetsRefreshing:
            self.parent.setModified()

    def handleMaxChanged(self, value):
        """
        Slot for handling change in the maximum radius for FT.
        Called when a valueChanged signal is emitted,
        from the the maxSpinBox.
        Alters the sample's maximum radius for FT as such.
        Parameters
        ----------
        value : float
            The new current value of the maxSpinBox.
        """
        self.sample.maxRadFT = value
        if not self.widgetsRefreshing:
            self.parent.setModified()

    def handleBroadeningFunctionChanged(self, value):
        """
        Slot for handling change in g(r) broadening at r = 1A.
        Called when a valueChanged signal is emitted,
        from the the broadeningFunctionSpinBox.
        Alters the sample's broadening function as such.
        Parameters
        ----------
        value : float
            The new current value of the broadeningFunctionSpinBox.
        """
        self.sample.grBroadening = value
        if not self.widgetsRefreshing:
            self.parent.setModified()

    def handleBroadeningPowerChanged(self, value):
        """
        Slot for handling change in the power for broadening.
        Called when a valueChanged signal is emitted,
        from the the broadeningPowerSpinBox.
        Alters the sample's broadening power as such.
        Parameters
        ----------
        value : float
            The new current value of the broadeningPowerSpinBox.
        """
        self.sample.powerForBroadening = value
        if not self.widgetsRefreshing:
            self.parent.setModified()

    def handleStepSizeChanged(self, value):
        """
        Slot for handling change in the step size in radius for final g(r).
        Called when a valueChanged signal is emitted,
        from the stepSizeSpinBox.
        Alters the sample's step size as such.
        Parameters
        ----------
        value : float
            The new current value of the stepSizeSpinBox.
        """
        self.sample.stepSize = value
        if not self.widgetsRefreshing:
            self.parent.setModified()

    def handleSelfScatteringFileChanged(self, value):
        """
        Slot for handling change in the file name for self scattering.
        Called when a textChanged signal is emitted,
        from the scatteringFileLineEdit.
        Alters the sample's file for self scattering as such.
        Parameters
        ----------
        value : str
            The new current text of the scatteringFileLineEdit.
        """
        self.sample.fileSelfScattering = value
        if not self.widgetsRefreshing:
            self.parent.setModified()

    def handleNormaliseToChanged(self, index):
        """
        Slot for handling change in the normalisation type.
        Called when a currentIndexChanged signal is emitted,
        from the normaliseToComboBox.
        Alters the sample's total cross section source as such.
        Parameters
        ----------
        index : int
            The new current index of the normaliseToComboBox.
        """
        self.sample.normaliseTo = self.normaliseToComboBox.itemData(index)
        if not self.widgetsRefreshing:
            self.parent.setModified()

    def handleOutputUnitsChanged(self, index):
        """
        Slot for handling change in the output units.
        Called when a currentIndexChanged signal is emitted,
        from the outputUnitsComboBox.
        Alters the sample's output units as such.
        Parameters
        ----------
        index : int
            The new current index of the outputUnitsComboBox.
        """
        self.sample.outputUnits = self.outputUnitsComboBox.itemData(index)
        if not self.widgetsRefreshing:
            self.parent.setModified()

    def handleAngleOfRotationChanged(self, value):
        """
        Slot for handling change in angle of rotation.
        Called when a valueChanged signal is emitted,
        from the angleOfRotationSpinBox.
        Alters the sample's angle of rotation as such.
        Parameters
        ----------
        value : float
            The new current value of the angleOfRotationSpinBox.
        """
        self.sample.angleOfRotation = value
        if not self.widgetsRefreshing:
            self.parent.setModified()

    def handleSampleWidthChanged(self, value):
        """
        Slot for handling change in sample width.
        Called when a valueChanged signal is emitted,
        from the sampleWidthSpinBox.
        Alters the sample's width as such.
        Parameters
        ----------
        value : float
            The new current value of the sampleWidthSpinBox.
        """
        self.sample.sampleWidth = value
        if not self.widgetsRefreshing:
            self.parent.setModified()

    def handleSampleHeightChanged(self, value):
        """
        Slot for handling change in sample height.
        Called when a valueChanged signal is emitted,
        from the sampleHeightSpinBox.
        Alters the sample's height as such.
        Parameters
        ----------
        value : float
            The new current value of the sampleHeightSpinBox.
        """
        self.sample.sampleHeight = value
        if not self.widgetsRefreshing:
            self.parent.setModified()

    def handleCorrectionFactorChanged(self, value):
        """
        Slot for handling change in the normalisation correction factor.
        Called when a valueChanged signal is emitted,
        from the correctionFactorSpinBox.
        Alters the sample's normalisation correction factor as such.
        Parameters
        ----------
        value : float
            The new current value of the correctionFactorSpinBox.
        """
        self.sample.normalisationCorrectionFactor = value
        if not self.widgetsRefreshing:
            self.parent.setModified()

    def handleScatteringFractionChanged(self, value):
        """
        Slot for handling change in the environment scattering fraction.
        Called when a valueChanged signal is emitted,
        from the scatteringFractionSpinBox.
        Alters the sample's scattering fraction as such.
        Parameters
        ----------
        value : float
            The new current value of the scatteringFractionSpinBox.
        """
        self.sample.scatteringFraction = value
        if not self.widgetsRefreshing:
            self.parent.setModified()

    def handleAttenuationCoefficientChanged(self, value):
        """
        Slot for handling change in the environment attenuation coefficient.
        Called when a valueChanged signal is emitted,
        from the attenuationCoefficientSpinBox.
        Alters the sample's attenuation coefficient as such.
        Parameters
        ----------
        value : float
            The new current value of the attenuationCoefficientSpinBox.
        """
        self.sample.attenuationCoefficient = value
        if not self.widgetsRefreshing:
            self.parent.setModified()

    def handleDataFilesAltered(self, item):
        """
        Slot for handling an item in the data files list being changed.
        Called when an itemChanged signal is emitted,
        from the dataFilesList.
        Alters the sample's data files as such.
        Parameters
        ----------
        item : QListWidgetItem
            The item altered.
        """
        index = item.row()
        value = item.text()
        if not value:
            self.sample.dataFiles.dataFiles.remove(index)
        else:
            self.sample.dataFiles.dataFiles[index] = value
        self.updateDataFilesList()
        if not self.widgetsRefreshing:
            self.parent.setModified()

    def handleDataFileInserted(self, item):
        """
        Slot for handling an item in the data files list being entered.
        Called when an itemEntered signal is emitted,
        from the dataFilesList.
        Alters the sample's data files as such.
        Parameters
        ----------
        item : QListWidgetItem
            The item entered.
        """
        value = item.text()
        self.sample.dataFiles.dataFiles.append(value)
        if not self.widgetsRefreshing:
            self.parent.setModified()

    def updateDataFilesList(self):
        """
        Fills the data files list.
        """
        self.dataFilesList.clear()
        self.dataFilesList.addItems(
            [df for df in self.sample.dataFiles.dataFiles]
        )

    def addFiles(self, target, title, regex):
        """
        Slot for adding files to the data files list.
        Called when a clicked signal is emitted,
        from the addDataFileButton.
        Parameters
        ----------
        target : QListWidget
            Target widget to add to.
        title : str
            Window title for QFileDialog.
        regex : str
            Regex-like expression to use for specifying file types.
        """
        files = QFileDialog.getOpenFileNames(self, title, ".", regex)[0]
        for file in files:
            if file:
                target.addItem(file.split("/")[-1])
                self.handleDataFileInserted(target.item(target.count() - 1))
        if not self.widgetsRefreshing:
            self.parent.setModified()

    def removeFile(self, target, dataFiles):
        """
        Slot for removing files from the data files list.
        Called when a clicked signal is emitted,
        from the removeDataFileButton.
        Parameters
        ----------
        target : QListWidget
            Target widget to add to.
        dataFiles : list
            dataFiles attribute belonging to DataFiles object.
        """
        if target.currentIndex().isValid():
            remove = target.takeItem(target.currentRow()).text()
            dataFiles.dataFiles.remove(remove)
            self.updateDataFilesList()
            if not self.widgetsRefreshing:
                self.parent.setModified()

    def updateCompositionTable(self):
        """
        Fills the composition table.
        """
        self.sampleCompositionTable.makeModel(self.sample.composition.elements)

    def handleInsertElement(self):
        """
        Slot for handling insertion to the composition table.
        Called when a clicked signal is emitted, from the
        insertElementButton.
        """
        self.sampleCompositionTable.insertRow()
        if not self.widgetsRefreshing:
            self.parent.setModified()

    def handleRemoveElement(self):
        """
        Slot for removing files from the data files list.
        Called when a clicked signal is emitted,
        from the removeDataFileButton.
        """
        self.sampleCompositionTable.removeRow(
            self.sampleCompositionTable.selectionModel().selectedRows()
        )
        if not self.widgetsRefreshing:
            self.parent.setModified()

    def updateExponentialTable(self):
        """
        Fills the exponential table.
        """
        self.exponentialValuesTable.makeModel(self.sample.exponentialValues)

    def updateResonanceTable(self):
        """
        Fills the resonance table.
        """
        self.resonanceValuesTable.makeModel(self.sample.resonanceValues)

    def handleInsertExponentialValue(self):
        """
        Slot for handling insertion to the exponential table.
        Called when a clicked signal is emitted, from the
        insertExponentialButton.
        """
        self.exponentialValuesTable.insertRow()
        if not self.widgetsRefreshing:
            self.parent.setModified()

    def handleRemoveExponentialValue(self):
        """
        Slot for removing values from the exponential table.
        Called when a clicked signal is emitted,
        from the removeExponentialButton.
        """
        self.exponentialValuesTable.removeRow(
            self.exponentialValuesTable.selectionModel().selectedRows()
        )
        if not self.widgetsRefreshing:
            self.parent.setModified()

    def handleInsertResonanceValue(self):
        """
        Slot for handling insertion to the resonance table.
        Called when a clicked signal is emitted, from the
        insertResonanceButton.
        """
        self.resonanceValuesTable.insertRow()
        if not self.widgetsRefreshing:
            self.parent.setModified()

    def handleRemoveResonanceValue(self):
        """
        Slot for removing values from the resonance table.
        Called when a clicked signal is emitted,
        from the removeResonanceButton.
        """
        self.resonanceValuesTable.removeRow(
            self.resonanceValuesTable.selectionModel().selectedRows()
        )
        if not self.widgetsRefreshing:
            self.parent.setModified()

    def connectSlots(self):
        """
        Connect the slots to the signals.
        """

        # Setup slot for period number.
        self.periodNoSpinBox.valueChanged.connect(self.handlePeriodNoChanged)

        # Setup slots for data files.
        self.dataFilesList.itemChanged.connect(self.handleDataFilesAltered)
        self.dataFilesList.itemEntered.connect(self.handleDataFileInserted)
        self.addDataFileButton.clicked.connect(
            lambda: self.addFiles(
                self.dataFilesList,
                "Add data files",
                f"{self.parent.gudrunFile.instrument.dataFileType}"
                f" (*.{self.parent.gudrunFile.instrument.dataFileType})",
            )
        )
        self.removeDataFileButton.clicked.connect(
            lambda: self.removeFile(self.dataFilesList, self.sample.dataFiles)
        )

        # Setup slots for run controls.
        self.forceCorrectionsCheckBox.stateChanged.connect(
            self.handleForceCorrectionsSwitched
        )

        # Fill geometry combo box.
        for g in Geometry:
            self.geometryComboBox.addItem(g.name, g)
        # Setup slots for geometry data.
        self.geometryComboBox.currentIndexChanged.connect(
            self.handleGeometryChanged
        )
        # Flatplate
        self.upstreamSpinBox.valueChanged.connect(
            self.handleUpstreamThicknessChanged
        )
        self.downstreamSpinBox.valueChanged.connect(
            self.handleDownstreamThicknessChanged
        )
        self.angleOfRotationSpinBox.valueChanged.connect(
            self.handleAngleOfRotationChanged
        )
        self.sampleWidthSpinBox.valueChanged.connect(
            self.handleSampleWidthChanged
        )

        # Cylindrical
        self.innerRadiiSpinBox.valueChanged.connect(
            self.handleInnerRadiiChanged
        )
        self.outerRadiiSpinBox.valueChanged.connect(
            self.handleOuterRadiiChanged
        )
        self.sampleHeightSpinBox.valueChanged.connect(
            self.handleSampleHeightChanged
        )

        # Fill the density units combo box.
        for du in UnitsOfDensity:
            self.densityUnitsComboBox.addItem(du.name, du)

        # Setup slots for density data.
        self.densitySpinBox.valueChanged.connect(
            self.handleDensityChanged
        )
        self.densityUnitsComboBox.currentIndexChanged.connect(
            self.handleDensityUnitsChanged
        )

        # Setup slots for other sample run controls.
        # Fill the cross section source combo box.
        for c in CrossSectionSource:
            self.totalCrossSectionComboBox.addItem(c.name, c)
    
        self.totalCrossSectionComboBox.currentIndexChanged.connect(
            self.handleCrossSectionSourceChanged
        )

        # Fill the normalisation type combo box.
        for n in NormalisationType:
            self.normaliseToComboBox.addItem(n.name, n)

        self.normaliseToComboBox.currentIndexChanged.connect(
            self.handleNormaliseToChanged
        )

        # Fill the output units combo box.
        for u in OutputUnits:
            self.outputUnitsComboBox.addItem(u.name, u)

        self.outputUnitsComboBox.currentIndexChanged.connect(
            self.handleOutputUnitsChanged
        )

        # Setup slot for tweak factor.
        self.tweakFactorSpinBox.valueChanged.connect(
            self.handleTweakFactorChanged
        )

        # Setup slots for Fourier Transform parameters.
        self.topHatWidthSpinBox.valueChanged.connect(
            self.handleTopHatWidthChanged
        )
        self.minSpinBox.valueChanged.connect(self.handleMinChanged)
        self.maxSpinBox.valueChanged.connect(self.handleMaxChanged)
        self.broadeningFunctionSpinBox.valueChanged.connect(
            self.handleBroadeningFunctionChanged
        )
        self.broadeningPowerSpinBox.valueChanged.connect(
            self.handleBroadeningPowerChanged
        )
        self.stepSizeSpinBox.valueChanged.connect(self.handleStepSizeChanged)

        # Setup slots for advanced attributes.
        self.scatteringFileLineEdit.textChanged.connect(
            self.handleSelfScatteringFileChanged
        )
        self.correctionFactorSpinBox.valueChanged.connect(
            self.handleCorrectionFactorChanged
        )
        self.scatteringFractionSpinBox.valueChanged.connect(
            self.handleScatteringFractionChanged
        )
        self.attenuationCoefficientSpinBox.valueChanged.connect(
            self.handleAttenuationCoefficientChanged
        )

        # Setup slots for composition.
        self.insertElementButton.clicked.connect(self.handleInsertElement)
        self.removeElementButton.clicked.connect(self.handleRemoveElement)

        # Setup slots for exponential values.
        self.insertExponentialButton.clicked.connect(
            self.handleInsertExponentialValue
        )
        self.removeExponentialButton.clicked.connect(
            self.handleRemoveExponentialValue
        )

        # Setup slots for resonance values.
        self.insertResonanceButton.clicked.connect(
            self.handleInsertResonanceValue
        )
        self.removeResonanceButton.clicked.connect(
            self.handleRemoveResonanceValue
        )

    def initComponents(self):
        """
        Populates the child widgets with their
        corresponding data from the attributes of the Sample object.
        """
        # Acquire the lock
        self.widgetsRefreshing = True

        # Populate period number widget.
        self.periodNoSpinBox.setValue(self.sample.periodNumber)

        # Populate the data files list.
        self.updateDataFilesList()

        # Populate the run controls.
        self.forceCorrectionsCheckBox.setChecked(
            Qt.Checked
            if self.sample.forceCalculationOfCorrections
            else Qt.Unchecked
        )

        # Populate the geometry data.
        self.geometryComboBox.setCurrentIndex(self.sample.geometry.value)
        self.geometryComboBox.setDisabled(True)

        # Ensure the correct attributes are being shown
        # for the correct geometry.
        self.geometryInfoStack.setCurrentIndex(config.geometry.value)
        self.geometryInfoStack_.setCurrentIndex(config.geometry.value)

        # Setup the widgets and slots for geometry specific attributes.
        # Flatplate
        self.upstreamSpinBox.setValue(self.sample.upstreamThickness)
        self.downstreamSpinBox.setValue(self.sample.downstreamThickness)

        self.angleOfRotationSpinBox.setValue(self.sample.angleOfRotation)
        self.sampleWidthSpinBox.setValue(self.sample.sampleWidth)

        # Cylindrical
        self.innerRadiiSpinBox.setValue(self.sample.innerRadius)
        self.outerRadiiSpinBox.setValue(self.sample.outerRadius)

        self.sampleHeightSpinBox.setValue(self.sample.sampleHeight)

        # Populate the density data.
        self.densitySpinBox.setValue(self.sample.density)
        self.densityUnitsComboBox.setCurrentIndex(
            self.sample.densityUnits.value
        )

        # Populate the other sample run controls.

        self.totalCrossSectionComboBox.setCurrentIndex(
            self.sample.totalCrossSectionSource.value
        )

        self.normaliseToComboBox.setCurrentIndex(self.sample.normaliseTo.value)

        self.outputUnitsComboBox.setCurrentIndex(self.sample.outputUnits.value)


        # Populate the tweak factor.
        self.tweakFactorSpinBox.setValue(self.sample.sampleTweakFactor)

        # Populate Fourier Transform parameters.
        self.topHatWidthSpinBox.setValue(self.sample.topHatW)

        self.minSpinBox.setValue(self.sample.minRadFT)
        self.maxSpinBox.setValue(self.sample.maxRadFT)

        self.broadeningFunctionSpinBox.setValue(self.sample.grBroadening)
        self.broadeningPowerSpinBox.setValue(self.sample.powerForBroadening)
        self.stepSizeSpinBox.setValue(self.sample.stepSize)

        # Populate advanced attributes.
        self.scatteringFileLineEdit.setText(self.sample.fileSelfScattering)

        self.correctionFactorSpinBox.setValue(
            self.sample.normalisationCorrectionFactor
        )

        self.scatteringFractionSpinBox.setValue(self.sample.scatteringFraction)

        self.attenuationCoefficientSpinBox.setValue(
            self.sample.attenuationCoefficient
        )

        # Populate the composition table.
        self.updateCompositionTable()

        # Populate the table containing exponential values.
        self.updateExponentialTable()

        # Populate the table containing resonance values.
        self.updateResonanceTable()

        # Release the lock
        self.widgetsRefreshing = False
