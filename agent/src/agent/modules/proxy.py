from typing import Optional
from urllib.parse import urlparse, urlunparse


class Proxy:
    def __init__(self, uri: str, username: str = '', password: str = ''):
        self.uri = uri
        self.username = username
        self.password = password


def get_config(proxy: Optional[Proxy]) -> dict:
    proxies = dict()
    if proxy:
        proxy_parsed = urlparse(proxy.uri)
        netloc = proxy_parsed.netloc
        if proxy.password:
            netloc = proxy.username + ':' + proxy.password + '@' + netloc
        proxies['http'] = urlunparse((proxy_parsed.scheme, netloc, proxy_parsed.path, '', '', ''))
        proxies['https'] = proxies['http']
    return proxies
