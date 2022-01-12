from functools import wraps
from agent.modules import data_source
from typing import Callable, Optional, Any

_sources = {}
_cache = {}


def provide(func):
    """
    Initializes lookup sources and cache and cleans them after the function execution
    Wrapped function must have a pipeline argument of the type Pipeline in the first position
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        _clean()
        _init_sources(args[0].config.get('lookup', {}))
        res = func(*args, **kwargs)
        # todo use finally or with
        _clean()
        return res

    return wrapper


def lookup(
    lookup_name: str,
    lookup_value: Any,
    key_field: str,
    value_field: str,
    compare_function: Callable,
) -> Optional[Any]:
    """
    Searches for a lookup_value in the key_field of a lookup using a provided compare function.
    Returns a value from the value_field. Example:

    aliases.csv
    Alias     Type     Full_name
    ifName_1  Network  Interface_name

    res = lookup(
        lookup_name='aliases.csv',
        lookup_value='ifName',
        key_field='Alias',
        value_field='Full_name',
        compare_function=startswith
    )
    res == 'Interface_name' // output: True
    """
    global _cache
    if lookup_name not in _cache:
        _cache[lookup_name] = _sources[lookup_name].get_data()
    res = None
    for obj in _cache[lookup_name]:
        if compare_function(obj[key_field], lookup_value):
            if res is not None:
                raise Exception(
                    '\n'.join([
                        'Multiple values exist in the lookup for provided params:',
                        f'lookup name: {lookup_name}',
                        f'lookup value: {lookup_value}',
                        f'key field: {key_field}',
                        f'value field: {value_field}',
                        f'compare function: {compare_function.__name__}',
                    ])
                )
            res = obj[value_field]
    return res


def _init_sources(lookup_configs: dict):
    global _sources
    for name, conf in lookup_configs.items():
        if name in _sources:
            raise Exception(f'Lookup source `{name}` already exists, lookup names should be unique')
        _sources[name] = data_source.build(conf)


def _clean():
    global _cache, _sources
    _cache = {}
    _sources = {}
