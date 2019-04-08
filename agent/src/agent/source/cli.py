import click
import json
import os

from .config_schema import sources_configs
from agent.streamsets_api_client import api_client
from agent.constants import PIPELINES_DIR, SOURCES_DIR


def get_previous_source_config(label):
    recent_pipeline_config = {}
    pipelines_with_source = api_client.get_pipelines(order_by='CREATED', order='DESC',
                                                     label=label)
    if len(pipelines_with_source) > 0:
        for filename in os.listdir(PIPELINES_DIR):
            if filename == pipelines_with_source[-1]['pipelineId'] + '.json':
                with open(os.path.join(PIPELINES_DIR, filename), 'r') as f:
                    recent_pipeline_config = json.load(f)['source']['config']
    return recent_pipeline_config


def get_configs(ctx, args, incomplete):
    configs = []
    for filename in os.listdir(SOURCES_DIR):
        if filename.endswith('.json') and incomplete in filename:
            configs.append(filename.replace('.json', ''))
    return configs


def get_configs_list():
    configs = []
    for filename in os.listdir(SOURCES_DIR):
        if filename.endswith('.json'):
            configs.append(filename.replace('.json', ''))
    return configs


@click.group()
def source():
    """
    Data sources management
    """
    pass


@click.command()
@click.option('-a', '--advanced', is_flag=True)
def create(advanced):
    """
    Create source
    """
    config = dict(config={})
    config['type'] = click.prompt('Choose source', type=click.Choice(sources_configs.keys()))
    config['name'] = click.prompt('Enter unique name for this source config', type=click.STRING)

    if os.path.isfile(os.path.join(SOURCES_DIR, config['name'] + '.json')):
        raise click.exceptions.ClickException('Source config with this name already exists')

    recent_pipeline_config = get_previous_source_config(config['type'])
    config['config'] = sources_configs[config['type']](recent_pipeline_config, advanced)

    with open(os.path.join(SOURCES_DIR, config['name'] + '.json'), 'w') as f:
        json.dump(config, f)

    click.secho('Source config created', fg='green')


@click.command()
@click.argument('name', autocompletion=get_configs)
@click.option('-a', '--advanced', is_flag=True)
def edit(name, advanced):
    """
    Edit source
    """
    with open(os.path.join(SOURCES_DIR, name + '.json'), 'r') as f:
        config = json.load(f)

    config['config'] = sources_configs[config['type']](config['config'], advanced)

    with open(os.path.join(SOURCES_DIR, name + '.json'), 'w') as f:
        json.dump(config, f)

    click.secho('Source config updated', fg='green')


@click.command(name='list')
def list_configs():
    """
    List all sources
    """
    for config in get_configs_list():
        click.echo(config)


@click.command()
@click.argument('name', autocompletion=get_configs)
def delete(name):
    """
    Delete source
    """
    file_path = os.path.join(SOURCES_DIR, name + '.json')
    if os.path.exists(file_path):
        os.remove(file_path)
        click.secho('Source config was deleted', fg='green')
    else:
        click.echo("The config does not exist")


source.add_command(create)
source.add_command(list_configs)
source.add_command(delete)
source.add_command(edit)
