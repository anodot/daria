import re
import sys

from typing import Callable


def startswith(s: str, prefix: str) -> bool:
    return s.startswith(prefix)


def equals(a, b) -> bool:
    return a == b


def contains(needle: str, haystack: str) -> bool:
    return needle in haystack


def regex_contains(pattern: str, s: str):
    try:
        pattern_ = re.compile(pattern)
    except re.error:
        raise Exception(f'Invalid regex pattern: {pattern}')
    return bool(re.search(pattern_, s))


def get_by_name(name: str) -> Callable:
    try:
        return getattr(sys.modules[__name__], name)
    except AttributeError:
        raise Exception(f'Transformation function `{name}` is not supported')
