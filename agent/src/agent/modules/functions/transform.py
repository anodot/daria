import inspect
import re
import sys

from typing import Callable


def to_upper(s: str) -> str:
    return s.upper()


def regex_substring(string: str, pattern: str, repl: str) -> str:
    res = re.sub(pattern, repl, string)
    if res == 'no_match':
        raise Exception(f'Pattern `{pattern}` didn\'t match anything for the string `{string}`, repl `{repl}`')
    return res


def divide(numerator: int | float, denominator: int | float) -> float:
    return numerator / denominator


def get_by_name(name: str) -> Callable:
    try:
        return getattr(sys.modules[__name__], name)
    except AttributeError:
        raise Exception(f'Transformation function `{name}` is not supported')


# todo this validation works during a pipeline run, not on creation
def validate(func: Callable, args: list):
    # users need to provide one argument less than a function takes because
    # the transformed value itself is the first argument, that's why minus 1
    num_function_args = len(inspect.signature(func).parameters) - 1
    if num_function_args != len(args):
        raise Exception(f'Function `{func.__name__}` expects {num_function_args} arguments, {len(args)} provided')
