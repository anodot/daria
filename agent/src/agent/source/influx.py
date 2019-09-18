import click
import time

from .abstract_source import Source
from agent.tools import infinite_retry
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

    def get_influx_client(self):
        influx_url_parsed = urlparse(self.config['host'])
        influx_url = influx_url_parsed.netloc.split(':')
        args = {'host': influx_url[0], 'port': influx_url[1]}
        if self.config['username'] != '':
            args['username'] = self.config['username']
            args['password'] = self.config['password']
        if influx_url_parsed.scheme == 'https':
            args['ssl'] = True

        if self.config.get('db'):
            args['database'] = self.config['db']
        return InfluxDBClient(**args)

    def has_write_access(self):
        client = self.get_influx_client()
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

    @infinite_retry
    def prompt_connection(self, default_config):
        self.config['host'] = click.prompt('InfluxDB API url', type=click.STRING, default=default_config.get('host'))
        if not is_url(self.config['host']):
            raise click.UsageError(f"{self.config['host']} is not and url")

        self.config['username'] = click.prompt('Username', type=click.STRING, default=default_config.get('username', ''))
        self.config['password'] = click.prompt('Password', type=click.STRING, default=default_config.get('password', ''))

        client = self.get_influx_client()
        client.ping()

    @infinite_retry
    def prompt_write_access(self, default_config):
        self.config['write_host'] = click.prompt('InfluxDB API url for writing data', type=click.STRING,
                                            default=default_config.get('write_host'))
        if not is_url(self.config['write_host']):
            raise click.UsageError(f"{self.config['write_host']} is not and url")

        self.config['write_username'] = click.prompt('Username', type=click.STRING,
                                                default=default_config.get('write_username', ''))
        self.config['write_password'] = click.prompt('Password', type=click.STRING,
                                                default=default_config.get('write_password', ''))
        self.config['write_db'] = click.prompt('Write database', type=click.STRING,
                                          default=default_config.get('write_db', ''))

    @infinite_retry
    def prompt_offset(self, default_config):
        self.config['offset'] = click.prompt(
            'Initial offset (amount of days ago or specific date in format "dd/MM/yyyy HH:mm")',
            type=click.STRING,
            default=default_config.get('offset', '')).strip()
        if self.config['offset']:
            if self.config['offset'].isdigit():
                try:
                    int(self.config['offset'])
                except ValueError:
                    raise click.UsageError(self.config['offset'] + ' is not a valid integer')
            else:
                try:
                    datetime.strptime(self.config['offset'], '%d/%m/%Y %H:%M').timestamp()
                except ValueError as e:
                    raise click.UsageError(str(e))

    def prompt(self, default_config, advanced=False):
        self.config = dict()
        self.prompt_connection(default_config)
        self.config['db'] = click.prompt('Database', type=click.STRING, default=default_config.get('db'))

        if self.config['username'] != '' and not self.has_write_access():
            self.prompt_write_access(default_config)

        self.prompt_offset(default_config)
        return self.config
