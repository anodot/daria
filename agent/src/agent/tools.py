import click

from agent.constants import ENV_PROD
from urllib.parse import urlparse


def infinite_retry(func):
    if not ENV_PROD:
        return func

    def new_func(*args, **kwargs):
        while True:
            try:
                return func(*args, **kwargs)
            except Exception as e:
                click.secho(str(e), err=True, color='red')
    return new_func


def is_url(url):
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except ValueError as e:
        return False
