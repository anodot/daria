import os
import json

from abc import ABC, abstractmethod
from agent.constants import DATA_DIR


class BaseSource(ABC):
    DIR = os.path.join(DATA_DIR, 'sources')

    @abstractmethod
    def get_type(self):
        ...

    def __init__(self, name):
        self.config = {'name': name, 'type': self.get_type(), 'config': {}}

    @property
    def file_path(self):
        return os.path.join(self.DIR, self.config['name'] + '.json')

    def exists(self):
        return os.path.isfile(self.file_path)

    def load(self):
        if not self.exists():
            raise SourceNotExists(f"Source config {self.config['name']} doesn't exist")

        with open(self.file_path, 'r') as f:
            self.config = json.load(f)

        return self.config

    def save(self):
        with open(os.path.join(self.DIR, self.config['name'] + '.json'), 'w') as f:
            json.dump(self.config, f)

    def create(self):
        if self.exists():
            raise SourceException(f"Source config {self.config['name']} already exists")

        self.save()

    def delete(self):
        if not self.exists():
            raise SourceNotExists(f"Source config {self.config['name']} doesn't exist")

        os.remove(self.file_path)


class SourceException(Exception):
    pass


class SourceNotExists(SourceException):
    pass
