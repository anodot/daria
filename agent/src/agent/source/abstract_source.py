import json
import os

from abc import ABC, abstractmethod
from agent.constants import DATA_DIR
from jsonschema import validate, ValidationError


class Source(ABC):
    VALIDATION_SCHEMA_FILE_NAME = ''
    DIR = os.path.join(DATA_DIR, 'sources')

    def __init__(self, name: str, source_type: str, config: dict):
        self.config = config
        self.type = source_type
        self.name = name

    def to_dict(self) -> dict:
        return {'name': self.name, 'type': self.type, 'config': self.config}

    @classmethod
    def get_file_path(cls, name: str) -> str:
        return os.path.join(cls.DIR, name + '.json')

    @classmethod
    def exists(cls, name: str) -> bool:
        return os.path.isfile(cls.get_file_path(name))

    @property
    def file_path(self) -> str:
        return self.get_file_path(self.name)

    def save(self):
        with open(self.file_path, 'w') as f:
            json.dump(self.to_dict(), f)

    def create(self):
        if self.exists(self.name):
            raise SourceException(f"Source config {self.name} already exists")

        self.save()

    def delete(self):
        if not self.exists(self.name):
            raise SourceNotExists(f"Source config {self.name} doesn't exist")

        os.remove(self.file_path)

    @abstractmethod
    def prompt(self, default_config, advanced=False):
        pass

    def validate(self):
        with open(os.path.join(os.path.dirname(os.path.realpath(__file__)),
                               'json_schema_definitions', self.VALIDATION_SCHEMA_FILE_NAME)) as f:
            json_schema = json.load(f)

        validate(self.config, json_schema)


class SourceException(Exception):
    pass


class SourceNotExists(SourceException):
    pass
