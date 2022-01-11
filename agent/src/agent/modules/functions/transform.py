import re


def to_upper(s: str) -> str:
    return s.upper()


def re_sub(string: str, pattern: str, repl: str) -> str:
    res = re.sub(pattern, repl, string)
    if res == 'no_match':
        raise Exception(f'Pattern `{pattern}` didn\'t match anything for the string `{string}`, repl `{repl}`')
    return res
