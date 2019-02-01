import click
import json
import jsonschema
import os

from .config_handler import PipelineConfigHandler
from .config_schema import config_schema
from ..destination.cli import get_configs_list as list_destinations, DATA_DIR as DESTINATIONS_DIR
from ..source.cli import get_configs_list as list_sources, DATA_DIR as SOURCES_DIR
from ..streamsets_api_client import api_client, StreamSetsApiClientException
from datetime import datetime
from texttable import Texttable


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


def prompt_pipeline_config():
    pipeline_config = dict()

    sources = list_sources()
    if len(sources) == 0:
        raise click.ClickException('No sources configs found. Use "pipeline source create"')

    destinations = list_destinations()
    if len(destinations) == 0:
        raise click.ClickException('No destinations configs found. Use "pipeline source create"')

    source_config_name = click.prompt('Choose source config', type=click.Choice(sources))
    with open(os.path.join(SOURCES_DIR, source_config_name + '.json'), 'r') as f:
        pipeline_config['source'] = json.load(f)

    destination_config_name = click.prompt('Choose destination config', type=click.Choice(destinations))
    with open(os.path.join(DESTINATIONS_DIR, destination_config_name + '.json'), 'r') as f:
        pipeline_config['destination'] = json.load(f)

    # pipeline config
    pipeline_config['pipeline_id'] = click.prompt('Pipeline ID (must be unique)', type=click.STRING)
    pipeline_config['measurement_name'] = click.prompt('Measurement name', type=click.STRING)

    pipeline_config['value'] = {}
    pipeline_config['value']['type'] = click.prompt('Value type', type=click.Choice(['column', 'constant']))
    pipeline_config['value']['value'] = click.prompt('Value (column name or constant value)', type=click.STRING)

    pipeline_config['target_type'] = click.prompt('Target type', type=click.Choice(['counter', 'gauge']),
                                                  default='gauge')

    pipeline_config['timestamp'] = {}
    pipeline_config['timestamp']['name'] = click.prompt('Timestamp column name', type=click.STRING)
    pipeline_config['timestamp']['type'] = click.prompt('Timestamp column type',
                                                        type=click.Choice(
                                                            ['string', 'datetime', 'unix', 'unix_ms']),
                                                        default='unix')
    if pipeline_config['timestamp']['type'] == 'string':
        pipeline_config['timestamp']['format'] = click.prompt('Timestamp format string', type=click.STRING)

    pipeline_config['dimensions'] = {}
    pipeline_config['dimensions']['required'] = click.prompt('Required dimensions',
                                                             type=click.STRING,
                                                             value_proc=lambda x: x.split(),
                                                             default=[])
    pipeline_config['dimensions']['optional'] = click.prompt('Optional dimensions',
                                                             type=click.STRING,
                                                             value_proc=lambda x: x.split(),
                                                             default=[])

    return pipeline_config


@click.command()
@click.option('-f', '--file', type=click.File('r'), default=None)
def create(file):
    if file:
        pipelines_configs = json.load(file)
    else:
        pipelines_configs = [prompt_pipeline_config()]

    try:
        jsonschema.validate(pipelines_configs, config_schema)
    except jsonschema.exceptions.ValidationError as e:
        click.secho('Validation error', fg='red')
        click.echo(str(e), err=True)
        return

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
        click.secho('Created pipeline {}'.format(pipeline_config['pipeline_id']), fg='green')


@click.command(name='list')
def list_pipelines():
    pipelines = api_client.get_pipelines()
    pipelines_status = api_client.get_pipelines_status()

    def get_row(item, statuses):
        return [item['title'], statuses[item['pipelineId']]['status'], item['pipelineId']]

    table = build_table(['Title', 'Status', 'ID'], pipelines, get_row, pipelines_status)

    click.echo(table.draw())


def get_pipelines_ids(ctx, args, incomplete):
    return [p['pipelineId'] for p in api_client.get_pipelines() if incomplete in p['pipelineId']]


@click.command()
@click.argument('pipeline_id', autocompletion=get_pipelines_ids)
def start(pipeline_id):
    try:
        api_client.start_pipeline(pipeline_id)
    except StreamSetsApiClientException as e:
        click.secho(str(e), err=True, fg='red')
        return
    click.echo('Pipeline starting')


@click.command()
@click.argument('pipeline_id', autocompletion=get_pipelines_ids)
def stop(pipeline_id):
    try:
        api_client.stop_pipeline(pipeline_id)
    except StreamSetsApiClientException as e:
        click.secho(str(e), err=True, fg='red')
        return
    click.echo('Pipeline stopping')


@click.command()
@click.argument('pipeline_id', autocompletion=get_pipelines_ids)
def delete(pipeline_id):
    try:
        api_client.delete_pipeline(pipeline_id)
    except StreamSetsApiClientException as e:
        click.secho(str(e), err=True, fg='red')
        return
    click.echo('Pipeline deleted')


@click.command()
@click.argument('pipeline_id', autocompletion=get_pipelines_ids)
@click.option('-l', '--lines', type=click.INT, default=10)
@click.option('-s', '--severity', type=click.Choice(['INFO', 'ERROR']), default=None)
def logs(pipeline_id, lines, severity):
    try:
        res = api_client.get_pipeline_logs(pipeline_id, severity=severity)
    except StreamSetsApiClientException as e:
        click.secho(str(e), err=True, fg='red')
        return

    def get_row(item):
        if 'message' not in item:
            return False
        return [item['timestamp'], item['severity'], item['category'], item['message']]

    table = build_table(['Timestamp', 'Severity', 'Category', 'Message'], res[-lines:], get_row)
    click.echo(table.draw())


@click.command()
@click.argument('pipeline_id', autocompletion=get_pipelines_ids)
@click.option('-l', '--lines', type=click.INT, default=10)
def info(pipeline_id, lines):
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
    table = build_table(['Timestamp', 'Status', 'Message', 'Records count'], history[:lines], get_row)
    click.echo('')
    click.secho('=== HISTORY ===', fg='green')
    click.echo(table.draw())


@click.command()
@click.argument('pipeline_id', autocompletion=get_pipelines_ids)
def reset(pipeline_id):
    try:
        api_client.reset_pipeline(pipeline_id)
    except StreamSetsApiClientException as e:
        click.secho(str(e), err=True, fg='red')
        return
    click.echo('Pipeline offset reset')


pipeline.add_command(create)
pipeline.add_command(list_pipelines)
pipeline.add_command(start)
pipeline.add_command(stop)
pipeline.add_command(delete)
pipeline.add_command(logs)
pipeline.add_command(info)
pipeline.add_command(reset)
