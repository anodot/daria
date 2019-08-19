import os
import json

from agent.constants import DATA_DIR
from . import prompters

DIR = os.path.join(DATA_DIR, 'sources')

TYPE_INFLUX = 'influx'
TYPE_KAFKA = 'kafka'
TYPE_MONGO = 'mongo'
TYPE_MYSQL = 'mysql'
TYPE_POSTGRES = 'postgres'
TYPE_MONITORING = 'Monitoring'

types = [TYPE_INFLUX, TYPE_KAFKA, TYPE_MONGO, TYPE_MYSQL, TYPE_POSTGRES]


def create_dir():
    if not os.path.exists(DIR):
        os.mkdir(DIR)


def get_file_path(name: str) -> str:
    return os.path.join(DIR, name + '.json')


def exists(name: str) -> bool:
    return os.path.isfile(get_file_path(name))


def get_list() -> list:
    configs = []
    for filename in os.listdir(DIR):
        if filename.endswith('.json'):
            configs.append(filename.replace('.json', ''))
    return configs


class Source:
    def __init__(self, name: str, source_type: str, config: dict, prompter: prompters.PromptInterface):
        self.config = config
        self.type = source_type
        self.name = name
        self.prompter = prompter

    def to_dict(self) -> dict:
        return {'name': self.name, 'type': self.type, 'config': self.config}

    @property
    def file_path(self) -> str:
        return get_file_path(self.name)

    def save(self):
        with open(self.file_path, 'w') as f:
            json.dump(self.to_dict(), f)

    def create(self):
        if exists(self.name):
            raise SourceException(f"Source config {self.name} already exists")

        self.save()

    def delete(self):
        if not exists(self.name):
            raise SourceNotExists(f"Source config {self.name} doesn't exist")

        os.remove(self.file_path)


class SourceException(Exception):
    pass


class SourceNotExists(SourceException):
    pass


prompters_types = {
    TYPE_INFLUX: prompters.PromptInflux,
    TYPE_KAFKA: prompters.PromptKafka,
    TYPE_MONGO: prompters.PromptMongo,
    TYPE_MYSQL: prompters.PromptJDBC,
    TYPE_POSTGRES: prompters.PromptJDBC,
}


def create_object(name: str, source_type: str) -> Source:
    if source_type not in types:
        raise ValueError(f'{source_type} isn\'t supported')
    return Source(name, source_type, {}, prompters_types[source_type]())


def load_object(name: str) -> Source:
    if not exists(name):
        raise SourceNotExists(f"Source config {name} doesn't exist")

    with open(get_file_path(name), 'r') as f:
        config = json.load(f)

    return Source(name, config['type'], config['config'], prompters_types[config['type']]())
