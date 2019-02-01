import click
import json
import os

from .config_schema import sources_configs
from agent.pipeline.config_handler import get_previous_pipeline_config


DATA_DIR = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'data')


@click.group()
def source():
    pass


@click.command()
def create():
    config = dict(config={})
    config['name'] = click.prompt('Choose source', type=click.Choice(['mongo']))
    file_name = click.prompt('Enter unique name for this source config', type=click.STRING)

    recent_pipeline_config = get_previous_pipeline_config(config['name'])
    for conf in sources_configs[config['name']]:
        default_value = recent_pipeline_config.get(conf['name'], conf.get('default'))
        if 'expression' in conf:
            default_value = conf['reverse_expression'](default_value)

        value = click.prompt(conf['prompt_string'], type=conf['type'], default=default_value)
        if 'expression' in conf:
            value = conf['expression'](value)

        config['config'][conf['name']] = value

    with open(os.path.join(DATA_DIR, file_name + '.json'), 'w') as f:
        json.dump(config, f)

    click.secho('Source config created', fg='green')


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
