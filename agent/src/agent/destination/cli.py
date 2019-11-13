import click

from .http import HttpDestination, DestinationException
from .. import source, pipeline
from ..streamsets_api_client import api_client
from agent.constants import ENV_PROD, MONITORING_SOURCE_NAME
from agent.tools import infinite_retry


def monitoring():

    try:
        if pipeline.Pipeline.exists('Monitoring'):
            pipeline_monitoring = pipeline.load_object('Monitoring')
            click.secho('Updating Monitoring pipeline...')
            api_client.stop_pipeline(pipeline_monitoring.id)
            pipeline_monitoring.wait_for_status(pipeline.Pipeline.STATUS_STOPPED)
            pipeline_monitoring.update()
        else:
            pipeline_monitoring = pipeline.create_object('Monitoring', MONITORING_SOURCE_NAME)
            click.secho('Starting Monitoring pipeline...')
            source.create_dir()
            pipeline.create_dir()
            pipeline_monitoring.create()

        api_client.start_pipeline(pipeline_monitoring.id)
        pipeline_monitoring.wait_for_status(pipeline.Pipeline.STATUS_RUNNING)
        click.secho('Monitoring pipeline is running')
        if ENV_PROD:
            pipeline_monitoring.wait_for_sending_data()
            click.secho('Monitoring pipeline is sending data')
    except pipeline.PipelineException as e:
        raise click.ClickException(str(e))


@infinite_retry
def create_destination():
    try:
        dest = HttpDestination()
        if dest.exists():
            dest.load()

        dest.update_url(click.prompt('Anodot api token', type=click.STRING))

        use_proxy = click.confirm('Use proxy for connecting to Anodot?')
        if use_proxy:
            uri = click.prompt('Proxy uri', type=click.STRING, default=dest.get_proxy_url())
            username = click.prompt('Proxy username', type=click.STRING, default=dest.get_proxy_username() or '')
            password = click.prompt('Proxy password', type=click.STRING, default='')
            dest.set_proxy(use_proxy, uri, username, password)
        else:
            dest.set_proxy(use_proxy)

        dest.save()
    except DestinationException as e:
        raise click.ClickException(str(e))


@click.command()
def destination():
    """
    Data destination config.
    Anodot API token - You can copy it from Settings > API tokens > Data Collection in your Anodot account
    Proxy for connecting to Anodot
    """

    create_destination()
    click.secho('Connection to Anodot established')
    monitoring()

    click.secho('Destination configured', fg='green')
