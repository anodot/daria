import time

from typing import Callable
from agent.data_extractor.topology import entity
from agent.data_extractor.topology import functions
from agent.modules import constants


def _get_expiration_time():
    return time.time() + constants.LOOKUP_CACHE_TTL_SECONDS


class Cache:
    def __init__(self):
        self.cache = {}
        self.expiration_timestamp = _get_expiration_time()

    def __getitem__(self, k):
        return self.cache[k]

    def __setitem__(self, k, v):
        self.cache[k] = v

    def __contains__(self, key):
        return key in self.cache

    def expired(self) -> bool:
        return time.time() >= self.expiration_timestamp


_sources = {}
_cache = Cache()


def init_sources(lookup_configs: dict):
    # todo cleanup sources like cache
    global _sources
    for name, conf in lookup_configs.items():
        # todo remove
        if '/usr/src/app' in conf['path']:
            conf['path'] = conf['path'].replace('/usr/src/app', '/Users/antonzelenin/Workspace/daria/agent')
        if name in _sources:
            raise Exception(f'Lookup source `{name}` already exists, lookup name should be unique')
        _sources[name] = entity.source.build(conf)


# todo should key field and value_field be in the lookup config? or can they be different for different fields?
# todo and the code is the same here and in the transform class
def lookup(lookup_name: str, value, key_field: str, value_field: str, compare_function: Callable):
    """
    Searches for a value in the key_field of a lookup using a provided compare function.
    Returns a value from the value_field. Example:

    aliases.csv
    Alias     Type     Full_name
    ifName_1  Network  Interface_name

    res = lookup(
        lookup_name='aliases.csv',
        value='ifName',
        key_field='Alias',
        value_field='Full_name',
        # todo compare function doesn't work yet
        compare_function=startswith
    )
    res == 'Interfaces_name' // output: True
    """
    global _cache
    if _cache.expired():
        _cache = Cache()
    if lookup_name not in _cache:
        _cache[lookup_name] = _sources[lookup_name].get_data()
    res = None
    for obj in _cache[lookup_name]:
        if compare_function(obj[key_field], value):
            if res is not None:
                raise Exception(
                    '\n'.join([
                        'Multiple values exist in the lookup for provided params:',
                        f'lookup name: {lookup_name}',
                        f'value: {value}',
                        f'key field: {key_field}',
                        f'value field: {value_field}',
                        f'compare function: {compare_function.__name__}',
                    ])
                )
            res = obj[value_field]
    return res


def clean_cache():
    global _cache
    _cache = Cache()


def get_compare_function(name: str) -> Callable:
    if name == 'startswith':
        return functions.compare.startswith
    elif name == 'equal':
        return functions.compare.equal
    elif name == 'like':
        return functions.compare.like
    else:
        raise Exception(f'Lookup function `{name}` is not supported')
