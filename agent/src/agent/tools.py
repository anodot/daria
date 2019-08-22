import click

from agent.constants import ENV_PROD


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
