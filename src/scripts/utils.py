from collections import deque
from itertools import islice


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


def bjoin(iterable, sep, lastsep=None, endsep='', sameseps=False):
    iterable = [
        str(i)
        if not isinstance(i, (str, list, tuple))
        else i
        for i in iterable
    ]
    iterable = [
        spacify(i)
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

    return sep.join(iterable[:-1]) + lastsep + iterable[-1] + endsep
