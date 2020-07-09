import urllib
import requests
import urllib.parse

from agent.anodot_api_client import AnodotApiClient
from agent import destination
from agent import proxy
from agent.tools import if_validation_enabled


class ValidationException(Exception):
    pass

  
@if_validation_enabled
def is_valid_destination_url(url: str, proxy_obj: proxy.Proxy = None) -> bool:
    status_url = urllib.parse.urljoin(url, destination.HttpDestination.STATUS_URL)
    try:
        response = requests.get(status_url, proxies=proxy.get_config(proxy_obj), timeout=5)
        response.raise_for_status()
    except (ConnectionError, requests.HTTPError, requests.exceptions.ConnectionError,
            requests.exceptions.ProxyError) as e:
        # todo this is a temporary solution, validation should be unified across the whole project
        raise ValidationException(str(e))
    return True


@if_validation_enabled
def is_valid_resource_url(resource_url: str) -> bool:
    response = requests.post(resource_url, timeout=5)
    if response.status_code != 401:
        response.raise_for_status()
    return response.status_code != 401


@if_validation_enabled
def is_valid_access_key(access_key: str, url: str) -> bool:
    try:
        # todo refactor validation?
        AnodotApiClient(access_key, proxies={}, base_url=url)
    except requests.HTTPError:
        return False
    return True
