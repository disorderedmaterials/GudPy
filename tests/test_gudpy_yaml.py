from unittest import TestCase

from src.gudrun_classes.gudrun_file import GudrunFile


class TestYAML(TestCase):

    def testYAML(self):

        gf1 = GudrunFile("tests/TestData/NIMROD-water/water.txt")
        gf1.write_yaml("water.yaml")
        gf2 = GudrunFile("water.yaml")

        def dict_zip(dictA, dictB):
            return {
                k: [dictA[k], dictB[k]]
                for k in dictA.keys() & dictB.keys()
            }
        i = 0
        def dict_eq(*dicts):
            print(i)
            i+=1
            for key, vals in dict_zip(*dicts).items():
                if dicts[0][key].__class__.__module__ == "builtins":
                    assert(len(set(vals)) == 1)
                    print(f"{key} is okay.")
                else:
                    dict_eq(*[val.__dict for val in vals])
        dict_eq(gf1.__dict__, gf2.__dict__)