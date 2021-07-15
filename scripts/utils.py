


def spacify(iterable, num_spaces=1):
    try:
        return (" "*num_spaces).join(iterable)
    except TypeError:
        return (" "*num_spaces).join([str(x) for x in iterable])

def numifyBool(boolean):
    try:
        return {False: 0, True: 1}[boolean]
    except KeyError:
        return 0

def boolifyNum(num):
    if num!=0 and num!=1:
        raise ValueError('Only 1 and 0 can be represented in boolean.')
    return {0: False, 1: True}[num]

def firstword(string):

    return string.split(" ")[0]

def extract_ints_from_string(string):
    ret = []
    for x in [ y for y in string.split(" ") if y]:
        try:
            a = int(x)
            ret.append(a)
        except ValueError:
            break
    return ret

def extract_floats_from_string(string):
    ret = []
    for x in [ y for y in string.split(" ") if y]:
        try:
            a = float(x)
            ret.append(a)
        except ValueError:
            break
    return ret

from collections import deque
from itertools import islice

def consume(iterable, n):

    deque(iterable, maxlen=0) if not n else next(islice(iterable,n,n),None)

def count_occurrences(substring, iterable):
    return sum(1 for string in iterable if substring in string)

def iteristype(iter, type):
    return all(isinstance(x, type) for x in iter)
