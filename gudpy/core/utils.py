from collections import deque
from itertools import islice
import os
import re


def spacify(iterable, num_spaces=1):
    """
    Spacifies an iterable. In effect, joins the iterable by
    `num_spaces` whitespaces.

    Parameters
    ----------
    iterable : list | tuple
        Target iterable.
    num_spaces : int, optional
        Number of spaces to use.
    
    Returns
    -------
    str : Joined iterable.
    """
    try:
        return (" " * num_spaces).join(iterable)
    except TypeError:
        return (" " * num_spaces).join([str(x) for x in iterable])


def numifyBool(boolean):
    """
    Converts a boolean value to integer.

    Parameters
    ----------
    boolean : bool
        Boolean value to convert.
    
    Returns
    -------
    int : integer representation of `boolean`.
    """
    return sum([boolean])


def boolifyNum(num):
    """
    Converts an integer value to boolean.

    Parameters
    ----------
    num : int
        Integer value to convert.
    
    Returns
    -------
    bool : boolean representation of `num`.
    """
    return not not num


def firstword(string):
    """
    Returns the "first word" in a string.

    Parameters
    ----------
    string : str
        Target string.
    
    Returns
    -------
    str : first word.
    """
    return string.split(" ")[0]


def extract_ints_from_string(string):
    """
    Casts chars to integers, until no more casting can be performed.

    Parameters
    ----------
    string : str
        Target string to extract ints from.
    
    Returns
    -------
    int[] : extracted integers.
    """
    ret = []
    for x in [y for y in string.split(" ") if y]:
        try:
            a = int(x)
            ret.append(a)
        except ValueError:
            break
    return ret


def extract_floats_from_string(string):
    """
    Casts chars to floats, until no more casting can be performed.

    Parameters
    ----------
    string : str
        Target string to extract floats from.
    
    Returns
    -------
    float[] : extracted integers.
    """
    ret = []
    for x in [y for y in string.split(" ") if y]:
        try:
            a = float(x)
            ret.append(a)
        except ValueError:
            break
    return ret


def isfloat(string):
    """
    Checks if a string is a float.

    Parameters
    ----------
    string : str
        Target string for conversion.
    
    Returns
    -------
    bool : is string a float?
    """
    try:
        float(string)
        return True
    except ValueError:
        return False


def isnumeric(string):
    """
    Checks if a string is a number.

    Parameters
    ----------
    string : str
        Target string for conversion.
    
    Returns
    -------
    bool : is string a number?
    """
    return isfloat(string) | string.isnumeric()


def extract_nums_from_string(string):
    """
    Casts chars to numbers, until no more casting can be performed.

    Parameters
    ----------
    string : str
        Target string to extract floats from.
    
    Returns
    -------
    float / int[] | None: extracted numbers.
    """
    if string:
        ret = [x for x in string.split(" ") if isnumeric(x)]
        return [float(x) if '.' in x else int(x) for x in ret]


def consume(iterable, n):
    """
    Consumes `n` values from an iterable by reference.

    Parameters
    ----------
    iterable : Iterable
        Target iterable to consume from.
    n : int
        Number of values to consume.
    """
    deque(iterable, maxlen=0) if not n else next(islice(iterable, n, n), None)


def count_occurrences(substring, iterable):
    """
    Counts the number of substrings in an iterable.

    Parameters
    ----------
    substring : str
        Substring to count.
    iterable : Iterable
        Target iterable to count substrings from.
    
    Returns
    -------
    int : number of occurences of substring.
    """
    return sum(1 for string in iterable if substring in string)


def iteristype(iter, type):
    """
    Checks if all values in `iter` are of type `type`.

    Parameters
    ----------
    iter : Iterable
        Target iterable to check types.
    type : Any
        Type to ensrure.
    
    Returns
    -------
    bool : are all elements of `iter` of type `type`?
    """
    return all(isinstance(x, type) for x in iter)


def isin(iter1, iter2):
    """
    Check if `iter1` is in `iter2`.

    Parameters
    ----------
    iter1 : Iterable
        First iterable.
    iter2 : Iterable
        Second iterable.
    
    Returns
    -------
    bool : is `iter1` in `iter2`?
    int : Index of `iter2` that `iter1` occurs in.
    """
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
    """
    Returns the nth word of a given string.

    Parameters
    ----------
    string : str
        Target tring.
    n : int
        Word number to extract.
    
    Returns
    -------
    str : nth word.
    """
    return string.split()[n]


def nthint(string, n):
    """
    Returns the nth int of a given string.

    Parameters
    ----------
    string : str
        Target tring.
    n : int
        Int number to extract.
    
    Returns
    -------
    int : nth int.
    """
    return int(nthword(string, n))


def nthfloat(string, n):
    """
    Returns the nth float of a given string.

    Parameters
    ----------
    string : str
        Target tring.
    n : int
        Float number to extract.
    
    Returns
    -------
    float : nth float.
    """
    return float(nthword(string, n))


def firstNInts(string, n):
    """
    Returns the fist n ints in a given string.

    Parameters
    ----------
    string : str
        Target string to extract from.
    n : int
        Number of ints to extract.
    
    Returns
    -------
    int[] : extracted integers.
    """
    ints = [int(x) for x in string.split()[:n]]
    if len(ints) != n:
        raise ValueError(f"Could not find {n} ints in {string}")
    else:
        return ints


def firstNFloats(string, n):
    """
    Returns the fist n floats in a given string.

    Parameters
    ----------
    string : str
        Target string to extract from.
    n : int
        Number of floats to extract.
    
    Returns
    -------
    float[] : extracted floats.
    """
    floats = [float(x) for x in string.split()[:n]]
    if len(floats) != n:
        raise ValueError(f"Could not find {n} floats in {string}")
    else:
        return floats


def bjoin(iterable, sep, lastsep=None, endsep='', sameseps=False, suffix=None):
    """
    A better version of `join`.

    Parameters
    ----------
    iterable : Iterable
        Iterable to join.
    sep : str
        Separator to use when joining.
    lastsep : None | str
        Separator to use for final join, if any.
    endsep : str
        Separator to use at the end.
    sameseps : bool
        Should the same separator be used for the end separator?
    suffix : None | str
        Suffix to append, if any.

    Returns
    -------
    str : Joined string.
    """

    # Cast to str.
    iterable = [
        str(i)
        if not isinstance(i, (str, list, tuple))
        else i
        for i in iterable
    ]

    # Spacify
    iterable = [
        spacify(i, num_spaces=2)
        if isinstance(i, (list, tuple))
        else i
        for i in iterable
    ]
    # if no lastsep, then lastsep is sep.
    if not lastsep:
        lastsep = sep
    # If sameseps, then endsep is seo.
    if sameseps:
        endsep = sep
    # If iterable is empty, return empty string.
    if len(iterable) == 0:
        return ""
    # If length of iterbale is one, simply append the sep.
    elif len(iterable) == 1:
        return (iterable[0]) + sep
    # If suffix, append it.
    if suffix:
        iterable = [i + f" {suffix}" for i in iterable]
    # Perform join.
    return sep.join(iterable[:-1]) + lastsep + iterable[-1] + endsep


def resolve(*args):
    """
    Resolve the absolute path of a list of paths.

    Parameters
    ----------
    str[] : args
        Path arguments to use.
    
    Returns
    -------
    str : absolute path that is resolved.
    """
    relativePath = os.sep.join(args)
    topLevel = os.sep.join(
        os.path.realpath(__file__).split(os.sep)[:-3]
    )
    return os.path.join(topLevel, relativePath)


def breplace(str, old, new):
    """
    A better version of `replace`.

    Parameters
    ----------
    str : str
        Target string for replacement.
    old : str
        What is to be replaced
    new : str
        To be replaced with
    
    Returns
    -------
    str : resultant string.
    """
    pattern = re.compile(old, re.IGNORECASE)
    return pattern.sub(new, str)


def nthreplace(str, old, new, nth):
    """
    Replace the `nth` instance of `old` in `str` with `new`.

    Parameters
    ----------
    str : str
        Target string for replacement.
    old : str
        What is to be replaced
    new : str
        To be replaced with
    nth : int
        Number instance of `old` to replace.
    
    Returns
    -------
    str : resultant string.
    """
    tokens = str.split(old)
    if len(tokens) > nth:
        string = f'{old.join(tokens[:nth])}{new}{old.join(tokens[nth:])}'
    return string
