import json
import jsonschema

from agent import pipeline
from agent.constants import ENV_PROD
from agent import source
from agent.streamsets_api_client import api_client

MAX_SAMPLE_RECORDS = 3


def create_source_obj(source_name: str, source_type: str) -> source.Source:
    return source.types[source_type](source_name, source_type, {})


def create_from_file(file):
    configs = extract_configs(file)
    source.manager.validate_configs_for_create(configs)

    exceptions = {}
    sources = []
    for config in configs:
        try:
            sources.append(
                source.manager.create_from_json(config)
            )
            # click.secho(f"Source {config['name']} created")
        except Exception as e:
            if not ENV_PROD:
                raise e
            exceptions[config['name']] = str(e)
    if exceptions:
        raise source.SourceException(json.dumps(exceptions))
    return sources


def edit_using_file(file):
    configs = extract_configs(file)
    source.manager.validate_configs_for_edit(configs)

    exceptions = {}
    for config in configs:
        try:
            source.manager.edit_using_json(config)
            # click.secho(f"Source {config['name']} updated")
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
    source_instance = source.manager.create_source_obj(config['name'], config['type'])
    source_instance.set_config(config['config'])
    source.validator.validate(source_instance)
    source.repository.create(source_instance)
    return source_instance


def edit_using_json(config: dict) -> source.Source:
    source_instance = source.repository.get(config['name'])
    source_instance.set_config(config['config'])
    source.validator.validate(source_instance)
    source.repository.update(source_instance)
    return source_instance


def validate_configs_for_create(json_data: dict):
    schema = {
        'type': 'array',
        'items': source.json_schema
    }
    jsonschema.validate(json_data, schema)


def validate_config_for_create(json_data: dict):
    jsonschema.validate(json_data, source.json_schema)


def validate_configs_for_edit(json_data: dict):
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
    jsonschema.validate(json_data, schema)


def validate_config_for_edit(json_data: dict):
    schema = {
        'type': 'object',
        'properties': {
            'name': {'type': 'string', 'minLength': 1, 'maxLength': 100, 'enum': source.repository.get_all()},
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
        # raise click.ClickException(str(e))


def get_previous_source_config(source_type):
    try:
        pipelines_with_source = api_client.get_pipelines(order_by='CREATED', order='DESC', label=source_type)
        if len(pipelines_with_source) > 0:
            pipeline_obj = pipeline.repository.get(pipelines_with_source[-1]['pipelineId'])
            return pipeline_obj.source.config
    except source.SourceConfigDeprecated:
        pass
    return {}
