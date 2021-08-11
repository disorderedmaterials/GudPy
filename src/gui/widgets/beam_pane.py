from PyQt5.QtWidgets import QWidget

from scripts.utils import spacify, numifyBool
from widgets.make_pairs import makeLabelTextPair, makeLabelComboBoxPair

from gudrun_classes.enums import Geometry

class BeamPane(QWidget):

	def __init__(self, beam, parent, x, y, relHeight, relWidth):
		self.beam = beam
		self.parent = parent
		self.x = x
		self.y = y
		self.relHeight = relHeight
		self.relWidth = relWidth
		super(BeamPane, self).__init__(parent)
		self.setGeometry(
			y,
			0,
			int(self.parent.size().width() * self.relWidth),
			int(self.parent.size().height() * self.relHeight),
		)
		self.childWidth = (self.parent.size().width()*self.relWidth) // 5
		self.childHeight =  (self.parent.size().height() * self.relHeight) // 20
		self.initComponents()

	def initComponents(self):
		self.geometryLabel, self.geometryCombo = (
			makeLabelComboBoxPair(
				self,
				"Geometry",
				self.beam.sampleGeometry.value,
				[g.name for g in Geometry],
				0,
				0
			)
		)
		self.noBeamValuesLabel, self.noBeamsValueText = (
			makeLabelTextPair(
				self,
				"No. of beam profile values",
				self.beam.noBeamProfileValues,
				self.childHeight,
				0
			)
		)

		self.beamProfileValuesLabel, self.beamProfileValuesText = (
			makeLabelTextPair(
				self,
				"Beam profile values",
				spacify(self.beam.beamProfileValues),
				self.childHeight*2,
				0            )
		)

		self.stepSizesNoSlicesLabel, self.stepSizesNoSlicesText = (
			makeLabelTextPair(
				self,
				"Step sizes for absorption, m.s calculation and no. slices",
				[self.beam.stepSizeAbsorption,
				self.beam.stepSizeMS,
				self.beam.noSlices],
				self.childHeight*3,
				0,
				isIterable=True
			)
		)

		self.angularStepLabel, self.angularStepText = (
			makeLabelTextPair(
				self,
				"Angular step size to be used in corrections",
				self.beam.angularStepForCorrections,
				self.childHeight*4,
				0
			)
		)

		self.incidentBeamEdgesLabel, self.incidentBeamEdgesText = (
			makeLabelTextPair(
				self,
				"Incident beam edges relative to centre of sample",
				[self.beam.incidentBeamLeftEdge,
				self.beam.incidentBeamRightEdge,
				self.beam.incidentBeamTopEdge,
				self.beam.incidentBeamBottomEdge],
				self.childHeight*5,
				0,
				isIterable=True
			)
		)

		self.scatteredBeamEdgesLabel, self.scatteredBeamEdgesText = (
			makeLabelTextPair(
				self, 
				"Scattered beam edges relative to centre of sample",
				[self.beam.scatteredBeamLeftEdge,
				self.beam.scatteredBeamRightEdge,
				self.beam.scatteredBeamTopEdge,
				self.beam.scatteredBeamBottomEdge],
				self.childHeight*6,
				0,
				isIterable=True
			)
		)

		self.filenameIBSpectrumParamsLabel, self.filenameIBSpectrumParamsText = (
			makeLabelTextPair(
				self,
				"Filename containing incident beam spectrun parameters",
				self.beam.filenameIncidentBeamSpectrumParams,
				self.childHeight*7,
				0
			)
		)
		
		self.overallBackgroundFactorLabel, self.overallBackgroundFactorText = (
			makeLabelTextPair(
				self,
				"Overall background factor",
				self.beam.overallBackgroundFactor,
				self.childHeight*8,
				0
			)
		)
		
		self.sampleDependantBackgroundFactorLabel, self.sampleDependantBackgroundFactorText = (
			makeLabelTextPair(
				self,
				"Sample dependant background factor",
				self.beam.sampleDependantBackgroundFactor,
				self.childHeight*9,
				0
			)
		)

		self.absorptionCoefficientShieldingLabel, self.absorptionCoefficientShieldingText = (
			makeLabelTextPair(
				self,
				"Absorption coefficient for shielding",
				self.beam.shieldingAttenuationCoefficient,
				self.childHeight*10,
				0
			)

		)

	def updateArea(self):

		self.setGeometry(
			self.y,
			0,
			int(self.parent.size().width() * self.relWidth),
			int(self.parent.size().height() * self.relHeight),
		)
