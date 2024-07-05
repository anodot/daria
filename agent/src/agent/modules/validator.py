import os
import sqlalchemy
import subprocess
import pyodbc

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


def file_exists(file_path: str):
    if not os.path.isfile(file_path):
        raise ValidationException(f'File {file_path} does not exist')


def dir_exists(directory: str):
    if not os.path.isdir(directory):
        raise ValidationException(f'Directory {directory} does not exist')


def validate_mysql_connection(connection_string: str):
    # todo raise validation exception
    eng = sqlalchemy.create_engine(connection_string)
    eng.connect()


def validate_actian_connection(connection_string: str):
    pyodbc.connect(connection_string)


def validate_python_file(file: str):
    if not os.path.isfile(file):
        raise ValidationException(f'No such file `{file}`')
    try:
        subprocess.check_output(['python', '-m', 'py_compile', file], stderr=subprocess.STDOUT)
    except subprocess.CalledProcessError as e:
        raise ValidationException(e.output)


class ValidationException(Exception):
    pass
