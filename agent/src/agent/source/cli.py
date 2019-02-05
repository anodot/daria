import click
import json
import os

from .config_schema import sources_configs
from agent.pipeline.config_handler import get_previous_pipeline_config


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
def create():
    config = dict(config={})
    config['type'] = click.prompt('Choose source', type=click.Choice(['mongo']), default='mongo')
    config['name'] = click.prompt('Enter unique name for this source config', type=click.STRING)

    if os.path.isfile(os.path.join(DATA_DIR, config['name'] + '.json')):
        raise click.exceptions.ClickException('Source config with this name already exists')

    recent_pipeline_config = get_previous_pipeline_config(config['type'])
    for conf in sources_configs[config['type']]:
        default_value = recent_pipeline_config.get(conf['name'], conf.get('default'))
        if 'expression' in conf:
            default_value = conf['reverse_expression'](default_value)

        value = click.prompt(conf['prompt_string'], type=conf['type'], default=default_value)
        if 'expression' in conf:
            value = conf['expression'](value)

        config['config'][conf['name']] = value

    with open(os.path.join(DATA_DIR, config['name'] + '.json'), 'w') as f:
        json.dump(config, f)

    click.secho('Source config created', fg='green')


@click.command()
@click.argument('name', autocompletion=get_configs)
def edit(name):

    with open(os.path.join(DATA_DIR, name + '.json'), 'r') as f:
        config = json.load(f)

    for conf in sources_configs[config['type']]:
        default_value = config['config'][conf['name']]
        if 'expression' in conf:
            default_value = conf['reverse_expression'](default_value)

        value = click.prompt(conf['prompt_string'], type=conf['type'], default=default_value)
        if 'expression' in conf:
            value = conf['expression'](value)

        config['config'][conf['name']] = value

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
