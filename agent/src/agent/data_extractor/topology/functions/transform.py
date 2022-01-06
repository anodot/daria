import re


def to_upper(s: str) -> str:
    return s.upper()


def re_sub(string: str, pattern: str, repl: str) -> str:
    return re.sub(pattern, repl, string)
