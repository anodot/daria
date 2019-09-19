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


def get_influx_client(host, username=None, password=None, db=None):
    influx_url_parsed = urlparse(host)
    influx_url = influx_url_parsed.netloc.split(':')
    args = {'host': influx_url[0]}
    if len(influx_url) > 1:
        args['port'] = influx_url[1]
    if username and username != '':
        args['username'] = username
        args['password'] = password
    if influx_url_parsed.scheme == 'https':
        args['ssl'] = True

    if db:
        args['database'] = db
    return InfluxDBClient(**args)


def has_write_access(client):
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


class InfluxSource(Source):

    @infinite_retry
    def prompt_connection(self, default_config):
        self.config['host'] = click.prompt('InfluxDB API url', type=click.STRING, default=default_config.get('host'))
        if not is_url(self.config['host']):
            raise click.UsageError(f"Wrong url format. Correct format is `scheme://host:port`")

        client = get_influx_client(self.config['host'])
        client.ping()
        click.secho('Connection successful')

    @infinite_retry
    def prompt_db(self, default_config):
        self.config['username'] = click.prompt('Username', type=click.STRING,
                                               default=default_config.get('username', ''))
        self.config['password'] = click.prompt('Password', type=click.STRING,
                                               default=default_config.get('password', ''))
        self.config['db'] = click.prompt('Database', type=click.STRING, default=default_config.get('db'))
        client = get_influx_client(self.config['host'], self.config['username'], self.config['password'])
        if not any([db['name'] == self.config['db'] for db in client.get_list_database()]):
            raise click.UsageError('Database not found. Please check your credentials again')
        click.secho('Access authorized')

    @infinite_retry
    def prompt_write_host(self, default_config):
        self.config['write_host'] = click.prompt('InfluxDB API url for writing data', type=click.STRING,
                                                 default=default_config.get('write_host'))
        if not is_url(self.config['write_host']):
            raise click.UsageError(f"{self.config['write_host']} is not and url")

        client = get_influx_client(self.config['write_host'])
        client.ping()
        click.secho('Connection successful')

    @infinite_retry
    def prompt_write_db(self, default_config):
        self.config['write_username'] = click.prompt('Username', type=click.STRING,
                                                     default=default_config.get('write_username', ''))
        self.config['write_password'] = click.prompt('Password', type=click.STRING,
                                                     default=default_config.get('write_password', ''))
        self.config['write_db'] = click.prompt('Write database', type=click.STRING,
                                               default=default_config.get('write_db', ''))
        client = get_influx_client(self.config['write_host'], self.config['write_username'],
                                   self.config['write_password'])
        if not any([db['name'] == self.config['write_db'] for db in client.get_list_database()]):
            raise click.UsageError('Database not found. Please check your credentials again')

    @infinite_retry
    def prompt_write_access(self, default_config):
        self.prompt_write_host(default_config)
        self.prompt_write_db(default_config)
        client = get_influx_client(self.config['write_host'], self.config['write_username'],
                                   self.config['write_password'],
                                   self.config['write_db'])
        if not has_write_access(client):
            raise click.UsageError('Client does not have write permissions')

    @infinite_retry
    def prompt_offset(self, default_config):
        self.config['offset'] = click.prompt(
            'Initial offset (amount of days ago or specific date in format "dd/MM/yyyy HH:mm")',
            type=click.STRING,
            default=default_config.get('offset', '')).strip()
        if not self.config['offset']:
            return

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
        self.prompt_db(default_config)
        client = get_influx_client(self.config['host'], self.config['username'], self.config['password'],
                                   self.config['db'])
        if self.config['username'] != '' and not has_write_access(client):
            self.prompt_write_access(default_config)

        self.prompt_offset(default_config)
        return self.config
