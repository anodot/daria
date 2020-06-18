import json
import os

from agent import pipeline
from agent.constants import DATA_DIR, MONITORING_SOURCE_NAME
from agent.source import Source, SourceNotExists, SourceException, MonitoringSource, TYPE_MONITORING, \
    SourceConfigDeprecated, json_schema as source_json_schema, types as source_types
from jsonschema import ValidationError, validate

SOURCE_DIRECTORY = os.path.join(DATA_DIR, 'sources')


def __get_file_path(name: str) -> str:
    return os.path.join(SOURCE_DIRECTORY, name + '.json')


def exists(name: str) -> bool:
    return os.path.isfile(__get_file_path(name))


def update(source: Source):
    with open(__get_file_path(source.name), 'w') as f:
        json.dump(source.to_dict(), f)


def create(source: Source):
    if exists(source.name):
        raise SourceException(f"Source config {source.name} already exists")
    update(source)


def delete(source: Source):
    delete_by_name(source.name)


def delete_by_name(source_name: str):
    if not exists(source_name):
        raise SourceNotExists(f"Source config {source_name} doesn't exist")

    pipelines = pipeline.get_pipelines(source_name=source_name)
    if pipelines:
        raise SourceException(f"Can't delete. Source is used by {', '.join([p.id for p in pipelines])} pipelines")

    os.remove(__get_file_path(source_name))


def get_all() -> list:
    configs = []
    if not os.path.exists(SOURCE_DIRECTORY):
        return configs

    for filename in os.listdir(SOURCE_DIRECTORY):
        if filename.endswith('.json'):
            configs.append(filename.replace('.json', ''))
    return configs


def get(name: str) -> Source:
    if name == MONITORING_SOURCE_NAME:
        return MonitoringSource(MONITORING_SOURCE_NAME, TYPE_MONITORING, {})

    if not exists(name):
        raise SourceNotExists(f"Source config {name} doesn't exist")

    with open(__get_file_path(name)) as f:
        config = json.load(f)

    validate(config, source_json_schema)

    obj = source_types[config['type']](name, config['type'], config['config'])
    try:
        obj.validate_json()
    except ValidationError:
        raise SourceConfigDeprecated(f'Config for source {name} is not supported. Please recreate the source')

    return obj
