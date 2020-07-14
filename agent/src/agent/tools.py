import time
import click
import json

from datetime import datetime
from urllib.parse import urlparse
from influxdb import InfluxDBClient
from influxdb.exceptions import InfluxDBClientError
from pymongo import MongoClient

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


def get_influx_client(host, username=None, password=None, db=None) -> InfluxDBClient:
    influx_url_parsed = urlparse(host)
    influx_url = influx_url_parsed.netloc.split(':')
    args = {'host': influx_url[0], 'port': influx_url[1]}
    if username and username != '':
        args['username'] = username
        args['password'] = password
    if influx_url_parsed.scheme == 'https':
        args['ssl'] = True
    if db:
        args['database'] = db
    return InfluxDBClient(**args)


def has_write_access(client: InfluxDBClient):
    try:
        client.write_points([{
            "measurement": "agent_test",
            "time": time.time_ns(),
            "fields": {
                "val": 1.0
            }
        }])
    except InfluxDBClientError as e:
        if e.code == 403:
            return False
    client.drop_measurement('agent_test')
    return True


def get_mongo_client(connection_string: str, username: str, password: str, auth_source: str) -> MongoClient:
    args = {}
    if username:
        args['authSource'] = auth_source
        args['username'] = username
        args['password'] = password
    return MongoClient(connection_string, **args)
