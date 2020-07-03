import click

from functools import wraps
from returns.primitives.exceptions import UnwrapFailedError


def print_unwrap_exception(func):
    @wraps(func)
    def decorator(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except UnwrapFailedError as e:
            raise click.ClickException(str(e))
    return decorator
