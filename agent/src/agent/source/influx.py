import click
import time

from .abstract_source import Source
from datetime import datetime
from urllib.parse import urlparse
from influxdb import InfluxDBClient
from influxdb.exceptions import InfluxDBClientError


def is_url(url):
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except ValueError as e:
        return False


class InfluxSource(Source):

    def has_write_access(self, config):
        influx_url_parsed = urlparse(config['host'])
        influx_url = influx_url_parsed.netloc.split(':')
        args = {'database': config['db'], 'host': influx_url[0], 'port': influx_url[1]}
        if config['username'] != '':
            args['username'] = config['username']
            args['password'] = config['password']
        if influx_url_parsed.scheme == 'https':
            args['ssl'] = True
        client = InfluxDBClient(**args)
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

    def prompt(self, default_config, advanced=False):
        config = dict()
        config['host'] = click.prompt('InfluxDB API url', type=click.STRING, default=default_config.get('host'))
        if not is_url(config['host']):
            raise click.UsageError(f"{config['host']} is not and url")

        config['username'] = click.prompt('Username', type=click.STRING, default=default_config.get('username', ''))
        config['password'] = click.prompt('Password', type=click.STRING, default=default_config.get('password', ''))

        config['db'] = click.prompt('Database', type=click.STRING, default=default_config.get('db'))
        if config['username'] != '' and not self.has_write_access(config):
            config['write_host'] = click.prompt('InfluxDB API url for writing data', type=click.STRING,
                                                default=default_config.get('write_host'))
            if not is_url(config['write_host']):
                raise click.UsageError(f"{config['write_host']} is not and url")

            config['write_username'] = click.prompt('Username', type=click.STRING,
                                                    default=default_config.get('write_username', ''))
            config['write_password'] = click.prompt('Password', type=click.STRING,
                                                    default=default_config.get('write_password', ''))
            config['write_db'] = click.prompt('Write database', type=click.STRING,
                                              default=default_config.get('write_db', ''))

        config['offset'] = click.prompt(
            'Initial offset (amount of days ago or specific date in format "dd/MM/yyyy HH:mm")',
            type=click.STRING,
            default=default_config.get('offset', '')).strip()
        if config['offset']:
            if config['offset'].isdigit():
                try:
                    int(config['offset'])
                except ValueError:
                    raise click.UsageError(config['offset'] + ' is not a valid integer')
            else:
                try:
                    datetime.strptime(config['offset'], '%d/%m/%Y %H:%M').timestamp()
                except ValueError as e:
                    raise click.UsageError(str(e))

        return config
