from abc import ABC, abstractmethod
from agent.data_extractor.topology import lookup

VARIABLE = 'variable'
CONSTANT = 'constant'

TRANSFORMATIONS = 'transformations'

FUNCTION_TRANSFORMATION = 'function'
LOOKUP_TRANSFORMATION = 'lookup'


class Transformer(ABC):
    @abstractmethod
    def transform(self, data) -> dict:
        pass


class FunctionTransformer(Transformer):
    SUPPORTED_FUNCTIONS = ['substring', 'concat']

    def __init__(self, func: str, *args):
        if func not in self.SUPPORTED_FUNCTIONS:
            # todo exception type
            raise Exception(f'Transformation function `{func}` is not supported')
        self.func = func

    def transform(self, value):
        # todo
        return value


class LookupTransformer(Transformer):
    def __init__(self, lookup_name: str, lookup_key: str, lookup_value: str):
        self.lookup_name = lookup_name
        self.lookup_key = lookup_key
        self.lookup_value = lookup_value

    # todo str or any?
    def transform(self, value) -> str:
        return lookup.lookup(self.lookup_name, value, self.lookup_key, self.lookup_value)


class Field(ABC):
    @abstractmethod
    def get_name(self) -> str:
        pass

    @abstractmethod
    def get_transformers(self) -> list[Transformer]:
        pass


class Variable(Field):
    def __init__(self, name: str, source_field: str, transformations: list[Transformer]):
        self.name: str = name
        self.source_field: str = source_field
        self.transformers: list = transformations

    def get_name(self) -> str:
        return self.name

    def get_transformers(self) -> list[Transformer]:
        return self.transformers


class Constant(Field):
    def __init__(self, name: str, value):
        self.name: str = name
        self.value = value

    def get_name(self) -> str:
        return self.name

    def get_transformers(self) -> list[Transformer]:
        return []


def extract(data: dict, field_: Field):
    # todo don't you think it looks like a class??? you're passing object into function
    if type(field_) is Variable:
        return data[field_.source_field]
    elif type(field_) is Constant:
        return field_.value
    else:
        raise Exception('Invalid field provided')


def build_fields(fields_conf: dict) -> list[Field]:
    fields = []
    for name, field_ in fields_conf.items():
        if field_['type'] == VARIABLE:
            fields.append(Variable(name, field_['source_field'], build_transformers(field_)))
        elif field_['type'] == CONSTANT:
            fields.append(Constant(name, field_['value']))
    return fields


def build_transformers(field_conf: dict) -> list:
    transformers = []
    for transform in field_conf.get(TRANSFORMATIONS, []):
        type_ = transform['type']
        if type_ == FUNCTION_TRANSFORMATION:
            transformers.append(FunctionTransformer(_get_function_name(transform)))
        elif type_ == LOOKUP_TRANSFORMATION:
            transformers.append(LookupTransformer(transform['name'], transform['key'], transform['value']))
        else:
            raise Exception(f'Invalid type of a transformation provided: `{type_}`')
    return transformers


def _get_function_name(transform_conf: dict) -> str:
    return transform_conf['value'].split(' ')[0]
