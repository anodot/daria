import click
import requests
import agent.destination

from agent.destination import destination
from agent import validator, pipeline
from agent.tools import infinite_retry
from agent.proxy import Proxy


@infinite_retry
def _prompt_proxy(dest: destination.HttpDestination):
    if click.confirm('Use proxy for connecting to Anodot?'):
        uri = _prompt_proxy_uri(dest.get_proxy_url())
        username = _prompt_proxy_username(dest.get_proxy_username())
        password = _prompt_proxy_password()
        proxy = Proxy(uri, username, password)
        if not validator.proxy.is_valid(proxy):
            raise click.ClickException('Proxy is invalid')
        dest.proxy = proxy


def _prompt_proxy_uri(default: str) -> str:
    return click.prompt('Proxy uri', type=click.STRING, default=default)


def _prompt_proxy_username(default: str) -> str:
    return click.prompt('Proxy username', type=click.STRING, default=default)


def _prompt_proxy_password() -> str:
    return click.prompt('Proxy password', type=click.STRING, default='')


@infinite_retry
def _prompt_url(dest: destination.HttpDestination):
    url = click.prompt('Destination url', type=click.STRING, default=dest.url)
    try:
        if not validator.is_valid_url(url):
            raise click.ClickException('Wrong url format, please specify the protocol and domain name')
        try:
            validator.destination.is_valid_destination_url(url, dest.proxy)
        except validator.destination.ValidationException as e:
            raise click.ClickException('Destination url validation failed: ' + str(e))
    except requests.exceptions.ProxyError as e:
        raise click.ClickException(str(e))
    dest.url = url


@infinite_retry
def _prompt_token(dest: destination.HttpDestination):
    token = click.prompt('Anodot api data collection token', type=click.STRING, default=dest.token)
    resource_url, monitoring_url = agent.destination.build_urls(dest.url, token)
    if not validator.destination.is_valid_resource_url(resource_url):
        raise click.ClickException('Data collection token is invalid')
    dest.token = token
    dest.resource_url = resource_url
    dest.monitoring_url = monitoring_url


@infinite_retry
def _prompt_access_key(dest: destination.HttpDestination):
    access_key = click.prompt('Anodot access key', type=click.STRING, default=dest.access_key or '')
    if access_key and not validator.destination.is_valid_access_key(access_key, dest.url):
        raise click.ClickException('Access key is invalid')
    dest.access_key = access_key


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
        result = agent.destination.manager.create(token, url, access_key, proxy_host, proxy_user, proxy_password, host_id)
        if result.is_err():
            raise click.ClickException(result.value)
    else:
        dest = agent.destination.HttpDestination.get_or_default()
        _prompt_proxy(dest)
        _prompt_url(dest)
        _prompt_token(dest)
        _prompt_access_key(dest)
        dest.save()

    click.secho('Connection to Anodot established')
    try:
        if pipeline.repository.exists(pipeline.MONITORING):
            click.secho('Updating Monitoring pipeline...')
            pipeline.manager.update_monitoring_pipeline()
        else:
            click.secho('Starting Monitoring pipeline...')
            pipeline.manager.start_monitoring_pipeline()
    except pipeline.pipeline.PipelineException as e:
        raise click.ClickException(str(e))
    click.secho('Destination configured', fg='green')
