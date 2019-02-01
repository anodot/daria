import click
import json
import os

from .config_schema import destinations_configs
from agent.pipeline.config_handler import get_previous_pipeline_config


DATA_DIR = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'data')


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
def destination():
    pass


@click.command()
def create():
    config = dict(config={})

    config['type'] = click.prompt('Choose destination', type=click.Choice(['http']), default='http')
    config['name'] = click.prompt('Enter unique name for this source config', type=click.STRING)

    if os.path.isfile(os.path.join(DATA_DIR, config['name'] + '.json')):
        raise click.exceptions.ClickException('Destination config with this name already exists')

    recent_pipeline_config = get_previous_pipeline_config(config['type'], -1)
    for conf in destinations_configs[config['type']]:
        default_value = recent_pipeline_config.get(conf['name'], conf.get('default'))
        config['config'][conf['name']] = click.prompt(conf['prompt_string'],
                                                      type=conf['type'],
                                                      default=default_value)

    with open(os.path.join(DATA_DIR, config['name'] + '.json'), 'w') as f:
        json.dump(config, f)

    click.secho('Destination config created', fg='green')


@click.command()
@click.argument('name', autocompletion=get_configs, type=click.Choice(get_configs_list()))
def edit(name):

    with open(os.path.join(DATA_DIR, name + '.json'), 'r') as f:
        config = json.load(f)

    for conf in destinations_configs[config['type']]:
        config['config'][conf['name']] = click.prompt(conf['prompt_string'],
                                                      type=conf['type'],
                                                      default=config['config'][conf['name']])

    with open(os.path.join(DATA_DIR, name + '.json'), 'w') as f:
        json.dump(config, f)

    click.secho('Destination config updated', fg='green')


@click.command(name='list')
def list_configs():
    for config in get_configs_list():
        click.echo(config)


@click.command()
@click.argument('name', autocompletion=get_configs, type=click.Choice(get_configs_list()))
def delete(name):
    file_path = os.path.join(DATA_DIR, name + '.json')
    if os.path.exists(file_path):
        os.remove(file_path)
        click.secho('Source config was deleted', fg='green')
    else:
        click.echo('The config does not exist')


destination.add_command(create)
destination.add_command(list_configs)
destination.add_command(delete)
destination.add_command(edit)
