import sys

from typing import Callable


def startswith(s: str, prefix: str) -> bool:
    return s.startswith(prefix)


def equal(a, b) -> bool:
    return a == b


def contains(haystack: str, needle: str) -> bool:
    return needle in haystack


def get_by_name(name: str) -> Callable:
    try:
        return getattr(sys.modules[__name__], name)
    except AttributeError:
        raise Exception(f'Transformation function `{name}` is not supported')
