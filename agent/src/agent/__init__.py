from functools import wraps
from returns.primitives.exceptions import UnwrapFailedError
from returns.result import Failure


def early_return(func):
    @wraps(func)
    def decorator(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except UnwrapFailedError as e:
            return Failure(e)
    return decorator
