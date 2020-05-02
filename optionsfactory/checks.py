"""Some common checks that can be imported for clarity
"""


def is_positive(x):
    return x > 0


def is_positive_or_None(x):
    if x is None:
        return True
    return is_positive(x)


def is_non_negative(x):
    return x >= 0


def is_non_negative_or_None(x):
    if x is None:
        return True
    return is_non_negative(x)


NoneType = type(None)
