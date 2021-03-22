import os
import sqlalchemy

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


def validate_dir(directory: str):
    if not os.path.isdir(directory):
        raise ValidationException(f'Directory {directory} does not exist')


def validate_mysql_connection(connection_string: str):
    # todo raise validation exception
    eng = sqlalchemy.create_engine(connection_string)
    eng.connect()


class ValidationException(Exception):
    pass
