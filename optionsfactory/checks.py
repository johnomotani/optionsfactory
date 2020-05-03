"""Some common checks that can be imported for clarity
"""


def is_positive(x):
    try:
        return x > 0
    except TypeError:
        return False


def is_positive_or_None(x):
    if x is None:
        return True
    return is_positive(x)


def is_non_negative(x):
    try:
        return x >= 0
    except TypeError:
        return False


def is_non_negative_or_None(x):
    if x is None:
        return True
    return is_non_negative(x)


def is_None(x):
    return x is None


NoneType = type(None)
