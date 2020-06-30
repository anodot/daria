import os
import click
import json

from agent import source, pipeline
from agent.constants import ENV_PROD
from agent.destination import HttpDestination
from agent.pipeline import manager
from agent.repository import source_repository, pipeline_repository
from agent.streamsets_api_client import api_client
from agent.tools import infinite_retry
from jsonschema import ValidationError, SchemaError


def autocomplete(ctx, args, incomplete):
    configs = []
    for filename in os.listdir(source.source_repository.SOURCE_DIRECTORY):
        if filename.endswith('.json') and incomplete in filename:
            configs.append(filename.replace('.json', ''))
    return configs


def get_previous_source_config(label):
    try:
        pipelines_with_source = api_client.get_pipelines(order_by='CREATED', order='DESC',
                                                         label=label)
        if len(pipelines_with_source) > 0:
            pipeline_obj = pipeline_repository.get(pipelines_with_source[-1]['pipelineId'])
            return pipeline_obj.source.config
    except source.SourceConfigDeprecated:
        pass
    return {}


@click.group(name='source')
def source_group():
    """
    Data sources management
    """
    pass


@infinite_retry
def prompt_source_name():
    source_name = click.prompt('Enter unique name for this source config', type=click.STRING).strip()
    if source_repository.exists(source_name):
        raise click.UsageError(f"Source config {source_name} already exists")
    return source_name


def extract_configs(file):
    try:
        configs = json.load(file)
        file.seek(0)
        return configs
    except json.decoder.JSONDecodeError as e:
        raise click.ClickException(str(e))


def create_from_file(file):
    configs = extract_configs(file)
    source.validate_json_for_create(configs)

    exceptions = {}
    for config in configs:
        try:
            source.create_from_json(config)
            click.secho(f"Source {config['name']} created")
        except Exception as e:
            if not ENV_PROD:
                raise e
            exceptions[config['name']] = str(e)
    if exceptions:
        raise source.SourceException(json.dumps(exceptions))


def edit_using_file(file):
    configs = extract_configs(file)
    source.validate_json_for_edit(configs)

    exceptions = {}
    for config in configs:
        try:
            source.edit_using_json(config)
            click.secho(f"Source {config['name']} updated")
            for pipeline_obj in pipeline_repository.get_by_source(config['name']):
                try:
                    manager.PipelineManager(pipeline_obj).update()
                except pipeline.pipeline.PipelineException as e:
                    print(str(e))
                    continue
                print(f'Pipeline {pipeline_obj.id} updated')
        except Exception as e:
            exceptions[config['name']] = str(e)
    if exceptions:
        raise source.SourceException(json.dumps(exceptions))


@click.command()
@click.option('-a', '--advanced', is_flag=True)
@click.option('-f', '--file', type=click.File())
def create(advanced, file):
    """
    Create source
    """
    if not HttpDestination.exists():
        raise click.ClickException('Destination is not configured. Please use `agent destination` command')

    if file:
        try:
            create_from_file(file)
            return
        except (ValidationError, SchemaError) as e:
            raise click.ClickException(str(e))

    source_type = click.prompt('Choose source', type=click.Choice(source.types)).strip()
    source_name = prompt_source_name()

    source_instance = source.create_object(source_name, source_type)
    recent_pipeline_config = get_previous_source_config(source_type)

    # todo refactor set_config
    source_instance.set_config(source_instance.prompt(recent_pipeline_config, advanced))
    source_repository.create(source_instance)

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
            edit_using_file(file)
            return
        except (ValidationError, SchemaError) as e:
            raise click.UsageError(str(e))

    source_instance = source_repository.get(name)
    # todo refactor set_config
    source_instance.set_config(source_instance.prompt(source_instance.config, advanced=advanced))
    source_repository.update(source_instance)

    click.secho('Source config updated', fg='green')

    for pipeline_obj in pipeline_repository.get_by_source(name):
        try:
            manager.PipelineManager(pipeline_obj).update()
        except pipeline.pipeline.PipelineException as e:
            print(str(e))
            continue
        print(f'Pipeline {pipeline_obj.id} updated')


@click.command(name='list')
def list_sources():
    """
    List all sources
    """
    for config in source_repository.get_all():
        click.echo(config)


@click.command()
@click.argument('name', autocompletion=autocomplete)
def delete(name):
    """
    Delete source
    """
    source_repository.delete_by_name(name)


source_group.add_command(create)
source_group.add_command(list_sources)
source_group.add_command(delete)
source_group.add_command(edit)
