from urllib.parse import urlparse
from agent.modules.tools import if_validation_enabled


@if_validation_enabled
def validate_url_format(url: str):
    result = urlparse(url)
    if not all([result.scheme, result.hostname]):
        raise ValidationException(f"{url} - invalid url, please provide url in format `scheme://host`")


@if_validation_enabled
def validate_url_format_with_port(url: str):
    result = urlparse(url)
    if not all([result.scheme, result.hostname, result.port]):
        raise ValidationException(f"{url} - invalid url, please provide url in format `scheme://host:port`")


class ValidationException(Exception):
    pass
