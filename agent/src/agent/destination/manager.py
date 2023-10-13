from agent import destination
from agent.destination import HttpDestination
from agent.destination.anodot_api_client import AnodotApiClient
from agent.modules import proxy
from result import Result, Ok, Err


def save(destination_: HttpDestination) -> Result[HttpDestination, str]:
    result = validate(destination_)
    if result.is_err():
        return result

    destination.repository.save(destination_)
    if destination_.auth_token:
        destination.repository.delete_auth_token(destination_.auth_token)
    auth_token = destination.AuthenticationToken(result.value.id, AnodotApiClient(result.value).get_new_token())
    destination.repository.save_auth_token(auth_token)
    return result


def build(
    destination_: HttpDestination,
    token: str,
    url: str,
    access_key: str = None,
    proxy_host: str = None,
    proxy_username: str = None,
    proxy_password: str = None,
    host_id: str = None,
    use_jks_truststore: bool = False,
) -> HttpDestination:
    destination_.token = token
    destination_.url = url.rstrip('/')
    destination_.use_jks_truststore = use_jks_truststore
    if proxy_host:
        destination_.proxy = proxy.Proxy(proxy_host, proxy_username, proxy_password)

    if access_key:
        destination_.access_key = access_key

    if host_id:
        destination_.host_id = host_id

    return destination_


def validate(destination_: HttpDestination) -> Result[HttpDestination, str]:
    if destination_.proxy:
        if not proxy.is_valid(destination_.proxy):
            return Err('Proxy data is invalid')

    if destination_.url:
        try:
            destination.validator.is_valid_destination_url(destination_.url, destination_.proxy)
        except destination.validator.ValidationException as e:
            return Err('Destination url validation failed: ' + str(e))

    if not destination.validator.is_valid_resource_url(destination_.metrics_url):
        return Err('Data collection token is invalid')

    if destination_.access_key:
        if not destination.validator.is_valid_access_key(destination_):
            return Err('Access key is invalid')
    return Ok(destination_)


def delete():
    destination.repository.delete()
