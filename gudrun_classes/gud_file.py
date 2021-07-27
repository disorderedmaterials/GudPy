import os
from os.path import isfile


class GudFile:

    def __init__(self, path):
        self.path = path
        fname = os.path.basename(self.path)
        ref_fname = "gudpy_{}".format(fname)
        dir = os.path.dirname(os.path.dirname(os.path.abspath(self.path)))
        self.outpath = "{}/{}".format(dir, ref_fname)
        self.name = ""
        self.title = ""
        self.author = ""
        self.stamp = ""
        self.densityAcm3 = 0.0
        self.densityGcm3 = 0.0
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

        if self.path.split(".")[-1] != "gud":
            raise ValueError("Only .gud files can be parsed.")

        if not isfile(self.path):
            raise ValueError("Please provide a valid path.")

        self.parse()

    def parse(self):

        with open(self.path) as f:
            self.contents = f.readlines()
            f.close()
        self.name = self.contents[0].strip()
        self.title = self.contents[2].strip()
        self.author = self.contents[4].strip()
        self.stamp = self.contents[6].strip()

        self.densityAcm3 = self.contents[8].split(" ")[-1].strip()
        self.densityGcm3 = self.contents[9].split(" ")[-1].strip()
        self.averageScatteringLength = self.contents[10].split(" ")[-1].strip()
        self.averageScatteringLengthSquared = (
            self.contents[11].split(" ")[-1].strip()
        )
        self.averageSquareOfScatteringLength = (
            self.contents[12].split(" ")[-1].strip()
        )
        self.coherentRatio = self.contents[13].split(" ")[-1].strip()

        self.expectedDCS = self.contents[15].split(" ")[-1].strip()

        line = self.contents[19]
        i = 1
        while not line.isspace():
            self.groups.append(line)
            line = self.contents[19 + i]
            i += 1

        self.groupsTable = "".join(self.groups)

        self.noGroups = self.contents[19 + i].split(" ")[-1].strip()
        self.averageLevelMergedDCS = (
            self.contents[19 + i + 2].split(" ")[-2].strip()
        )
        self.gradient = self.contents[19 + i + 4].split(" ")[-4].strip()

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

        self.suggestedTweakFactor = self.contents[-1].split(" ")[-1].strip()

    def __str__(self):
        if self.err:
            return """ {}

 {}

 {}

 {}

 Number density of this sample (atoms/A**3) =  {}
 Corresponding density in g/cm**3 =    {}
 Average scattering length of the sample (10**-12cm) =   {}
 Average scattering length of squared (barns) =  {}
 Average square of the scattering length (barns) =  {}
 Ratio of (coherent) single to interference =  {}

 Expected level of DCS [b/sr/atom] =    {}

 Group number,  first Q,   last Q,   level [b/sr/atom],   gradient in Q (%)

{}
 No. of groups accepted for merge =   {}

 Average level of merged dcs is   {} b/sr/atom;

 Gradient of merged dcs: {} of average level.

{} Suggested tweak factor:   {}
""".format(
                self.name,
                self.title,
                self.author,
                self.stamp,
                self.densityAcm3,
                self.densityGcm3,
                self.averageScatteringLength,
                self.averageScatteringLengthSquared,
                self.averageSquareOfScatteringLength,
                self.coherentRatio,
                self.expectedDCS,
                self.groupsTable,
                self.noGroups,
                self.averageLevelMergedDCS,
                self.gradient,
                self.err,
                self.suggestedTweakFactor,
            )
        else:
            return """ {}

 {}

 {}

 {}

 Number density of this sample (atoms/A**3) =  {}
 Corresponding density in g/cm**3 =    {}
 Average scattering length of the sample (10**-12cm) =   {}
 Average scattering length of squared (barns) =  {}
 Average square of the scattering length (barns) =  {}
 Ratio of (coherent) single to interference =  {}

 Expected level of DCS [b/sr/atom] =    {}

 Group number,  first Q,   last Q,   level [b/sr/atom],   gradient in Q (%)

{}
 No. of groups accepted for merge =   {}

 Average level of merged dcs is   {} b/sr/atom;

 Gradient of merged dcs: {} of average level.

{} Suggested tweak factor:   {}
""".format(
                self.name,
                self.title,
                self.author,
                self.stamp,
                self.densityAcm3,
                self.densityGcm3,
                self.averageScatteringLength,
                self.averageScatteringLengthSquared,
                self.averageSquareOfScatteringLength,
                self.coherentRatio,
                self.expectedDCS,
                self.groupsTable,
                self.noGroups,
                self.averageLevelMergedDCS,
                self.gradient,
                self.result,
                self.suggestedTweakFactor,
            )

    def write_out(self, overwrite=False):
        if not overwrite:
            f = open(self.outpath, "w", encoding="utf-8")
        else:
            f = open(self.path, "w", encoding="utf-8")
        f.write(str(self))
        f.close()


if __name__ == "__main__":
    g = GudFile("NIMROD00016608_H2O_in_N9.gud")
    g.parse()
    print(str(g))
