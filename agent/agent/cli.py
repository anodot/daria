import click
import json
import jsonschema
import os

from .pipeline_config_handler import PipelineConfigHandler
from .streamsets_api_client import StreamSetsApiClient
from texttable import Texttable

# https://json-schema.org/latest/json-schema-validation.html#rfc.section.6.5.3
pipeline_config_schema = {
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

api_client = StreamSetsApiClient(os.environ.get('STREAMSETS_USERNAME', 'admin'),
                                 os.environ.get('STREAMSETS_PASSWORD', 'admin'),
                                 os.environ.get('STREAMSETS_URL', 'http://localhost:18630'))


@click.group()
def pipeline():
    pass


@click.command()
@click.argument('config_file', type=click.File('r'))
def create(config_file):
    pipelines_configs = json.load(config_file)

    jsonschema.validate(pipelines_configs, pipeline_config_schema)

    for pipeline_config in pipelines_configs:
        config_handler = PipelineConfigHandler(pipeline_config)

        pipeline_obj = api_client.create_pipeline(pipeline_config['name'])

        new_config = config_handler.override_base_config(pipeline_obj['uuid'], pipeline_obj['title'])
        api_client.update_pipeline(pipeline_obj['pipelineId'], new_config)

        pipeline_rules = api_client.get_pipeline_rules(pipeline_obj['pipelineId'])
        new_rules = config_handler.override_base_rules(pipeline_rules['uuid'])
        api_client.update_pipeline_rules(pipeline_obj['pipelineId'], new_rules)
        click.echo('Created pipeline {}'.format(pipeline_config['name']))


@click.command(name='list')
def list_pipelines():
    pipelines = api_client.get_pipelines()
    pipelines_status = api_client.get_pipelines_status()

    table = Texttable()
    table.set_deco(Texttable.HEADER)
    header = ['Title', 'Status', 'ID']
    table.header(header)
    table.set_header_align(['l' for i in range(len(header))])

    max_widths = [0 for i in range(len(header))]
    for p in pipelines:
        row = [p['title'], pipelines_status[p['pipelineId']]['status'], p['pipelineId']]
        table.add_row(row)
        for idx, item in enumerate(row):
            max_widths[idx] = max(max_widths[idx], len(item))

    table.set_cols_width(max_widths)

    click.echo(table.draw())


@click.command()
@click.argument('pipeline_id')
def start(pipeline_id):
    api_client.start_pipeline(pipeline_id)
    click.echo('Pipeline starting')


@click.command()
@click.argument('pipeline_id')
def stop(pipeline_id):
    api_client.stop_pipeline(pipeline_id)
    click.echo('Pipeline stopping')


@click.command()
@click.argument('pipeline_id')
def delete(pipeline_id):
    api_client.delete_pipeline(pipeline_id)
    click.echo('Pipeline delete')


pipeline.add_command(create)
pipeline.add_command(list_pipelines)
pipeline.add_command(start)
pipeline.add_command(stop)
pipeline.add_command(delete)
