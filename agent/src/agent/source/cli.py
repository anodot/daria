import click
import json
import os

from .config_schema import sources_configs
from agent.streamsets_api_client import api_client


def get_previous_pipeline_config(label, stage=0):
    recent_pipeline_config = {}
    pipelines_with_source = api_client.get_pipelines(order_by='CREATED', order='DESC',
                                                     label=label)
    if len(pipelines_with_source) > 0:
        recent_pipeline = api_client.get_pipeline(pipelines_with_source[0]['pipelineId'])
        for conf in recent_pipeline['stages'][stage]['configuration']:
            recent_pipeline_config[conf['name']] = conf['value']
    return recent_pipeline_config


DATA_DIR = os.path.join(os.environ['DATA_DIR'], 'sources')


def get_configs(ctx, args, incomplete):
    configs = []
    for filename in os.listdir(DATA_DIR):
        if filename.endswith('.json') and incomplete in filename:
            configs.append(filename.replace('.json', ''))
    return configs


def get_configs_list():
    configs = []
    for filename in os.listdir(DATA_DIR):
        if filename.endswith('.json'):
            configs.append(filename.replace('.json', ''))
    return configs


@click.group()
def source():
    pass


@click.command()
@click.option('-a', '--advanced', is_flag=True)
def create(advanced):
    config = dict(config={})
    config['type'] = click.prompt('Choose source', type=click.Choice(sources_configs.keys()))
    config['name'] = click.prompt('Enter unique name for this source config', type=click.STRING)

    if os.path.isfile(os.path.join(DATA_DIR, config['name'] + '.json')):
        raise click.exceptions.ClickException('Source config with this name already exists')

    recent_pipeline_config = get_previous_pipeline_config(config['type'])
    config['config'] = sources_configs[config['type']](recent_pipeline_config, advanced)

    with open(os.path.join(DATA_DIR, config['name'] + '.json'), 'w') as f:
        json.dump(config, f)

    click.secho('Source config created', fg='green')


@click.command()
@click.argument('name', autocompletion=get_configs)
@click.option('-a', '--advanced', is_flag=True)
def edit(name, advanced):

    with open(os.path.join(DATA_DIR, name + '.json'), 'r') as f:
        config = json.load(f)

    config['config'] = sources_configs[config['type']](config['config'], advanced)

    with open(os.path.join(DATA_DIR, name + '.json'), 'w') as f:
        json.dump(config, f)

    click.secho('Source config updated', fg='green')


@click.command(name='list')
def list_configs():
    for config in get_configs_list():
        click.echo(config)


@click.command()
@click.argument('name', autocompletion=get_configs)
def delete(name):
    file_path = os.path.join(DATA_DIR, name + '.json')
    if os.path.exists(file_path):
        os.remove(file_path)
        click.secho('Source config was deleted', fg='green')
    else:
        click.echo("The config does not exist")


source.add_command(create)
source.add_command(list_configs)
source.add_command(delete)
source.add_command(edit)
