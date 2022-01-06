from abc import ABC, abstractmethod
from typing import Callable

from agent.data_extractor.topology import lookup, functions

TYPE = 'type'

TRANSFORMATIONS = 'transformations'

FUNCTION_TRANSFORMATION = 'function'
LOOKUP_TRANSFORMATION = 'lookup'


class Transformer(ABC):
    @abstractmethod
    def transform(self, data) -> dict:
        pass


class FunctionTransformer(Transformer):
    def __init__(self, func: str, args: list):
        # todo validate that args are fine for the func
        self.func = get_transform_function(func)
        self.args = args

    def transform(self, val):
        return self.func(val, *self.args)


class LookupTransformer(Transformer):
    def __init__(self, lookup_name: str, lookup_key: str, lookup_value: str, compare_func: Callable):
        self.lookup_name = lookup_name
        self.lookup_key = lookup_key
        self.lookup_value = lookup_value
        self.compare_func = compare_func

    # todo str or any?
    def transform(self, value) -> str:
        # todo why do I pass all params from an object into a function?
        return lookup.lookup(self.lookup_name, value, self.lookup_key, self.lookup_value, self.compare_func)


def build_transformers(field_conf: dict) -> list:
    transformers = []
    for transform in field_conf.get(TRANSFORMATIONS, []):
        type_ = transform[TYPE]
        if type_ == FUNCTION_TRANSFORMATION:
            transformers.append(FunctionTransformer(_get_function_name(transform), _get_function_args(transform)))
        elif type_ == LOOKUP_TRANSFORMATION:
            transformers.append(
                LookupTransformer(
                    transform['name'],
                    transform['key'],
                    transform['value'],
                    # todo not obvious default value, also duplicate string 'equal', constant better
                    lookup.get_compare_function(transform.get('compare_function', 'equal'))
                )
            )
        else:
            raise Exception(f'Invalid type of a transformation provided: `{type_}`')
    return transformers


def _get_function_name(transform_conf: dict) -> str:
    # todo probably value is not the best key
    return transform_conf['value'].split(' ')[0]


def _get_function_args(transform_conf: dict) -> list:
    return transform_conf['value'].split(' ')[1:]


def get_transform_function(name: str) -> Callable:
    if name == 'toUpper':
        return functions.transform.to_upper
    elif name == 're.sub':
        return functions.transform.re_sub
    else:
        raise Exception(f'Transformation function `{name}` is not supported')
