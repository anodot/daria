import click
import json
import os
import random
import time

from .config import pipeline_configs
from ..source.cli import get_configs_list as list_sources
from ..streamsets_api_client import api_client, StreamSetsApiClientException
from agent.constants import DESTINATION_FILE, PIPELINES_DIR, SOURCES_DIR
from datetime import datetime
from pymongo import MongoClient
from texttable import Texttable


def get_previous_pipeline_config(label):
    recent_pipeline_config = {}
    pipelines_with_source = api_client.get_pipelines(order_by='CREATED', order='DESC',
                                                     label=label)
    if len(pipelines_with_source) > 0:
        for filename in os.listdir(PIPELINES_DIR):
            if filename == pipelines_with_source[-1]['pipelineId'] + '.json':
                with open(os.path.join(PIPELINES_DIR, filename), 'r') as f:
                    recent_pipeline_config = json.load(f)
    return recent_pipeline_config


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


@click.command()
@click.option('-a', '--advanced', is_flag=True)
def create(advanced):
    """
    Create pipeline
    """
    sources = list_sources()
    if len(sources) == 0:
        raise click.ClickException('No sources configs found. Use "agent source create"')

    if not os.path.isfile(DESTINATION_FILE):
        raise click.ClickException('Destination is not configured. Use "agent destination"')

    default_source = sources[0] if len(sources) == 1 else None
    source_config_name = click.prompt('Choose source config', type=click.Choice(sources), default=default_source)

    with open(os.path.join(SOURCES_DIR, source_config_name + '.json'), 'r') as f:
        source_config = json.load(f)

    pipeline_config = get_previous_pipeline_config(source_config['type'])
    pipeline_config['source'] = source_config
    destination_type = click.prompt('Choose destination', type=click.Choice(['http']),
                                    default='http')
    if destination_type == 'http':
        with open(DESTINATION_FILE, 'r') as f:
            pipeline_config['destination'] = json.load(f)

    pipeline_config['pipeline_id'] = click.prompt('Pipeline ID (must be unique)', type=click.STRING)

    pipeline_c = pipeline_configs[pipeline_config['source']['type']]
    pipeline_config.update(pipeline_c.prompt(pipeline_config, advanced))

    config_handler = pipeline_c.get_config_handler(pipeline_config)

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

    with open(os.path.join(PIPELINES_DIR, pipeline_config['pipeline_id'] + '.json'), 'w') as f:
        json.dump(pipeline_config, f)

    click.secho('Created pipeline {}'.format(pipeline_config['pipeline_id']), fg='green')


@click.command()
@click.argument('pipeline_id', autocompletion=get_pipelines_ids_complete)
@click.option('-a', '--advanced', is_flag=True)
def edit(pipeline_id, advanced):
    """
    Edit pipeline
    """
    with open(os.path.join(PIPELINES_DIR, pipeline_id + '.json'), 'r') as f:
        pipeline_config = json.load(f)

    with open(os.path.join(SOURCES_DIR, pipeline_config['source']['name'] + '.json'), 'r') as f:
        pipeline_config['source'] = json.load(f)

    if pipeline_config['destination']['type'] == 'http':
        with open(DESTINATION_FILE, 'r') as f:
            pipeline_config['destination'] = json.load(f)

    pipeline_c = pipeline_configs[pipeline_config['source']['type']]
    pipeline_config.update(pipeline_c.prompt(pipeline_config, advanced))

    pipeline_obj = api_client.get_pipeline(pipeline_config['pipeline_id'])

    config_handler = pipeline_c.get_config_handler(pipeline_config, pipeline_obj)
    new_config = config_handler.override_base_config()

    try:
        api_client.update_pipeline(pipeline_config['pipeline_id'], new_config)
    except StreamSetsApiClientException as e:
        click.secho(str(e), err=True, fg='red')
        return

    with open(os.path.join(PIPELINES_DIR, pipeline_config['pipeline_id'] + '.json'), 'w') as f:
        json.dump(pipeline_config, f)

    click.secho('Updated pipeline {}'.format(pipeline_config['pipeline_id']), fg='green')


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
        api_client.delete_pipeline(pipeline_id)
        file_path = os.path.join(PIPELINES_DIR, pipeline_id + '.json')
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
        api_client.reset_pipeline(pipeline_id)
    except StreamSetsApiClientException as e:
        click.secho(str(e), err=True, fg='red')
        return
    click.echo('Pipeline offset reset')


@click.command()
@click.argument('pipeline_id', autocompletion=get_pipelines_ids_complete)
def dummy(pipeline_id):
    """
    Generate dummy data based on pipeline's config. (Works only for mongo - http pipelines)
    """
    with open(os.path.join(PIPELINES_DIR, pipeline_id + '.json'), 'r') as f:
        pipeline_config = json.load(f)
    if pipeline_config['timestamp']['type'] == 'string':
        click.secho('Pipelines with string timestamp type are not supported yet', err=True, fg='red')
        return

    value_range = None
    if pipeline_config['value']['type'] == 'column':
        value_range = click.prompt('Value range', type=click.STRING, value_proc=lambda x: x.split())

    dimensions = {}
    for d in pipeline_config['dimensions']['required'] + pipeline_config['dimensions']['optional']:
        dimensions_values = click.prompt(f'Values for {d}', type=click.STRING, value_proc=lambda x: x.split(),
                                         default=[])
        if len(dimensions_values) > 0:
            dimensions[d] = dimensions_values

    batch_size = click.prompt('Number of records per minute', type=click.IntRange(min=1, max=10000))

    click.secho('Generating records...', fg='green')

    it_wait_time = 0.1
    interval = int(60 * (1 // it_wait_time))
    batch_size_ps = batch_size // interval

    mongo = pipeline_config['source']['config']['configBean.mongoConfig.connectionString'].replace('mongodb://', '')
    user_pass = ''
    if pipeline_config['source']['config']['configBean.mongoConfig.username'] != '':
        user_pass = pipeline_config['source']['config']['configBean.mongoConfig.username'] + ':' + \
                    pipeline_config['source']['config']['configBean.mongoConfig.password'] + '@'
    auth_source = ''
    if pipeline_config['source']['config']['configBean.mongoConfig.authSource'] != '':
        auth_source = '/' + pipeline_config['source']['config']['configBean.mongoConfig.authSource']
    client = MongoClient('mongodb://' + user_pass + mongo + auth_source)

    db = client[pipeline_config['source']['config']['configBean.mongoConfig.database']]
    collection = db[pipeline_config['source']['config']['configBean.mongoConfig.collection']]
    while True:

        batch_start = time.time()
        for i in range(interval):
            start_time = time.time()
            for j in range(batch_size_ps):
                document = {'target_type': pipeline_config['target_type']}
                if value_range:
                    document[pipeline_config['value']['value']] = random.randint(int(value_range[0]),
                                                                                 int(value_range[1]))
                if pipeline_config['timestamp']['name'] != '_id':
                    if pipeline_config['timestamp']['type'] == 'unix':
                        document[pipeline_config['timestamp']['name']] = int(time.time())
                    elif pipeline_config['timestamp']['type'] == 'unix_ms':
                        document[pipeline_config['timestamp']['name']] = int(time.time() * 1000)
                    elif pipeline_config['timestamp']['type'] == 'datetime':
                        document[pipeline_config['timestamp']['name']] = datetime.now()
                for key, val in dimensions.items():
                    document[key] = random.choice(val)

                collection.insert_one(document)
            time.sleep(max(it_wait_time - (time.time() - start_time), 0))
        print(batch_size_ps, time.time() - batch_start)


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
pipeline.add_command(dummy)
