import os
from unittest import TestCase

from core.exception import ParserException
from core.gud_file import GudFile
from core import gudpy


class TestParseGudFile(TestCase):

    def setUp(self) -> None:
        self.gudpy = gudpy.GudPy()
        self.expectedGudFileA = {
            "path": "NIMROD00016608_H2O_in_N9.gud",
            "name": "NIMROD00016608_H2O_in_N9.gud",
            "title": (
                'H2O in 1mm TiZr Can N9 pos 11 Beam 30x30mm'
                ' Mod 195.3x115mm HxV JC6Y -10'),
            "author": "T. G. A. Youngs, D.",
            "stamp": "23-OCT-2012 17:45:25",
            "atomicDensity": 0.1,
            "chemicalDensity": 0.99717,
            "averageScatteringLength": -0.05583,
            "averageScatteringLengthSquared": 0.311736E-02,
            "averageSquareOfScatteringLength": 0.205450E+00,
            "coherentRatio": 0.659052E+02,
            "expectedDCS": 4.46355,
            "groupsTable": """    1            0.0000    0.0000        0.00000              0.0000
    2            0.0000    0.0000        0.00000              0.0000
    3            0.0000    0.0000        0.00000              0.0000
    4            0.0000    0.0000        0.00000              0.0000
    5            0.0000    0.0000        0.00000              0.0000
    6            0.0000    0.0000        0.00000              0.0000
    7            0.0000    0.0000        0.00000              0.0000
    8            0.0000    0.0000        0.00000              0.0000
    9            0.0173    4.0723        4.51058             -0.6170
   10            0.0173    4.1473        5.09312             -7.8750
   11            0.0195    4.6973        4.72996             -9.2335
   12            0.0312   10.0223        3.68924              0.2426
   13            0.0394   12.1972        3.95174             -0.4543
   14            0.0539   15.1222        4.16429             -0.2578
   15            0.0631   17.0472        4.29016             -0.4672
   16            0.0829   22.3971        4.14903             -0.3993
   17            0.0932   25.3720        4.16614             -0.4412
   18            0.1047   28.9720        4.27231             -0.2909
   19            0.1223   32.1469        4.24109             -0.2913
   20            0.1603   43.5476        4.08767             -0.3182
   21            0.1798   48.9480        3.95260             -0.2382
   22            0.2175   49.9980        3.93814             -0.3060
   23            0.2345   49.9980        3.81525             -0.3096
   24            0.2722   49.9980        3.75996             -0.4879
   25            0.3153   49.9980        3.26407             -0.4735
""",
            "noGroups": 25,
            "averageLevelMergedDCS": 3.81991,
            "gradient": -0.5106,
            "err": """WARNING! This DCS level is   14.4% BELOW expected level.

 Please check sample density, size or thickness, and composition.
 If all is in order, then refer to your local contact for further advice

""",
            "suggestedTweakFactor": 1.16850,
            "output": "-14.4%"
        }

        self.expectedGudFileB = {
            "path": "NIMROD00016609_D2O_in_N10.gud",
            "name": "NIMROD00016609_D2O_in_N10.gud",
            "title": (
                'D2O in 1mm TiZr Can N10 pos 10 Beam 30x30mm'
                ' Mod 195.3x115mm HxV JC6Y -10'),
            "author": "T. G. A. Youngs, D.",
            "stamp": "23-OCT-2012 18:43:54",
            "atomicDensity": 0.1,
            "chemicalDensity": 1.10854,
            "averageScatteringLength": 0.63817,
            "averageScatteringLengthSquared": 0.407257E+00,
            "averageSquareOfScatteringLength": 0.408931E+00,
            "coherentRatio": 0.100411E+01,
            "expectedDCS": 0.51757,
            "groupsTable": """    1            0.0000    0.0000        0.00000              0.0000
    2            0.0000    0.0000        0.00000              0.0000
    3            0.0000    0.0000        0.00000              0.0000
    4            0.0000    0.0000        0.00000              0.0000
    5            0.0000    0.0000        0.00000              0.0000
    6            0.0000    0.0000        0.00000              0.0000
    7            0.0000    0.0000        0.00000              0.0000
    8            0.0000    0.0000        0.00000              0.0000
    9            0.0173    4.0723        1.01210             22.7862
   10            0.0173    4.1473        0.66457              3.1237
   11            0.0195    4.6973        0.70931            -12.0485
   12            0.0312   10.0223        0.53959              2.9086
   13            0.0394   12.1972        0.55239             -1.2262
   14            0.0539   15.1222        0.54596             -0.3330
   15            0.0631   17.0472        0.57143             -0.5615
   16            0.0829   22.3971        0.55611             -0.3554
   17            0.0932   25.3720        0.56652             -0.4537
   18            0.1047   28.9720        0.57449             -0.3043
   19            0.1223   32.1469        0.57886             -0.2909
   20            0.1603   43.5476        0.55092             -0.1788
   21            0.1798   48.9480        0.54972             -0.1652
   22            0.2175   49.9980        0.53192             -0.0765
   23            0.2345   49.9980        0.52964             -0.0661
   24            0.2722   49.9980        0.51460              0.0200
   25            0.3153   49.9980        0.51156              0.0656
""",
            "noGroups": 25,
            "averageLevelMergedDCS": 0.51788,
            "gradient": -0.0235,
            "result": "This DCS level is  100.1% of expected level",
            "suggestedTweakFactor": 0.99941,
            "output": "+0.1%"
        }

        self.expectedGudFileC = {
            "path": "NIMROD00016741_HDO_in_N6.gud",
            "name": "NIMROD00016741_HDO_in_N6.gud",
            "title": (
                'HDO in 1mm TiZr Can N6 pos 14 at 25oC Beam 30x30mm'
                ' Mod 195.3x115mm HxV JC6Y -10'),
            "author": "T. Youngs",
            "stamp": "28-OCT-2012 12:56:29",
            "atomicDensity": 0.1,
            "chemicalDensity": 1.05285,
            "averageScatteringLength": 0.29117,
            "averageScatteringLengthSquared": 0.847780E-01,
            "averageSquareOfScatteringLength": 0.307191E+00,
            "coherentRatio": 0.362347E+01,
            "expectedDCS": 2.49056,
            "groupsTable": """    1            0.0000    0.0000        0.00000              0.0000
    2            0.0000    0.0000        0.00000              0.0000
    3            0.0000    0.0000        0.00000              0.0000
    4            0.0000    0.0000        0.00000              0.0000
    5            0.0000    0.0000        0.00000              0.0000
    6            0.0000    0.0000        0.00000              0.0000
    7            0.0000    0.0000        0.00000              0.0000
    8            0.0000    0.0000        0.00000              0.0000
    9            0.0173    4.0723        3.90068            -10.2779
   10            0.0173    4.1473        3.49550             -9.5540
   11            0.0195    4.6973        3.40612            -11.9263
   12            0.0312   10.0223        2.29892              0.1412
   13            0.0394   12.1972        2.53271             -0.7931
   14            0.0539   15.1222        2.60066             -0.2992
   15            0.0631   17.0472        2.68473             -0.5292
   16            0.0829   22.3971        2.59275             -0.3875
   17            0.0932   25.3720        2.61295             -0.4559
   18            0.1047   28.9720        2.67214             -0.2956
   19            0.1223   32.1469        2.66878             -0.3048
   20            0.1603   43.5476        2.55599             -0.2616
   21            0.1798   48.9480        2.49774             -0.1992
   22            0.2175   49.9980        2.52220             -0.2660
   23            0.2345   49.9980        2.45249             -0.2312
   24            0.2722   49.9980        2.45972             -0.3599
   25            0.3153   49.9980        2.18191             -0.2975
""",
            "noGroups": 25,
            "averageLevelMergedDCS": 2.45211,
            "gradient": -0.3551,
            "result": " This DCS level is   98.5% of expected level",
            "suggestedTweakFactor": 1.01568,
            "output": "-1.5%"
        }

        self.expectedGudFileD = {
            "path": "NIMROD00016742_NullWater_in_N8.gud",
            "name": "NIMROD00016742_NullWater_in_N8.gud",
            "title": (
                'Null Water in 1mm TiZr Can N8 pos 12 at 25oC Beam 30x30mm'
                ' Mod 195.3x115mm HxV JC'),
            "author": "T. Youngs",
            "stamp": "28-OCT-2012 13:53:13",
            "atomicDensity": 0.1,
            "chemicalDensity": 1.03732,
            "averageScatteringLength": 0.19358,
            "averageScatteringLengthSquared": 0.374735E-01,
            "averageSquareOfScatteringLength": 0.278574E+00,
            "coherentRatio": 0.743389E+01,
            "expectedDCS": 3.04538,
            "groupsTable": """    1            0.0000    0.0000        0.00000              0.0000
    2            0.0000    0.0000        0.00000              0.0000
    3            0.0000    0.0000        0.00000              0.0000
    4            0.0000    0.0000        0.00000              0.0000
    5            0.0000    0.0000        0.00000              0.0000
    6            0.0000    0.0000        0.00000              0.0000
    7            0.0000    0.0000        0.00000              0.0000
    8            0.0000    0.0000        0.00000              0.0000
    9            0.0173    4.0723        5.98709            -18.0575
   10            0.0173    4.1473        3.68017             -9.8484
   11            0.0195    4.6973        3.10580             -7.0014
   12            0.0312   10.0223        2.54798              0.6062
   13            0.0394   12.1972        2.69266             -0.5174
   14            0.0539   15.1222        2.80330             -0.2056
   15            0.0631   17.0472        2.91898             -0.5090
   16            0.0829   22.3971        2.82441             -0.3903
   17            0.0932   25.3720        2.83648             -0.4413
   18            0.1047   28.9720        2.89998             -0.2775
   19            0.1223   32.1469        2.90026             -0.2865
   20            0.1603   43.5476        2.78588             -0.2666
   21            0.1798   48.9480        2.69915             -0.1802
   22            0.2175   49.9980        2.71768             -0.2497
   23            0.2345   49.9980        2.66016             -0.2462
   24            0.2722   49.9980        2.63808             -0.3647
   25            0.3153   49.9980        2.33847             -0.3202
""",
            "noGroups": 25,
            "averageLevelMergedDCS": 2.64872,
            "gradient": -0.3721,
            "err": """WARNING! This DCS level is   13.0% BELOW expected level.

 Please check sample density, size or thickness, and composition.
 If all is in order, then refer to your local contact for further advice

""",
            "suggestedTweakFactor": 1.14976,
            "output": "-13.0%"
        }

        self.keepsakes = os.listdir()

        path = "TestData/NIMROD-water/good_water"

        if os.name == "nt":
            from pathlib import Path

            dirpath = Path().resolve() / "test/" / Path(path)
        else:
            dirpath = (
                "/".join(os.path.realpath(__file__).split("/")[:-1])
                + "/"
                + path
            )

        self.keepsakes = os.listdir()

        for f in os.listdir(dirpath):
            self.keepsakes.append(f)

        self.gudpy.loadFromProject(
            projectDir == os.path.abspath(dirpath)
        )

        from pathlib import Path
        dataFileDir = Path("test/TestData/NIMROD-water/raw").absolute()
        self.gudpy.gudrunFile.instrument.dataFileDir = str(dataFileDir) + "/"
        return super().setUp()

    def tearDown(self) -> None:
        [os.remove(f) for f in os.listdir() if f not in self.keepsakes]
        [os.remove(f) for f in os.listdir(self.gudpy.projectDir)
         if f not in self.keepsakes]
        return super().tearDown()

    def testEmptyPath(self):

        emptyPath = ""
        self.assertRaises(ParserException, GudFile, emptyPath)

    def testInvalidFileType(self):

        invalid_file_type = "NIMROD0001_H20_in_N9.txt"
        self.assertRaises(ParserException, GudFile, invalid_file_type)

    def testInvalidPath(self):

        invalid_path = "invalid_path.gud"
        self.assertRaises(ParserException, GudFile, invalid_path)

    def testValidPath(self):
        self.gudpy.runGudrun()
        gf = GudFile(
            self.gudpy.gudrun.gudrunOutput.gudFile(0)
        )
        self.assertIsInstance(gf, GudFile)

    def testLoadGudFileA(self):
        self.gudpy.runGudrun()
        gf = GudFile(
            self.gudpy.gudrun.gudrunOutput.gudFile(0)
        )

        self.assertIsInstance(gf, GudFile)

        gudAttrsDict = gf.__dict__
        for key in gudAttrsDict.keys():
            if key in ["path", "groups", "stream", "result", "outpath", "err"]:
                continue
            if key == "groupsTable":

                for rowA, rowB in zip(
                    self.expectedGudFileA[key].split("\n"),
                    gf.groupsTable.split("\n"),
                ):
                    for valueA, valueB in zip(rowA.split(), rowB.split()):
                        self.assertAlmostEqual(float(valueA), float(valueB), 1)
            elif key == "gradient":
                self.assertAlmostEqual(
                    self.expectedGudFileA[key],
                    gudAttrsDict[key],
                    1,
                )
            else:
                try:
                    self.assertEqual(
                        self.expectedGudFileA[key], gudAttrsDict[key]
                    )
                except AssertionError as e:
                    try:
                        self.assertAlmostEqual(
                            float(self.expectedGudFileA[key]),
                            float(gudAttrsDict[key]),
                            1,
                        )
                    except Exception:
                        raise e

    def testLoadGudFileB(self):
        self.gudpy.runGudrun()
        gf = GudFile(
            self.gudpy.gudrun.gudrunOutput.gudFile(1)
        )

        self.assertIsInstance(gf, GudFile)

        gudAttrsDict = gf.__dict__
        for key in gudAttrsDict.keys():
            if key in ["path", "groups", "stream", "err", "outpath", "result"]:
                continue
            if key == "groupsTable":

                for rowA, rowB in zip(
                    self.expectedGudFileB[key].split("\n"),
                    gf.groupsTable.split("\n"),
                ):
                    for valueA, valueB in zip(rowA.split(), rowB.split()):
                        self.assertAlmostEqual(float(valueA), float(valueB), 1)
            elif key == "gradient":
                self.assertAlmostEqual(
                    self.expectedGudFileB[key],
                    gudAttrsDict[key],
                    1,
                )
            else:
                try:
                    float(self.expectedGudFileB[key])
                except ValueError:
                    self.assertEqual(
                        self.expectedGudFileB[key],
                        gudAttrsDict[key]
                    )
                else:
                    self.assertAlmostEqual(
                        float(self.expectedGudFileB[key]),
                        float(gudAttrsDict[key]),
                        1,
                    )

    def testLoadGudFileC(self):
        self.gudpy.runGudrun()
        gf = GudFile(
            self.gudpy.gudrun.gudrunOutput.gudFile(2)
        )

        self.assertIsInstance(gf, GudFile)

        gudAttrsDict = gf.__dict__
        for key in gudAttrsDict.keys():
            if key in ["path", "groups", "stream", "err", "outpath", "result"]:
                continue
            if key == "groupsTable":

                for rowA, rowB in zip(
                    self.expectedGudFileC[key].split("\n"),
                    gf.groupsTable.split("\n"),
                ):
                    for valueA, valueB in zip(rowA.split(), rowB.split()):
                        self.assertAlmostEqual(float(valueA), float(valueB), 1)
            elif key == "gradient":
                self.assertAlmostEqual(
                    self.expectedGudFileC[key],
                    gudAttrsDict[key],
                    1,
                )
            else:
                try:
                    self.assertEqual(
                        self.expectedGudFileC[key], gudAttrsDict[key]
                    )
                except AssertionError as e:
                    try:
                        self.assertAlmostEqual(
                            float(self.expectedGudFileC[key]),
                            float(gudAttrsDict[key]),
                            1,
                        )
                    except Exception:
                        raise e

    def testLoadGudFileD(self):
        self.gudpy.runGudrun()
        gf = GudFile(
            self.gudpy.gudrun.gudrunOutput.gudFile(3)
        )
        self.assertIsInstance(gf, GudFile)

        gudAttrsDict = gf.__dict__
        for key in gudAttrsDict.keys():
            if key in ["path", "groups", "stream", "result", "outpath", "err"]:
                continue
            if key == "groupsTable":

                for rowA, rowB in zip(
                    self.expectedGudFileD[key].split("\n"),
                    gf.groupsTable.split("\n"),
                ):
                    for valueA, valueB in zip(rowA.split(), rowB.split()):
                        self.assertAlmostEqual(float(valueA), float(valueB), 1)
            elif key == "gradient":
                self.assertAlmostEqual(
                    self.expectedGudFileD[key],
                    gudAttrsDict[key],
                    1,
                )
            else:
                try:
                    self.assertEqual(
                        self.expectedGudFileD[key], gudAttrsDict[key]
                    )
                except AssertionError as e:
                    try:
                        self.assertAlmostEqual(
                            float(self.expectedGudFileD[key]),
                            float(gudAttrsDict[key]),
                            1,
                        )
                    except Exception:
                        raise e

    def testWriteGudFileA(self):
        self.gudpy.runGudrun()
        gf = GudFile(
            self.gudpy.gudrun.gudrunOutput.gudFile(0)
        )
        gf.write_out()
        gf1 = GudFile(gf.OUTPATH)

        dicA = gf.__dict__
        dicA.pop("outpath")
        dicA.pop("path")
        dicA.pop("result")
        dicA.pop("err")

        dicB = gf1.__dict__
        dicB.pop("outpath")
        dicB.pop("path")
        dicB.pop("result")
        dicB.pop("err")

        for v1, v2 in zip(gf.__dict__.values(), gf1.__dict__.values()):
            self.assertEqual(v1, v2)

    def testWriteGudFileB(self):
        self.gudpy.runGudrun()
        gf = GudFile(
            self.gudpy.gudrun.gudrunOutput.gudFile(1)
        )
        gf.write_out()
        gf1 = GudFile(gf.OUTPATH)

        dicA = gf.__dict__
        dicA.pop("outpath")
        dicA.pop("path")
        dicA.pop("result")
        dicA.pop("err")

        dicB = gf1.__dict__
        dicB.pop("outpath")
        dicB.pop("path")
        dicB.pop("result")
        dicB.pop("err")

        for v1, v2 in zip(gf.__dict__.values(), gf1.__dict__.values()):
            self.assertEqual(v1, v2)
