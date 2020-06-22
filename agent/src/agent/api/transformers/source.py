from typing import Callable

from agent import source


def get_transformer(source_type: str) -> Callable:
    return transformers[source_type]


def transform_influx_data(data: dict) -> dict:
    config = {'name': data['name'], 'type': data['type'], 'config': {}}
    config['config']['host'] = data['url']
    config['config']['db'] = data['database']
    config['config']['username'] = data.get('username', '')
    config['config']['password'] = data.get('password', '')
    config['config']['write_host'] = data.get('write_url', '')
    config['config']['write_db'] = data.get('write_database', '')
    config['config']['write_username'] = data.get('write_username', '')
    config['config']['write_password'] = data.get('write_password', '')
    config['config']['offset'] = data.get('initial_offset', '')
    return config


transformers = {
    source.TYPE_INFLUX: transform_influx_data,
    source.TYPE_KAFKA: 1,
    source.TYPE_MONGO: 1,
    source.TYPE_MYSQL: 1,
    source.TYPE_POSTGRES: 1,
    source.TYPE_ELASTIC: 1,
    source.TYPE_SPLUNK: 1,
    source.TYPE_DIRECTORY: 1,
}
