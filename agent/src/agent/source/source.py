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
    TYPE_POSTGRES = 'postgres'
    TYPE_MONITORING = 'Monitoring'

    types = [TYPE_INFLUX, TYPE_KAFKA, TYPE_MONGO, TYPE_MYSQL, TYPE_POSTGRES]

    def __init__(self, name: str, source_type: str, config: dict, prompter: prompters.PromptInterface):
        self.config = {'name': name, 'type': source_type, 'config': config}
        self.prompter = prompter

    @classmethod
    def create_dir(cls):
        if not os.path.exists(cls.DIR):
            os.mkdir(cls.DIR)

    @classmethod
    def get_file_path(cls, name: str) -> str:
        return os.path.join(cls.DIR, name + '.json')

    @classmethod
    def exists(cls, name: str) -> bool:
        return os.path.isfile(cls.get_file_path(name))

    @property
    def file_path(self) -> str:
        return self.get_file_path(self.config['name'])

    def save(self):
        with open(self.file_path, 'w') as f:
            json.dump(self.config, f)

    def create(self):
        if self.exists(self.config['name']):
            raise SourceException(f"Source config {self.config['name']} already exists")

        self.save()

    def delete(self):
        if not self.exists(self.config['name']):
            raise SourceNotExists(f"Source config {self.config['name']} doesn't exist")

        os.remove(self.file_path)

    @classmethod
    def get_list(cls) -> list:
        configs = []
        for filename in os.listdir(cls.DIR):
            if filename.endswith('.json'):
                configs.append(filename.replace('.json', ''))
        return configs


class SourceException(Exception):
    pass


class SourceNotExists(SourceException):
    pass


prompters_types = {
    Source.TYPE_INFLUX: prompters.PromptInflux,
    Source.TYPE_KAFKA: prompters.PromptKafka,
    Source.TYPE_MONGO: prompters.PromptMongo,
    Source.TYPE_MYSQL: prompters.PromptJDBC,
    Source.TYPE_POSTGRES: prompters.PromptJDBC,
}


def create_source_object(name: str, source_type: str) -> Source:
    if source_type not in Source.types:
        raise ValueError(f'{source_type} isn\'t supported')
    return Source(name, source_type, {}, prompters_types[source_type]())


def load_source_object(name: str) -> Source:
    if not Source.exists(name):
        raise SourceNotExists(f"Source config {name} doesn't exist")

    with open(Source.get_file_path(name), 'r') as f:
        config = json.load(f)

    return Source(name, config['type'], config['config'], prompters_types[config['type']]())
