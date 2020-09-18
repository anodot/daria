import requests

from agent.modules.tools import if_validation_enabled
from urllib.parse import urlparse, urlunparse


class Proxy:
    def __init__(self, uri: str, username: str = '', password: str = ''):
        self.uri = uri
        self.username = username
        self.password = password


def get_config(proxy: Proxy) -> dict:
    proxies = dict()
    if proxy:
        proxy_parsed = urlparse(proxy.uri)
        netloc = proxy_parsed.netloc
        if proxy.password:
            netloc = proxy.username + ':' + proxy.password + '@' + netloc
        proxies['http'] = urlunparse((proxy_parsed.scheme, netloc, proxy_parsed.path, '', '', ''))
        proxies['https'] = proxies['http']
    return proxies


@if_validation_enabled
def is_valid(proxy_obj: Proxy) -> bool:
    try:
        requests.get('http://example.com', proxies=get_config(proxy_obj), timeout=5)
    except requests.exceptions.ProxyError:
        return False
    except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
        # we cannot validate a proxy now, probably due to network restrictions
        return True
    return True
