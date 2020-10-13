import urllib
import requests
import urllib.parse

from agent.destination import HttpDestination, anodot_api_client
from agent.modules import proxy
from agent.modules.tools import if_validation_enabled


class ValidationException(Exception):
    pass


@if_validation_enabled
def is_valid_destination_url(url: str, proxy_obj: proxy.Proxy = None) -> bool:
    status_url = urllib.parse.urljoin(url, HttpDestination.STATUS_URL)
    try:
        response = requests.get(status_url, proxies=proxy.get_config(proxy_obj), timeout=5)
        response.raise_for_status()
    except (ConnectionError, requests.HTTPError, requests.exceptions.ConnectionError,
            requests.exceptions.ProxyError) as e:
        raise ValidationException(str(e))
    return True


@if_validation_enabled
def is_valid_resource_url(resource_url: str) -> bool:
    response = requests.post(resource_url, timeout=5)
    if response.status_code != 401:
        response.raise_for_status()
    return response.status_code != 401


@if_validation_enabled
def is_valid_access_key(destination_: HttpDestination) -> bool:
    try:
        client = anodot_api_client.AnodotApiClient(destination_, False)
        client.get_new_token()
    except requests.HTTPError:
        return False
    return True
