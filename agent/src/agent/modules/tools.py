import os
import re
import shutil
import tarfile
import click
import json

from enum import Enum
from datetime import datetime
from agent.modules import constants
from tabulate import tabulate
from typing import Any


def infinite_retry(func):
    if not constants.ENV_PROD:
        return func

    def new_func(*args, **kwargs):
        while True:
            try:
                return func(*args, **kwargs)
            except (KeyboardInterrupt, SystemExit, click.Abort) as e:
                raise click.Abort() from e
            except click.UsageError as e:
                click.secho(str(e.message), err=True, color='red')
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
        mapping = dict(enumerate(mapping))
    return [{new_key: record[int(idx)] for idx, new_key in mapping.items()} for record in records]


def if_validation_enabled(func):
    if not constants.VALIDATION_ENABLED:

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


def replace_illegal_chars(value):
    if type(value) == str:
        return _replace_illegal_chars(value)
    elif type(value) == dict:
        return _replace_dict_illegal_chars(value)
    elif type(value) == list:
        return _replace_list_illegal_chars(value)
    else:
        raise Exception('Unsupported type of value')


def _replace_illegal_chars(value: str) -> str:
    value = value.strip().replace(".", "_")
    return re.sub('\s+', '_', value)


def _replace_list_illegal_chars(list_: list) -> list:
    return [replace_illegal_chars(v) for v in list_]


def _replace_dict_illegal_chars(dict_: dict) -> dict:
    return {replace_illegal_chars(k): replace_illegal_chars(v) for k, v in dict_.items()}


def deep_update(src: dict, dst: Any):
    """Updates a nested dictionary. Modifies dst in place"""
    if not isinstance(dst, dict):
        dst = src.copy()
    for key, value in src.items():
        if isinstance(value, dict) and value:
            deep_update(value, dst.setdefault(key, {}))
        else:
            dst[key] = value


def escape_quotes(s: str) -> str:
    return s.replace("'", "\\'")


class ArchiveCompressionType(Enum):
    GZ = 'gz'
    BZ2 = 'bz2'
    XZ = 'xz'


def extract_archive(
    archive_path: str,
    destination_path: str,
    compression: ArchiveCompressionType = ArchiveCompressionType.GZ,
):
    if not os.path.isfile(archive_path):
        raise ArchiveNotExistsException()
    with tarfile.open(archive_path, f'r:{compression.value}') as tar:
        tar.extractall(path=destination_path)


def copy_dir(source_dir: str, destination_dir: str):
    os.makedirs(os.path.dirname(destination_dir), exist_ok=True)
    shutil.copytree(source_dir, destination_dir)


def get_all_files(directory: str):
    if not os.path.isdir(directory):
        raise NotADirectoryError(f'`{directory}` is not a directory')
    for root, dirs, files in os.walk(directory):
        for dir_ in dirs:
            get_all_files(dir_)
        for file in files:
            yield os.path.join(root, file)


def chunks(lst, n):
    for i in range(0, len(lst), n):
        yield lst[i:i + n]


class ArchiveNotExistsException(Exception):
    pass
