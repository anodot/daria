import json
import jsonschema

from typing import List
from agent import source
from agent.modules.logger import get_logger
from agent.source import Source

logger_ = get_logger(__name__, stdout=True)


def create_from_file(file):
    build_multiple(extract_configs(file))


def edit_using_file(file):
    edit_multiple(extract_configs(file))


def build_multiple(configs: list) -> List[Source]:
    _validate_configs_for_create(configs)
    exceptions = {}
    sources = []
    for config in configs:
        try:
            source.manager.check_source_name(config['name'])
            sources.append(
                build(config)
            )
            print(f"Source {config['name']} created")
        except Exception as e:
            exceptions[config['name']] = f'{type(e).__name__}: {e}\n'
            logger_.debug(e, exc_info=True)
    if exceptions:
        raise source.SourceException(json.dumps(exceptions))
    return sources


def build(config: dict) -> Source:
    _validate_config_for_create(config)
    source_ = source.manager.create_source_obj(config['name'], config['type'])
    source_.set_config(config['config'])
    source.validator.validate(source_)
    source.repository.save(source_)
    return source_


def edit_multiple(configs: list) -> List[Source]:
    if not isinstance(configs, list):
        raise ValueError(f'Provided data must be a list of configs, {type(configs).__name__} provided instead')
    exceptions = {}
    sources = []
    for config in configs:
        try:
            source_ = edit(config)
            print(f"Source {config['name']} updated")
            sources.append(source_)
        except Exception as e:
            exceptions[config['name']] = f'{type(e).__name__}: {e}'
            logger_.debug(e, exc_info=True)
    if exceptions:
        raise source.SourceException(json.dumps(exceptions))
    return sources


def edit(config: dict) -> Source:
    _validate_config_for_edit(config)
    source_ = source.repository.get_by_name(config['name'])
    source_.set_config(config['config'])
    source.manager.update(source_)
    return source_


def extract_configs(file) -> list:
    configs = json.load(file)
    file.seek(0)

    json_schema = {
        'type': 'array',
        'items': {
            'type': 'object',
            'properties': {
                'name': {'type': 'string'},
                'type': {'type': 'string'}
            },
            'required': ['name']
        }
    }
    jsonschema.validate(configs, json_schema)
    return configs


def _validate_configs_for_create(json_data: list):
    schema = {
        'type': 'array',
        'items': source.json_schema
    }
    jsonschema.validate(json_data, schema)


def _validate_config_for_create(json_data: dict):
    jsonschema.validate(json_data, source.json_schema)


def _validate_config_for_edit(json_data: dict):
    schema = {
        'type': 'object',
        'properties': {
            'name': {'type': 'string', 'minLength': 1, 'maxLength': 100, 'enum': source.repository.get_all_names()},
            'config': {'type': 'object'}
        },
        'required': ['name', 'config']
    }
    jsonschema.validate(json_data, schema)
