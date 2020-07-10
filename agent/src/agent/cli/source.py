import os
import click

from agent import pipeline
from agent import source
from agent.destination import HttpDestination
from agent.tools import infinite_retry
from jsonschema import ValidationError, SchemaError


def autocomplete(ctx, args, incomplete):
    configs = []
    for filename in os.listdir(source.repository.SOURCE_DIRECTORY):
        if filename.endswith('.json') and incomplete in filename:
            configs.append(filename.replace('.json', ''))
    return configs


@click.group(name='source')
def source_group():
    """
    Data sources management
    """
    pass


@click.command(name='list')
def list_sources():
    """
    List all sources
    """
    for config in source.repository.get_all():
        click.echo(config)


# todo move up
@click.command()
@click.option('-a', '--advanced', is_flag=True)
@click.option('-f', '--file', type=click.File())
def create(advanced, file):
    if not HttpDestination.exists():
        raise click.ClickException('Destination is not configured. Please use `agent destination` command')
    if file:
        try:
            sources = source.manager.create_from_file(file)
            click.secho(f"Created sources: {', '.join(map(lambda x: x.name, sources))}")
            return
        except (ValidationError, SchemaError) as e:
            raise click.ClickException(str(e))

    source_type = click.prompt('Choose source', type=click.Choice(source.types)).strip()
    source_name = prompt_source_name()

    source_instance = source.manager.create_object(source_name, source_type)

    # todo refactor set_config
    source_instance.set_config(source_instance.prompt(source.manager.get_previous_source_config(source_type), advanced))
    source.repository.create(source_instance)

    click.secho('Source config created', fg='green')


@click.command()
@click.argument('name', autocompletion=autocomplete, required=False)
@click.option('-a', '--advanced', is_flag=True)
@click.option('-f', '--file', type=click.File())
def edit(name, advanced, file):
    if not file and not name:
        raise click.UsageError('Specify source name or file path')

    if file:
        try:
            source.manager.edit_using_file(file)
            return
        except (ValidationError, SchemaError) as e:
            raise click.UsageError(str(e))

    source_instance = source.repository.get(name)
    # todo refactor set_config
    source_instance.set_config(source_instance.prompt(source_instance.config, advanced=advanced))
    source.repository.update(source_instance)

    click.secho('Source config updated', fg='green')

    for pipeline_obj in pipeline.repository.get_by_source(name):
        try:
            pipeline.manager.update(pipeline_obj)
        except pipeline.pipeline.PipelineException as e:
            print(str(e))
            continue
        print(f'Pipeline {pipeline_obj.id} updated')


@click.command()
@click.argument('name', autocompletion=autocomplete)
def delete(name):
    """
    Delete source
    """
    source.repository.delete_by_name(name)


@infinite_retry
def prompt_source_name():
    source_name = click.prompt('Enter unique name for this source config', type=click.STRING).strip()
    if source.repository.exists(source_name):
        raise click.UsageError(f"Source config {source_name} already exists")
    return source_name


source_group.add_command(create)
source_group.add_command(list_sources)
source_group.add_command(delete)
source_group.add_command(edit)
