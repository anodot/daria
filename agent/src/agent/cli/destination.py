import click
import requests
import agent.destination

from agent.destination import HttpDestination
from agent.destination.anodot_api_client import AnodotApiClient
from agent.modules.tools import infinite_retry
from agent.modules import proxy, validator


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
        destination_ = agent.destination.repository.get()\
            if agent.destination.repository.exists()\
            else HttpDestination()
        _prompt_proxy(destination_)
        _prompt_url(destination_)
        _prompt_token(destination_)
        _prompt_access_key(destination_)
        agent.destination.repository.save(destination_)
        # todo code duplicate, try to avoid it
        auth_token = agent.destination.AuthenticationToken(destination_.id, AnodotApiClient(destination_).get_new_token())
        agent.destination.repository.save_auth_token(auth_token)

        click.secho('Connection to Anodot established')
    click.secho('Destination configured', fg='green')


@infinite_retry
def _prompt_proxy(dest: HttpDestination):
    if click.confirm('Use proxy for connecting to Anodot?'):
        uri = _prompt_proxy_uri(dest.get_proxy_url())
        username = _prompt_proxy_username(dest.get_proxy_username())
        password = _prompt_proxy_password()
        proxy_ = proxy.Proxy(uri, username, password)
        if not proxy.is_valid(proxy_):
            raise click.ClickException('Proxy is invalid')
        dest.proxy = proxy_
    else:
        dest.proxy = None


def _prompt_proxy_uri(default: str) -> str:
    return click.prompt('Proxy uri', type=click.STRING, default=default)


def _prompt_proxy_username(default: str) -> str:
    return click.prompt('Proxy username', type=click.STRING, default=default)


def _prompt_proxy_password() -> str:
    return click.prompt('Proxy password', type=click.STRING, default='')


@infinite_retry
def _prompt_url(dest: HttpDestination):
    url = click.prompt('Destination url', type=click.STRING, default=dest.url)
    try:
        try:
            validator.validate_url_format(url)
        except validator.ValidationException as e:
            raise click.ClickException(str(e))
        try:
            agent.destination.validator.is_valid_destination_url(url, dest.proxy)
        except agent.destination.validator.ValidationException as e:
            raise click.ClickException('Destination url validation failed: ' + str(e))
    except requests.exceptions.ProxyError as e:
        raise click.ClickException(str(e))
    dest.url = url


@infinite_retry
def _prompt_token(dest: HttpDestination):
    token = click.prompt('Anodot api data collection token', type=click.STRING, default=dest.token)
    dest.token = token
    if not agent.destination.validator.is_valid_resource_url(dest.metrics_url, dest.proxy):
        raise click.ClickException('Data collection token is invalid')


@infinite_retry
def _prompt_access_key(dest: HttpDestination):
    dest.access_key = click.prompt('Anodot access key', type=click.STRING, default=dest.access_key)
    if not agent.destination.validator.is_valid_access_key(dest):
        raise click.ClickException('Access key is invalid')
