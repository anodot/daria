from . import transformer
from .transformer import Transformer
from abc import ABC, abstractmethod

TYPE = 'type'

VARIABLE = 'variable'
CONSTANT = 'constant'


class Field(ABC):
    @abstractmethod
    def get_name(self) -> str:
        pass

    @abstractmethod
    def get_transformers(self) -> list[Transformer]:
        pass

    @abstractmethod
    def extract_from(self, data) -> list[Transformer]:
        pass


class Variable(Field):
    def __init__(self, name: str, value_path: str, transformations: list[Transformer]):
        self.name: str = name
        self.value_path: str = value_path
        self.transformers: list = transformations

    def get_name(self) -> str:
        return self.name

    def get_transformers(self) -> list[Transformer]:
        return self.transformers

    def extract_from(self, obj: dict) -> list[Transformer]:
        return obj[self.value_path]


class Constant(Field):
    def __init__(self, name: str, value):
        self.name: str = name
        self.value = value

    def get_name(self) -> str:
        return self.name

    def get_transformers(self) -> list[Transformer]:
        return []

    def extract_from(self, data) -> list[Transformer]:
        return self.value


def build_fields(fields_conf: dict) -> list[Field]:
    fields = []
    for name, field_ in fields_conf.items():
        type_ = field_.get(TYPE, VARIABLE)
        if type_ == VARIABLE:
            fields.append(Variable(name, field_['value_path'], transformer.build_transformers(field_)))
        elif type_ == CONSTANT:
            fields.append(Constant(name, field_['value']))
    return fields


def extract_fields(fields: list[Field], data: dict) -> dict:
    """
    Returns a dictionary with extracted values
    """
    values = {}
    for field_ in fields:
        value = field_.extract_from(data)
        for transformer_ in field_.get_transformers():
            value = transformer_.transform(value)
        values[field_.get_name()] = value
    return values
