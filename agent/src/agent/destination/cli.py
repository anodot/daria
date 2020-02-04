import click

from .http import HttpDestination, DestinationException
from .. import source, pipeline
from agent.constants import ENV_PROD, MONITORING_SOURCE_NAME
from agent.tools import infinite_retry


def monitoring():

    try:
        if pipeline.Pipeline.exists('Monitoring'):
            pipeline_manager = pipeline.PipelineManager(pipeline.load_object('Monitoring'))
            click.secho('Updating Monitoring pipeline...')
            pipeline_manager.pipeline.stop()
            pipeline_manager.update()
        else:
            pipeline_manager = pipeline.PipelineManager(pipeline.create_object('Monitoring', MONITORING_SOURCE_NAME))
            click.secho('Starting Monitoring pipeline...')
            source.create_dir()
            pipeline.create_dir()
            pipeline_manager.create()

        pipeline_manager.pipeline.start()
        click.secho('Monitoring pipeline is running')
        if ENV_PROD:
            pipeline_manager.pipeline.wait_for_sending_data()
            click.secho('Monitoring pipeline is sending data')
    except pipeline.PipelineException as e:
        raise click.ClickException(str(e))


@infinite_retry
def prompt_destination(dest: HttpDestination):

    token = click.prompt('Anodot api token', type=click.STRING)
    dest.update_url(token)

    use_proxy = click.confirm('Use proxy for connecting to Anodot?')
    if use_proxy:
        uri = click.prompt('Proxy uri', type=click.STRING, default=dest.get_proxy_url())
        username = click.prompt('Proxy username', type=click.STRING, default=dest.get_proxy_username() or '')
        password = click.prompt('Proxy password', type=click.STRING, default='')
        dest.set_proxy(use_proxy, uri, username, password)
    else:
        dest.set_proxy(use_proxy)

    dest.validate()


@click.command()
@click.option('-t', '--token', type=click.STRING, default=None)
@click.option('--proxy/--no-proxy', default=False)
@click.option('--proxy-host', type=click.STRING, default=None)
@click.option('--proxy-user', type=click.STRING, default=None)
@click.option('--proxy-password', type=click.STRING, default=None)
def destination(token, proxy, proxy_host, proxy_user, proxy_password):
    """
    Data destination config.
    Anodot API token - You can copy it from Settings > API tokens > Data Collection in your Anodot account
    Proxy for connecting to Anodot
    """
    dest = HttpDestination()
    if dest.exists():
        dest.load()

    if token:
        dest.update_url(token)
        dest.set_proxy(proxy, proxy_host, proxy_user, proxy_password)
    else:
        prompt_destination(dest)

    dest.save()
    click.secho('Connection to Anodot established')
    monitoring()

    click.secho('Destination configured', fg='green')
