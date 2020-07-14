import os
import click

from agent import pipeline
from agent import source
from agent.destination import HttpDestination
from agent.tools import infinite_retry
from jsonschema import ValidationError, SchemaError
from . import source_builders


def autocomplete(ctx, args, incomplete):
    configs = []
    for filename in os.listdir(source.repository.SOURCE_DIRECTORY):
        if filename.endswith('.json') and incomplete in filename:
            configs.append(filename.replace('.json', ''))
    return configs


@click.group(name='source')
def source_group():
    pass


@click.command(name='list')
def list_sources():
    for config in source.repository.get_all():
        click.echo(config)


@click.command()
@click.option('-a', '--advanced', is_flag=True)
@click.option('-f', '--file', type=click.File())
def create(advanced, file):
    if not HttpDestination.exists():
        raise click.ClickException('Destination is not configured. Please use `agent destination` command')
    _create_from_file(file) if file else _prompt(advanced)


@click.command()
@click.argument('name', autocompletion=autocomplete, required=False)
@click.option('-a', '--advanced', is_flag=True)
@click.option('-f', '--file', type=click.File())
def edit(name, advanced, file):
    if not file and not name:
        raise click.UsageError('Specify source name or file path')
    _edit_using_file(file) if file else _prompt_edit(name, advanced)
    pipeline.manager.update_source_pipelines(name)


@click.command()
@click.argument('name', autocompletion=autocomplete)
def delete(name):
    source.repository.delete_by_name(name)


@infinite_retry
def _prompt_source_name():
    source_name = click.prompt('Enter unique name for this source config', type=click.STRING).strip()
    if source.repository.exists(source_name):
        raise click.UsageError(f"Source config {source_name} already exists")
    return source_name


def _create_from_file(file):
    try:
        sources = source.manager.create_from_file(file)
        click.secho(f"Created sources: {', '.join(map(lambda x: x.name, sources))}")
    except (ValidationError, SchemaError) as e:
        raise click.ClickException(str(e))


def _prompt(advanced: bool):
    source_type = _prompt_source_type()
    source_name = _prompt_source_name()
    builder = source_builders.get_builder(source_name, source_type)
    source.repository.create(
        builder.prompt(source.manager.get_previous_source_config(source_type), advanced)
    )
    click.secho('Source config created', fg='green')


def _edit_using_file(file):
    try:
        source.manager.edit_using_file(file)
        return
    except (ValidationError, SchemaError) as e:
        raise click.UsageError(str(e))


def _prompt_edit(name: str, advanced: bool):
    source_ = source.repository.get(name)
    builder = source_builders.get_builder(source_.name, source_.type)
    source.repository.update(
        builder.prompt(source_.config, advanced=advanced)
    )
    click.secho('Source config updated', fg='green')


def _prompt_source_type():
    return click.prompt('Choose source', type=click.Choice(source.types)).strip()


source_group.add_command(create)
source_group.add_command(list_sources)
source_group.add_command(delete)
source_group.add_command(edit)
