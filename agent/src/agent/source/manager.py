import json
import jsonschema

from typing import List
from agent import pipeline
from agent import source
from agent.source import SourceException
from agent.modules.streamsets_api_client import api_client

MAX_SAMPLE_RECORDS = 3


def create_source_obj(source_name: str, source_type: str) -> source.Source:
    return source.types[source_type](source_name, source_type, {})


def create_from_file(file):
    create_from_json(extract_configs(file))


def edit_using_file(file):
    edit_using_json(extract_configs(file))


def create_from_json(configs: dict) -> List[source.Source]:
    validate_configs_for_create(configs)
    exceptions = {}
    sources = []
    for config in configs:
        try:
            check_source_name(config['name'])
            sources.append(
                create_source_from_json(config)
            )
            print(f"Source {config['name']} created")
        except Exception as e:
            # todo traceback?
            exceptions[config['name']] = f'{type(e).__name__}: {str(e)}'
    if exceptions:
        raise source.SourceException(json.dumps(exceptions))
    return sources


def create_source_from_json(config: dict) -> source.Source:
    source.manager.validate_config_for_create(config)
    source_ = source.manager.create_source_obj(config['name'], config['type'])
    source_.set_config(config['config'])
    source.validator.validate(source_)
    source.repository.save(source_)
    return source_


def edit_using_json(configs: list) -> List[source.Source]:
    if not isinstance(configs, list):
        raise ValueError(f'Provided data must be a list of configs, {type(configs).__name__} provided instead')
    exceptions = {}
    sources = []
    for config in configs:
        try:
            source_ = edit_source_using_json(config)
            print(f"Source {config['name']} updated")
            sources.append(source_)
        except Exception as e:
            exceptions[config['name']] = f'{type(e).__name__}: {str(e)}'
    if exceptions:
        raise source.SourceException(json.dumps(exceptions))
    return sources


def edit_source_using_json(config: dict) -> source.Source:
    validate_config_for_edit(config)
    source_ = source.repository.get_by_name(config['name'])
    source_.set_config(config['config'])
    source.validator.validate(source_)
    source.repository.save(source_)
    pipeline.manager.update_source_pipelines(source_)
    return source_


def validate_configs_for_create(json_data: dict):
    schema = {
        'type': 'array',
        'items': source.json_schema
    }
    jsonschema.validate(json_data, schema)


def validate_config_for_create(json_data: dict):
    jsonschema.validate(json_data, source.json_schema)


def validate_config_for_edit(json_data: dict):
    schema = {
        'type': 'object',
        'properties': {
            'name': {'type': 'string', 'minLength': 1, 'maxLength': 100, 'enum': source.repository.get_all_names()},
            'config': {'type': 'object'}
        },
        'required': ['name', 'config']
    }
    jsonschema.validate(json_data, schema)


def extract_configs(file):
    try:
        configs = json.load(file)
        file.seek(0)
        return configs
    except json.decoder.JSONDecodeError as e:
        raise Exception(str(e))


def get_previous_source_config(source_type):
    try:
        pipelines_with_source = api_client.get_pipelines(order_by='CREATED', order='DESC', label=source_type)
        if len(pipelines_with_source) > 0:
            pipeline_obj = pipeline.repository.get_by_name(pipelines_with_source[-1]['pipelineId'])
            return pipeline_obj.source.config
    except source.SourceConfigDeprecated:
        pass
    return {}


def check_source_name(source_name: str):
    if source.repository.exists(source_name):
        raise SourceException(f"Source {source_name} already exists")
