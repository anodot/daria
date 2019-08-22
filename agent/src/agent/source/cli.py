import click

from agent import source
from agent.pipeline import Pipeline
from agent.streamsets_api_client import api_client
from agent.destination import HttpDestination


def get_previous_source_config(label):
    pipelines_with_source = api_client.get_pipelines(order_by='CREATED', order='DESC',
                                                     label=label)
    if len(pipelines_with_source) > 0:
        pipeline_obj = Pipeline(pipelines_with_source[-1]['pipelineId'])
        pipeline_obj.load()
        return pipeline_obj.config['source']['config']
    return {}


@click.group(name='source')
def source_group():
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
    if not HttpDestination.exists():
        raise click.ClickException('Destination is not configured. Please use `agent destination` command')
    source_type = click.prompt('Choose source', type=click.Choice(source.types))
    source_name = click.prompt('Enter unique name for this source config', type=click.STRING)

    source_instance = source.create_object(source_name, source_type)

    try:
        recent_pipeline_config = get_previous_source_config(source_type)
        source_instance.config = source_instance.prompt(recent_pipeline_config, advanced)

        source_instance.create()
    except source.SourceException as e:
        raise click.ClickException(str(e))

    click.secho('Source config created', fg='green')


@click.command()
@click.argument('name', autocompletion=source.autocomplete)
@click.option('-a', '--advanced', is_flag=True)
def edit(name, advanced):
    """
    Edit source
    """
    source_instance = source.load_object(name)

    try:
        source_instance.config = source_instance.prompt(source_instance.config, advanced=advanced)
        source_instance.save()
    except source.SourceException as e:
        raise click.ClickException(str(e))

    click.secho('Source config updated', fg='green')


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
