import json
import os
import agent.source
from agent.repository import pipeline_repository
from agent.source import abstract_source
from agent.constants import DATA_DIR, MONITORING_SOURCE_NAME
from jsonschema import ValidationError, validate

SOURCE_DIRECTORY = os.path.join(DATA_DIR, 'sources')


def __get_file_path(name: str) -> str:
    return os.path.join(SOURCE_DIRECTORY, name + '.json')


def exists(name: str) -> bool:
    return os.path.isfile(__get_file_path(name))


def __save(source: abstract_source.Source):
    with open(__get_file_path(source.name), 'w') as f:
        json.dump(source.to_dict(), f)


def update(source: abstract_source.Source):
    __save(source)


def create(source: abstract_source.Source):
    if exists(source.name):
        raise agent.source.SourceException(f"Source config {source.name} already exists")
    __save(source)


def delete_by_name(source_name: str):
    if not exists(source_name):
        raise agent.source.SourceNotExists(f"Source config {source_name} doesn't exist")
    pipelines = pipeline_repository.get_by_source(source_name)
    if pipelines:
        raise Exception(
            f"Can't delete. Source is used by {', '.join([p.id for p in pipelines])} pipelines"
        )
    os.remove(__get_file_path(source_name))


def get_all() -> list:
    configs = []
    if not os.path.exists(SOURCE_DIRECTORY):
        return configs

    for filename in os.listdir(SOURCE_DIRECTORY):
        if filename.endswith('.json'):
            configs.append(filename.replace('.json', ''))
    return configs


def get(name: str) -> abstract_source.Source:
    if name == MONITORING_SOURCE_NAME:
        return agent.source.MonitoringSource(MONITORING_SOURCE_NAME, agent.source.TYPE_MONITORING, {})

    if not exists(name):
        raise agent.source.SourceNotExists(f"Source config {name} doesn't exist")

    with open(__get_file_path(name)) as f:
        config = json.load(f)

    validate(config, agent.source.json_schema)

    obj = agent.source.types[config['type']](name, config['type'], config['config'])
    try:
        obj.validate_json()
    except ValidationError:
        raise agent.source.SourceConfigDeprecated(
            f'Config for source {name} is not supported. Please recreate the source'
        )

    return obj


def create_dir():
    if not os.path.exists(SOURCE_DIRECTORY):
        os.mkdir(SOURCE_DIRECTORY)
