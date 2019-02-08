import click
import json
import os
import urllib.parse

from .config_handler import PipelineConfigHandler
from ..source.cli import get_configs_list as list_sources, DATA_DIR as SOURCES_DIR
from ..streamsets_api_client import api_client, StreamSetsApiClientException
from datetime import datetime
from texttable import Texttable

DATA_DIR = os.path.join(os.environ['DATA_DIR'], 'pipelines')
TOKEN_FILE = os.path.join(os.environ['DATA_DIR'], 'anodot-token')

SDC_DATA_PATH = os.environ.get('SDC_DATA_PATH', '/sdc-data')
SDC_RESULTS_PATH = os.path.join(SDC_DATA_PATH, 'out')


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


def prompt_pipeline_config(config, advanced=False):
    config['measurement_name'] = click.prompt('Measurement name', type=click.STRING,
                                              default=config.get('measurement_name'))

    config['value'] = config.get('value', {})
    if advanced or config['value'].get('type') == 'constant':
        config['value']['value'] = click.prompt('Value (column name or constant value)', type=click.STRING,
                                                default=config['value'].get('value'))
        config['value']['type'] = click.prompt('Value type', type=click.Choice(['column', 'constant']),
                                               default=config['value'].get('type'))
    else:
        config['value']['type'] = 'column'
        config['value']['value'] = click.prompt('Value column name', type=click.STRING,
                                                default=config['value'].get('value'))

    config['target_type'] = click.prompt('Target type', type=click.Choice(['counter', 'gauge']),
                                         default=config.get('target_type', 'gauge'))

    config['timestamp'] = config.get('timestamp', {})
    config['timestamp']['name'] = click.prompt('Timestamp column name', type=click.STRING,
                                               default=config['timestamp'].get('name'))
    config['timestamp']['type'] = click.prompt('Timestamp column type',
                                               type=click.Choice(
                                                   ['string', 'datetime', 'unix', 'unix_ms']),
                                               default=config['timestamp'].get('type', 'unix'))

    if config['timestamp']['type'] == 'string':
        config['timestamp']['format'] = click.prompt('Timestamp format string', type=click.STRING,
                                                     default=config['timestamp'].get('format'))

    config['dimensions'] = config.get('dimensions', {})
    config['dimensions']['required'] = click.prompt('Required dimensions',
                                                    type=click.STRING,
                                                    value_proc=lambda x: x.split(),
                                                    default=config['dimensions'].get('required', []))
    config['dimensions']['optional'] = click.prompt('Optional dimensions',
                                                    type=click.STRING,
                                                    value_proc=lambda x: x.split(),
                                                    default=config['dimensions'].get('optional', []))

    return config


def get_http_destination():
    api_url = os.environ.get('ANODOT_API_URL', 'https://api.anodot.com')
    with open(TOKEN_FILE, 'r') as f:
        token = f.read()
    return {
        "config": {
            "conf.resourceUrl": urllib.parse.urljoin(api_url, f'api/v1/metrics?token={token}&protocol=anodot20')
        },
        "type": "http"
    }


@click.command()
@click.option('-a', '--advanced', is_flag=True)
def create(advanced):
    pipeline_config = dict()

    sources = list_sources()
    if len(sources) == 0:
        raise click.ClickException('No sources configs found. Use "agent source create"')

    if not os.path.isfile(TOKEN_FILE):
        raise click.ClickException('No anodot api token configured. Use "agent token"')

    default_source = sources[0] if len(sources) == 1 else None
    source_config_name = click.prompt('Choose source config', type=click.Choice(sources), default=default_source)
    with open(os.path.join(SOURCES_DIR, source_config_name + '.json'), 'r') as f:
        pipeline_config['source'] = json.load(f)

    destination_type = click.prompt('Choose destination', type=click.Choice(['http']),
                                           default='http')
    if destination_type == 'http':
        pipeline_config['destination'] = get_http_destination()

    pipeline_config['pipeline_id'] = click.prompt('Pipeline ID (must be unique)', type=click.STRING)

    pipeline_config = prompt_pipeline_config(pipeline_config, advanced)

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

    with open(os.path.join(DATA_DIR, pipeline_config['pipeline_id'] + '.json'), 'w') as f:
        json.dump(pipeline_config, f)

    click.secho('Created pipeline {}'.format(pipeline_config['pipeline_id']), fg='green')


@click.command()
@click.argument('pipeline_id', autocompletion=get_pipelines_ids_complete)
@click.option('-a', '--advanced', is_flag=True)
def edit(pipeline_id, advanced):
    with open(os.path.join(DATA_DIR, pipeline_id + '.json'), 'r') as f:
        pipeline_config = json.load(f)

    with open(os.path.join(SOURCES_DIR, pipeline_config['source']['name'] + '.json'), 'r') as f:
        pipeline_config['source'] = json.load(f)

    if pipeline_config['destination']['type'] == 'http':
        pipeline_config['destination'] = get_http_destination()

    pipeline_config = prompt_pipeline_config(pipeline_config, advanced)

    pipeline_obj = api_client.get_pipeline(pipeline_config['pipeline_id'])

    config_handler = PipelineConfigHandler(pipeline_config, pipeline_obj)
    new_config = config_handler.override_base_config()

    try:
        api_client.update_pipeline(pipeline_config['pipeline_id'], new_config)
    except StreamSetsApiClientException as e:
        click.secho(str(e), err=True, fg='red')
        return

    with open(os.path.join(DATA_DIR, pipeline_config['pipeline_id'] + '.json'), 'w') as f:
        json.dump(pipeline_config, f)

    click.secho('Updated pipeline {}'.format(pipeline_config['pipeline_id']), fg='green')


@click.command(name='list')
def list_pipelines():
    pipelines = api_client.get_pipelines()
    pipelines_status = api_client.get_pipelines_status()

    def get_row(item, statuses):
        return [item['title'], statuses[item['pipelineId']]['status'], item['pipelineId']]

    table = build_table(['Title', 'Status', 'ID'], pipelines, get_row, pipelines_status)

    click.echo(table.draw())


@click.command()
@click.argument('pipeline_id', autocompletion=get_pipelines_ids_complete)
def start(pipeline_id):
    try:
        api_client.start_pipeline(pipeline_id)
    except StreamSetsApiClientException as e:
        click.secho(str(e), err=True, fg='red')
        return
    click.echo('Pipeline starting')


@click.command()
@click.argument('pipeline_id', autocompletion=get_pipelines_ids_complete)
def stop(pipeline_id):
    try:
        api_client.stop_pipeline(pipeline_id)
    except StreamSetsApiClientException as e:
        click.secho(str(e), err=True, fg='red')
        return
    click.echo('Pipeline stopping')


@click.command()
@click.argument('pipeline_id', autocompletion=get_pipelines_ids_complete)
def delete(pipeline_id):
    try:
        api_client.delete_pipeline(pipeline_id)
        file_path = os.path.join(DATA_DIR, pipeline_id + '.json')
        os.remove(file_path)
    except StreamSetsApiClientException as e:
        click.secho(str(e), err=True, fg='red')
        return
    click.echo('Pipeline deleted')


@click.command()
@click.argument('pipeline_id', autocompletion=get_pipelines_ids_complete)
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
@click.argument('pipeline_id', autocompletion=get_pipelines_ids_complete)
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
@click.argument('pipeline_id', autocompletion=get_pipelines_ids_complete)
def reset(pipeline_id):
    try:
        api_client.reset_pipeline(pipeline_id)
    except StreamSetsApiClientException as e:
        click.secho(str(e), err=True, fg='red')
        return
    click.echo('Pipeline offset reset')


@click.group()
def pipeline():
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
