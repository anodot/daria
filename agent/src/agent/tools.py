import click
import json

from agent.constants import ENV_PROD, VALIDATION_ENABLED
from urllib.parse import urlparse
from tabulate import tabulate


def infinite_retry(func):
    if not ENV_PROD:
        return func

    def new_func(*args, **kwargs):
        while True:
            try:
                return func(*args, **kwargs)
            except (KeyboardInterrupt, SystemExit, click.Abort):
                raise click.Abort()
            except Exception as e:
                click.secho(str(e), err=True, color='red')
    return new_func


def is_url(url):
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc, result.port])
    except ValueError as e:
        return False


def print_dicts(dicts: list):
    print(tabulate(list(zip(*[[f'{idx}: {item}' for idx, item in dict_item.items()] for dict_item in dicts]))))


def print_json(records):
    print('\n', '=========', sep='')
    for record in records:
        print(json.dumps(record, indent=4, sort_keys=True))
        print('=========')
    print('\n')


def map_keys(records, mapping):
    return [{new_key: record[int(idx)] for idx, new_key in mapping.items()} for record in records]


def if_validation_enabled(func):
    if not VALIDATION_ENABLED:
        def new_func(*args, **kwargs):
            return True
        return new_func
    return func
