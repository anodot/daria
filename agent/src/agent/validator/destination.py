import urllib
import requests

from urllib.parse import urlparse
from agent.anodot_api_client import AnodotApiClient
from agent import destination


def is_valid_destination_url(url: str) -> bool:
    result = urlparse(url)
    if not result.netloc or not result.scheme:
        return False
    status_url = urllib.parse.urljoin(url, destination.HttpDestination.STATUS_URL)
    try:
        response = requests.get(status_url, timeout=5)
        response.raise_for_status()
    except (ConnectionError, requests.HTTPError, requests.exceptions.ConnectionError):
        return False
    return True


def is_valid_resource_url(resource_url: str) -> bool:
    response = requests.post(resource_url, timeout=5)
    if response.status_code != 401:
        response.raise_for_status()
    return response.status_code != 401


def is_valid_access_key(access_key: str, url: str) -> bool:
    try:
        # todo refactor validation?
        AnodotApiClient(access_key, proxies={}, base_url=url)
    except requests.HTTPError:
        return False
    return True
