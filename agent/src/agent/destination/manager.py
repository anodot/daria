from agent import destination
from agent.destination import HttpDestination
from agent.destination.anodot_api_client import AnodotApiClient
from agent.modules import proxy
from result import Result, Ok, Err


def create(
    token: str,
    url: str,
    access_key: str = None,
    proxy_host: str = None,
    proxy_username: str = None,
    proxy_password: str = None,
    host_id: str = None,
) -> Result[HttpDestination, str]:
    result = _build(HttpDestination(), token, url, access_key, proxy_host, proxy_username, proxy_password, host_id)
    if not result.is_err():
        # todo duplicate code, try to avoid it
        auth_token = destination.AuthenticationToken(result.value.id, AnodotApiClient(result.value).get_new_token())
        destination.repository.save_auth_token(auth_token)
    return result


def edit(
    destination_: HttpDestination,
    token: str,
    url: str,
    access_key: str = None,
    proxy_host: str = None,
    proxy_username: str = None,
    proxy_password: str = None,
    host_id: str = None,
) -> Result[HttpDestination, str]:
    result = _build(destination_, token, url, access_key, proxy_host, proxy_username, proxy_password, host_id)
    if not result.is_err():
        if destination_.auth_token:
            destination.repository.delete_auth_token(destination_.auth_token)
        # todo duplicate code, try to avoid it
        auth_token = destination.AuthenticationToken(result.value.id, AnodotApiClient(result.value).get_new_token())
        destination.repository.save_auth_token(auth_token)
    return result


def _build(
    destination_: HttpDestination,
    token: str,
    url: str,
    access_key: str = None,
    proxy_host: str = None,
    proxy_username: str = None,
    proxy_password: str = None,
    host_id: str = None,
) -> Result[HttpDestination, str]:
    proxy_ = proxy.Proxy(proxy_host, proxy_username, proxy_password) if proxy_host else None
    if proxy_:
        if not proxy.is_valid(proxy_):
            return Err('Proxy data is invalid')
        destination_.proxy = proxy_
    if url:
        try:
            destination.validator.is_valid_destination_url(url, destination_.proxy)
        except destination.validator.ValidationException as e:
            return Err('Destination url validation failed: ' + str(e))
        destination_.url = url
    if token:
        destination_.token = token
        if not destination.validator.is_valid_resource_url(destination_.metrics_url):
            return Err('Data collection token is invalid')
    if access_key:
        destination_.access_key = access_key
        if not destination.validator.is_valid_access_key(destination_):
            return Err('Access key is invalid')
    if host_id:
        destination_.host_id = host_id
    destination.repository.save(destination_)
    return Ok(destination_)


def delete():
    destination.repository.delete()
