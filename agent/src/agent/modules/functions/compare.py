from typing import Callable


def startswith(s: str, prefix: str) -> bool:
    return s.startswith(prefix)


def equal(a, b) -> bool:
    return a == b


def contains(haystack: str, needle: str) -> bool:
    return needle in haystack


def get_by_name(name: str) -> Callable:
    if name == 'startswith':
        return startswith
    elif name == 'equal':
        return equal
    elif name == 'like':
        return contains
    else:
        raise Exception(f'Lookup function `{name}` is not supported')
