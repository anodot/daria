import json
import jsonschema
import click
import requests
import agent.destination

from agent.destination import HttpDestination
from agent.modules.tools import infinite_retry
from agent.modules import proxy, validator


@click.command()
@click.option('-t', '--token', type=click.STRING, default=None)
@click.option('-f', '--filepath', type=click.STRING, default=None)
@click.option('--proxy-host', type=click.STRING, default=None)
@click.option('--proxy-user', type=click.STRING, default=None)
@click.option('--proxy-password', type=click.STRING, default=None)
@click.option('--host-id', type=click.STRING, default=None)
@click.option('--access-key', type=click.STRING, default=None)
@click.option('--url', type=click.STRING, default=None)
@click.option('--use-jks-truststore', is_flag=True, default=False)
def destination(token, filepath, proxy_host, proxy_user, proxy_password, host_id, access_key, url, use_jks_truststore):
    """
    Data destination config.
    Anodot API token - You can copy it from Settings > API tokens > Data Collection in your Anodot account
    Proxy for connecting to Anodot
    """
    destination_ = agent.destination.repository.get() \
        if agent.destination.repository.exists() \
        else HttpDestination()

    # take all data from the command arguments if token is provided, otherwise ask for input
    if token:
        destination_ = agent.destination.manager.build(destination_, token, url, access_key, proxy_host, proxy_user,
                                                       proxy_password, host_id, use_jks_truststore)
    elif filepath:
        destination_ = _build_from_file(destination_, filepath)
    else:
        destination_ = _build_from_prompt(destination_)

    result = agent.destination.manager.save(destination_)

    if result.is_err():
        raise click.ClickException(result.value)

    click.secho('Destination configured', fg='green')


def _build_from_file(destination_: HttpDestination, filepath: str):
    file_schema = {
        "type": "object",
        "properties": {
            "host_id": {"type": "string", "minLength": 1},
            "access_key": {"type": "string", "minLength": 1},
            "config": {
                "type": "object",
                "properties": {
                    "url": {"type": "string", "minLength": 1},
                    "token": {"type": "string", "minLength": 1},
                },
                "required": ["url", "token"]
            },
        },
        "required": ["config", "access_key", "host_id"]
    }
    with open(filepath) as f:
        config = json.load(f)

    try:
        jsonschema.validate(config, file_schema)
    except jsonschema.exceptions.ValidationError as e:
        raise click.ClickException(e.message)

    destination_.config = config['config']
    destination_.access_key = config['access_key']
    if 'host_id' in config:
        destination_.host_id = config['host_id']
    return destination_


def _build_from_prompt(destination_: HttpDestination):
    _prompt_proxy(destination_)
    destination_.use_jks_truststore = click.confirm('Use jks truststore with a custom ssl certificate?')
    _prompt_url(destination_)
    _prompt_token(destination_)
    _prompt_access_key(destination_)
    return destination_


@click.command()
@click.option('-f', '--filepath', type=click.STRING, default=None)
def destination_export(filepath):
    destination_ = agent.destination.repository.get()
    if not destination_:
        raise click.ClickException('Destination doesn\'t exist')

    if not filepath:
        filepath = 'destination.json'
    with open(filepath, 'w') as f:
        json.dump(destination_.to_dict(), f, indent=4)
    click.secho(f'Destination config exported to {filepath}', fg='green')


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
            agent.destination.validator.is_valid_destination_url(url, dest.proxy, not dest.use_jks_truststore)
        except agent.destination.validator.ValidationException as e:
            raise click.ClickException('Destination url validation failed: ' + str(e))
    except requests.exceptions.ProxyError as e:
        raise click.ClickException(str(e))
    dest.url = url


@infinite_retry
def _prompt_token(dest: HttpDestination):
    token = click.prompt('Anodot api data collection token', type=click.STRING, default=dest.token)
    dest.token = token
    if not agent.destination.validator.is_valid_resource_url(dest.metrics_url, dest.proxy, not dest.use_jks_truststore):
        raise click.ClickException('Data collection token is invalid')


@infinite_retry
def _prompt_access_key(dest: HttpDestination):
    dest.access_key = click.prompt('Anodot access key', type=click.STRING, default=dest.access_key)
    if not agent.destination.validator.is_valid_access_key(dest):
        raise click.ClickException('Access key is invalid')
