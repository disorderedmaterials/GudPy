from src.gudrun_classes.enums import (
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

    def __init__(self, sample, parent=None):
        """
        Constructs all the necessary attributes for the SampleWidget object.
        Calls the initComponents method, to load the UI file and populate data.
        Parameters
        ----------
        sample : Sample
            Sample object belonging to the GudrunFile.
        parent : QWidget
            Parent widget.
        """
        self.sample = sample
        self.parent = parent

        super(SampleWidget, self).__init__(parent=self.parent)
        self.initComponents()

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

    def handleInnerRadiiChanged(self, value):
        """
        Slot for handling change in the inner radii.
        Called when a valueChanged signal is emitted,
        from the innerRadiiSpinBox.
        Alters the normalisation's inner radius as such.
        Parameters
        ----------
        value : float
            The new value of the innerRadiiSpinBox.
        """
        self.sample.innerRadius = value

    def handleOuterRadiiChanged(self, value):
        """
        Slot for handling change in the outer radii.
        Called when a valueChanged signal is emitted,
        from the outerRadiiSpinBox.
        Alters the normalisation's outer radius as such.
        Parameters
        ----------
        value : float
            The new value of the outerRadiiSpinBox.
        """
        self.sample.outerRadius = value

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
        paths = QFileDialog.getOpenFileNames(self, title, ".", regex)
        for path in paths:
            if path:
                target.addItem(path)
                self.handleDataFileInserted(target.item(target.count() - 1))

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

    def handleRemoveElement(self):
        """
        Slot for removing files from the data files list.
        Called when a clicked signal is emitted,
        from the removeDataFileButton.
        """
        self.sampleCompositionTable.removeRow(
            self.sampleCompositionTable.selectionModel().selectedRows()
        )

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

    def handleRemoveExponentialValue(self):
        """
        Slot for removing values from the exponential table.
        Called when a clicked signal is emitted,
        from the removeExponentialButton.
        """
        self.exponentialValuesTable.removeRow(
            self.exponentialValuesTable.selectionModel().selectedRows()
        )

    def handleInsertResonanceValue(self):
        """
        Slot for handling insertion to the resonance table.
        Called when a clicked signal is emitted, from the
        insertResonanceButton.
        """
        self.resonanceValuesTable.insertRow()

    def handleRemoveResonanceValue(self):
        """
        Slot for removing values from the resonance table.
        Called when a clicked signal is emitted,
        from the removeResonanceButton.
        """
        self.resonanceValuesTable.removeRow(
            self.resonanceValuesTable.selectionModel().selectedRows()
        )

    def initComponents(self):
        """
        Loads the UI file for the SampleWidget object,
        and then populates the child widgets with their
        corresponding data from the attributes of the Sample object.
        """
        current_dir = os.path.dirname(os.path.realpath(__file__))
        uifile = os.path.join(current_dir, "ui_files/sampleWidget.ui")
        uic.loadUi(uifile, self)

        self.periodNoSpinBox.setValue(self.sample.periodNumber)
        self.periodNoSpinBox.valueChanged.connect(self.handlePeriodNoChanged)

        self.updateDataFilesList()
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
        self.forceCorrectionsCheckBox.setChecked(
            Qt.Checked
            if self.sample.forceCalculationOfCorrections
            else Qt.Unchecked
        )
        self.forceCorrectionsCheckBox.stateChanged.connect(
            self.handleForceCorrectionsSwitched
        )

        for g in Geometry:
            self.geometryComboBox.addItem(g.name, g)
        self.geometryComboBox.setCurrentIndex(self.sample.geometry.value)
        self.geometryComboBox.currentIndexChanged.connect(
            self.handleGeometryChanged
        )
        self.geometryComboBox.setDisabled(True)

        self.upstreamSpinBox.setValue(self.sample.upstreamThickness)
        self.upstreamSpinBox.valueChanged.connect(
            self.handleUpstreamThicknessChanged
        )
        self.downstreamSpinBox.setValue(self.sample.downstreamThickness)
        self.downstreamSpinBox.valueChanged.connect(
            self.handleDownstreamThicknessChanged
        )

        self.innerRadiiSpinBox.setValue(self.sample.innerRadius)
        self.innerRadiiSpinBox.valueChanged.connect(
            self.handleInnerRadiiChanged
        )
        self.outerRadiiSpinBox.setValue(self.sample.outerRadius)
        self.outerRadiiSpinBox.valueChanged.connect(
            self.handleOuterRadiiChanged
        )

        self.densitySpinBox.setValue(self.sample.density)
        for du in UnitsOfDensity:
            self.densityUnitsComboBox.addItem(du.name, du)
        self.densityUnitsComboBox.setCurrentIndex(
            self.sample.densityUnits.value
        )
        self.densityUnitsComboBox.currentIndexChanged.connect(
            self.handleDensityUnitsChanged
        )

        crossSectionSources = ["TABLES", "TRANSMISSION MONITOR", "FILENAME"]
        if "TABLES" in self.sample.totalCrossSectionSource:
            index = 0
        elif "TRANSMISSION" in self.sample.totalCrossSectionSource:
            index = 1
        else:
            index = 2
        self.totalCrossSectionComboBox.addItems(crossSectionSources)
        self.totalCrossSectionComboBox.setCurrentIndex(index)
        self.totalCrossSectionComboBox.currentIndexChanged.connect(
            self.handleCrossSectionSourceChanged
        )

        self.tweakFactorSpinBox.setValue(self.sample.sampleTweakFactor)
        self.tweakFactorSpinBox.valueChanged.connect(
            self.handleTweakFactorChanged
        )

        self.topHatWidthSpinBox.setValue(self.sample.topHatW)
        self.topHatWidthSpinBox.valueChanged.connect(
            self.handleTopHatWidthChanged
        )
        self.minSpinBox.setValue(self.sample.minRadFT)
        self.minSpinBox.valueChanged.connect(self.handleMinChanged)
        self.maxSpinBox.setValue(self.sample.maxRadFT)
        self.maxSpinBox.valueChanged.connect(self.handleMaxChanged)

        self.broadeningFunctionSpinBox.setValue(self.sample.grBroadening)
        self.broadeningFunctionSpinBox.valueChanged.connect(
            self.handleBroadeningFunctionChanged
        )
        self.broadeningPowerSpinBox.setValue(self.sample.powerForBroadening)
        self.broadeningPowerSpinBox.valueChanged.connect(
            self.handleBroadeningPowerChanged
        )

        self.stepSizeSpinBox.setValue(self.sample.stepSize)
        self.stepSizeSpinBox.valueChanged.connect(self.handleStepSizeChanged)

        self.scatteringFileLineEdit.setText(self.sample.fileSelfScattering)
        self.scatteringFileLineEdit.textChanged.connect(
            self.handleSelfScatteringFileChanged
        )

        for n in NormalisationType:
            self.normaliseToComboBox.addItem(n.name, n)
        self.normaliseToComboBox.setCurrentIndex(self.sample.normaliseTo.value)
        self.normaliseToComboBox.currentIndexChanged.connect(
            self.handleNormaliseToChanged
        )

        for u in OutputUnits:
            self.outputUnitsComboBox.addItem(u.name, u)
        self.outputUnitsComboBox.setCurrentIndex(self.sample.outputUnits.value)
        self.outputUnitsComboBox.currentIndexChanged.connect(
            self.handleOutputUnitsChanged
        )

        self.geometryInfoStack.setCurrentIndex(config.geometry.value)
        self.geometryInfoStack_.setCurrentIndex(self.sample.geometry.value)

        self.angleOfRotationSpinBox.setValue(self.sample.angleOfRotation)
        self.angleOfRotationSpinBox.valueChanged.connect(
            self.handleAngleOfRotationChanged
        )
        self.sampleWidthSpinBox.setValue(self.sample.sampleWidth)
        self.sampleWidthSpinBox.valueChanged.connect(
            self.handleSampleWidthChanged
        )
        self.sampleHeightSpinBox.setValue(self.sample.sampleHeight)
        self.sampleHeightSpinBox.valueChanged.connect(
            self.handleSampleHeightChanged
        )

        self.correctionFactorSpinBox.setValue(
            self.sample.normalisationCorrectionFactor
        )
        self.correctionFactorSpinBox.valueChanged.connect(
            self.handleCorrectionFactorChanged
        )
        self.scatteringFractionSpinBox.setValue(self.sample.scatteringFraction)
        self.scatteringFractionSpinBox.valueChanged.connect(
            self.handleScatteringFractionChanged
        )
        self.attenuationCoefficientSpinBox.setValue(
            self.sample.attenuationCoefficient
        )
        self.attenuationCoefficientSpinBox.valueChanged.connect(
            self.handleAttenuationCoefficientChanged
        )

        self.updateCompositionTable()
        self.insertElementButton.clicked.connect(self.handleInsertElement)
        self.removeElementButton.clicked.connect(self.handleRemoveElement)

        self.updateExponentialTable()
        self.insertExponentialButton.clicked.connect(
            self.handleInsertExponentialValue
        )
        self.removeExponentialButton.clicked.connect(
            self.handleRemoveExponentialValue
        )

        self.updateResonanceTable()
        self.insertResonanceButton.clicked.connect(
            self.handleInsertResonanceValue
        )
        self.removeResonanceButton.clicked.connect(
            self.handleRemoveResonanceValue
        )
