from urllib.parse import urlparse

from . import destination
from . import proxy


def is_valid_url(url: str) -> bool:
    result = urlparse(url)
    return bool(result.netloc) and bool(result.scheme)
