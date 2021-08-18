from PyQt5.QtWidgets import QTableWidgetItem, QWidget
from PyQt5 import uic
import os
from gudrun_classes.enums import Geometry

class BeamWidget(QWidget):
    def __init__(self, beam, parent=None):
        self.beam = beam
        self.parent = parent

        super(BeamWidget, self).__init__(self.parent)
        self.initComponents()
    
    def initComponents(self):
        current_dir = os.path.dirname(os.path.realpath(__file__))
        uifile = os.path.join(current_dir, "ui_files/beamWidget.ui")
        uic.loadUi(uifile, self)

        self.sampleGeometryComboBox.addItems([g.name for g in Geometry])
        self.sampleGeometryComboBox.setCurrentIndex(self.beam.sampleGeometry.value)

        self.absorptionStepSizeLineEdit.setText(str(self.beam.stepSizeAbsorption))
        self.msCalculationStepSizeLineEdit.setText(str(self.beam.stepSizeMS))
        self.noSlicesLineEdit.setText(str(self.beam.noSlices))
        self.stepForCorrectionsLineEdit.setText(str(self.beam.angularStepForCorrections))
        
        self.leftIncidentBeamLineEdit.setText(str(self.beam.incidentBeamLeftEdge))
        self.rightIncidentBeamLineEdit.setText(str(self.beam.incidentBeamRightEdge))
        self.topIncidentBeamLineEdit.setText(str(self.beam.incidentBeamTopEdge))
        self.bottomIncidentBeamLineEdit.setText(str(self.beam.incidentBeamBottomEdge))

        self.leftScatteredBeamLineEdit.setText(str(self.beam.scatteredBeamLeftEdge))
        self.rightScatteredBeamLineEdit.setText(str(self.beam.scatteredBeamRightEdge))
        self.topScatteredBeamLineEdit.setText(str(self.beam.scatteredBeamTopEdge))
        self.bottomScatteredBeamLineEdit.setText(str(self.beam.scatteredBeamBottomEdge))

        self.incidentBeamSpectrumParametersLineEdit.setText(self.beam.filenameIncidentBeamSpectrumParams)

        self.overallBackgroundFactorLineEdit.setText(str(self.beam.overallBackgroundFactor))
        self.sampleDependantBackgroundFactorLineEdit.setText(str(self.beam.sampleDependantBackgroundFactor))
        self.shieldingLineEdit.setText(str(self.beam.shieldingAttenuationCoefficient))

        for i, val in enumerate(self.beam.beamProfileValues):
            self.beamProfileValuesTable.setItem(i//5, i%5, QTableWidgetItem(str(val)))