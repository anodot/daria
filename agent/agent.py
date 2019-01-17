import time
import json
import jsonschema
import os

from . import config
from .logger import get_logger
from .pipeline_config_handler import PipelineConfigHandler
from .streamsets_api_client import StreamSetsApiClient

# https://json-schema.org/latest/json-schema-validation.html#rfc.section.6.5.3
schema = {
    'type': 'array',
    'items': {
        'type': 'object',
        'properties': {
            'name': {'type': 'string'},  # name of the pipeline
            'source_name': {'type': 'string', 'enum': ['mongo']},
            'source_config': {'type': 'object', 'properties': {
                'configBean.mongoConfig.connectionString': {'type': 'string'},
                'configBean.mongoConfig.username': {'type': 'string'},
                'configBean.mongoConfig.password': {'type': 'string'},
                'configBean.mongoConfig.database': {'type': 'string'},
                'configBean.mongoConfig.collection': {'type': 'string'},
                'configBean.mongoConfig.isCapped': {'type': 'boolean'},
                'configBean.mongoConfig.initialOffset': {'type': 'string'},  # date
            }},
            'measurement_name': {'type': 'string'},
            'value_field_name': {'type': 'string'},
            'timestamp_field_name': {'type': 'string'},  # unix timestamp
            'dimensions': {'type': 'array', 'items': {'type': 'string'}},
            'destination_url': {'type': 'string'},  # anodot metric api url with token and protocol params
        },
        'required': ['name', 'source_name', 'source_config', 'measurement_name', 'value_field_name', 'dimensions',
                     'timestamp_field_name', 'destination_url']},
}


def run():
    api_client = StreamSetsApiClient(config.streamsets_username, config.streamsets_password,
                                     config.streamsets_api_base_url)

    with open(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'pipeline_config_example.json'), 'r') as f:
        pipelines_configs = json.load(f)

    jsonschema.validate(pipelines_configs, schema)

    for pipeline_config in pipelines_configs:
        config_handler = PipelineConfigHandler(pipeline_config)

        pipeline = api_client.create_pipeline(pipeline_config['name'])

        new_config = config_handler.override_base_config(pipeline['uuid'], pipeline['title'])
        api_client.update_pipeline(pipeline['pipelineId'], new_config)

        pipeline_rules = api_client.get_pipeline_rules(pipeline['pipelineId'])
        new_rules = config_handler.override_base_rules(pipeline_rules['uuid'])
        api_client.update_pipeline_rules(pipeline['pipelineId'], new_rules)

        api_client.start_pipeline(pipeline['pipelineId'])

        time.sleep(13)
        api_client.stop_pipeline(pipeline['pipelineId'])
