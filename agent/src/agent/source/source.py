import os
import json

from agent.constants import DATA_DIR
from . import prompters


class Source:
    DIR = os.path.join(DATA_DIR, 'sources')

    TYPE_INFLUX = 'influx'
    TYPE_KAFKA = 'kafka'
    TYPE_MONGO = 'mongo'
    TYPE_MYSQL = 'mysql'
    TYPE_MONITORING = 'Monitoring'

    types = [TYPE_INFLUX, TYPE_KAFKA, TYPE_MONGO, TYPE_MYSQL]

    prompters = {
        TYPE_INFLUX: prompters.PromptInflux,
        TYPE_KAFKA: prompters.PromptKafka,
        TYPE_MONGO: prompters.PromptMongo,
        TYPE_MYSQL: prompters.PromptJDBC
    }

    def __init__(self, name, source_type=None):
        self.config = {'name': name, 'type': source_type, 'config': {}}

    @classmethod
    def create_dir(cls):
        if not os.path.exists(cls.DIR):
            os.mkdir(cls.DIR)

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
        with open(self.file_path, 'w') as f:
            json.dump(self.config, f)

    def create(self):
        if self.exists():
            raise SourceException(f"Source config {self.config['name']} already exists")

        self.save()

    def delete(self):
        if not self.exists():
            raise SourceNotExists(f"Source config {self.config['name']} doesn't exist")

        os.remove(self.file_path)

    def prompt(self, default_config=None, advanced=False):
        if not default_config:
            default_config = self.config['config']
        self.config['config'] = self.prompters[self.config['type']]().prompt(default_config, advanced)

    @classmethod
    def get_list(cls):
        configs = []
        for filename in os.listdir(cls.DIR):
            if filename.endswith('.json'):
                configs.append(filename.replace('.json', ''))
        return configs


class SourceException(Exception):
    pass


class SourceNotExists(SourceException):
    pass
