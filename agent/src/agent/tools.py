import click
import json

from datetime import datetime

from agent.constants import ENV_PROD, VALIDATION_ENABLED
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


def print_dicts(dicts: list):
    print(tabulate(list(zip(*[[f'{idx}: {item}' for idx, item in dict_item.items()] for dict_item in dicts]))))


def print_json(records):
    print('\n', '=========', sep='')
    for record in records:
        print(json.dumps(record, indent=4, sort_keys=True))
        print('=========')
    print('\n')


def map_keys(records, mapping):
    if type(mapping) is list:
        mapping = {idx: item for idx, item in enumerate(mapping)}
    return [{new_key: record[int(idx)] for idx, new_key in mapping.items()} for record in records]


def if_validation_enabled(func):
    if not VALIDATION_ENABLED:
        def new_func(*args, **kwargs):
            return True
        return new_func
    return func


def dict_get_nested(dictionary: dict, keys: list):
    element = dictionary
    for key in keys:
        if key not in element:
            return None
        element = element[key]
    return element


def sdc_record_map_to_dict(record: dict):
    if 'value' not in record:
        return record

    if type(record['value']) is list:
        if record['type'] == 'LIST_MAP':
            d = {}
            for item in record['value']:
                key = item['sqpath'].replace('/', '')
                try:
                    key = int(key)
                except ValueError:
                    pass
                d[key] = sdc_record_map_to_dict(item)
            return d
        if record['type'] == 'LIST':
            return [sdc_record_map_to_dict(item) for item in record['value']]
        return {key: sdc_record_map_to_dict(item) for key, item in enumerate(record['value'])}

    if type(record['value']) is dict:
        return {key: sdc_record_map_to_dict(item) for key, item in record['value'].items()}

    if 'type' in record and record['type'] == 'DATETIME':
        return datetime.fromtimestamp(record['value'] // 1000).strftime('%Y-%m-%d %H:%M:%S')

    return record['value']
