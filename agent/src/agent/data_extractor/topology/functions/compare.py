def startswith(s: str, prefix: str) -> bool:
    return s.startswith(prefix)


def equal(a, b) -> bool:
    return a == b


def like(haystack: str, needle: str) -> bool:
    return needle in haystack
