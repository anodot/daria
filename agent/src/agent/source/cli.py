import click
import json

from .. import source, pipeline
from agent.constants import ENV_PROD
from agent.destination import HttpDestination
from agent.streamsets_api_client import api_client
from agent.tools import infinite_retry
from jsonschema import validate, ValidationError, SchemaError


def get_previous_source_config(label):
    pipelines_with_source = api_client.get_pipelines(order_by='CREATED', order='DESC',
                                                     label=label)
    if len(pipelines_with_source) > 0:
        pipeline_obj = pipeline.load_object(pipelines_with_source[-1]['pipelineId'])
        return pipeline_obj.source.config
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
    if source.Source.exists(source_name):
        raise click.UsageError(f"Source config {source_name} already exists")
    return source_name


def parse_config(file):
    try:
        return json.load(file)
    except json.decoder.JSONDecodeError as e:
        raise click.ClickException(str(e))


def create_with_file(file):
    data = parse_config(file)
    json_schema = {
        'type': 'array',
        'items': {
            'type': 'object',
            'properties': {
                'type': {'type': 'string', 'enum': list(source.get_types())},
                'name': {'type': 'string', 'minLength': 1, 'maxLength': 100},
                'config': {'type': 'object'}
            },
            'required': ['type', 'name', 'config']
        }
    }
    validate(data, json_schema)

    exceptions = {}
    for item in data:
        try:
            source_instance = source.create_object(item['name'], item['type'])
            source_instance.set_config(item['config'])
            source_instance.validate()
            source_instance.create()
            click.secho(f"Source {item['name']} created")
        except Exception as e:
            if not ENV_PROD:
                raise e
            exceptions[item['name']] = str(e)
    if exceptions:
        raise source.SourceException(json.dumps(exceptions))


def edit_with_file(file):

    data = parse_config(file)
    json_schema = {
        'type': 'array',
        'items': {
            'type': 'object',
            'properties': {
                'name': {'type': 'string', 'minLength': 1, 'maxLength': 100, 'enum': source.get_list()},
                'config': {'type': 'object'}
            },
            'required': ['name', 'config']
        }
    }
    validate(data, json_schema)

    exceptions = {}
    for item in data:
        try:
            source_instance = source.load_object(item['name'])
            source_instance.set_config(item['config'])
            source_instance.validate()
            source_instance.save()
            click.secho(f"Source {item['name']} edited")
            for pipeline_obj in pipeline.get_pipelines(source_name=item['name']):
                pipeline.PipelineManager(pipeline_obj).update()
                print(f'Pipeline {pipeline_obj.id} updated')
        except Exception as e:
            exceptions[item['name']] = str(e)
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
            create_with_file(file)
            return
        except (source.SourceException, ValidationError, SchemaError) as e:
            raise click.ClickException(str(e))

    source_type = click.prompt('Choose source', type=click.Choice(source.types)).strip()
    source_name = prompt_source_name()

    try:
        source_instance = source.create_object(source_name, source_type)
        recent_pipeline_config = get_previous_source_config(source_type)
        source_instance.set_config(source_instance.prompt(recent_pipeline_config, advanced))

        source_instance.create()
    except source.SourceException as e:
        raise click.ClickException(str(e))

    click.secho('Source config created', fg='green')


@click.command()
@click.argument('name', autocompletion=source.autocomplete, required=False)
@click.option('-a', '--advanced', is_flag=True)
@click.option('-f', '--file', type=click.File())
def edit(name, advanced, file):
    """
    Edit source
    """
    if not file and not name:
        raise click.UsageError('Specify source name or file path')

    if file:
        try:
            edit_with_file(file)
            return
        except (source.SourceException, ValidationError, SchemaError) as e:
            raise click.UsageError(str(e))

    source_instance = source.load_object(name)

    try:
        source_instance.set_config(source_instance.prompt(source_instance.config, advanced=advanced))
        source_instance.save()
    except source.SourceException as e:
        raise click.UsageError(str(e))

    click.secho('Source config updated', fg='green')

    for pipeline_obj in pipeline.get_pipelines(source_name=name):
        pipeline.PipelineManager(pipeline_obj).update()
        print(f'Pipeline {pipeline_obj.id} updated')


@click.command(name='list')
def list_configs():
    """
    List all sources
    """
    for config in source.get_list():
        click.echo(config)


@click.command()
@click.argument('name', autocompletion=source.autocomplete)
def delete(name):
    """
    Delete source
    """
    source_instance = source.load_object(name)

    try:
        source_instance.delete()
    except source.SourceException as e:
        raise click.ClickException(str(e))


source_group.add_command(create)
source_group.add_command(list_configs)
source_group.add_command(delete)
source_group.add_command(edit)
