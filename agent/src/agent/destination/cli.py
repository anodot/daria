import click

from .http import HttpDestination
from .. import source, pipeline
from agent.constants import MONITORING_SOURCE_NAME
from agent.tools import infinite_retry
from urllib.parse import urlparse


def monitoring():
    try:
        if pipeline.Pipeline.exists('Monitoring'):
            pipeline_manager = pipeline.PipelineManager(pipeline.load_object('Monitoring'))
            click.secho('Updating Monitoring pipeline...')
            pipeline_manager.stop()
            pipeline_manager.update()
        else:
            pipeline_manager = pipeline.PipelineManager(pipeline.create_object('Monitoring', MONITORING_SOURCE_NAME))
            click.secho('Starting Monitoring pipeline...')
            source.create_dir()
            pipeline.create_dir()
            pipeline_manager.create()

        pipeline_manager.start()
    except pipeline.PipelineException as e:
        raise click.ClickException(str(e))


@infinite_retry
def prompt_destination(dest: HttpDestination):
    dest.url = __prompt_url(default=dest.url)
    dest.token = click.prompt('Anodot api data collection token', type=click.STRING, default=dest.config.get('token'))
    dest.update_urls()

    if click.confirm('Use proxy for connecting to Anodot?'):
        uri = click.prompt('Proxy uri', type=click.STRING, default=dest.get_proxy_url())
        username = click.prompt('Proxy username', type=click.STRING, default=dest.get_proxy_username() or '')
        password = click.prompt('Proxy password', type=click.STRING, default='')
        dest.set_proxy(True, uri, username, password)
    else:
        dest.set_proxy(False)

    dest.validate_token()


@infinite_retry
def __prompt_url(default: str):
    url = click.prompt('Destination url', type=click.STRING, default=default)
    __check_url(url)
    return url


def __check_url(url: str):
    result = urlparse(url)
    if not result.netloc or not result.scheme:
        raise click.ClickException('Wrong url format, please specify the protocol and domain name')


@infinite_retry
def prompt_api_key(dest: HttpDestination):
    dest.api_key = click.prompt('Anodot api key', type=click.STRING,
                                default=dest.api_key if dest.api_key else '')
    dest.validate_api_key()


@click.command()
@click.option('-t', '--token', type=click.STRING, default=None)
@click.option('--proxy/--no-proxy', default=False)
@click.option('--proxy-host', type=click.STRING, default=None)
@click.option('--proxy-user', type=click.STRING, default=None)
@click.option('--proxy-password', type=click.STRING, default=None)
@click.option('--host-id', type=click.STRING, default=None)
@click.option('--api-key', type=click.STRING, default=None)
@click.option('--url', type=click.STRING, default=None)
def destination(token, proxy, proxy_host, proxy_user, proxy_password, host_id, api_key, url):
    """
    Data destination config.
    Anodot API token - You can copy it from Settings > API tokens > Data Collection in your Anodot account
    Proxy for connecting to Anodot
    """
    dest = HttpDestination(host_id=host_id, api_key=api_key)
    if dest.exists():
        dest.load()
    if url:
        __check_url(url)
        dest.url = url

    if token:
        dest.token = token
        dest.update_urls()
        dest.set_proxy(proxy, proxy_host, proxy_user, proxy_password)
    else:
        prompt_destination(dest)
        prompt_api_key(dest)

    dest.save()
    click.secho('Connection to Anodot established')
    monitoring()

    click.secho('Destination configured', fg='green')
