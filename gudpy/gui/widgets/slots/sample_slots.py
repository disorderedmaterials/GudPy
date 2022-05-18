import os
from PySide6.QtWidgets import QAbstractItemView, QFileDialog

from core.enums import (
    CrossSectionSource, Geometry,
    NormalisationType, OutputUnits, FTModes, UnitsOfDensity
)
from core import config
from core.utils import nthfloat


class SampleSlots():

    def __init__(self, widget, parent):
        self.widget = widget
        self.parent = parent
        self.setupSampleSlots()

    def setSample(self, sample):
        self.sample = sample
        self.widget.parameterTabs.setTabText(0, self.sample.name)
        # Acquire the lock
        self.widgetsRefreshing = True

        # Populate period number widget.
        self.widget.samplePeriodNoSpinBox.setValue(self.sample.periodNumber)

        # Populate the data files list.
        self.updatesampleDataFilesList()

        # Populate the run controls.
        self.widget.sampleForceCorrectionsCheckBox.setChecked(
            self.sample.forceCalculationOfCorrections
        )

        # Populate the geometry data.
        self.widget.sampleGeometryComboBox.setCurrentIndex(
            self.sample.geometry.value
        )
        self.widget.sampleGeometryComboBox.setDisabled(True)

        # Ensure the correct attributes are being shown
        # for the correct geometry.
        self.widget.sampleGeometryInfoStack.setCurrentIndex(
            config.geometry.value
        )

        # Populate geometry specific attributes.
        # Flatplate
        self.widget.sampleUpstreamSpinBox.setValue(
            self.sample.upstreamThickness
        )
        self.widget.sampleDownstreamSpinBox.setValue(
            self.sample.downstreamThickness
        )
        total = (
            self.sample.upstreamThickness +
            self.sample.downstreamThickness
        )
        self.widget.totalSampleThicknessLabel.setText(
            f"Total: {total} cm"
        )

        self.widget.angleOfRotationSpinBox.setValue(
            self.sample.angleOfRotation
        )
        self.widget.sampleWidthSpinBox.setValue(
            self.sample.sampleWidth
        )

        # Cylindrical
        self.widget.sampleInnerRadiiSpinBox.setValue(self.sample.innerRadius)
        self.widget.sampleOuterRadiiSpinBox.setValue(self.sample.outerRadius)

        self.widget.sampleHeightSpinBox.setValue(self.sample.sampleHeight)

        # Populate the density data.
        self.widget.sampleDensitySpinBox.setValue(self.sample.density)
        self.widget.sampleDensityUnitsComboBox.setCurrentIndex(
            self.sample.densityUnits.value
        )

        # Populate the other sample run controls.

        self.widget.sampleTotalCrossSectionComboBox.setCurrentIndex(
            self.sample.totalCrossSectionSource.value
        )
        self.widget.sampleCrossSectionFileLineEdit.setText(
            self.sample.crossSectionFilename
        )
        self.widget.sampleCrossSectionFileWidget.setVisible(
            self.sample.totalCrossSectionSource == CrossSectionSource.FILE
        )

        self.widget.normaliseToComboBox.setCurrentIndex(
            self.sample.normaliseTo.value
        )

        self.widget.outputUnitsComboBox.setCurrentIndex(
            self.sample.outputUnits.value
        )

        # Populate the tweak factor.
        self.widget.tweakFactorSpinBox.setValue(self.sample.sampleTweakFactor)

        # Populate the packing fraction.
        if self.sample.sampleTweakFactor > 0.0:
            self.widget.packingFractionSpinBox.setValue(1.0 / self.sample.sampleTweakFactor)
        else:
            self.widget.packingFractionSpinBox.setValue(0.0)

        self.packingFractionChanging = False

        # Populate Fourier Transform parameters.
        self.widget.topHatWidthSpinBox.setValue(self.sample.topHatW)

        self.widget.FTModeComboBox.setCurrentIndex(
            self.sample.FTMode.value
        )

        self.widget.minSpinBox.setValue(self.sample.minRadFT)
        self.widget.maxSpinBox.setValue(self.sample.maxRadFT)

        self.widget.broadeningFunctionSpinBox.setValue(
            self.sample.grBroadening
        )
        self.widget.broadeningPowerSpinBox.setValue(
            self.sample.powerForBroadening
        )
        self.widget.stepSizeSpinBox.setValue(self.sample.stepSize)

        # Populate advanced attributes.
        self.widget.scatteringFileLineEdit.setText(
            self.sample.fileSelfScattering
        )

        self.widget.correctionFactorSpinBox.setValue(
            self.sample.normalisationCorrectionFactor
        )

        self.widget.sampleScatteringFractionSpinBox.setValue(
            self.sample.scatteringFraction
        )

        self.widget.sampleAttenuationCoefficientSpinBox.setValue(
            self.sample.attenuationCoefficient
        )

        # Populate the composition table.
        self.updateCompositionTable()

        # Populate the table containing exponential values.
        self.updateExponentialTable()

        # Populate the table containing resonance values.
        self.updateResonanceTable()

        # Calculate the expected DCS level.
        self.updateExpectedDCSLevel()

        self.widget.sampleCompositionTable.model().dataChanged.connect(
            self.updateExpectedDCSLevel
        )
        self.widget.sampleRatioCompositionTable.model().dataChanged.connect(
            self.updateExpectedDCSLevel
        )

        # Release the lock
        self.widgetsRefreshing = False

    def setupSampleSlots(self):
        # Setup slot for period number.
        self.widget.samplePeriodNoSpinBox.valueChanged.connect(
            self.handlePeriodNoChanged
        )

        # Setup slots for data files.
        self.widget.sampleDataFilesList.itemChanged.connect(
            self.handleDataFilesAltered
        )
        self.widget.sampleDataFilesList.itemEntered.connect(
            self.handleDataFileInserted
        )
        self.widget.addSampleDataFileButton.clicked.connect(
            lambda: self.addFiles(
                self.widget.sampleDataFilesList,
                "Add data files",
                f"{self.parent.gudrunFile.instrument.dataFileType}"
                f" (*.{self.parent.gudrunFile.instrument.dataFileType})",
            )
        )
        self.widget.removeSampleDataFileButton.clicked.connect(
            lambda: self.removeFile(
                self.widget.sampleDataFilesList, self.sample.dataFiles
            )
        )

        # Setup slots for run controls.
        self.widget.sampleForceCorrectionsCheckBox.stateChanged.connect(
            self.handleForceCorrectionsSwitched
        )

        # Fill geometry combo box.
        for g in Geometry:
            self.widget.sampleGeometryComboBox.addItem(g.name, g)
        # Setup slots for geometry data.
        self.widget.sampleGeometryComboBox.currentIndexChanged.connect(
            self.handleGeometryChanged
        )
        # Flatplate
        self.widget.sampleUpstreamSpinBox.valueChanged.connect(
            self.handleUpstreamThicknessChanged
        )
        self.widget.sampleDownstreamSpinBox.valueChanged.connect(
            self.handleDownstreamThicknessChanged
        )
        self.widget.angleOfRotationSpinBox.valueChanged.connect(
            self.handleAngleOfRotationChanged
        )
        self.widget.sampleWidthSpinBox.valueChanged.connect(
            self.handleSampleWidthChanged
        )

        # Cylindrical
        self.widget.sampleInnerRadiiSpinBox.valueChanged.connect(
            self.handleInnerRadiiChanged
        )
        self.widget.sampleOuterRadiiSpinBox.valueChanged.connect(
            self.handleOuterRadiiChanged
        )
        self.widget.sampleHeightSpinBox.valueChanged.connect(
            self.handleSampleHeightChanged
        )

        # Fill the density units combo box.
        for du in UnitsOfDensity:
            self.widget.sampleDensityUnitsComboBox.addItem(du.name, du)

        # Setup slots for density data.
        self.widget.sampleDensitySpinBox.valueChanged.connect(
            self.handleDensityChanged
        )
        self.widget.sampleDensityUnitsComboBox.currentIndexChanged.connect(
            self.handleDensityUnitsChanged
        )

        # Setup slots for other sample run controls.
        # Fill the cross section source combo box.
        for c in CrossSectionSource:
            self.widget.sampleTotalCrossSectionComboBox.addItem(c.name, c)

        (
            self.widget.sampleTotalCrossSectionComboBox.
            currentIndexChanged
        ).connect(
            self.handleCrossSectionSourceChanged
        )
        self.widget.sampleCrossSectionFileLineEdit.textChanged.connect(
            self.handleCrossSectionFileChanged
        )
        self.widget.browseSampleCrossSectionFileButto.clicked.connect(
            self.handleBrowseCrossSectionFile
        )

        # Fill the normalisation type combo box.
        for n in NormalisationType:
            self.widget.normaliseToComboBox.addItem(n.name, n)

        self.widget.normaliseToComboBox.currentIndexChanged.connect(
            self.handleNormaliseToChanged
        )

        # Fill the output units combo box.
        for u in OutputUnits:
            self.widget.outputUnitsComboBox.addItem(u.name, u)

        self.widget.outputUnitsComboBox.currentIndexChanged.connect(
            self.handleOutputUnitsChanged
        )

        # Setup slot for tweak factor.
        self.widget.tweakFactorSpinBox.valueChanged.connect(
            self.handleTweakFactorChanged
        )

        # Setup slot for packing fraction
        self.widget.packingFractionSpinBox.valueChanged.connect(
            self.handlePackingFractionChanged
        )

        # Setup slots for Fourier Transform parameters.
        self.widget.topHatWidthSpinBox.valueChanged.connect(
            self.handleTopHatWidthChanged
        )

        # Fill top hat width combo box.
        for tp in FTModes:
            self.widget.FTModeComboBox.addItem(tp.name, tp)

        self.widget.FTModeComboBox.currentIndexChanged.connect(
            self.handleBackgroundScatteringSubtractionModeChanged
        )

        self.widget.minSpinBox.valueChanged.connect(self.handleMinChanged)
        self.widget.maxSpinBox.valueChanged.connect(self.handleMaxChanged)
        self.widget.broadeningFunctionSpinBox.valueChanged.connect(
            self.handleBroadeningFunctionChanged
        )
        self.widget.broadeningPowerSpinBox.valueChanged.connect(
            self.handleBroadeningPowerChanged
        )
        self.widget.stepSizeSpinBox.valueChanged.connect(
            self.handleStepSizeChanged
        )

        # Setup slots for advanced attributes.
        self.widget.scatteringFileLineEdit.textChanged.connect(
            self.handleSelfScatteringFileChanged
        )
        self.widget.correctionFactorSpinBox.valueChanged.connect(
            self.handleCorrectionFactorChanged
        )
        self.widget.sampleScatteringFractionSpinBox.valueChanged.connect(
            self.handleScatteringFractionChanged
        )
        self.widget.sampleAttenuationCoefficientSpinBox.valueChanged.connect(
            self.handleAttenuationCoefficientChanged
        )

        # Setup slots for composition.
        self.widget.insertSampleElementButton.clicked.connect(
            self.handleInsertElement
        )
        self.widget.removeSampleElementButton.clicked.connect(
            self.handleRemoveElement
        )

        self.widget.insertSampleComponentButton.clicked.connect(
            self.handleInsertComponent
        )

        self.widget.removeSampleComponentButton.clicked.connect(
            self.handleRemoveComponent
        )

        # Setup slots for exponential values.
        self.widget.insertExponentialButton.clicked.connect(
            self.handleInsertExponentialValue
        )
        self.widget.removeExponentialButton.clicked.connect(
            self.handleRemoveExponentialValue
        )

        # Setup slots for resonance values.
        self.widget.insertResonanceButton.clicked.connect(
            self.handleInsertResonanceValue
        )
        self.widget.removeResonanceButton.clicked.connect(
            self.handleRemoveResonanceValue
        )

    def handlePeriodNoChanged(self, value):
        """
        Slot for handling change in the period number.
        Called when a valueChanged signal is emitted,
        from the samplePeriodNoSpinBox.
        Alters the sample's period number as such.
        Parameters
        ----------
        value : float
            The new value of the samplePeriodNoSpinBox.
        """
        self.sample.periodNo = value
        if not self.widgetsRefreshing:
            self.parent.setModified()
            if not self.parent.gudrunFile.purgeFile.excludeSampleAndCan:
                self.parent.gudrunFile.purged = False

    def handleForceCorrectionsSwitched(self, state):
        """
        Slot for handling switching forcing correction calculations on/off.
        Called when a stateChanged signal is emitted,
        from the sampleForceCorrectionsCheckBox.
        Alters the sample's forcing calculations of
        corrections as such.
        Parameters
        ----------
        state : int
            The new state of the sampleForceCorrectionsCheckBox
            (1: True, 0: False)
        """
        self.sample.forceCalculationOfCorrections = bool(state)
        if not self.widgetsRefreshing:
            self.parent.setModified()

    def handleGeometryChanged(self, index):
        """
        Slot for handling change in sample geometry.
        Called when a currentIndexChanged signal is emitted,
        from the sampleGeometryComboBox.
        Alters the sample geometry as such.
        Parameters
        ----------
        index : int
            The new current index of the sampleGeometryComboBox.
        """
        self.sample.geometry = (
            self.widget.sampleGeometryComboBox.itemData(index)
        )
        self.widget.sampleGeometryInfoStack.setCurrentIndex(
            self.sample.geometry.value
        )

    def handleUpstreamThicknessChanged(self, value):
        """
        Slot for handling change in the upstream thickness.
        Called when a valueChanged signal is emitted,
        from the sampleUpstreamSpinBox.
        Alters the sample's upstream thickness as such.
        Parameters
        ----------
        value : float
            The new value of the sampleUpstreamSpinBox.
        """
        self.sample.upstreamThickness = value
        total = (
            self.sample.upstreamThickness +
            self.sample.downstreamThickness
        )
        self.widget.totalSampleThicknessLabel.setText(
            f"Total: {total} cm"
        )
        if not self.widgetsRefreshing:
            self.parent.setModified()

    def handleDownstreamThicknessChanged(self, value):
        """
        Slot for handling change in the downstream thickness.
        Called when a valueChanged signal is emitted,
        from the sampleDownstreamSpinBox.
        Alters the sample's downstream thickness as such.
        Parameters
        ----------
        value : float
            The new value of the sampleDownstreamSpinBox.
        """
        self.sample.downstreamThickness = value
        total = (
            self.sample.upstreamThickness +
            self.sample.downstreamThickness
        )
        self.widget.totalSampleThicknessLabel.setText(
            f"Total: {total} cm"
        )
        if not self.widgetsRefreshing:
            self.parent.setModified()

    def handleInnerRadiiChanged(self, value):
        """
        Slot for handling change in the inner radii.
        Called when a valueChanged signal is emitted,
        from the sampleInnerRadiiSpinBox.
        Alters the sample's inner radius as such.
        Parameters
        ----------
        value : float
            The new value of the sampleInnerRadiiSpinBox.
        """
        self.sample.innerRadius = value
        if not self.widgetsRefreshing:
            self.parent.setModified()

    def handleOuterRadiiChanged(self, value):
        """
        Slot for handling change in the outer radii.
        Called when a valueChanged signal is emitted,
        from the sampleOuterRadiiSpinBox.
        Alters the sample's outer radius as such.
        Parameters
        ----------
        value : float
            The new value of the sampleOuterRadiiSpinBox.
        """
        self.sample.outerRadius = value
        if not self.widgetsRefreshing:
            self.parent.setModified()

    def handleDensityChanged(self, value):
        """
        Slot for handling change in density.
        Called when a valueChanged signal is emitted,
        from the sampleDensitySpinBox.
        Alters the sample density as such.
        Parameters
        ----------
        value : float
            The new current index of the sampleDensitySpinBox.
        """
        self.sample.density = value
        if not self.widgetsRefreshing:
            self.parent.setModified()

    def handleDensityUnitsChanged(self, index):
        """
        Slot for handling change in density units.
        Called when a currentIndexChanged signal is emitted,
        from the sampleDensityUnitsComboBox.
        Alters the sample density units as such.
        Parameters
        ----------
        index : int
            The new current index of the sampleDensityUnitsComboBox.
        """
        self.sample.densityUnits = (
            self.widget.sampleDensityUnitsComboBox.itemData(index)
        )
        if not self.widgetsRefreshing:
            self.parent.setModified()

    def handleCrossSectionSourceChanged(self, index):
        """
        Slot for handling change in total cross section source.
        Called when a currentIndexChanged signal is emitted,
        from the sampleTotalCrossSectionComboBox.
        Alters the sample's total cross section source as such.
        Parameters
        ----------
        index : int
            The new current index of the sampleTotalCrossSectionComboBox.
        """
        self.sample.totalCrossSectionSource = (
            self.widget.sampleTotalCrossSectionComboBox.itemData(index)
        )
        self.widget.sampleCrossSectionFileWidget.setVisible(
            self.sample.totalCrossSectionSource == CrossSectionSource.FILE
        )
        if not self.widgetsRefreshing:
            self.parent.setModified()

    def handleCrossSectionFileChanged(self, value):
        """
        Slot for handling change in total cross section source file name.
        Called when a textChanged signal is emitted,
        from the sampleCrossSectionFileLineEdit.
        Alters the sample's total cross section source file name as such.
        Parameters
        ----------
        value : str
            The new text of the sampleCrossSectionFileLineEdit.
        """
        self.sample.crossSectionFilename = value
        if not self.widgetsRefreshing:
            self.parent.setModified()

    def handleBrowseCrossSectionFile(self):
        """
        Slot for browsing for a cross section source file.
        Called when a clicked signal is emitted,
        from the browseSampleCrossSectionFileButto.
        Alters the corresponding line edit as such.
        as such.
        """
        filename, _ = QFileDialog.getOpenFileName(
            self.widget, "Total cross section source", "")
        if filename:
            self.widget.sampleCrossSectionFileLineEdit.setText(filename)

    def handleTweakFactorChanged(self, value):
        """
        Slot for handling change in the sample tweak factor.
        Called when a valueChanged signal is emitted,
        from the the tweakFactorSpinBox.
        Alters the sample's tweak factor as such.
        Also updates the packing fraction.
        Parameters
        ----------
        value : float
            The new current value of the tweakFactorSpinBox.
        """
        self.sample.sampleTweakFactor = value
        self.packingFractionChanging = True
        if value > 0.0:
            self.widget.packingFractionSpinBox.setValue(1.0 / value)
        else:
            self.widget.packingFractionSpinBox.setValue(0.0)
        self.packingFractionChanging = False
        if not self.widgetsRefreshing:
            self.parent.setModified()

    def handlePackingFractionChanged(self, value):
        """
        Slot for handling change in the sample packing fraction.
        Called when a valueChanged signal is emitted,
        from the the packingFractionSpinBox.
        Updates the sample's tweak factor to reflect
        the new packing fraction.
        Parameters
        ----------
        value : float
            The new current value of the packingFractionSpinBox.
        """
        if not self.packingFractionChanging:
            if value > 0.0:
                self.widget.tweakFactorSpinBox.setValue(1.0 / value)
            else:
                self.widget.tweakFactorSpinBox.setValue(0.0)

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

    def handleBackgroundScatteringSubtractionModeChanged(self, index):
        """
        Slot for handling change in FT Mode.
        Called when a currentIndexChanged signal is emitted,
        from the FTModeComboBox.
        Alters the sample's FT mode as such.
        Parameters
        ----------
        index : int
            The new current index of the
            FTModeComboBox.
        """
        self.sample.singleAtomBackgroundScatteringSubtractionMode = (
            self.widget.FTModeComboBox.itemData(index)
        )

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
        self.sample.normaliseTo = (
            self.widget.normaliseToComboBox.itemData(index)
        )
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
        self.sample.outputUnits = (
            self.widget.outputUnitsComboBox.itemData(index)
        )
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
        from the sampleScatteringFractionSpinBox.
        Alters the sample's scattering fraction as such.
        Parameters
        ----------
        value : float
            The new current value of the sampleScatteringFractionSpinBox.
        """
        self.sample.scatteringFraction = value
        if not self.widgetsRefreshing:
            self.parent.setModified()

    def handleAttenuationCoefficientChanged(self, value):
        """
        Slot for handling change in the environment attenuation coefficient.
        Called when a valueChanged signal is emitted,
        from the sampleAttenuationCoefficientSpinBox.
        Alters the sample's attenuation coefficient as such.
        Parameters
        ----------
        value : float
            The new current value of the sampleAttenuationCoefficientSpinBox.
        """
        self.sample.attenuationCoefficient = value
        if not self.widgetsRefreshing:
            self.parent.setModified()

    def handleDataFilesAltered(self, item):
        """
        Slot for handling an item in the data files list being changed.
        Called when an itemChanged signal is emitted,
        from the sampleDataFilesList.
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
            self.sample.dataFiles[index] = value
        self.updatesampleDataFilesList()
        if not self.widgetsRefreshing:
            self.parent.setModified()
            self.parent.gudrunFile.purged = False

    def handleDataFileInserted(self, item):
        """
        Slot for handling an item in the data files list being entered.
        Called when an itemEntered signal is emitted,
        from the sampleDataFilesList.
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
            self.parent.gudrunFile.purged = False

    def updatesampleDataFilesList(self):
        """
        Fills the data files list.
        """
        self.widget.sampleDataFilesList.clear()
        self.widget.sampleDataFilesList.addItems(
            [df for df in self.sample.dataFiles]
        )

    def addFiles(self, target, title, regex):
        """
        Slot for adding files to the data files list.
        Called when a clicked signal is emitted,
        from the addSampleDataFileButton.
        Parameters
        ----------
        target : QListWidget
            Target widget to add to.
        title : str
            Window title for QFileDialog.
        regex : str
            Regex-like expression to use for specifying file types.
        """
        files, _ = QFileDialog.getOpenFileNames(
            self.widget, title,
            self.parent.gudrunFile.instrument.dataFileDir, regex
        )
        for file in files:
            if file:
                target.addItem(file.split(os.path.sep)[-1])
                self.handleDataFileInserted(target.item(target.count() - 1))
        if not self.widgetsRefreshing:
            self.parent.setModified()

    def removeFile(self, target, dataFiles):
        """
        Slot for removing files from the data files list.
        Called when a clicked signal is emitted,
        from the removeSampleDataFileButton.
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
            if not self.widgetsRefreshing:
                self.parent.setModified()
                self.parent.gudrunFile.purged = False

    def updateCompositionTable(self):
        """
        Fills the composition list.
        """
        self.updateRatioCompositions()
        self.updateExactCompositions()
        if config.USE_USER_DEFINED_COMPONENTS:
            self.widget.insertSampleElementButton.setEnabled(False)
            self.widget.removeSampleElementButton.setEnabled(False)
            self.widget.sampleCompositionTable.setEditTriggers(
                QAbstractItemView.EditTrigger.NoEditTriggers
            )
            self.widget.sampleRatioCompositionTab.setEnabled(True)
            (
                self.widget.sampleRatioCompositionTable
                .model().dataChanged.connect(
                    self.translateAndUpdate
                )
            )
            (
                self.widget.sampleRatioCompositionTable
                .model().rowsInserted.connect(
                    self.translateAndUpdate
                )
            )
        else:
            self.widget.insertSampleElementButton.setEnabled(True)
            self.widget.removeSampleElementButton.setEnabled(True)
            self.widget.sampleRatioCompositionTab.setEnabled(False)
            self.widget.sampleCompositionTable.setEditTriggers(
                QAbstractItemView.EditTrigger.DoubleClicked |
                QAbstractItemView.EditTrigger.EditKeyPressed |
                QAbstractItemView.EditTrigger.AnyKeyPressed
            )
        if not self.widgetsRefreshing:
            self.parent.setModified()

    def updateRatioCompositions(self):
        self.widget.sampleRatioCompositionTable.makeModel(
            self.parent.gudrunFile,
            self.sample.composition.weightedComponents,
            self.sample
        )

    def translateAndUpdate(self):
        self.sample.composition.translate()
        self.updateExactCompositions()

    def updateExactCompositions(self):
        self.widget.sampleCompositionTable.makeModel(
            self.sample.composition.elements, self.sample
        )

    def handleInsertElement(self):
        """
        Slot for handling insertion to the composition table.
        Called when a clicked signal is emitted, from the
        insertSampleElementButton.
        """
        self.widget.sampleCompositionTable.insertRow()
        if not self.widgetsRefreshing:
            self.parent.setModified()

    def handleRemoveElement(self):
        """
        Slot for removing files from the data files list.
        Called when a clicked signal is emitted,
        from the removeSampleElementButton.
        """
        self.widget.sampleCompositionTable.removeRow(
            self.widget.sampleCompositionTable.selectionModel().selectedRows()
        )
        self.updateExpectedDCSLevel()
        if not self.widgetsRefreshing:
            self.parent.setModified()

    def handleInsertComponent(self):
        self.widget.sampleRatioCompositionTable.insertRow()
        self.updateExpectedDCSLevel()
        if not self.widgetsRefreshing:
            self.parent.setModified()

    def handleRemoveComponent(self):
        self.widget.sampleRatioCompositionTable.removeRow(
            self.widget.sampleRatioCompositionTable
            .selectionModel().selectedRows()
        )
        self.updateExpectedDCSLevel()
        if not self.widgetsRefreshing:
            self.parent.setModified()

    def updateExponentialTable(self):
        """
        Fills the exponential table.
        """
        self.widget.exponentialValuesTable.makeModel(
            self.sample.exponentialValues
        )

    def updateResonanceTable(self):
        """
        Fills the resonance table.
        """
        self.widget.resonanceValuesTable.makeModel(self.sample.resonanceValues)

    def handleInsertExponentialValue(self):
        """
        Slot for handling insertion to the exponential table.
        Called when a clicked signal is emitted, from the
        insertExponentialButton.
        """
        self.widget.exponentialValuesTable.insertRow()
        if not self.widgetsRefreshing:
            self.parent.setModified()

    def handleRemoveExponentialValue(self):
        """
        Slot for removing values from the exponential table.
        Called when a clicked signal is emitted,
        from the removeExponentialButton.
        """
        self.widget.exponentialValuesTable.removeRow(
            self.widget.exponentialValuesTable.selectionModel().selectedRows()
        )
        if not self.widgetsRefreshing:
            self.parent.setModified()

    def handleInsertResonanceValue(self):
        """
        Slot for handling insertion to the resonance table.
        Called when a clicked signal is emitted, from the
        insertResonanceButton.
        """
        self.widget.resonanceValuesTable.insertRow()
        if not self.widgetsRefreshing:
            self.parent.setModified()

    def handleRemoveResonanceValue(self):
        """
        Slot for removing values from the resonance table.
        Called when a clicked signal is emitted,
        from the removeResonanceButton.
        """
        self.widget.resonanceValuesTable.removeRow(
            self.widget.resonanceValuesTable.selectionModel().selectedRows()
        )
        if not self.widgetsRefreshing:
            self.parent.setModified()

    def updateExpectedDCSLevel(self, _=None, __=None):
        """
        Updates the expectedDcsLabel,
        to show the expected DCS level of the sample.
        """
        if config.USE_USER_DEFINED_COMPONENTS:
            elements = self.sample.composition.shallowTranslate()
            dcsLevel = self.sample.composition.calculateExpectedDCSLevel(
                elements
            )
            self.widget.expectedDcsLabel.setText(
                f"Expected DCS Level: {dcsLevel}"
            )
        else:
            elements = self.sample.composition.elements
            dcsLevel = self.sample.composition.calculateExpectedDCSLevel(
                elements
            )
            self.widget.expectedDcsLabel.setText(
                f"Expected DCS Level: {dcsLevel}"
            )
        if self.widget.dcsLabel.text() != "DCS Level":
            actualDcsLevel = nthfloat(self.widget.dcsLabel.text(), 2)
            try:
                error = round(
                        ((actualDcsLevel - dcsLevel) / actualDcsLevel)*100, 1
                )
            except ZeroDivisionError:
                error = 100.
            self.widget.resultLabel.setText(f"{error}%")
            if abs(error) > 10:
                self.widget.resultLabel.setStyleSheet(
                    "background-color: red"
                )
            else:
                self.widget.resultLabel.setStyleSheet(
                    "background-color: green"
                )
