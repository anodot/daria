import time

from agent.data_extractor.topology import entity
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
    global _sources
    for name, conf in lookup_configs.items():
        if name in _sources:
            raise Exception(f'Lookup source `{name}` already exists, lookup name should be unique')
        _sources[name] = entity.source.get(conf)


# todo should key field and value_field be in the lookup config? or can they be different for different fields?
# todo and the code is the same here and in the transform class
def lookup(lookup_name: str, value, key_field: str, value_field: str):
    global _cache
    if _cache.expired():
        _cache = Cache()
    # todo would be nice to have name in the object, but it's not needed for a regular-not-lookup source, think about it
    if lookup_name not in _cache:
        _cache[lookup_name] = _sources[lookup_name].get_data()
    for obj in _cache[lookup_name]:
        if obj[key_field] == value:
            return obj[value_field]
    raise Exception(f'Did not find the value `{value}` in the `{lookup_name}` lookup')
