import click
import json
import jsonschema
import os

from .pipeline_config_handler import PipelineConfigHandler
from .streamsets_api_client import StreamSetsApiClient, StreamSetsApiClientException
from datetime import datetime
from texttable import Texttable

# https://json-schema.org/latest/json-schema-validation.html#rfc.section.6.5.3
pipeline_config_schema = {
    'type': 'array',
    'items': {
        'type': 'object',
        'properties': {
            'pipeline_id': {'type': 'string'},  # name of the pipeline
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
        'required': ['pipeline_id', 'source_name', 'source_config', 'measurement_name', 'value_field_name',
                     'dimensions', 'timestamp_field_name', 'destination_url']},
}

api_client = StreamSetsApiClient(os.environ.get('STREAMSETS_USERNAME', 'admin'),
                                 os.environ.get('STREAMSETS_PASSWORD', 'admin'),
                                 os.environ.get('STREAMSETS_URL', 'http://localhost:18630'))


def build_table(header, data, get_row, *args):
    """

    :param header: list
    :param data: list
    :param get_row: function - accepts item as first argument and *args; return false if row is needed to be skipped
    :param args: list
    :return:
    """
    table = Texttable()
    table.set_deco(Texttable.HEADER)
    table.header(header)
    table.set_header_align(['l' for i in range(len(header))])

    max_widths = [len(i) for i in header]
    for item in data:
        row = get_row(item, *args)
        if not row:
            continue
        table.add_row(row)
        for idx, i in enumerate(row):
            max_widths[idx] = max(max_widths[idx], len(i))

    table.set_cols_width([min(i, 100) for i in max_widths])
    return table


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

        try:
            pipeline_obj = api_client.create_pipeline(pipeline_config['pipeline_id'])
        except StreamSetsApiClientException as e:
            click.secho(str(e), err=True, fg='red')
            return

        new_config = config_handler.override_base_config(pipeline_obj['uuid'], pipeline_obj['title'])
        api_client.update_pipeline(pipeline_obj['pipelineId'], new_config)

        pipeline_rules = api_client.get_pipeline_rules(pipeline_obj['pipelineId'])
        new_rules = config_handler.override_base_rules(pipeline_rules['uuid'])
        api_client.update_pipeline_rules(pipeline_obj['pipelineId'], new_rules)
        click.echo('Created pipeline {}'.format(pipeline_config['pipeline_id']))


@click.command(name='list')
def list_pipelines():
    pipelines = api_client.get_pipelines()
    pipelines_status = api_client.get_pipelines_status()

    def get_row(item, statuses):
        return [item['title'], statuses[item['pipelineId']]['status'], item['pipelineId']]

    table = build_table(['Title', 'Status', 'ID'], pipelines, get_row, pipelines_status)

    click.echo(table.draw())


@click.command()
@click.argument('pipeline_id')
def start(pipeline_id):
    try:
        api_client.start_pipeline(pipeline_id)
    except StreamSetsApiClientException as e:
        click.secho(str(e), err=True, fg='red')
        return
    click.echo('Pipeline starting')


@click.command()
@click.argument('pipeline_id')
def stop(pipeline_id):
    try:
        api_client.stop_pipeline(pipeline_id)
    except StreamSetsApiClientException as e:
        click.secho(str(e), err=True, fg='red')
        return
    click.echo('Pipeline stopping')


@click.command()
@click.argument('pipeline_id')
def delete(pipeline_id):
    try:
        api_client.delete_pipeline(pipeline_id)
    except StreamSetsApiClientException as e:
        click.secho(str(e), err=True, fg='red')
        return
    click.echo('Pipeline delete')


@click.command()
@click.argument('pipeline_id')
@click.option('-s', '--severity', type=click.Choice(['INFO', 'ERROR']), default=None)
def logs(pipeline_id, severity):
    try:
        res = api_client.get_pipeline_logs(pipeline_id, severity=severity)
    except StreamSetsApiClientException as e:
        click.secho(str(e), err=True, fg='red')
        return

    def get_row(item):
        if 'message' not in item:
            return False
        return [item['timestamp'], item['severity'], item['category'], item['message']]

    table = build_table(['Timestamp', 'Severity', 'Category', 'Message'], res, get_row)
    click.echo(table.draw())


@click.command()
@click.argument('pipeline_id')
def info(pipeline_id):
    # status
    try:
        status = api_client.get_pipeline_status(pipeline_id)
    except StreamSetsApiClientException as e:
        click.secho(str(e), err=True, fg='red')
        return
    click.secho('=== STATUS ===', fg='green')
    click.echo('{status} {message}'.format(**status))

    # metrics
    metrics = json.loads(status['metrics']) if status['metrics'] else api_client.get_pipeline_metrics(pipeline_id)

    def get_metrics_string(metrics_obj):
        stats = {
            'in': metrics_obj['counters']['pipeline.batchInputRecords.counter']['count'],
            'out': metrics_obj['counters']['pipeline.batchOutputRecords.counter']['count'],
            'errors': metrics_obj['counters']['pipeline.batchErrorRecords.counter']['count'],
        }
        stats['errors_perc'] = stats['errors'] * 100 / stats['in'] if stats['in'] != 0 else 0
        return 'In: {in} - Out: {out} - Errors {errors} ({errors_perc:.1f}%)'.format(**stats)

    if metrics:
        click.echo(get_metrics_string(metrics))

    # issues
    pipeline_info = api_client.get_pipeline(pipeline_id)
    if pipeline_info['issues']['issueCount'] > 0:
        click.echo('')
        click.secho('=== ISSUES ===', bold=True, fg='red')
        for i in pipeline_info['issues']['pipelineIssues']:
            click.echo('{level} - {configGroup} - {configName} - {message}'.format(**i))
        for stage, issues in pipeline_info['issues']['stageIssues'].items():
            click.secho(stage, bold=True)
            for i in issues:
                click.echo('{level} - {configGroup} - {configName} - {message}'.format(**i))

    # history
    def get_row(item):
        metrics_str = get_metrics_string(json.loads(item['metrics'])) if item['metrics'] else ' '
        message = item['message'] if item['message'] else ' '
        return [datetime.utcfromtimestamp(item['timeStamp'] / 1000).strftime('%Y-%m-%d %H:%M:%S'), item['status'],
                message, metrics_str]

    history = api_client.get_pipeline_history(pipeline_id)
    table = build_table(['Timestamp', 'Status', 'Message', 'Records count'], history, get_row)
    click.echo('')
    click.secho('=== HISTORY ===', fg='green')
    click.echo(table.draw())


pipeline.add_command(create)
pipeline.add_command(list_pipelines)
pipeline.add_command(start)
pipeline.add_command(stop)
pipeline.add_command(delete)
pipeline.add_command(logs)
pipeline.add_command(info)
