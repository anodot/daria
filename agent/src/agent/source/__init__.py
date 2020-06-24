import os
import jsonschema

from .abstract_source import Source, SourceNotExists, SourceException, SourceConfigDeprecated
from .jdbc import JDBCSource
from .influx import InfluxSource
from .kafka import KafkaSource
from .mongo import MongoSource
from .elastic import ElasticSource
from .tcp import TCPSource
from .directory import DirectorySource
from .monitoring import MonitoringSource
from agent.constants import MONITORING_SOURCE_NAME
from agent.repository import source_repository

TYPE_INFLUX = 'influx'
TYPE_KAFKA = 'kafka'
TYPE_MONGO = 'mongo'
TYPE_MYSQL = 'mysql'
TYPE_POSTGRES = 'postgres'
TYPE_ELASTIC = 'elastic'
TYPE_SPLUNK = 'splunk'
TYPE_DIRECTORY = 'directory'
TYPE_MONITORING = 'Monitoring'

types = {
    TYPE_INFLUX: InfluxSource,
    TYPE_KAFKA: KafkaSource,
    TYPE_MONGO: MongoSource,
    TYPE_MYSQL: JDBCSource,
    TYPE_POSTGRES: JDBCSource,
    TYPE_ELASTIC: ElasticSource,
    TYPE_SPLUNK: TCPSource,
    TYPE_DIRECTORY: DirectorySource
}

json_schema = {
    'type': 'object',
    'properties': {
        'type': {'type': 'string', 'enum': list(types.keys())},
        'name': {'type': 'string', 'minLength': 1, 'maxLength': 100},
        'config': {'type': 'object'}
    },
    'required': ['type', 'name', 'config']
}


def create_dir():
    if not os.path.exists(Source.DIR):
        os.mkdir(Source.DIR)


def autocomplete(ctx, args, incomplete):
    configs = []
    for filename in os.listdir(Source.DIR):
        if filename.endswith('.json') and incomplete in filename:
            configs.append(filename.replace('.json', ''))
    return configs


def create_object(name: str, source_type: str) -> Source:
    if name == MONITORING_SOURCE_NAME:
        return MonitoringSource(MONITORING_SOURCE_NAME, TYPE_MONITORING, {})

    if source_type not in types:
        raise ValueError(f'{source_type} isn\'t supported')
    return types[source_type](name, source_type, {})


def create_from_json(config: dict) -> Source:
    source_instance = create_object(config['name'], config['type'])
    source_instance.set_config(config['config'])
    source_instance.validate()
    source_repository.create(source_instance)
    return source_instance


def edit_using_json(config: dict) -> Source:
    source_instance = source_repository.get(config['name'])
    source_instance.set_config(config['config'])
    source_instance.validate()
    source_repository.update(source_instance)
    return source_instance


def validate_json_for_create(json: dict):
    schema = {
        'type': 'array',
        'items': json_schema
    }
    jsonschema.validate(json, schema)


def validate_json_for_edit(json: dict):
    schema = {
        'type': 'array',
        'items': {
            'type': 'object',
            'properties': {
                'name': {'type': 'string', 'minLength': 1, 'maxLength': 100, 'enum': source_repository.get_all()},
                'config': {'type': 'object'}
            },
            'required': ['name', 'config']
        }
    }
    jsonschema.validate(json, schema)
