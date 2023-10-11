from collections import deque
from itertools import islice
import os
import re


def spacify(iterable, num_spaces=1):
    try:
        return (" " * num_spaces).join(iterable)
    except TypeError:
        return (" " * num_spaces).join([str(x) for x in iterable])


def numifyBool(boolean):
    return sum([boolean])


def boolifyNum(num):
    return not not num


def firstword(string):

    return string.split(" ")[0]


def extract_ints_from_string(string):
    ret = []
    for x in [y for y in string.split(" ") if y]:
        try:
            a = int(x)
            ret.append(a)
        except ValueError:
            break
    return ret


def extract_floats_from_string(string):
    ret = []
    for x in [y for y in string.split(" ") if y]:
        try:
            a = float(x)
            ret.append(a)
        except ValueError:
            break
    return ret


def isfloat(string):
    try:
        float(string)
        return True
    except ValueError:
        return False


def isnumeric(string):
    return isfloat(string) | string.isnumeric()


def extract_nums_from_string(string):
    if string:
        ret = [x for x in string.split(" ") if isnumeric(x)]
        return [float(x) if '.' in x else int(x) for x in ret]


def consume(iterable, n):

    deque(iterable, maxlen=0) if not n else next(islice(iterable, n, n), None)


def count_occurrences(substring, iterable):
    return sum(1 for string in iterable if substring in string)


def iteristype(iter, type):
    return all(isinstance(x, type) for x in iter)


def isin(iter1, iter2):
    if isinstance(iter1, (list, tuple)):
        for i, line in enumerate(iter2):
            if all(word.lower() in str(line).lower() for word in iter1):
                return True, i
        return False, 0
    elif isinstance(iter1, str):
        for j, line in enumerate(iter2):
            if iter1.lower() in str(line).lower():
                return True, j
        return False, 0


def nthword(string, n):
    return string.split()[n]


def nthint(string, n):
    return int(nthword(string, n))


def nthfloat(string, n):
    return float(nthword(string, n))


def firstNInts(string, n):
    ints = [int(x) for x in string.split()[:n]]
    if len(ints) != n:
        raise ValueError(f"Could not find {n} ints in {string}")
    else:
        return ints


def firstNFloats(string, n):
    floats = [float(x) for x in string.split()[:n]]
    if len(floats) != n:
        raise ValueError(f"Could not find {n} floats in {string}")
    else:
        return floats


def bjoin(iterable, sep, lastsep=None, endsep='', sameseps=False, suffix=None):
    iterable = [
        str(i)
        if not isinstance(i, (str, list, tuple))
        else i
        for i in iterable
    ]
    iterable = [
        spacify(i, num_spaces=2)
        if isinstance(i, (list, tuple))
        else i
        for i in iterable
    ]
    if not lastsep:
        lastsep = sep
    if sameseps:
        endsep = sep
    if len(iterable) == 0:
        return ""
    elif len(iterable) == 1:
        return (iterable[0]) + sep
    if suffix:
        iterable = [i + f" {suffix}" for i in iterable]
    return sep.join(iterable[:-1]) + lastsep + iterable[-1] + endsep


def resolve(*args):
    relativePath = os.sep.join(args)
    topLevel = os.sep.join(
        os.path.realpath(__file__).split(os.sep)[:-3]
    )
    return os.path.join(topLevel, relativePath)


def breplace(str, old, new):
    pattern = re.compile(old, re.IGNORECASE)
    return pattern.sub(new, str)


def nthreplace(str, old, new, nth):
    tokens = str.split(old)
    if len(tokens) > nth:
        string = f'{old.join(tokens[:nth])}{new}{old.join(tokens[nth:])}'
    return string


def makeDir(targetPath):
    """Creates directory if it doesn't already exist

    Parameters
    ----------
    targetPath : str
        Path where directory is to be made

    Returns
    -------
    dirPath : str
        Path of created directory
    """
    if not os.path.isdir(targetPath):
        os.makedirs(targetPath)

    return targetPath


def uniquify(path, sep="_", incFirst=False):
    """
    Function to increment path based on the amount
    of existing paths

    Parameters
    ----------
    path : str
        requested path
    sep : str
        desired seperator between basename and number
    incFirst : bool
        whether to increment the first instance of the
        path

    Returns
    -------
    str
        avaliable path
    """

    root, ext = os.path.splitext(path)
    fileCount = 1
    if incFirst:
        path = root + sep + str(fileCount) + ext
        fileCount += 1
    while os.path.exists(path):
        path = root + sep + str(fileCount) + ext
        fileCount += 1
    return path


def uniquifyName(basename, names, sep="_", incFirst=False):
    """
    Function to increment a default name based on the amount
    of existing default names

    Parameters
    ----------
    basename : str
        base default name
    names : str[]
        list of current existing names
    sep : str
        desired seperator between basename and number
    incFirst : bool
        whether to increment the first instance of the
        path

    Returns
    -------
    str
        avaliable path
    """

    nameCount = 1
    name = basename
    if incFirst:
        name = basename + sep + str(nameCount)
        nameCount += 1
    while name in names:
        name = basename + sep + str(nameCount)
        nameCount += 1
    return name
