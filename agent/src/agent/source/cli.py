import click
import os

from .source import Source, SourceException
from agent.pipeline import Pipeline
from agent.streamsets_api_client import api_client


def get_previous_source_config(label):
    pipelines_with_source = api_client.get_pipelines(order_by='CREATED', order='DESC',
                                                     label=label)
    if len(pipelines_with_source) > 0:
        pipeline_obj = Pipeline(pipelines_with_source[-1]['pipelineId'])
        pipeline_obj.load()
        return pipeline_obj.config['source']['config']
    return {}


def sources_autocomplete(ctx, args, incomplete):
    configs = []
    for filename in os.listdir(Source.DIR):
        if filename.endswith('.json') and incomplete in filename:
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
    source_type = click.prompt('Choose source', type=click.Choice(Source.types))
    source_name = click.prompt('Enter unique name for this source config', type=click.STRING)

    source_instance = Source(source_name, source_type)

    try:
        recent_pipeline_config = get_previous_source_config(source_type)
        source_instance.prompt(recent_pipeline_config, advanced)

        source_instance.create()
    except SourceException as e:
        raise click.ClickException(str(e))

    click.secho('Source config created', fg='green')


@click.command()
@click.argument('name', autocompletion=sources_autocomplete)
@click.option('-a', '--advanced', is_flag=True)
def edit(name, advanced):
    """
    Edit source
    """
    source_instance = Source(name)

    try:
        source_instance.load()
        source_instance.prompt(advanced=advanced)
        source_instance.save()
    except SourceException as e:
        raise click.ClickException(str(e))

    click.secho('Source config updated', fg='green')


@click.command(name='list')
def list_configs():
    """
    List all sources
    """
    for config in Source.get_list():
        click.echo(config)


@click.command()
@click.argument('name', autocompletion=sources_autocomplete)
def delete(name):
    """
    Delete source
    """
    source_instance = Source(name)

    try:
        source_instance.load()
        source_instance.delete()
    except SourceException as e:
        raise click.ClickException(str(e))


source.add_command(create)
source.add_command(list_configs)
source.add_command(delete)
source.add_command(edit)
