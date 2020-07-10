import json
import os
from agent import source
from agent import pipeline
from agent.constants import DATA_DIR, MONITORING_SOURCE_NAME
from jsonschema import ValidationError, validate

SOURCE_DIRECTORY = os.path.join(DATA_DIR, 'sources')


def _get_file_path(name: str) -> str:
    return os.path.join(SOURCE_DIRECTORY, name + '.json')


def exists(name: str) -> bool:
    return os.path.isfile(_get_file_path(name))


def _save(source_obj: source.Source):
    with open(_get_file_path(source_obj.name), 'w') as f:
        json.dump(source_obj.to_dict(), f)


def update(source_obj: source.Source):
    _save(source_obj)


def create(source_obj: source.Source):
    if exists(source_obj.name):
        raise source.SourceException(f"Source config {source_obj.name} already exists")
    _save(source_obj)


def delete_by_name(source_name: str):
    if not exists(source_name):
        raise SourceNotExists(f"Source config {source_name} doesn't exist")
    pipelines = pipeline.repository.get_by_source(source_name)
    if pipelines:
        raise Exception(
            f"Can't delete. Source is used by {', '.join([p.id for p in pipelines])} pipelines"
        )
    os.remove(_get_file_path(source_name))


def get_all() -> list:
    configs = []
    if not os.path.exists(SOURCE_DIRECTORY):
        return configs

    for filename in os.listdir(SOURCE_DIRECTORY):
        if filename.endswith('.json'):
            configs.append(filename.replace('.json', ''))
    return configs


def get(name: str) -> source.Source:
    if name == MONITORING_SOURCE_NAME:
        return source.MonitoringSource(MONITORING_SOURCE_NAME, source.TYPE_MONITORING, {})
    if not exists(name):
        raise SourceNotExists(f"Source config {name} doesn't exist")
    with open(_get_file_path(name)) as f:
        config = json.load(f)
    validate(config, source.json_schema)
    source_obj = source.Source(name, config['type'], config['config'])
    try:
        source.validator.validate_json(source_obj)
    except ValidationError:
        raise SourceConfigDeprecated(f'Config for source {name} is not supported. Please recreate the source')
    return source_obj


def create_dir():
    if not os.path.exists(SOURCE_DIRECTORY):
        os.mkdir(SOURCE_DIRECTORY)


class SourceNotExists(Exception):
    pass


class SourceConfigDeprecated(Exception):
    pass
