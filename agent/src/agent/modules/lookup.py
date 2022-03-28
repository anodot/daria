from agent.modules import data_source
from typing import Callable, Optional, Any


class Provide:
    def __init__(self, lookup_configs: dict):
        self.lookup_configs = lookup_configs

    def __enter__(self):
        _init_sources(self.lookup_configs)

    def __exit__(self, exc_type, exc_value, exc_traceback):
        _clean()


_sources = {}
_lookup_cache = {}
_results_cache = {}


def lookup(
    lookup_name: str,
    lookup_value: Any,
    key_field: str,
    value_field: str,
    compare_function: Callable,
    strict: bool,
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
    global _lookup_cache

    if lookup_name not in _lookup_cache:
        _lookup_cache[lookup_name] = _sources[lookup_name].get_data()

    result_cache_key = _build_result_cache_key(lookup_name, lookup_value, key_field, value_field, compare_function)
    if result_cache_key in _results_cache:
        return _results_cache[result_cache_key]

    res = [obj[value_field] for obj in _lookup_cache[lookup_name] if compare_function(obj[key_field], lookup_value)]

    if len(res) > 1 and strict:
        raise Exception(
            '\n'.join([
                'Multiple values exist in the lookup for provided params:',
                f'lookup name: {lookup_name}',
                f'lookup value: {lookup_value}',
                f'key field: {key_field}',
                f'value field: {value_field}',
                f'compare function: {compare_function.__name__}',
                f'matched values: {", ".join(res)}',
            ])
        )

    _results_cache[result_cache_key] = _extract_result(res)
    return _results_cache[result_cache_key]


def _extract_result(res: list):
    if len(res) > 1:
        res.sort()
    return res[0] if res else None


def _init_sources(lookup_configs: dict):
    global _sources
    for name, conf in lookup_configs.items():
        if name in _sources:
            raise Exception(f'Lookup source `{name}` already exists, lookup names should be unique')
        _sources[name] = data_source.build(conf)


def _clean():
    global _lookup_cache, _results_cache, _sources
    _lookup_cache = {}
    _results_cache = {}
    _sources = {}


def _build_result_cache_key(
    lookup_name: str,
    lookup_value: Any,
    key_field: str,
    value_field: str,
    compare_function: Callable,
) -> Optional[Any]:
    return "_".join([lookup_name, str(lookup_value), key_field, value_field, compare_function.__name__])
