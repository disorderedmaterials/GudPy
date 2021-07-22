import sys, os
from os.path import isfile
import time
from copy import deepcopy

try:
    sys.path.insert(1, os.path.join(sys.path[0], '../scripts'))
    from utils import *
    from instrument import Instrument
    from beam import Beam
    from normalisation import Normalisation
    from sample import Sample
    from sample_background import SampleBackground
    from container import Container
    from composition import Composition
    from element import Element
    from data_files import DataFiles
except ModuleNotFoundError:
    sys.path.insert(1, os.path.join(sys.path[0], 'scripts'))
    from scripts.utils import *
    from gudrun_classes.beam import Beam
    from gudrun_classes.composition import Composition
    from gudrun_classes.container import Container
    from gudrun_classes.data_files import DataFiles
    from gudrun_classes.element import Element
    from gudrun_classes.instrument import Instrument
    from gudrun_classes.normalisation import Normalisation
    from gudrun_classes.sample_background import SampleBackground
    from gudrun_classes.sample import Sample

class GudrunFile:
    def __init__(self, path=None, data=None):
        self.path = path
        fname = os.path.basename(self.path)
        ref_fname = 'gudpy_{}'.format(fname)
        dir = os.path.dirname(self.path)
        self.outpath = '{}/{}'.format(dir, ref_fname)
        #If a dictionary of data is supplied, unpack the dictionary and assign the values.
        #Otherwise, parse via the path.
        if data:
            try:
                self.instrument = data['instrument']
                self.beam = data['beam']
                self.normalisation = data['normalisation']
                self.samples = data['samples']
            except KeyError as keyError:
                raise KeyError('Dictionary is of incorrect format, KeyError was raised when accessing a key: ' + str(keyError))
        else:
            self.instrument = None
            self.beam = None
            self.normalisation = None
            self.sampleBackgrounds = []
            self.ignoredSamples = []
            self.error = None
            self.parse()
    

    def parseInstrument(self, lines):
        self.instrument = Instrument()

        KEYPHRASES = {

            "name" : "name",
            "GudrunInputFileDir" : "Gudrun input file dir",
            "dataFileDir" : "Data file dir",
            "dataFileType" : "Data file type",
            "detectorCalibrationFileName" : "Detector calibration",
            "columnNoPhiVals" : "phi values",
            "groupFileName" : "Groups file name",
            "deadtimeConstantsFileName" : "Deadtime constants",          
            "spectrumNumbersForIncidentBeamMonitor" : ["Spectrum", "number", "incident"],
            "wavelengthRangeForMonitorNormalisation" : ["Wavelength", "range", "normalisation"],
            "spectrumNumbersForTransmissionMonitor" : ["Spectrum", "number", "transmission"],
            "incidentMonitorQuietCountConst" : ["Incident", "quiet", "count"],
            "transmissionMonitorQuietCountConst" : ["Transmission", "quiet", "count"],
            "channelNosSpikeAnalysis" : "Channel numbers",
            "spikeAnalysisAcceptanceFactor" : "Spike analysis acceptance",
            "wavelengthRangeStepSize" : ["Wavelength", "range", "step", "size"],
            "NoSmoothsOnMonitor" : "smooths on monitor",
            "XScaleRangeStep" : "x-scale",
            "groupsAcceptanceFactor" : "Groups acceptance",
            "mergePower" : "Merge power",
            "subSingleAtomScattering" : ["single", "atom", "scattering?"],
            "byChannel" : "By channel?",
            "incidentFlightPath" : "Incident flight path",
            "spectrumNumberForOutputDiagnosticFiles" : ["Spectrum", "number", "diagnostic"],
            "neutronScatteringParametersFile" : "Neutron scattering parameters",
            "scaleSelection" : "Scale selection",
            "subWavelengthBinnedData" : ["Subtract", "wavelength-binned"],
            "GudrunStartFolder" : "Folder where Gudrun started",
            "startupFileFolder" : "Folder containing the startup file",
            "logarithmicStepSize" : "Logarithmic",
            "hardGroupEdges" : "edges?",
            "numberIterations" : "iterations",
            "tweakTweakFactors": "tweak"
        }   



        #Extract marker line
        lines = [line for line in lines if not 'end input of specified values' in line]

        #Check if the grouping parameter panel attribute is present in the file
        isGroupingParameterPanelUsed = [line for line in lines if 'Group, Xmin, Xmax, Background factor' in line]

        #If grouping parameter panel is not being used, remove its key from the dict
        auxVars = deepcopy(self.instrument.__dict__)
        if not len(isGroupingParameterPanelUsed):
            auxVars.pop('groupingParameterPanel', None)

        #Map the attributes of the Instrument class to line numbers.


        FORMAT_MAP = dict.fromkeys(auxVars.keys())
        FORMAT_MAP.update((k, i) for i,k in enumerate(FORMAT_MAP))
        #Categorise attributes by variables, for easier handling.

        STRINGS = [x for x in self.instrument.__dict__.keys() if isinstance(self.instrument.__dict__[x],str)]
        LISTS = [x for x in self.instrument.__dict__.keys() if isinstance(self.instrument.__dict__[x], list)]
        INTS = [x for x in self.instrument.__dict__.keys() if isinstance(self.instrument.__dict__[x], int) and not isinstance(self.instrument.__dict__[x], bool)]
        FLOATS = [x for x in self.instrument.__dict__.keys() if isinstance(self.instrument.__dict__[x], float)]
        BOOLS = [x for x in self.instrument.__dict__.keys() if isinstance(self.instrument.__dict__[x], bool)]
        TUPLES = [x for x in self.instrument.__dict__.keys() if isinstance(self.instrument.__dict__[x], tuple)]
        TUPLE_INTS = [x for x in TUPLES if iteristype(self.instrument.__dict__[x], int)]
        TUPLE_FLOATS = [x for x in TUPLES if iteristype(self.instrument.__dict__[x], float)]

        """
        Get all attributes that are strings:
            - Instrument name
            - Gudrun input file directory
            - Data file directory
            - Data file type
            - Detector calibration file name
            - Group file name
            - Deadtime constants file name
            - Neutron scattering parameters file
            - Gudrun start folder
            - Startup file folder
        """

        for key in STRINGS:
            try:
                isin_, i = isin(KEYPHRASES[key], lines)
                if not isin_:
                    raise ValueError("Whilst parsing INSTRUMENT, {} was not found".format(key))
                if i!=FORMAT_MAP[key]:
                    FORMAT_MAP[key] = i
                self.instrument.__dict__[key] = firstword(lines[FORMAT_MAP[key]])
            except IndexError:
                continue        
        """
        Get all attributes that are integers:
            - User table column number for phi values
            - Spike analysis acceptance factor
            - Number of smooths on monitor
            - Merge power
            - Channel for subtracting single atom scattering
            - Spectrum number for output diagnostic files
            - Scale selection
            - Number of iterations
        """

        for key in INTS:
            isin_, i = isin(KEYPHRASES[key], lines)
            if not isin_:
                raise ValueError("Whilst parsing INSTRUMENT, {} was not found".format(key))
            if i!=FORMAT_MAP[key]:
                FORMAT_MAP[key] = i
            self.instrument.__dict__[key] = int(firstword(lines[FORMAT_MAP[key]]))

        """
        Get all attributes that are floats (doubles):
            - Incident monitor quiet count constant
            - Transmission monitor quiet count constant
            - Groups acceptance factor
            - Incident flight path
            - Logarithmic step size
        """

        for key in FLOATS:
            isin_, i = isin(KEYPHRASES[key], lines)
            if not isin_:
                raise ValueError("Whilst parsing INSTRUMENT, {} was not found".format(key))
            if i!=FORMAT_MAP[key]:
                FORMAT_MAP[key] = i
            self.instrument.__dict__[key] = float(firstword(lines[FORMAT_MAP[key]]))

        """
        Get all attributes that are boolean values:
            - Subtract single atom scattering?
            - Subtract wavelength-binned data?
            - Hard group edges?
            - Tweak the tweak factor(s)?
        """

        for key in BOOLS:
            isin_, i = isin(KEYPHRASES[key], lines)
            if not isin_:
                raise ValueError("Whilst parsing INSTRUMENT, {} was not found".format(key))
            if i!=FORMAT_MAP[key]:
                FORMAT_MAP[key] = i
            self.instrument.__dict__[key] = boolifyNum(int(firstword(lines[FORMAT_MAP[key]])))

        """
        Get all attributes that need to be stored in arbitrary sized lists:
            - Spectrum numbers for incident beam monitor
            - Spectrum numbers for transmission monitor
        """

        for key in LISTS:
            isin_, i = isin(KEYPHRASES[key], lines)
            if not isin_:
                raise ValueError("Whilst parsing INSTRUMENT, {} was not found".format(key))
            if i!=FORMAT_MAP[key]:
                FORMAT_MAP[key] = i
            self.instrument.__dict__[key] = extract_ints_from_string(lines[FORMAT_MAP[key]])
        
        """
        Get all attributes that need to be stored specifically as a tuple of ints:
            - Wavelength range for monitor normalisation
            - Channel numbers for spike analysis
        """

        for key in TUPLE_INTS:
            isin_, i = isin(KEYPHRASES[key], lines)
            if not isin_:
                raise ValueError("Whilst parsing INSTRUMENT, {} was not found".format(key))
            if i!=FORMAT_MAP[key]:
                FORMAT_MAP[key] = i
            self.instrument.__dict__[key] = tuple(extract_ints_from_string(lines[FORMAT_MAP[key]]))
        
        """
        Get all attributes that need to be stored specifically as a tuple of floats (doubles):
            - Wavelength range to use and step size.
        """

        for key in TUPLE_FLOATS:
            isin_, i = isin(KEYPHRASES[key], lines)
            if not isin_:
                raise ValueError("Whilst parsing INSTRUMENT, {} was not found".format(key))
            if i!=FORMAT_MAP[key]:
                FORMAT_MAP[key] = i
            self.instrument.__dict__[key] = tuple(extract_floats_from_string(lines[FORMAT_MAP[key]]))

        """
        Get the attributes for the grouping parameter panel:
            - Group
            - Xmin
            - Xmax
            - Background factor
        """
        if isGroupingParameterPanelUsed:
            key = 'groupingParameterPanel'
            group = int(firstword(lines[FORMAT_MAP[key]]))
            maxMinBf = extract_floats_from_string(lines[FORMAT_MAP[key]])[1:]
            groupingParameterPanel = tuple([group] + maxMinBf)
            self.instrument.__dict__[key] = groupingParameterPanel

    def parseBeam(self, lines):
        self.beam = Beam()

        KEYPHRASES = {

            "sampleGeometry" : "Sample geometry",
            "noBeamProfileValues" : ["number","beam", "profile", "values"],
            "beamProfileValues" : ["Beam", "profile", "values", "("],
            "stepSizeAbsorptionMSNoSlices" : ["Step", "size", "m.s"],
            "angularStepForCorrections" : "Angular step",
            "incidentBeamEdgesRelCentroid" : "Incident beam edges",
            "scatteredBeamEdgesRelCentroid" : "Scattered beam edges",
            "filenameIncidentBeamSpectrumParams" : ["Filename", "incident", "spectrum", "parameters"],
            "overallBackgroundFactor" : "Overall background factor",
            "sampleDependantBackgroundFactor" : "Sample dependent background",
            "shieldingAttenuationCoefficient" : ["Shielding", "attenuation", "coefficient"]

        }

        #Map the attributes of the Beam class to line numbers.

        FORMAT_MAP = dict.fromkeys(self.beam.__dict__.keys())
        FORMAT_MAP.update((k, i) for i,k in enumerate(FORMAT_MAP))

        #Categorise attributes by variables, for easier handling.

        STRINGS = [x for x in self.beam.__dict__.keys() if isinstance(self.beam.__dict__[x],str)]
        LISTS = [x for x in self.beam.__dict__.keys() if isinstance(self.beam.__dict__[x], list)]
        INTS = [x for x in self.beam.__dict__.keys() if isinstance(self.beam.__dict__[x], int) and not isinstance(self.beam.__dict__[x], bool)]
        FLOATS = [x for x in self.beam.__dict__.keys() if isinstance(self.beam.__dict__[x], float)]
        TUPLES = [x for x in self.beam.__dict__.keys() if isinstance(self.beam.__dict__[x], tuple)]
        TUPLE_FLOATS = [x for x in TUPLES if iteristype(self.beam.__dict__[x], float)] 

        """
        Get all attributes that are strings:
            - Sample geometry
            - Filename for incident beam spectrum parameters
        """

        for key in STRINGS:
            isin_, i = isin(KEYPHRASES[key], lines)
            if not isin_:
                raise ValueError("Whilst parsing BEAM, {} was not found".format(key))
            if i!=FORMAT_MAP[key]:
                FORMAT_MAP[key] = i
            self.beam.__dict__[key] = firstword(lines[FORMAT_MAP[key]])
        
        """
        Get all attributes that are integers:
            - Number of beam profile values
            - Angular step for corrections
        """

        for key in INTS:
            isin_, i = isin(KEYPHRASES[key], lines)
            if not isin_:
                raise ValueError("Whilst parsing BEAM, {} was not found".format(key))
            if i!=FORMAT_MAP[key]:
                FORMAT_MAP[key] = i 
            self.beam.__dict__[key] = int(firstword(lines[FORMAT_MAP[key]]))
        
        """
        Get all attributes that are floats (doubles):
            - Overall background factor
            - Sample dependant background factor
            - Shielding attenuation coefficient
        """

        for key in FLOATS:
            isin_, i = isin(KEYPHRASES[key], lines)
            if not isin_:
                raise ValueError("Whilst parsing BEAM, {} was not found".format(key))
            if i!=FORMAT_MAP[key]:
                FORMAT_MAP[key] = i 
            self.beam.__dict__[key] = float(firstword(lines[FORMAT_MAP[key]]))


        """
        Get all attributes that need to be stored in arbitrary sized lists:
            - Beam profile values
        """

        for key in LISTS:
            isin_, i = isin(KEYPHRASES[key], lines)
            if not isin_:
                raise ValueError("Whilst parsing BEAM, {} was not found".format(key))
            if i!=FORMAT_MAP[key]:
                FORMAT_MAP[key] = i 
            self.beam.__dict__[key] = extract_floats_from_string(lines[FORMAT_MAP[key]])
        
        """
        Get all attributes that need to be stored specifically as a tuple of floats (doubles):
            - Incident beam edges relative to centre of sample
            - Scattered beam edges relative to centre of sample
        """

        for key in TUPLE_FLOATS:
            isin_, i = isin(KEYPHRASES[key], lines)
            if not isin_:
                raise ValueError("Whilst parsing BEAM, {} was not found".format(key))
            if i!=FORMAT_MAP[key]:
                FORMAT_MAP[key] = i 
            self.beam.__dict__[key] = tuple(extract_floats_from_string(lines[FORMAT_MAP[key]]))

        """
        Get the step size for absorption and m.s. calculation and number of slices
        """

        key = 'stepSizeAbsorptionMSNoSlices'
        isin_, i = isin(KEYPHRASES[key], lines)
        if not isin_:
            raise ValueError("Whilst parsing BEAM, {} was not found".format(key))
        if i!=FORMAT_MAP[key]:
            FORMAT_MAP[key] = i 
        stepSizeAbsorptionMS = extract_floats_from_string(lines[FORMAT_MAP[key]])[:2]
        noSlices = int(extract_floats_from_string(lines[FORMAT_MAP[key]])[2])
        stepSizeAbsorptionMSNoSlices = tuple(stepSizeAbsorptionMS + [noSlices])
        self.beam.__dict__[key] = stepSizeAbsorptionMSNoSlices

    def parseNormalisation(self, lines):
        self.normalisation = Normalisation()

        KEYPHRASES = {

            "forceCalculationOfCorrections": ["Force", "corrections?"],
            "geometry" : "Geometry",
            "thickness" : ["Upstream", "downstream", "thickness"],
            "angleOfRotationSampleWidth" : "Angle of rotation",
            "densityOfAtoms" : "Density",
            "tempForNormalisationPC" : "Placzek correction",
            "totalCrossSectionSource" : "Total cross",
            "normalisationDifferentialCrossSectionFilename" : ["Normalisation", "cross section", "filename"],
            "lowerLimitSmoothedNormalisation" : "Lower limit",
            "normalisationDegreeSmoothing" : "Normalisation degree",
            "minNormalisationSignalBR" : "background ratio"
            
        }


        #Count the number of data files and background data files.
        numberFiles = extract_ints_from_string(lines[0])[0]
        numberFilesBG = extract_ints_from_string(lines[numberFiles+1])[0]

        #Count the number of elements
        numberElements = count_occurrences('Normalisation atomic composition', lines) + count_occurrences('Composition', lines)

        #Map the attributes of the Beam class to line numbers.

        FORMAT_MAP = dict.fromkeys(self.normalisation.__dict__.keys())
        FORMAT_MAP.pop('dataFiles', None)
        FORMAT_MAP.pop('dataFilesBg', None)
        FORMAT_MAP.pop('composition', None)
        FORMAT_MAP.update((k, i) for i,k in enumerate(FORMAT_MAP))


        #Index arithmetic to fix indexes, which get skewed by data files and elements

        for key in FORMAT_MAP.keys():
            if FORMAT_MAP[key] > 0:
                FORMAT_MAP[key]+=numberFiles
        
        marker = 0
        for key in FORMAT_MAP.keys():
            if FORMAT_MAP[key]-numberFiles == 1:
                marker = FORMAT_MAP[key]
                continue
            if marker:
                if FORMAT_MAP[key] > marker:
                    FORMAT_MAP[key]+=numberFilesBG
        
        marker = 0
        for key in FORMAT_MAP.keys():
            if FORMAT_MAP[key]-numberFilesBG-numberFiles == 2:
                marker = FORMAT_MAP[key]
                continue
            if marker:
                if FORMAT_MAP[key] > marker:
                    FORMAT_MAP[key]+=numberElements+1


        #Categorise attributes by variables, for easier handling.
        STRINGS = [x for x in self.normalisation.__dict__.keys() if isinstance(self.normalisation.__dict__[x],str)]
        INTS = [x for x in self.normalisation.__dict__.keys() if isinstance(self.normalisation.__dict__[x], int) and not isinstance(self.normalisation.__dict__[x], bool)]
        FLOATS = [x for x in self.normalisation.__dict__.keys() if isinstance(self.normalisation.__dict__[x], float)]
        BOOLS = [x for x in self.normalisation.__dict__.keys() if isinstance(self.normalisation.__dict__[x], bool)]
        TUPLES = [x for x in self.normalisation.__dict__.keys() if isinstance(self.normalisation.__dict__[x], tuple)]
        TUPLE_FLOATS = [x for x in TUPLES if iteristype(self.normalisation.__dict__[x], float)] 
        TUPLE_INTS = [x for x in TUPLES if iteristype(self.normalisation.__dict__[x], int)]


        """
        Get all attributes that are strings:
            - Geometry
            - Total cross section source
            - Normalisation differential cross section filename
        """

        for key in STRINGS:
            isin_, i = isin(KEYPHRASES[key], lines)
            if not isin_:
                raise ValueError("Whilst parsing NORMALISATION  , {} was not found".format(key))
            if i!=FORMAT_MAP[key]:
                FORMAT_MAP[key] = i 
            self.normalisation.__dict__[key] = firstword(lines[FORMAT_MAP[key]])
            
        """
        Get all attributes that are integers:
            - Temperature for normalisation Placzek correction
        """

        for key in INTS:
            isin_, i = isin(KEYPHRASES[key], lines)
            if not isin_:
                raise ValueError("Whilst parsing NORMALISATION  , {} was not found".format(key))
            if i!=FORMAT_MAP[key]:
                FORMAT_MAP[key] = i 
            self.normalisation.__dict__[key] = int(firstword(lines[FORMAT_MAP[key]]))
                 
        """
        Get all attributes that are floats (doubles):
            - Density of atoms
            - Lower limit on smoothed normalisation
            - Normalisation degree smoothing
            - Minimum normalisation signal to background ratio
        """

        for key in FLOATS:
            isin_, i = isin(KEYPHRASES[key], lines)
            if not isin_:
                raise ValueError("Whilst parsing NORMALISATION  , {} was not found".format(key))
            if i!=FORMAT_MAP[key]:
                FORMAT_MAP[key] = i 
            self.normalisation.__dict__[key] = float(firstword(lines[FORMAT_MAP[key]]))

        """
        Get all attributes that are boolean values:
            - Subtract single atom scattering?
            - Subtract wavelength-binned data?
            - Hard group edges?
            - Tweak the tweak factor(s)?
        """

        for key in BOOLS:
            isin_, i = isin(KEYPHRASES[key], lines)
            if not isin_:
                raise ValueError("Whilst parsing NORMALISATION  , {} was not found".format(key))
            if i!=FORMAT_MAP[key]:
                FORMAT_MAP[key] = i 
            self.normalisation.__dict__[key] = boolifyNum(int(firstword(lines[FORMAT_MAP[key]])))


        """
        Get all attributes that need to be stored specifically as a tuple of floats (doubles):
            - Upstream and downstream thickness
            - Angle of rotation and sample width
        """

        for key in TUPLE_FLOATS:
            isin_, i = isin(KEYPHRASES[key], lines)
            if not isin_:
                raise ValueError("Whilst parsing NORMALISATION  , {} was not found".format(key))
            if i!=FORMAT_MAP[key]:
                FORMAT_MAP[key] = i 
            self.normalisation.__dict__[key] = tuple(extract_floats_from_string(lines[FORMAT_MAP[key]]))
            if key == 'angleOfRotationSampleWidth':
                self.normalisation.__dict__[key] = (self.normalisation.__dict__[key][0], int(self.normalisation.__dict__[key][1]))


        """
        Get all attributes that need to be stored specifically as a tuple of ints:
            - Number of files and period number
            - Number of background files and period number
        """

        for key in TUPLE_INTS:
            self.normalisation.__dict__[key] = tuple(extract_ints_from_string(lines[FORMAT_MAP[key]]))
        
        
        #Get all of the normalisation datafiles and their information.
        

        dataFiles = []
        for j in range (self.normalisation.numberOfFilesPeriodNumber[0]):
            curr = lines[FORMAT_MAP['numberOfFilesPeriodNumber']+j+1]
            if 'data files' in curr or 'Data files' in curr:
                dataFiles.append(firstword(curr))
            else:
                raise ValueError('Number of data files does not match number of data files specified')
        self.normalisation.dataFiles = DataFiles(deepcopy(dataFiles), 'NORMALISATION')

        #Get all of the normalisation background datafiles and their information.


        dataFiles = []
        for j in range (self.normalisation.numberOfFilesPeriodNumberBg[0]):
            curr = lines[FORMAT_MAP['numberOfFilesPeriodNumberBg']+j+1]
            if 'data files' in curr or 'Data files' in curr:
                dataFiles.append(firstword(curr))
            else:
                raise ValueError('Number of data files does not match number of data files specified')
        self.normalisation.dataFilesBg = DataFiles(deepcopy(dataFiles), 'NORMALISATION BACKGROUND')

        #Get all of the elements and their information, and then build the composition

        elements = []
        for j in range (numberElements):
            curr = lines[FORMAT_MAP['forceCalculationOfCorrections']+j+1]
            if 'Normalisation atomic composition' in curr or 'Composition' in curr :
                elementInfo = [x for x in curr.split(" ") if x][:3]
                element = Element(elementInfo[0], int(elementInfo[1]), float(elementInfo[2]))
                elements.append(element)

        self.normalisation.composition = Composition(elements, 'Normalisation')

                    
    def parseSampleBackground(self, lines):
        sampleBackground = SampleBackground()

        if not isin("Number of files and period number", lines[0]):
            raise ValueError("Whilst parsing SAMPLE BACKGROUND {}, numberOfFilesPeriodNumber was not found".format(len(self.sampleBackgrounds+1)))

        #Get the number of files and period number.
        sampleBackground.numberOfFilesPeriodNumber = tuple(extract_ints_from_string(lines[0]))
        #Get the associated data files.
        dataFiles = []
        for i in range(sampleBackground.numberOfFilesPeriodNumber[0]):
            if 'data files' in lines[i+1]:
                dataFiles.append(firstword(lines[i+1]))
            else:
                raise ValueError('Number of data files does not match number of data files specified')
        sampleBackground.dataFiles = DataFiles(dataFiles, 'SAMPLE BACKGROUND')

        return sampleBackground


    def parseSample(self, lines):
        sample = Sample()

        #Extract the name from the lines, and then discard the unnecessary lines.
        sample.name = str(lines[0][:-2]).strip()
        lines[:] = lines[2:]

        KEYPHRASES = {
            
            "numberOfFilesPeriodNumber" : ["files", "period number"],
            "forceCalculationOfCorrections": ["Force", "corrections?"],
            "geometry" : "Geometry",
            "thickness" : ["Upstream", "downstream", "thickness"],
            "angleOfRotationSampleWidth" : "Angle of rotation",
            "densityOfAtoms" : "Density",
            "tempForNormalisationPC" : "Placzek correction",
            "totalCrossSectionSource" : "Total cross",
            "sampleTweakFactor" : "tweak factor",
            "topHatW" : "Top hat width",
            "minRadFT" : "Minimum radius for FT",
            "gor" : "g(r)",
            "expAandD" : ["Exponential", "amplitude", "decay"],
            "normalisationCorrectionFactor" : "Normalisation correction factor",
            "fileSelfScattering" : ["file", "self scattering", "function"],
            "normaliseTo" : "Normalise",
            "maxRadFT": "Maximum radius for FT",
            "outputUnits": "Output units",
            "powerForBroadening" : "Power for broadening",
            "stepSize": "Step size",
            "analyse" : ["Analyse", "sample?"],
            "sampleEnvironementScatteringFuncAttenuationCoeff" : ["environment", "scattering fraction", "attenuation coefficient"]
        
        }

        #Discard lines which don't contain information.
        lines = [line for line in lines if not 'end of' in line and not 'to finish' in line]

        #Count the number of files and the number of elements.
        numberFiles = count_occurrences('data files', lines)
        numberElements = count_occurrences('Sample atomic composition', lines) + count_occurrences('Composition', lines)

        #Map the attributes of the Sample class to line numbers.

        FORMAT_MAP = dict.fromkeys(sample.__dict__.keys())
        FORMAT_MAP.pop('name', None)
        FORMAT_MAP.pop('dataFiles', None)
        FORMAT_MAP.pop('composition', None)
        FORMAT_MAP.pop('sampleBackground', None)
        FORMAT_MAP.pop('containers', None)
        FORMAT_MAP.update((k, i) for i,k in enumerate(FORMAT_MAP))



        #Index arithmetic to fix indexes, which get skewed by data files and elements

        for key in FORMAT_MAP.keys():
            if FORMAT_MAP[key] > 0:
                FORMAT_MAP[key]+=numberFiles
        
        marker = 0
        for key in FORMAT_MAP.keys():
            if FORMAT_MAP[key]-numberFiles == 1:
                marker = FORMAT_MAP[key]
                # print(key)
                continue
            if marker:
                if FORMAT_MAP[key] > marker:
                    FORMAT_MAP[key]+=numberElements

        #Categorise attributes by variables, for easier handling.
        STRINGS = [x for x in sample.__dict__.keys() if isinstance(sample.__dict__[x],str)]
        INTS = [x for x in sample.__dict__.keys() if isinstance(sample.__dict__[x], int) and not isinstance(sample.__dict__[x], bool)]
        FLOATS = [x for x in sample.__dict__.keys() if isinstance(sample.__dict__[x], float)]
        BOOLS = [x for x in sample.__dict__.keys() if isinstance(sample.__dict__[x], bool)]
        TUPLES = [x for x in sample.__dict__.keys() if isinstance(sample.__dict__[x], tuple)]
        TUPLE_FLOATS = [x for x in TUPLES if iteristype(sample.__dict__[x], float)] 
        TUPLE_INTS = [x for x in TUPLES if iteristype(sample.__dict__[x], int)]


        """
        Get all attributes that are strings:
            - Geometry
            - Total cross section source
            - File containing self scattering as a function of wavelength [A]
        """

        for key in STRINGS:
            try:
                isin_, i = isin(KEYPHRASES[key], lines)
                if not isin_:
                    raise ValueError("Whilst parsing {}  , {} was not found".format(sample.name, key))
                if i!=FORMAT_MAP[key]:
                    FORMAT_MAP[key] = i 
                sample.__dict__[key] = firstword(lines[FORMAT_MAP[key]])
            except KeyError:
                continue
            # print(firstword(lines(FORMAT_MAP[key])))
            
        """
        Get all attributes that are integers:
            - Temperature for normalisation Placzek correction
            - Top hat width (1/\u212b) for cleaning up Fourier Transform
            - Normalise to
            - Output units
        """

        for key in INTS:
            isin_, i = isin(KEYPHRASES[key], lines)
            if not isin_:
                raise ValueError("Whilst parsing {}, {} was not found".format(sample.name, key))
            if i!=FORMAT_MAP[key]:
                FORMAT_MAP[key] = i 
            sample.__dict__[key] = int(firstword(lines[FORMAT_MAP[key]]))
                 
        """
        Get all attributes that are floats (doubles):
            - Density of atoms
            - Sample tweak factor
            - Minimum radius for Fourier Transform
            - g(r) broadening at r= 1A
            - Maximum radius for Fourier Transform
            - Power for broadening function
            - Step size
        """

        for key in FLOATS:
            isin_, i = isin(KEYPHRASES[key], lines)
            if not isin_:
                raise ValueError("Whilst parsing {}, {} was not found".format(sample.name, key))
            if i!=FORMAT_MAP[key]:
                FORMAT_MAP[key] = i 
            sample.__dict__[key] = float(firstword(lines[FORMAT_MAP[key]]))

        """
        Get all attributes that are boolean values:
            - Force calculation of corrections?
            - Analyse this sample?
        """

        for key in BOOLS:
            isin_, i = isin(KEYPHRASES[key], lines)
            if not isin_:
                raise ValueError("Whilst parsing {}, {} was not found".format(sample.name, key))
            if i!=FORMAT_MAP[key]:
                FORMAT_MAP[key] = i 
            sample.__dict__[key] = boolifyNum(int(firstword(lines[FORMAT_MAP[key]])))


        """
        Get all attributes that need to be stored specifically as a tuple of floats (doubles):
            - Upstream and downstream thickness
            - Angle of rotation and sample width
            - Sample environment scattering fraction and attenuation coefficient
        """

        for key in TUPLE_FLOATS:
            isin_, i = isin(KEYPHRASES[key], lines)
            if not isin_:
                raise ValueError("Whilst parsing {}, {} was not found".format(sample.name, key))
            if i!=FORMAT_MAP[key]:
                FORMAT_MAP[key] = i 
            sample.__dict__[key] = tuple(extract_floats_from_string(lines[FORMAT_MAP[key]]))
            if key == 'angleOfRotationSampleWidth':
                sample.__dict__[key] = (sample.__dict__[key][0], int(sample.__dict__[key][1]))


        """
        Get all attributes that need to be stored specifically as a tuple of ints:
            - Number of files and period number
        """

        for key in TUPLE_INTS:
            isin_, i = isin(KEYPHRASES[key], lines)
            if not isin_:
                raise ValueError("Whilst parsing {}, {} was not found".format(sample.name, key))
            if i!=FORMAT_MAP[key]:
                FORMAT_MAP[key] = i 
            sample.__dict__[key] = tuple(extract_ints_from_string(lines[FORMAT_MAP[key]]))

        """
        Get the exponential amplitude and decay
        """

        key = 'expAandD'
        isin_, i = isin(KEYPHRASES[key], lines)
        if not isin_:
            raise ValueError("Whilst parsing {}, {} was not found".format(sample.name, key))
        if i!=FORMAT_MAP[key]:
            FORMAT_MAP[key] = i 
        expAmp = extract_floats_from_string(lines[FORMAT_MAP[key]])[:2]
        decay = int(extract_floats_from_string(lines[FORMAT_MAP[key]])[2])
        expAandD = tuple(expAmp + [decay])
        sample.__dict__[key] = expAandD
        
        #Get all of the sample datafiles and their information.

        dataFiles = []
        for j in range (sample.numberOfFilesPeriodNumber[0]):
            curr = lines[FORMAT_MAP['numberOfFilesPeriodNumber']+j+1]
            if 'data files' in curr:
                dataFiles.append(firstword(curr))
            else:
                raise ValueError('Number of data files does not match number of data files specified')
        sample.dataFiles = DataFiles(deepcopy(dataFiles), '{}'.format(sample.name))

        #Get all of the elements and their information, and then build the composition

        elements = []
        for j in range (numberElements):
            curr = lines[FORMAT_MAP['forceCalculationOfCorrections']+j+1]
            if 'Sample atomic composition' in curr or 'Composition' in curr:
                elementInfo = [x for x in curr.split(" ") if x][:3]
                element = Element(elementInfo[0], int(elementInfo[1]), float(elementInfo[2]))
                elements.append(element)

        sample.composition = Composition(elements, 'Sample')

        return sample

    def parseContainer(self, lines):
        container = Container()
        #Extract the name from the lines, and then discard the unnecessary lines.
        container.name = str(lines[0][:-2]).strip()
        lines[:] = lines[2:]


        KEYPHRASES = {
            
            "numberOfFilesPeriodNumber" : ["files", "period number"],
            "geometry" : "Geometry",
            "thickness" : ["Upstream", "downstream", "thickness"],
            "angleOfRotationSampleWidth" : "Angle of rotation",
            "densityOfAtoms" : "Density",
            "totalCrossSectionSource" : "Total cross",
            "tweakFactor" : "tweak factor",
            "scatteringFractionAttenuationCoefficient" : ["environment", "scattering fraction", "attenuation coefficient"]
        
        }


        lines = [line for line in lines if not 'end of' in line]

        #Count the number of files and number of elements.
        numberFiles = count_occurrences('data files', lines)
        numberElements = count_occurrences('Container atomic composition', lines) + count_occurrences('Composition', lines)

        #Map the attributes of the Beam class to line numbers.

        FORMAT_MAP = dict.fromkeys(container.__dict__.keys())
        FORMAT_MAP.pop('name', None)
        FORMAT_MAP.pop('dataFiles', None)
        FORMAT_MAP.pop('composition', None)
        FORMAT_MAP.update((k, i) for i,k in enumerate(FORMAT_MAP))

        for key in FORMAT_MAP.keys():
            if FORMAT_MAP[key] > 0:
                FORMAT_MAP[key]+=numberFiles+numberElements


        #Categorise attributes by variables, for easier handling.
        STRINGS = [x for x in container.__dict__.keys() if isinstance(container.__dict__[x],str)]
        FLOATS = [x for x in container.__dict__.keys() if isinstance(container.__dict__[x], float)]
        TUPLES = [x for x in container.__dict__.keys() if isinstance(container.__dict__[x], tuple)]
        TUPLE_FLOATS = [x for x in TUPLES if iteristype(container.__dict__[x], float)] 
        TUPLE_INTS = [x for x in TUPLES if iteristype(container.__dict__[x], int)]

        """
        Get all attributes that are strings:
            - Geometry
            - Total cross section source
        """

        for key in STRINGS:
            try:
                isin_, i = isin(KEYPHRASES[key], lines)
                if not isin_:
                    raise ValueError("Whilst parsing {}, {} was not found".format(container.name, key))
                if i!=FORMAT_MAP[key]:
                    FORMAT_MAP[key] = i 
                container.__dict__[key] = firstword(lines[FORMAT_MAP[key]])
            except KeyError:
                continue

        """
        Get all attributes that are floats (doubles):
            - Density of atoms
            - Tweak factor
        """

        for key in FLOATS:
            isin_, i = isin(KEYPHRASES[key], lines)
            if not isin_:
                raise ValueError("Whilst parsing {}, {} was not found".format(container.name, key))
            if i!=FORMAT_MAP[key]:
                FORMAT_MAP[key] = i 
            container.__dict__[key] = float(firstword(lines[FORMAT_MAP[key]]))
        
        """
        Get all attributes that need to be stored specifically as a tuple of floats (doubles):
            - Upstream and downstream thickness
            - Angle of rotation and sample width
            - Sample environment scattering fraction and attenuation coefficient
        """

        for key in TUPLE_FLOATS:
            isin_, i = isin(KEYPHRASES[key], lines)
            if not isin_:
                raise ValueError("Whilst parsing {}, {} was not found".format(container.name, key))
            if i!=FORMAT_MAP[key]:
                FORMAT_MAP[key] = i 
            container.__dict__[key] = tuple(extract_floats_from_string(lines[FORMAT_MAP[key]]))
            # if key == 'angleOfRotationSampleWidth':
            #     container.__dict__[key] = (container.__dict__[key][0], int(container.__dict__[key][1]))

        """
        Get all attributes that need to be stored specifically as a tuple of ints:
            - Number of files and period number
        """

        for key in TUPLE_INTS:
            isin_, i = isin(KEYPHRASES[key], lines)
            if not isin_:
                raise ValueError("Whilst parsing {}, {} was not found".format(container.name, key))
            if i!=FORMAT_MAP[key]:
                FORMAT_MAP[key] = i 
            container.__dict__[key] = tuple(extract_ints_from_string(lines[FORMAT_MAP[key]]))
        
        #Get all of the normalisation datafiles and their information.
        

        dataFiles = []
        for j in range (numberFiles):
            curr = lines[FORMAT_MAP['numberOfFilesPeriodNumber']+j+1]
            if 'data files' in curr:
                dataFiles.append(firstword(curr))
            else:
                raise ValueError('Number of data files does not match number of data files specified')
        container.dataFiles = DataFiles(deepcopy(dataFiles), '{}'.format(container.name))

        #Get all elements in the composition and their details.

        elements = []
        for j in range (numberElements):
            curr = lines[FORMAT_MAP['numberOfFilesPeriodNumber']+j+numberFiles+1]
            if 'atomic composition' in curr or 'Composition' in curr:
                elementInfo = [x for x in curr.split(" ") if x][:3]
                element = Element(elementInfo[0], int(elementInfo[1]), float(elementInfo[2]))
                elements.append(element)
            else:
                print('ERROR ' + str(curr))

        container.composition = Composition(elements, 'Container')

        return container
            

    def makeParse(self, lines, key):

        #Dictionary of the parsing functions.
        parsingFunctions = {
                            'INSTRUMENT' : self.parseInstrument,
                            'BEAM' : self.parseBeam,
                            'NORMALISATION': self.parseNormalisation,
                            'SAMPLE BACKGROUND': self.parseSampleBackground,
                            'SAMPLE': self.parseSample,
                            'CONTAINER' : self.parseContainer,
                            }
        return parsingFunctions[key](lines)

    def sampleHelper(self, lines):

        KEYWORDS = {'SAMPLE BACKGROUND': None, 'SAMPLE': None, 'CONTAINER': []}

        #Iterate through the lines, parsing any Samples, backgrounds and containers found
        parsing = ''
        for i, line in enumerate(lines):
            for key in KEYWORDS.keys():
                if key in line and firstword(line) in KEYWORDS.keys():
                    parsing = key
                    start = i
                    break
            if line[0] == "}":
                end = i
                if parsing == 'SAMPLE BACKGROUND': start+=2
                slice = deepcopy(lines[start:end-1])
                if isinstance(KEYWORDS[parsing], list):
                    print('container found!')
                    KEYWORDS[parsing].append(self.makeParse(slice,parsing))
                else:
                    KEYWORDS[parsing] = self.makeParse(slice, parsing)
                start = end = 0
        
        #Assign the sampleBackground and container(s) found to the sample.
        KEYWORDS['SAMPLE'].sampleBackground = KEYWORDS['SAMPLE BACKGROUND']
        KEYWORDS['SAMPLE'].containers = KEYWORDS['CONTAINER']

        return KEYWORDS['SAMPLE']

    def sampleBackgroundHelper(self, lines):

        KEYWORDS = {'SAMPLE BACKGROUND': None, 'SAMPLE': [], 'CONTAINER': Container}
        containers = []
        #Iterate through the lines, parsing any Samples, backgrounds and containers found
        parsing = ''
        start = end = 0
        for i, line in enumerate(lines):
            for key in KEYWORDS.keys():
                if key in line and firstword(line) in KEYWORDS.keys():
                    parsing = key
                    start = i
                    break
            if line[0] == "}":
                end = i
                if parsing == 'SAMPLE BACKGROUND': start+=2
                slice = deepcopy(lines[start:end-1])
                if parsing == "SAMPLE":
                    KEYWORDS[parsing].append(self.makeParse(slice,parsing))
                elif parsing == "CONTAINER":
                    KEYWORDS['SAMPLE'][-1].containers.append(deepcopy(self.makeParse(slice, parsing)))
                else:
                    KEYWORDS[parsing] = self.makeParse(slice, parsing)
                start = end = 0
        KEYWORDS['SAMPLE BACKGROUND'].samples = KEYWORDS['SAMPLE']

        return KEYWORDS['SAMPLE BACKGROUND'] 


    def parse(self):

        #Ensure only valid files are given.
        if not self.path:
            raise ValueError('Path not supplied. Cannot parse from an empty path!')
        if not isfile(self.path):
            raise ValueError('The path supplied is invalid. Cannot parse from an invalid path')
        parsing = ''

        start = end = 0
        KEYWORDS = {'INSTRUMENT' : False, 'BEAM': False, 'NORMALISATION': False}

        #Iterate through the file, parsing the Instrument, Beam and Normalisation.
        with open(self.path, encoding="utf-8") as fp:
            lines = fp.readlines()
            split = 0
            for i, line in enumerate(lines):
                if firstword(line) in KEYWORDS.keys() and not KEYWORDS[firstword(line)]:
                    parsing = firstword(line)
                    start = i
                elif line[0] == "}":
                    end = i
                    slice = deepcopy(lines[start+2:end-1])
                    self.makeParse(slice, parsing)
                    KEYWORDS[parsing] = True
                    if parsing == 'NORMALISATION' : 
                        split = end
                        break
                    start = end = 0

            #If we didn't parse each one of the keywords, then panic
            if not all(KEYWORDS.values()):
                raise ValueError ('INSTRUMENT, BEAM and NORMALISATION were not parsed. It\'s possible the file supplied is of an incorrect format!')
            
            #Get everything after the final item parsed
            lines_split = deepcopy(lines[split+1:])
            start = end = 0
            found = False
            
            #Parse sample backgrounds and corresponding samples and containers.
            for i, line in enumerate(lines_split):
                if ('SAMPLE BACKGROUND' in line and '{' in line) and not found:
                    start = i
                    found = True
                    continue
                elif (('SAMPLE BACKGROUND' in line and '{' in line) or ('END' in line)) and found:
                    end = i
                    found = False
                    slice = deepcopy(lines_split[start:end])
                    self.sampleBackgrounds.append(self.sampleBackgroundHelper(slice))
                    start = end + 1
                else:
                    continue

    def __str__(self):
        LINEBREAK = '\n\n'
        header = "'  '  '        '  '/'" + LINEBREAK
        instrument = "INSTRUMENT        {\n\n" + str(self.instrument) + LINEBREAK + "}"
        beam = "BEAM        {\n\n" + str(self.beam) + LINEBREAK + "}"
        normalisation = "NORMALISATION        {\n\n" + str(self.normalisation) + LINEBREAK + "}"        
        sampleBackgrounds = "\n".join([str(x) for x in self.sampleBackgrounds]).rstrip()
        footer = "\n\n\nEND\n1\nDate and Time last written:  {}\nN".format(time.strftime('%Y%m%d %H:%M:%S') )
        return (
            header + 
            instrument + 
            LINEBREAK + 
            beam +
            LINEBREAK +
            normalisation +
            LINEBREAK +
            sampleBackgrounds +
            footer
        )

    def write_out(self):
        fname = os.path.basename(self.path)
        ref_fname = 'gudpy_{}'.format(fname)
        dir = os.path.dirname(self.path)
        f = open("{}/{}".format(dir, ref_fname), "w", encoding="utf-8")
        f.write(str(self))
        f.close()

    def dcs(self):
        import subprocess
        try:   
            result = subprocess.run(['gudrun_dcs', self.path], capture_output=True, text=True)
        except FileNotFoundError:
            gudrun_dcs = sys._MEIPASS + os.sep + 'gudrun_dcs'
            result = subprocess.run([gudrun_dcs, self.path], capture_output=True, text=True)            
        return result

if __name__ == '__main__':
    g = GudrunFile(path="NIMROD-water/water.txt")
    g.write_out()

