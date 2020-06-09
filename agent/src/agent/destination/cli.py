import click
from result import Err

from .http import HttpDestination
from .. import source, pipeline
from agent.constants import MONITORING_SOURCE_NAME
from agent.tools import infinite_retry
from urllib.parse import urlparse
from agent.destination.http import create
from agent.destination import Proxy
from typing import Optional


def __validate_url(url: str):
    result = urlparse(url)
    if not result.netloc or not result.scheme:
        raise click.ClickException('Wrong url format, please specify the protocol and domain name')


@infinite_retry
def __prompt_url(default: str):
    url = click.prompt('Destination url', type=click.STRING, default=default)
    __validate_url(url)
    return url


def __prompt_token(default: str):
    return click.prompt('Anodot api data collection token', type=click.STRING, default=default)


def __prompt_proxy(default_dest: HttpDestination) -> Optional[Proxy]:
    if click.confirm('Use proxy for connecting to Anodot?'):
        uri = __prompt_proxy_uri(default_dest.get_proxy_url())
        username = __prompt_proxy_username(default_dest.get_proxy_username())
        password = __prompt_proxy_password()
        return Proxy(uri, username, password)
    return None


def __prompt_proxy_uri(default: str) -> str:
    return click.prompt('Proxy uri', type=click.STRING, default=default)


def __prompt_proxy_username(default: str) -> str:
    return click.prompt('Proxy username', type=click.STRING, default=default)


def __prompt_proxy_password() -> str:
    return click.prompt('Proxy password', type=click.STRING, default='')


@infinite_retry
def __prompt_access_key(default: str):
    return click.prompt('Anodot access key', type=click.STRING, default=default)


def __start_monitoring_pipeline():
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
    proxy_obj = None
    # take all data from the command arguments if token is provided, otherwise ask for input
    if token:
        if url:
            __validate_url(url)
        if proxy:
            if not proxy_host:
                raise click.ClickException('Proxy host is not provided')
            proxy_obj = Proxy(proxy_host, proxy_user, proxy_password)
    else:
        default_dest = HttpDestination.get_or_default()
        url = __prompt_url(default=default_dest.url)
        token = __prompt_token(default_dest.config.get('token'))
        proxy_obj = __prompt_proxy(default_dest)
        api_key = __prompt_access_key(default_dest.api_key)

    result = create(token, url, api_key, proxy_obj, host_id)
    if result.is_err():
        print(result.value)
        return
    click.secho('Connection to Anodot established')
    __start_monitoring_pipeline()
    click.secho('Destination configured', fg='green')
