import os
from os.path import isfile


class GudFile:
    """
    Class to represent a GudFile (files with .gud extension).
    .gud files are outputted by gudrun_dcs, via merge_routines
    each .gud file belongs to an individual sample.

    ...

    Attributes
    ----------
    path : str
        Path to the file.
    outpath : str
        Path to write to, when not overwriting the initial file.
    name : str
        'Name' of the GudFile - this is usually the same as the filename.
    title : str
        Title of the run.
    author : str
        Author of the run.
    stamp : str
        Date and time that the run was completed.
    atomicDensity : float
        Number density of sample (atoms/Angstrom^3).
    chemicalDensity : float
        Chemical density of sample (g/cm^3).
    averageScatteringLength : float
        Average scattering length of the sample (10^-12cm).
    averageScatteringLengthSquared : float
        Average scattering length squared of the sample (barns).
    averageSquareOfScatteringLength : float
        Average square of the scattering length (barns).
    coherentRatio : float
        Ratio of coherent single to interference.
    expectedDCS : float
        Expected level of DCS [b/sr/atom].
    groups : str[]
        List of strings of information regarding the groups table.
        Each string is as such:
        Group number, first Q, last Q, DCS level, gradient in Q.
    groupsTable : str
        String representation of the 'groups' attribute.
    noGroups : int
        Number of groups accepted for merge.
    averageLevelMergedDCS : float
        Average level of merged DCS [b/sr/atom].
    gradient : float
        Gradient of merged DCS.
    err : str
        Error (warning) message produced. Effectively STDERR of GudFile.
    result : str
        When 'err' attribute is not active, result stores the non-error
        output. Effectively STDOUT of GudFile.
    suggestedTweakFactor : str
        Tweak factor suggested to bring the produced gradient of merged DCS
        closer to the expected level. Particularly used when iterating by
        tweak factor - where the suggested tweak factor is applied accross
        iterations.
    contents : str
        Contents of the .gud file.
    Methods
    -------
    parse():
        Parses the GudFile from path, assigning values
        to each of the attributes.
    write_out(overwrite=False)
        Writes out the string representation of the GudFile to a file.
    """
    def __init__(self, path):
        """
        Constructs all the necessary attributes for the GudFile object.
        Calls the GudFiles parse method, to parse the GudFile from its path.

        Parameters
        ----------
        path : str
            Path to the file.
        """
        self.path = path

        # Construct the outpath
        fname = os.path.basename(self.path)
        ref_fname = "gudpy_{}".format(fname)
        dir = os.path.dirname(os.path.dirname(os.path.abspath(self.path)))
        self.outpath = "{}/{}".format(dir, ref_fname)

        self.name = ""
        self.title = ""
        self.author = ""
        self.stamp = ""
        self.atomicDensity = 0.0
        self.chemicalDensity = 0.0
        self.averageScatteringLength = 0.0
        self.averageScatteringLengthSquared = 0.0
        self.averageSquareOfScatteringLength = 0.0
        self.coherentRatio = 0.0
        self.expectedDCS = 0.0
        self.groups = []
        self.groupsTable = ""
        self.noGroups = 0
        self.averageLevelMergedDCS = 0.0
        self.gradient = 0.0
        self.err = ""
        self.result = ""
        self.suggestedTweakFactor = 0.0
        self.contents = ""

        # Handle edge cases - invalid extensions and paths.
        if self.path.split(".")[-1] != "gud":
            raise ValueError("Only .gud files can be parsed.")

        if not isfile(self.path):
            raise ValueError("Please provide a valid path.")

        # Parse the GudFile
        self.parse()

    def parse(self):
        """
        Parses the GudFile from its path, assigning extracted variables to
        their corresponding attributes.

        Parameters
        ----------
        None
        Returns
        -------
        None
        """

        # Read the contents into an auxilliary variable.
        with open(self.path) as f:
            self.contents = f.readlines()
            f.close()

        # Simple cases, we can just extract the stripped lines.
        self.name = self.contents[0].strip()
        self.title = self.contents[2].strip()
        self.author = self.contents[4].strip()
        self.stamp = self.contents[6].strip()

        # Extract the last item of data from the lines.
        self.atomicDensity = self.contents[8].split(" ")[-1].strip()
        self.chemicalDensity = self.contents[9].split(" ")[-1].strip()
        self.averageScatteringLength = self.contents[10].split(" ")[-1].strip()
        self.averageScatteringLengthSquared = (
            self.contents[11].split(" ")[-1].strip()
        )
        self.averageSquareOfScatteringLength = (
            self.contents[12].split(" ")[-1].strip()
        )
        self.coherentRatio = self.contents[13].split(" ")[-1].strip()
        self.expectedDCS = self.contents[15].split(" ")[-1].strip()

        # Extract the groups table.
        line = self.contents[19]
        i = 1
        while not line.isspace():
            self.groups.append(line)
            line = self.contents[19 + i]
            i += 1

        self.groupsTable = "".join(self.groups)

        # Extract the last item of data from the line.
        self.noGroups = self.contents[19 + i].split(" ")[-1].strip()

        # Extract the last but one item of data from the line.
        self.averageLevelMergedDCS = (
            self.contents[19 + i + 2].split(" ")[-2].strip()
        )

        # Extract the last but four item of data from the line.
        self.gradient = self.contents[19 + i + 4].split(" ")[-4].strip()

        # Get the output information (err/result).
        start = 19 + i + 6
        end = 0
        line = self.contents[start]
        if "WARNING!" in line:
            while "Suggested tweak factor" not in line:
                end += 1
                line = self.contents[start + end]
            end += 19 + i + 6

            self.err = "".join(self.contents[start:end])
        else:
            self.result = line

        # Collect the suggested tweak factor from the end of the final line.
        self.suggestedTweakFactor = self.contents[-1].split(" ")[-1].strip()

    def __str__(self):
        """
        Returns the string representation of the GudFile object.

        Parameters
        ----------
        None

        Returns
        -------
        string : str
            String representation of GudFile.
        """
        outLine = (
            f'{self.err}'
            if self.err
            else
            f'{self.result}'
        )

        return (

            f' {self.name}\n\n'
            f' {self.title}\n\n'
            f' {self.author}\n\n'
            f' {self.stamp}\n\n'
            f' Number density of this sample (atoms/\u212b**3) =  '
            f'{self.atomicDensity}\n'
            f' Corresponding density in g/cm**3 =    '
            f'{self.chemicalDensity}\n'
            f' Average scattering length of the sample (10**-12cm) =   '
            f'{self.averageScatteringLength}\n'
            f' Average scattering length of squared (barns) =  '
            f'{self.averageScatteringLengthSquared}\n'
            f' Average square of the scattering length (barns) =  '
            f'{self.averageSquareOfScatteringLength}\n'
            f' Ratio of (coherent) single to interference =  '
            f'{self.coherentRatio}\n\n'
            f' Expected level of DCS [b/sr/atom] =    '
            f'{self.expectedDCS}\n\n'
            f' Group number,  first Q,   last Q,'
            f'   level [b/sr/atom],   gradient in Q (%)\n\n'
            f'{self.groupsTable}\n'
            f' No. of groups accepted for merge =   '
            f'{self.noGroups}\n\n'
            f' Average level of merged dcs is   '
            f'{self.averageLevelMergedDCS} b/sr/atom;\n\n'
            f' Gradient of merged dcs: '
            f'{self.gradient} of average level.\n\n'
            f'{outLine}'
            f' Suggested tweak factor:   '
            f'{self.suggestedTweakFactor}\n'

        )

    def write_out(self, overwrite=False):
        """
        Writes out the string representation of the GudFile.
        If 'overwrite' is True, then the initial file is overwritten.
        Otherwise, it is written to 'gudpy_{initial filename}.gud'.

        Parameters
        ----------
        overwrite : bool, optional
            Overwrite the initial file? (default is False).

        Returns
        -------
        None
        """
        if not overwrite:
            f = open(self.outpath, "w", encoding="utf-8")
        else:
            f = open(self.path, "w", encoding="utf-8")
        f.write(str(self))
        f.close()
