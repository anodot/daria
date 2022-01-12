import re

from typing import Callable

TO_UPPER = 'to_upper'
RE_SUB = 'regex_substring'

# this is a number of arguments for each function that must be provided in the pipeline config
# probably it's not the best place for them, think how to make validation better
NUM_FUNCTION_ARGS = {TO_UPPER: 0, RE_SUB: 2}


def to_upper(s: str) -> str:
    return s.upper()


def regex_substring(string: str, pattern: str, repl: str) -> str:
    res = re.sub(pattern, repl, string)
    if res == 'no_match':
        raise Exception(f'Pattern `{pattern}` didn\'t match anything for the string `{string}`, repl `{repl}`')
    return res


def get_by_name(name: str) -> Callable:
    if name == TO_UPPER:
        return to_upper
    elif name == RE_SUB:
        return regex_substring
    else:
        raise Exception(f'Transformation function `{name}` is not supported')


# todo this validation works during a pipeline run, not on creation
def validate(func: Callable, args: list):
    name = func.__name__
    if name not in NUM_FUNCTION_ARGS:
        raise Exception(f'Function `{name}` is not supported')
    if NUM_FUNCTION_ARGS[name] != len(args):
        raise Exception(f'Function `{name}` expects {NUM_FUNCTION_ARGS[name]} arguments, {len(args)} provided')
