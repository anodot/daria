from agent.modules import lookup
from agent.modules import functions
from abc import ABC, abstractmethod
from typing import Callable, Optional, Any

TYPE = 'type'

TRANSFORMATIONS = 'transformations'

FUNCTION_TRANSFORMATION = 'function'
LOOKUP_TRANSFORMATION = 'lookup'


class Transformer(ABC):
    @abstractmethod
    def transform(self, data) -> dict:
        pass


class FunctionTransformer(Transformer):
    def __init__(self, func: Callable, args: list):
        # todo validate function args?
        self.func = func
        self.args = args

    def transform(self, val):
        return self.func(val, *self.args)


class LookupTransformer(Transformer):
    def __init__(self, lookup_name: str, lookup_key: str, lookup_value: Any, compare_func_name: Optional[str]):
        self.compare_func = lookup.get_compare_function(compare_func_name) \
            if compare_func_name is not None \
            else functions.compare.equal
        self.lookup_name = lookup_name
        self.lookup_key = lookup_key
        self.lookup_value = lookup_value

    def transform(self, value) -> Optional[Any]:
        return lookup.lookup(self.lookup_name, value, self.lookup_key, self.lookup_value, self.compare_func)


def build_transformers(field_conf: dict) -> list:
    transformers = []
    for transform in field_conf.get(TRANSFORMATIONS, []):
        type_ = transform[TYPE]
        if type_ == FUNCTION_TRANSFORMATION:
            transformers.append(
                FunctionTransformer(
                    _get_transform_function(transform),
                    _get_function_args(transform),
                )
            )
        elif type_ == LOOKUP_TRANSFORMATION:
            transformers.append(
                LookupTransformer(
                    transform['name'],
                    transform['key'],
                    transform['value'],
                    transform.get('compare_function'),
                )
            )
        else:
            raise Exception(f'Invalid type of a transformation provided: `{type_}`')
    return transformers


def _get_function_args(transform_conf: dict) -> list:
    return transform_conf['value'].split(' ')[1:]


def _get_transform_function(transform_conf: dict) -> Callable:
    name = _get_function_name(transform_conf)
    if name == 'to_upper':
        return functions.transform.to_upper
    elif name == 're.sub':
        return functions.transform.re_sub
    else:
        raise Exception(f'Transformation function `{name}` is not supported')


def _get_function_name(transform_conf: dict) -> str:
    return transform_conf['value'].split(' ')[0]
