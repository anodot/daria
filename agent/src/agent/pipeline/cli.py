import click
import json
import re

from .pipeline_manager import PipelineManager, delete_pipeline, stop_pipeline, force_stop_pipeline
from .. import pipeline, source
from ..streamsets_api_client import api_client, StreamSetsApiClientException
from agent.destination.http import HttpDestination
from agent.tools import infinite_retry
from jsonschema import validate, ValidationError
from datetime import datetime
from texttable import Texttable


def get_previous_pipeline_config(label):
    try:
        pipelines_with_source = api_client.get_pipelines(order_by='CREATED', order='DESC',
                                                         label=label)
        if len(pipelines_with_source) > 0:
            pipeline_obj = pipeline.load_object(pipelines_with_source[-1]['pipelineId'])
            return pipeline_obj.to_dict()
    except source.SourceConfigDeprecated:
        pass
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
                'source': {'type': 'string', 'enum': source.get_list()},
                'pipeline_id': {'type': 'string', 'minLength': 1, 'maxLength': 100}
            },
            'required': ['source', 'pipeline_id']
        }
    }
    validate(data, json_schema)

    for item in data:
        pipeline_manager = PipelineManager(pipeline.create_object(item['pipeline_id'], item['source']))
        pipeline_manager.load_config(item)
        pipeline_manager.create()

        click.secho('Created pipeline {}'.format(item['pipeline_id']), fg='green')


@infinite_retry
def prompt_pipeline_id():
    pipeline_id = click.prompt('Pipeline ID (must be unique)', type=click.STRING).strip()
    if pipeline.Pipeline.exists(pipeline_id):
        raise click.UsageError(f"Pipeline {pipeline_id} already exists")
    return pipeline_id


@click.command()
@click.option('-a', '--advanced', is_flag=True)
@click.option('-f', '--file', type=click.File())
def create(advanced, file):
    check_destination()
    sources = source.get_list()
    check_sources(sources)

    if file:
        create_using_file(file)
        return

    source_config_name = click.prompt('Choose source config', type=click.Choice(sources),
                                      default=get_default_source(sources))
    pipeline_id = prompt_pipeline_id()
    pipeline_manager = PipelineManager(pipeline.create_object(pipeline_id, source_config_name))
    previous_config = get_previous_pipeline_config(pipeline_manager.pipeline.source.type)
    # the rest of the data is prompted in the .prompt() call
    pipeline_manager.prompt(previous_config, advanced)
    pipeline_manager.create()

    click.secho('Created pipeline {}'.format(pipeline_id), fg='green')

    if click.confirm('Would you like to see the result data preview?', default=True):
        pipeline_manager.show_preview()
        print('To change the config use `agent pipeline edit`')


def create_using_file(file):
    try:
        create_multiple(file)
    except (StreamSetsApiClientException, ValidationError) as e:
        raise click.ClickException(str(e))


def check_sources(sources):
    if len(sources) == 0:
        raise click.ClickException('No sources configs found. Use "agent source create"')


def check_destination():
    if not HttpDestination.exists():
        raise click.ClickException('Destination is not configured. Use "agent destination"')


def get_default_source(sources):
    return sources[0] if len(sources) == 1 else None


def get_pipelines_from_file(file):
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
    return data


def edit_multiple(file):
    for item in get_pipelines_from_file(file):
        try:
            pipeline_manager = PipelineManager(pipeline.load_object(item['pipeline_id']))
            pipeline_manager.load_config(item, edit=True)
            pipeline_manager.update()
        except pipeline.PipelineNotExistsException:
            raise click.UsageError(f'{item["pipeline_id"]} does not exist')

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

    try:
        pipeline_manager = PipelineManager(pipeline.load_object(pipeline_id))
        pipeline_manager.prompt(pipeline_manager.pipeline.to_dict(), advanced=advanced)
        pipeline_manager.update()

        click.secho('Updated pipeline {}'.format(pipeline_id), fg='green')
        if click.confirm('Would you like to see the result data preview?', default=True):
            pipeline_manager.show_preview()
            print('To change the config use `agent pipeline edit`')
    except pipeline.PipelineNotExistsException:
        raise click.UsageError(f'{pipeline_id} does not exist')


@click.command()
@click.argument('pipeline_id', autocompletion=get_pipelines_ids_complete)
@click.option('--enable/--disable', default=False)
def destination_logs(pipeline_id, enable):
    """
    Enable destination response logs for a pipeline (for debugging purposes only)
    """

    pipeline_manager = PipelineManager(pipeline.load_object(pipeline_id))
    pipeline_manager.enable_destination_logs(enable)

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
@click.argument('pipeline_id', autocompletion=get_pipelines_ids_complete, required=False)
@click.option('-f', '--file', type=click.File())
def start(pipeline_id, file):
    """
    Start pipeline
    """

    if not file and not pipeline_id:
        raise click.UsageError('Specify pipeline id or file')

    pipeline_ids = [item['pipeline_id'] for item in get_pipelines_from_file(file)] if file else [pipeline_id]

    for idx in pipeline_ids:
        try:
            pipeline_manager = PipelineManager(pipeline.load_object(idx))
            click.echo(f'Pipeline {idx} is starting...')
            pipeline_manager.start()
        except (StreamSetsApiClientException, pipeline.PipelineException) as e:
            click.secho(str(e), err=True, fg='red')
            continue


@click.command()
@click.argument('pipeline_id', autocompletion=get_pipelines_ids_complete, required=False)
@click.option('-f', '--file', type=click.File())
def stop(pipeline_id, file):
    """
    Stop pipeline
    """

    if not file and not pipeline_id:
        raise click.UsageError('Specify pipeline id or file')

    pipeline_ids = [item['pipeline_id'] for item in get_pipelines_from_file(file)] if file else [pipeline_id]

    for idx in pipeline_ids:
        try:
            stop_pipeline(idx)
            click.secho(f'Pipeline {idx} is stopped', fg='green')
        except (StreamSetsApiClientException, pipeline.PipelineException) as e:
            click.secho(str(e), err=True, fg='red')
            continue


@click.command()
@click.argument('pipeline_id', autocompletion=get_pipelines_ids_complete)
def force_stop(pipeline_id):
    """
    Force stop pipeline
    """
    try:
        click.echo('Force pipeline stopping...')
        force_stop_pipeline(pipeline_id)
        click.secho('Pipeline is stopped', fg='green')
    except (StreamSetsApiClientException, pipeline.PipelineException) as e:
        click.secho(str(e), err=True, fg='red')
        return


@click.command()
@click.argument('pipeline_id', autocompletion=get_pipelines_ids_complete, required=False)
@click.option('-f', '--file', type=click.File())
def delete(pipeline_id, file):
    """
    Delete pipeline
    """
    if not file and not pipeline_id:
        raise click.UsageError('Specify pipeline id or file')

    pipeline_ids = [item['pipeline_id'] for item in get_pipelines_from_file(file)] if file else [pipeline_id]

    for idx in pipeline_ids:
        try:
            delete_pipeline(idx)
            click.echo(f'Pipeline {idx} deleted')
        except (StreamSetsApiClientException, pipeline.PipelineException) as e:
            click.secho(str(e), err=True, fg='red')
            continue


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

    def get_timestamp(utc_time):
        return datetime.utcfromtimestamp(utc_time / 1000).strftime('%Y-%m-%d %H:%M:%S')

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

    for name, counter in metrics['counters'].items():
        stage_name = re.search('stage\.(.+)\.errorRecords\.counter', name)
        if counter['count'] == 0 or not stage_name:
            continue

        click.echo('')
        click.secho('=== ERRORS ===', fg='red')
        for error in api_client.get_pipeline_errors(pipeline_id, stage_name.group(1)):
            click.echo(f'{get_timestamp(error["header"]["errorTimestamp"])} - {error["header"]["errorMessage"]}')

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
        return [get_timestamp(item['timeStamp']), item['status'], message, metrics_str]

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
        pipeline_manager = PipelineManager(pipeline.load_object(pipeline_id))
        pipeline_manager.reset()

    except StreamSetsApiClientException as e:
        click.secho(str(e), err=True, fg='red')
        return
    click.echo('Pipeline offset reset')


@click.group(name='pipeline')
def pipeline_group():
    """
    Pipelines management
    """
    pass


pipeline_group.add_command(create)
pipeline_group.add_command(list_pipelines)
pipeline_group.add_command(start)
pipeline_group.add_command(stop)
pipeline_group.add_command(force_stop)
pipeline_group.add_command(delete)
pipeline_group.add_command(logs)
pipeline_group.add_command(info)
pipeline_group.add_command(reset)
pipeline_group.add_command(edit)
pipeline_group.add_command(destination_logs)
