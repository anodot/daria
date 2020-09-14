import requests

from agent.modules import proxy
from agent.modules.tools import if_validation_enabled


@if_validation_enabled
def is_valid(proxy_obj: proxy.Proxy) -> bool:
    try:
        requests.get('http://example.com', proxies=proxy.get_config(proxy_obj), timeout=5)
    except requests.exceptions.ProxyError:
        return False
    except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
        # we cannot validate a proxy now, probably due to network restrictions
        return True
    return True
