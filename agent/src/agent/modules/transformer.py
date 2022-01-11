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
    def transform(self, data):
        pass


class FunctionTransformer(Transformer):
    def __init__(self, func: Callable, args: list):
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


def build_transformers(field_conf: dict) -> list[Transformer]:
    transformers = []
    for transform in field_conf.get(TRANSFORMATIONS, []):
        type_ = transform[TYPE]
        if type_ == FUNCTION_TRANSFORMATION:
            func = functions.transform.get_by_name(transform['name'])
            args = transform.get('args', [])
            functions.transform.validate(func, args)
            transformers.append(FunctionTransformer(func, args))
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
