import sys, os
from unittest import TestCase
try:
    sys.path.insert(1, os.path.join(sys.path[0], '../gudrun_classes'))
    from gudrun_file import GudrunFile
    from beam import Beam
    from composition import Composition
    from container import Container
    from data_files import DataFiles
    from element import Element
    from instrument import Instrument
    from normalisation import Normalisation
    from sample_background import SampleBackground
    from sample import Sample
except ModuleNotFoundError:
    sys.path.insert(1, os.path.join(sys.path[0], 'gudrun_classes'))
    from gudrun_classes.gudrun_file import GudrunFile
    from gudrun_classes.beam import Beam
    from gudrun_classes.composition import Composition
    from gudrun_classes.container import Container
    from gudrun_classes.data_files import DataFiles
    from gudrun_classes.element import Element
    from gudrun_classes.instrument import Instrument
    from gudrun_classes.normalisation import Normalisation
    from gudrun_classes.sample_background import SampleBackground
    from gudrun_classes.sample import Sample


class TestGudPyIO(TestCase):

    def setUp(self) -> None:
        self.expectedInstrument = {

            "name" : "NIMROD",
            "GudrunInputFileDir" : "/home/test/gudpy-water/",
            "dataFileDir" : "NIMROD-water/raw/",
            "dataFileType" : "raw",
            "detectorCalibrationFileName" : "StartupFiles/NIMROD/NIMROD84modules+9monitors+LAB5Oct2012Detector.dat",
            "columnNoPhiVals" : 4,
            "groupFileName" : "StartupFiles/NIMROD/NIMROD84modules+9monitors+LAB5Oct2012Groups.dat",
            "deadtimeConstantsFileName" : "StartupFiles/NIMROD/NIMRODdeadtimeNone.cor",
            "spectrumNumbersForIncidentBeamMonitor" : [4,5],
            "wavelengthRangeForMonitorNormalisation" : (0,0),
            "spectrumNumbersForTransmissionMonitor" : [8,9],
            "incidentMonitorQuietCountConst" : 0.0001,
            "transmissionMonitorQuietCountConst" : 0.0001,
            "channelNosSpikeAnalysis" : (0,0),
            "spikeAnalysisAcceptanceFactor" : 5,
            "wavelengthRangeStepSize" : (0.05, 12.0, 0.1),
            "NoSmoothsOnMonitor" : 200,
            "XScaleRangeStep" : (0.01, 50.0, -0.025),
            "groupingParameterPanel" : (0,0.,0.,0.),
            "groupsAcceptanceFactor" : 1.0,
            "mergePower" : 4,
            "subSingleAtomScattering" : False,
            "byChannel" : 2,
            "incidentFlightPath" : 20.0,
            "spectrumNumberForOutputDiagnosticFiles" : 0,
            "neutronScatteringParametersFile" : "StartupFiles/NIMROD/sears91_gudrun.dat",
            "scaleSelection" : 1,
            "subWavelengthBinnedData" : 0,
            "GudrunStartFolder" : "/home/test/src/Gudrun2017/Gudrun",
            "startupFileFolder" : "/oldwork/test/water",
            "logarithmicStepSize" : 0.04,
            "hardGroupEdges" : True,
            "numberIterations" : 2,
            "tweakTweakFactors" : False

        }

        self.expectedBeam = {

            "sampleGeometry" : "FLATPLATE",
            "noBeamProfileValues" : 2,
            "beamProfileValues" : [1.0,1.0],
            "stepSizeAbsorptionMSNoSlices" : (0.05, 0.2, 100), 
            "angularStepForCorrections" : 10,
            "incidentBeamEdgesRelCentroid" : (-1.5, 1.5, -1.5, 1.5),
            "scatteredBeamEdgesRelCentroid" : (-2.1, 2.1, -2.1, 2.1),
            "filenameIncidentBeamSpectrumParams" : "StartupFiles/NIMROD/spectrum000.dat",
            "overallBackgroundFactor" : 1.0,
            "sampleDependantBackgroundFactor" : 0.0,
            "shieldingAttenuationCoefficient" : 0.0

        }

        self.expectedNormalisation = {

            "numberOfFilesPeriodNumber" : (1,1),
            "dataFiles" : DataFiles(["NIMROD00016702_V.raw"], "NORMALISATION"),
            "numberOfFilesPeriodNumberBg" : (2,1),
            "dataFilesBg" : DataFiles(["NIMROD00016698_EmptyInst.raw", "NIMROD00016703_EmptyInst.raw"], "NORMALISATION BACKGROUND"),
            "forceCalculationOfCorrections" : True,
            "composition" : Composition([Element("V", 0, 1.0)], "Normalisation"),
            "geometry" : "SameAsBeam",
            "thickness" : (0.15, 0.15),
            "angleOfRotationSampleWidth" : (0.0, 5),
            "densityOfAtoms" : -0.0721,
            "tempForNormalisationPC" : 200,
            "totalCrossSectionSource" : "TABLES",
            "normalisationDifferentialCrossSectionFilename" : "*",
            "lowerLimitSmoothedNormalisation" : 0.01,
            "normalisationDegreeSmoothing" : 1.00,
            "minNormalisationSignalBR" : 0.0
        
        }

        self.expectedContainerA = {

            "name" : "CONTAINER N9",
            "numberOfFilesPeriodNumber" : (3,1),
            "dataFiles" : DataFiles(["NIMROD00016694_Empty_N9.raw", "NIMROD00016699_Empty_N9.raw", "NIMROD00016704_Empty_N9.raw"], "CONTAINER N9"),
            "composition" : Composition([Element("Ti", 0, 7.16), Element("Zr", 0, 3.438)], "Container"),
            "geometry" : "SameAsBeam",
            "thickness" : (0.1, 0.1),
            "angleOfRotationSampleWidth" : (0, 5),
            "densityOfAtoms" : -0.0542,
            "totalCrossSectionSource" : "TABLES",
            "tweakFactor" : 1.0,
            "scatteringFractionAttenuationCoefficient" : (1.0, 0.0)
       
        }

        self.expectedContainerB = {

            "name" : "CONTAINER N10",
            "numberOfFilesPeriodNumber" : (3,1),
            "dataFiles" : DataFiles(["NIMROD00016695_Empty_N10.raw", "NIMROD00016700_Empty_N10.raw", "NIMROD00016705_Empty_N10.raw"], "CONTAINER N10"),
            "composition" : Composition([Element("Ti", 0, 7.16), Element("Zr", 0, 3.438)], "Container"),
            "geometry" : "SameAsBeam",
            "thickness" : (0.1, 0.1),
            "angleOfRotationSampleWidth" : (0, 5),
            "densityOfAtoms" : -0.0542,
            "totalCrossSectionSource" : "TABLES",
            "tweakFactor" : 1.0,
            "scatteringFractionAttenuationCoefficient" : (1.0, 0.0)
    
        }

        self.expectedContainerC = {

            "name" : "CONTAINER N6",
            "numberOfFilesPeriodNumber" : (1,1),
            "dataFiles" : DataFiles(["NIMROD00014908_Empty_N6.raw"], "CONTAINER N6"),
            "composition" : Composition([Element("Ti", 0, 7.16), Element("Zr", 0, 3.438)], "Container"),
            "geometry" : "SameAsBeam",
            "thickness" : (0.1, 0.1),
            "angleOfRotationSampleWidth" : (0, 5),
            "densityOfAtoms" : -0.0542,
            "totalCrossSectionSource" : "TABLES",
            "tweakFactor" : 1.0,
            "scatteringFractionAttenuationCoefficient" : (1.0, 0.0)
       
        }

        self.expectedContainerD = {

            "name" : "CONTAINER N8",
            "numberOfFilesPeriodNumber" : (1,1),
            "dataFiles" : DataFiles(["NIMROD00016994_Empty_N8.raw"], "CONTAINER N8"),
            "composition" : Composition([Element("Ti", 0, 7.16), Element("Zr", 0, 3.438)], "Container"),
            "geometry" : "SameAsBeam",
            "thickness" : (0.1, 0.1),
            "angleOfRotationSampleWidth" : (0, 5),
            "densityOfAtoms" : -0.0542,
            "totalCrossSectionSource" : "TABLES",
            "tweakFactor" : 1.0,
            "scatteringFractionAttenuationCoefficient" : (1.0, 0.0)

        }

        self.expectedSampleA = {

            "name" : "SAMPLE H2O, Can N9",
            "numberOfFilesPeriodNumber" : (2,1),
            "dataFiles" : DataFiles(["NIMROD00016608_H2O_in_N9.raw", "NIMROD00016610_H2O_in_N9.raw"], "SAMPLE H2O, Can N9"),
            "forceCalculationOfCorrections" : True,
            "composition" : Composition([Element('H', 0, 2.0), Element('O', 0, 1.0)], "Sample"),
            "geometry" : "SameAsBeam",
            "thickness" : (0.05, 0.05),
            "angleOfRotationSampleWidth" : (0, 5),
            "densityOfAtoms" : -0.1,
            "tempForNormalisationPC" : 0, 
            "totalCrossSectionSource" : 'TRANSMISSION',
            "sampleTweakFactor" : 1.0,
            "topHatW" :-10.0,
            "minRadFT" : 0.8,
            "gor" : 0.1,
            "expAandD"  : (0.0, 1.5, 0),
            "normalisationCorrectionFactor" : 1.0,
            "fileSelfScattering" : "NIMROD00016608_H2O_in_N9.msubw01",
            "normaliseTo" : 0,
            "maxRadFT"  : 50.0,
            "outputUnits"  : 0,
            "powerForBroadening" : 0.5,
            "stepSize" : 0.03,
            "analyse" : False,
            "sampleEnvironementScatteringFuncAttenuationCoeff" : (1.0, 0.0),
            "containers" : [self.expectedContainerA]
        
        }

        self.expectedSampleB = {

            "name" : "SAMPLE D2O, Can N10",
            "numberOfFilesPeriodNumber" : (2,1),
            "dataFiles" : DataFiles(["NIMROD00016609_D2O_in_N10.raw", "NIMROD00016611_D2O_in_N10.raw"], "SAMPLE D2O, Can N10"),
            "forceCalculationOfCorrections" : True,
            "composition" : Composition([Element('H', 2, 2.0), Element('O', 0, 1.0)], "Sample"),
            "geometry" : "SameAsBeam",
            "thickness" : (0.05, 0.05),
            "angleOfRotationSampleWidth" : (0, 5),
            "densityOfAtoms" : -0.1,
            "tempForNormalisationPC" : 0,
            "totalCrossSectionSource" : "TRANSMISSION",
            "sampleTweakFactor" : 1.0,
            "topHatW" :-10.0,
            "minRadFT" : 0.8,
            "gor" : 0.0,
            "expAandD"  : (0.0, 1.5, 0),
            "normalisationCorrectionFactor" : 1.0,
            "fileSelfScattering" : "NIMROD00016609_D2O_in_N10.msubw01",
            "normaliseTo" : 0,
            "maxRadFT"  : 50.0,
            "outputUnits"  : 0,
            "powerForBroadening" : 0.0,
            "stepSize" : 0.03,
            "analyse" : True,
            "sampleEnvironementScatteringFuncAttenuationCoeff" : (1.0, 0.0),
            "containers" : [self.expectedContainerB]

        }

        self.expectedSampleC = {

            "name" : "SAMPLE HDO, Can N6",
            "numberOfFilesPeriodNumber" : (2,1),
            "dataFiles" : DataFiles(["NIMROD00016741_HDO_in_N6.raw", "NIMROD00016743_HDO_in_N6.raw"], "SAMPLE HDO, Can N6"),
            "forceCalculationOfCorrections" : True,
            "composition" : Composition([Element('H', 0, 1.0), Element('O', 0, 1.0), Element('H', 2, 1.0)], "Sample"),
            "geometry" : "SameAsBeam",
            "thickness" : (0.05, 0.05),
            "angleOfRotationSampleWidth" : (0, 5),
            "densityOfAtoms" : -0.1,
            "tempForNormalisationPC" : 0,
            "totalCrossSectionSource" : "TRANSMISSION",
            "sampleTweakFactor" : 1.0,
            "topHatW" :-10.0,
            "minRadFT" : 0.8,
            "gor" : 0.1,
            "expAandD"  : (0.0, 1.5, 0),
            "normalisationCorrectionFactor" : 1.0,
            "fileSelfScattering" : "NIMROD00016741_HDO_in_N6.msubw01",
            "normaliseTo" : 0,
            "maxRadFT"  : 50.0,
            "outputUnits"  : 0,
            "powerForBroadening" : 0.5,
            "stepSize" : 0.03,
            "analyse" : False,
            "sampleEnvironementScatteringFuncAttenuationCoeff" : (1.0, 0.0),
            "containers" : [self.expectedContainerC]

        }

        self.expectedSampleD = {

            "name" : "SAMPLE Null Water, Can N8",
            "numberOfFilesPeriodNumber" : (2,1),
            "dataFiles" : DataFiles(["NIMROD00016742_NullWater_in_N8.raw", "NIMROD00016742_NullWater_in_N8.raw"], "SAMPLE Null Water, Can N8"),
            "forceCalculationOfCorrections" : True,
            "composition" : Composition([Element('H', 0, 1.281), Element('O', 0, 1.0), Element('H', 2, 0.7185)], "SAMPLE Null Water, Can N8"),
            "geometry" : "SameAsBeam",
            "thickness" : (0.05, 0.05),
            "angleOfRotationSampleWidth" : (0, 5),
            "densityOfAtoms" : -0.1,
            "tempForNormalisationPC" : 0,
            "totalCrossSectionSource" : "TRANSMISSION",
            "sampleTweakFactor" : 1.0,
            "topHatW" :-10.0,
            "minRadFT" : 0.8,
            "gor" : 0.1,
            "expAandD"  : (0.0, 1.5, 0),
            "normalisationCorrectionFactor" : 1.0,
            "fileSelfScattering" : "NIMROD00016742_NullWater_in_N8.msubw01",
            "normaliseTo" : 0,
            "maxRadFT"  : 50.0,
            "outputUnits"  : 0,
            "powerForBroadening" : 0.5,
            "stepSize" : 0.03,
            "analyse" : False,
            "sampleEnvironementScatteringFuncAttenuationCoeff" : (1.0, 0.0),
            "containers" : [self.expectedContainerD]
        }

        self.expectedSampleBackgrounds = {
            "1" : {
                "numberOfFilesPeriodNumber" : (2,1),
                "dataFiles" : DataFiles(["NIMROD00016698_EmptyInst.raw", "NIMROD00016703_EmptyInst.raw"], "SAMPLE BACKGROUND"),
                "samples" : [self.expectedSampleA, self.expectedSampleB, self.expectedSampleC]
            }
        }


        return super().setUp()

    def tearDown(self) -> None:

        return super().tearDown()

    def testLoadGudrunFile(self):
        path = 'TestData/NIMROD-water/water.txt'
        dirpath = "/".join(os.path.realpath(__file__).split("/")[:-1]) + "/" + path
        g = GudrunFile(dirpath)
        self.assertIsInstance(g, GudrunFile)
        
        instrumentAttrsDict = g.instrument.__dict__

        for key in instrumentAttrsDict.keys():
            self.assertEqual(self.expectedInstrument[key], instrumentAttrsDict[key])

        beamAttrsDict = g.beam.__dict__

        for key in beamAttrsDict.keys():
            self.assertEqual(self.expectedBeam[key], beamAttrsDict[key])
        
        normalisationAttrsDict = g.normalisation.__dict__

        for key in normalisationAttrsDict.keys():
            if isinstance(normalisationAttrsDict[key], (DataFiles, Composition)):
                self.assertEqual(str(self.expectedNormalisation[key]), str(normalisationAttrsDict[key]))
            else:
                self.assertEqual(self.expectedNormalisation[key], normalisationAttrsDict[key])

        self.assertEqual(len(g.sampleBackgrounds), 1)

        sampleBackgroundsAttrsDict = g.sampleBackgrounds[0].__dict__


        for key in sampleBackgroundsAttrsDict.keys():
            if key == "samples":
                for i, sample in enumerate(self.expectedSampleBackgrounds["1"][key]):
            
                    sampleAttrsDict = g.sampleBackgrounds[0].samples[i].__dict__

                    for key_ in sampleAttrsDict.keys():

                        if key_ == "containers":
                            for j, container in enumerate(sample[key_]):
                                containerAttrsDict = g.sampleBackgrounds[0].samples[i].containers[j].__dict__

                                for _key in containerAttrsDict.keys():

                                    if isinstance(container[_key], (DataFiles, Composition)):
                                        self.assertEqual(str(container[_key]), str(containerAttrsDict[_key]))
                                    else:
                                        self.assertEqual(container[_key], containerAttrsDict[_key])

                        elif isinstance(sample[key_], (DataFiles, Composition)):
                            self.assertEqual(str(sample[key_]), str(sampleAttrsDict[key_]))
                        else:
                            self.assertEqual(sample[key_], sampleAttrsDict[key_])


            elif isinstance(sampleBackgroundsAttrsDict[key], DataFiles):
                self.assertEqual(str(self.expectedSampleBackgrounds["1"][key]), str(sampleBackgroundsAttrsDict[key]))
            else:
                self.assertEqual(self.expectedSampleBackgrounds["1"][key], sampleBackgroundsAttrsDict[key])            