import click
import json

from .pipeline import Pipeline, PipelineException
from ..source import Source
from ..streamsets_api_client import api_client, StreamSetsApiClientException
from agent.destination.http import HttpDestination
from jsonschema import validate, ValidationError
from datetime import datetime
from texttable import Texttable


def get_previous_pipeline_config(label):
    pipelines_with_source = api_client.get_pipelines(order_by='CREATED', order='DESC',
                                                     label=label)
    if len(pipelines_with_source) > 0:
        pipeline_obj = Pipeline(pipelines_with_source[-1]['pipelineId'])
        return pipeline_obj.load()
    return {}


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


def get_pipelines_ids_complete(ctx, args, incomplete):
    return [p['pipelineId'] for p in api_client.get_pipelines() if incomplete in p['pipelineId']]


def get_pipelines_ids():
    return [p['pipelineId'] for p in api_client.get_pipelines()]


def create_multiple(file):
    data = json.load(file)

    json_schema = {
        'type': 'array',
        'items': {
            'type': 'object',
            'properties': {
                'source': {'type': 'string', 'enum': Source.get_list()},
                'pipeline_id': {'type': 'string', 'minLength': 1, 'maxLength': 100}
            },
            'required': ['source', 'pipeline_id']
        }
    }
    validate(data, json_schema)

    for item in data:
        pipeline_obj = Pipeline(item['pipeline_id'], item['source'])
        pipeline_obj.load_client_data(item)
        pipeline_obj.create()

        click.secho('Created pipeline {}'.format(item['pipeline_id']), fg='green')


@click.command()
@click.option('-a', '--advanced', is_flag=True)
@click.option('-f', '--file', type=click.File())
def create(advanced, file):
    """
    Create pipeline
    """
    sources = Source.get_list()
    if len(sources) == 0:
        raise click.ClickException('No sources configs found. Use "agent source create"')

    if not HttpDestination.exists():
        raise click.ClickException('Destination is not configured. Use "agent destination"')

    if file:
        try:
            create_multiple(file)
        except (StreamSetsApiClientException, PipelineException, ValidationError) as e:
            raise click.ClickException(str(e))
        return

    default_source = sources[0] if len(sources) == 1 else None
    source_config_name = click.prompt('Choose source config', type=click.Choice(sources), default=default_source)

    pipeline_id = click.prompt('Pipeline ID (must be unique)', type=click.STRING)

    pipeline_obj = Pipeline(pipeline_id, source_config_name)
    pipeline_obj.prompt(get_previous_pipeline_config(pipeline_obj.source_type), advanced)
    pipeline_obj.create()

    click.secho('Created pipeline {}'.format(pipeline_id), fg='green')


def edit_multiple(file):
    data = json.load(file)

    json_schema = {
        'type': 'array',
        'items': {
            'type': 'object',
            'properties': {
                'pipeline_id': {'type': 'string', 'minLength': 1, 'maxLength': 100}
            },
            'required': ['pipeline_id']
        }
    }
    validate(data, json_schema)

    for item in data:
        pipeline_obj = Pipeline(item['pipeline_id'])
        pipeline_obj.load()
        pipeline_obj.load_client_data(item, edit=True)
        pipeline_obj.update()

        click.secho('Updated pipeline {}'.format(item['pipeline_id']), fg='green')


@click.command()
@click.argument('pipeline_id', autocompletion=get_pipelines_ids_complete, required=False)
@click.option('-a', '--advanced', is_flag=True)
@click.option('-f', '--file', type=click.File())
def edit(pipeline_id, advanced, file):
    """
    Edit pipeline
    """
    if not file and not pipeline_id:
        raise click.UsageError('Specify pipeline id or file')

    if file:
        edit_multiple(file)
        return

    pipeline_obj = Pipeline(pipeline_id)
    pipeline_obj.load()
    pipeline_obj.prompt(advanced=advanced)
    pipeline_obj.update()

    click.secho('Updated pipeline {}'.format(pipeline_id), fg='green')


@click.command()
@click.argument('pipeline_id', autocompletion=get_pipelines_ids_complete)
@click.option('--enable/--disable', default=False)
def destination_logs(pipeline_id, enable):
    """
    Enable destination response logs for a pipeline (for debugging purposes only)
    """

    pipeline_obj = Pipeline(pipeline_id)
    pipeline_obj.enable_destination_logs(enable)

    click.secho('Updated pipeline {}'.format(pipeline_id), fg='green')


@click.command(name='list')
def list_pipelines():
    """
    List all pipelines
    """
    pipelines = api_client.get_pipelines()
    pipelines_status = api_client.get_pipelines_status()

    def get_row(item, statuses):
        return [item['title'], statuses[item['pipelineId']]['status'], item['pipelineId']]

    table = build_table(['Title', 'Status', 'ID'], pipelines, get_row, pipelines_status)

    click.echo(table.draw())


@click.command()
@click.argument('pipeline_id', autocompletion=get_pipelines_ids_complete)
def start(pipeline_id):
    """
    Start pipeline
    """
    try:
        api_client.start_pipeline(pipeline_id)
    except StreamSetsApiClientException as e:
        click.secho(str(e), err=True, fg='red')
        return
    click.echo('Pipeline starting')


@click.command()
@click.argument('pipeline_id', autocompletion=get_pipelines_ids_complete)
def stop(pipeline_id):
    """
    Stop pipeline
    """
    try:
        api_client.stop_pipeline(pipeline_id)
    except StreamSetsApiClientException as e:
        click.secho(str(e), err=True, fg='red')
        return
    click.echo('Pipeline stopping')


@click.command()
@click.argument('pipeline_id', autocompletion=get_pipelines_ids_complete)
def delete(pipeline_id):
    """
    Delete pipeline
    """
    try:
        pipeline_obj = Pipeline(pipeline_id)
        pipeline_obj.delete()
    except StreamSetsApiClientException as e:
        click.secho(str(e), err=True, fg='red')
        return
    click.echo('Pipeline deleted')


@click.command()
@click.argument('pipeline_id', autocompletion=get_pipelines_ids_complete)
@click.option('-l', '--lines', type=click.INT, default=10)
@click.option('-s', '--severity', type=click.Choice(['INFO', 'ERROR']), default=None)
def logs(pipeline_id, lines, severity):
    """
    Show pipeline logs
    """
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
@click.argument('pipeline_id', autocompletion=get_pipelines_ids_complete)
@click.option('-l', '--lines', type=click.INT, default=10)
def info(pipeline_id, lines):
    """
    Show pipeline status, errors if any, statistics about amount of records sent
    """
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
@click.argument('pipeline_id', autocompletion=get_pipelines_ids_complete)
def reset(pipeline_id):
    """
    Reset pipeline's offset
    """
    try:
        pipeline_obj = Pipeline(pipeline_id)
        pipeline_obj.reset()

    except StreamSetsApiClientException as e:
        click.secho(str(e), err=True, fg='red')
        return
    click.echo('Pipeline offset reset')


@click.group()
def pipeline():
    """
    Pipelines management
    """
    pass


pipeline.add_command(create)
pipeline.add_command(list_pipelines)
pipeline.add_command(start)
pipeline.add_command(stop)
pipeline.add_command(delete)
pipeline.add_command(logs)
pipeline.add_command(info)
pipeline.add_command(reset)
pipeline.add_command(edit)
pipeline.add_command(destination_logs)
