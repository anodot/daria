import requests

from agent import proxy


def is_valid(proxy_obj: proxy.Proxy) -> bool:
    try:
        requests.get('http://example.com', proxies=proxy.get_config(proxy_obj), timeout=5)
    except requests.exceptions.ProxyError:
        return False
    return True
