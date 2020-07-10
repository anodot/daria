import json

import jsonschema

from agent import pipeline
from agent.constants import MONITORING_SOURCE_NAME, ENV_PROD
from agent import source
from agent.streamsets_api_client import api_client


def create_object(name: str, source_type: str) -> source.Source:
    if name == MONITORING_SOURCE_NAME:
        return source.MonitoringSource(MONITORING_SOURCE_NAME, source.TYPE_MONITORING, {})

    if source_type not in source.types:
        raise ValueError(f'{source_type} isn\'t supported')
    return source.types[source_type](name, source_type, {})


def create_from_file(file):
    configs = extract_configs(file)
    source.manager.validate_json_for_create(configs)

    exceptions = {}
    sources = []
    for config in configs:
        try:
            sources.append(
                source.manager.create_from_json(config)
            )
            click.secho(f"Source {config['name']} created")
        except Exception as e:
            if not ENV_PROD:
                raise e
            exceptions[config['name']] = str(e)
    if exceptions:
        raise source.SourceException(json.dumps(exceptions))
    return sources


def edit_using_file(file):
    configs = extract_configs(file)
    source.manager.validate_json_for_edit(configs)

    exceptions = {}
    for config in configs:
        try:
            source.manager.edit_using_json(config)
            click.secho(f"Source {config['name']} updated")
            for pipeline_obj in pipeline.repository.get_by_source(config['name']):
                try:
                    pipeline.manager.update(pipeline_obj)
                except pipeline.pipeline.PipelineException as e:
                    print(str(e))
                    continue
                print(f'Pipeline {pipeline_obj.id} updated')
        except Exception as e:
            exceptions[config['name']] = str(e)
    if exceptions:
        raise source.SourceException(json.dumps(exceptions))


def create_from_json(config: dict) -> source.Source:
    source_instance = create_object(config['name'], config['type'])
    source_instance.set_config(config['config'])
    source_instance.validate()
    source.repository.create(source_instance)
    return source_instance


def edit_using_json(config: dict) -> source.Source:
    source_instance = source.repository.get(config['name'])
    source_instance.set_config(config['config'])
    source_instance.validate()
    source.repository.update(source_instance)
    return source_instance


def validate_json_for_create(json: dict):
    schema = {
        'type': 'array',
        'items': source.json_schema
    }
    jsonschema.validate(json, schema)


def validate_json_for_edit(json: dict):
    schema = {
        'type': 'array',
        'items': {
            'type': 'object',
            'properties': {
                'name': {'type': 'string', 'minLength': 1, 'maxLength': 100, 'enum': source.repository.get_all()},
                'config': {'type': 'object'}
            },
            'required': ['name', 'config']
        }
    }
    jsonschema.validate(json, schema)


def extract_configs(file):
    try:
        configs = json.load(file)
        file.seek(0)
        return configs
    except json.decoder.JSONDecodeError as e:
        raise click.ClickException(str(e))


def get_previous_source_config(source_type):
    try:
        pipelines_with_source = api_client.get_pipelines(order_by='CREATED', order='DESC', label=source_type)
        if len(pipelines_with_source) > 0:
            pipeline_obj = pipeline.repository.get(pipelines_with_source[-1]['pipelineId'])
            return pipeline_obj.source.config
    except source.SourceConfigDeprecated:
        pass
    return {}
