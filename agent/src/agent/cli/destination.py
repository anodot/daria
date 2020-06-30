import click
import requests

from agent import source, pipeline
from agent.destination import HttpDestination, build_urls, create
from agent import validator
from agent.constants import MONITORING_SOURCE_NAME
from agent.tools import infinite_retry
from agent.proxy import Proxy
from agent.pipeline import manager


@infinite_retry
def __prompt_proxy(dest: HttpDestination):
    if click.confirm('Use proxy for connecting to Anodot?'):
        uri = __prompt_proxy_uri(dest.get_proxy_url())
        username = __prompt_proxy_username(dest.get_proxy_username())
        password = __prompt_proxy_password()
        proxy = Proxy(uri, username, password)
        if not validator.proxy.is_valid(proxy):
            raise click.ClickException('Proxy is invalid')
        dest.proxy = proxy


def __prompt_proxy_uri(default: str) -> str:
    return click.prompt('Proxy uri', type=click.STRING, default=default)


def __prompt_proxy_username(default: str) -> str:
    return click.prompt('Proxy username', type=click.STRING, default=default)


def __prompt_proxy_password() -> str:
    return click.prompt('Proxy password', type=click.STRING, default='')


@infinite_retry
def __prompt_url(dest: HttpDestination):
    url = click.prompt('Destination url', type=click.STRING, default=dest.url)
    try:
        if not validator.destination.is_valid_destination_url(url, dest.proxy):
            raise click.ClickException('Wrong url format, please specify the protocol and domain name')
    except requests.exceptions.ProxyError as e:
        raise click.ClickException(str(e))
    dest.url = url


@infinite_retry
def __prompt_token(dest: HttpDestination):
    token = click.prompt('Anodot api data collection token', type=click.STRING, default=dest.token)
    resource_url, monitoring_url = build_urls(dest.url, token)
    if not validator.destination.is_valid_resource_url(resource_url):
        raise click.ClickException('Data collection token is invalid')
    dest.token = token
    dest.resource_url = resource_url
    dest.monitoring_url = monitoring_url


@infinite_retry
def __prompt_access_key(dest: HttpDestination):
    access_key = click.prompt('Anodot access key', type=click.STRING, default=dest.access_key or '')
    if access_key and not validator.destination.is_valid_access_key(access_key, dest.url):
        raise click.ClickException('Access key is invalid')
    dest.access_key = access_key


def __start_monitoring_pipeline():
    try:
        if pipeline.pipeline.Pipeline.exists('Monitoring'):
            pipeline_manager = manager.PipelineManager(pipeline.load_object('Monitoring'))
            click.secho('Updating Monitoring pipeline...')
            pipeline_manager.stop()
            pipeline_manager.update()
        else:
            pipeline_manager = manager.PipelineManager(pipeline.create_object('Monitoring', MONITORING_SOURCE_NAME))
            click.secho('Starting Monitoring pipeline...')
            source.create_dir()
            pipeline.create_dir()
            pipeline_manager.create()

        pipeline_manager.start()
    except pipeline.pipeline.PipelineException as e:
        raise click.ClickException(str(e))


@click.command()
@click.option('-t', '--token', type=click.STRING, default=None)
@click.option('--proxy/--no-proxy', default=False)
@click.option('--proxy-host', type=click.STRING, default=None)
@click.option('--proxy-user', type=click.STRING, default=None)
@click.option('--proxy-password', type=click.STRING, default=None)
@click.option('--host-id', type=click.STRING, default=None)
@click.option('--access-key', type=click.STRING, default=None)
@click.option('--url', type=click.STRING, default=None)
def destination(token, proxy, proxy_host, proxy_user, proxy_password, host_id, access_key, url):
    """
    Data destination config.
    Anodot API token - You can copy it from Settings > API tokens > Data Collection in your Anodot account
    Proxy for connecting to Anodot
    """
    # take all data from the command arguments if token is provided, otherwise ask for input
    if token:
        result = create(token, url, access_key, proxy_host, proxy_user, proxy_password, host_id)
        if result.is_err():
            raise click.ClickException(result.value)
    else:
        dest = HttpDestination.get_or_default()
        __prompt_proxy(dest)
        __prompt_url(dest)
        __prompt_token(dest)
        __prompt_access_key(dest)
        dest.save()

    click.secho('Connection to Anodot established')
    __start_monitoring_pipeline()
    click.secho('Destination configured', fg='green')
