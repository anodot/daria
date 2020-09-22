from urllib.parse import urlparse
from agent.modules.tools import if_validation_enabled


@if_validation_enabled
def is_valid_url(url: str) -> bool:
    result = urlparse(url)
    return all([result.scheme, result.netloc])
