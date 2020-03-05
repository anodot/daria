import os
import json

from .abstract_source import Source, SourceNotExists, SourceException, SourceConfigDeprecated
from .jdbc import JDBCSource
from .influx import InfluxSource
from .kafka import KafkaSource
from .mongo import MongoSource
from .elastic import ElasticSource
from .tcp import TCPSource
from .monitoring import MonitoringSource
from jsonschema import ValidationError, validate
from typing import Iterable

from agent.constants import MONITORING_SOURCE_NAME

TYPE_INFLUX = 'influx'
TYPE_KAFKA = 'kafka'
TYPE_MONGO = 'mongo'
TYPE_MYSQL = 'mysql'
TYPE_POSTGRES = 'postgres'
TYPE_ELASTIC = 'elastic'
TYPE_TCP = 'tcp_server'
TYPE_MONITORING = 'Monitoring'


def get_list() -> list:
    configs = []
    for filename in os.listdir(Source.DIR):
        if filename.endswith('.json'):
            configs.append(filename.replace('.json', ''))
    return configs


def create_dir():
    if not os.path.exists(Source.DIR):
        os.mkdir(Source.DIR)


def autocomplete(ctx, args, incomplete):
    configs = []
    for filename in os.listdir(Source.DIR):
        if filename.endswith('.json') and incomplete in filename:
            configs.append(filename.replace('.json', ''))
    return configs


types = {
    TYPE_INFLUX: InfluxSource,
    TYPE_KAFKA: KafkaSource,
    TYPE_MONGO: MongoSource,
    TYPE_MYSQL: JDBCSource,
    TYPE_POSTGRES: JDBCSource,
    TYPE_ELASTIC: ElasticSource,
    TYPE_TCP: TCPSource
}


def get_types() -> Iterable:
    return types.keys()


def create_object(name: str, source_type: str) -> Source:
    if name == MONITORING_SOURCE_NAME:
        return MonitoringSource(MONITORING_SOURCE_NAME, TYPE_MONITORING, {})

    if source_type not in types:
        raise ValueError(f'{source_type} isn\'t supported')
    return types[source_type](name, source_type, {})


json_schema = {
    'type': 'object',
    'properties': {
        'type': {'type': 'string', 'enum': list(get_types())},
        'name': {'type': 'string', 'minLength': 1, 'maxLength': 100},
        'config': {'type': 'object'}
    },
    'required': ['type', 'name', 'config']
}


def load_object(name: str) -> Source:
    if name == MONITORING_SOURCE_NAME:
        return MonitoringSource(MONITORING_SOURCE_NAME, TYPE_MONITORING, {})

    if not Source.exists(name):
        raise SourceNotExists(f"Source config {name} doesn't exist")

    with open(Source.get_file_path(name), 'r') as f:
        config = json.load(f)

    validate(config, json_schema)

    obj = types[config['type']](name, config['type'], config['config'])
    try:
        obj.validate_json()
    except ValidationError:
        raise SourceConfigDeprecated(f'Config for source {name} is not supported. Please recreate the source')

    return obj
