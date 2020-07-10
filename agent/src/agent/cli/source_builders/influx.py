import click
import time

from .abstract_builder import Builder
from agent.tools import infinite_retry, is_url, print_dicts, map_keys, if_validation_enabled
from datetime import datetime
from urllib.parse import urlparse
from influxdb import InfluxDBClient
from influxdb.exceptions import InfluxDBClientError
from agent import source


def get_influx_client(host, username=None, password=None, db=None):
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


class InfluxSource(Builder):
    def prompt(self, default_config, advanced=False):
        self.prompt_connection(default_config)
        self.prompt_db(default_config)

        client = get_influx_client(self.source.config['host'], self.source.config['username'],
                                   self.source.config['password'],
                                   self.source.config['db'])
        if self.source.config['username'] != '' and not has_write_access(client):
            self.prompt_write_host(default_config)
            self.prompt_write_db(default_config)
        self.prompt_offset(default_config)
        # todo refactor
        self.source.set_config(self.source.config)
        return self.source

    def validate(self):
        source.validator.validate_json(self.source)
        self.validate_connection()
        self.validate_db()
        if 'write_host' in self.source.config:
            self.validate_write_host()
            self.validate_write_db()
            self.validate_write_access()
        self.validate_offset()

    @if_validation_enabled
    def validate_connection(self):
        if not is_url(self.source.config['host']):
            raise click.UsageError(
                f"{self.source.config['host']} - wrong url format. Correct format is `scheme://host:port`")
        client = get_influx_client(self.source.config['host'])
        client.ping()
        click.secho('Connection successful')

    @infinite_retry
    def prompt_connection(self, default_config):
        self.source.config['host'] = click.prompt('InfluxDB API url', type=click.STRING,
                                                  default=default_config.get('host')).strip()
        self.validate_connection()

    @if_validation_enabled
    def validate_db(self):
        client = get_influx_client(self.source.config['host'], self.source.config.get('username'),
                                   self.source.config.get('password'))
        if not any([db['name'] == self.source.config['db'] for db in client.get_list_database()]):
            raise click.UsageError(
                f"Database {self.source.config['db']} not found. Please check your credentials again")
        click.secho('Access authorized')

    @infinite_retry
    def prompt_db(self, default_config):
        self.source.config['username'] = click.prompt('Username', type=click.STRING,
                                                      default=default_config.get('username', '')).strip()
        self.source.config['password'] = click.prompt('Password', type=click.STRING,
                                                      default=default_config.get('password', ''))
        self.source.config['db'] = click.prompt('Database', type=click.STRING, default=default_config.get('db')).strip()
        self.validate_db()

    @if_validation_enabled
    def validate_write_host(self):
        if not is_url(self.source.config['write_host']):
            raise click.UsageError(
                f"{self.source.config['write_host']} - wrong url format. Correct format is `scheme://host:port`")
        client = get_influx_client(self.source.config['write_host'])
        client.ping()
        click.secho('Connection successful')

    @infinite_retry
    def prompt_write_host(self, default_config):
        self.source.config['write_host'] = click.prompt('InfluxDB API url for writing data', type=click.STRING,
                                                        default=default_config.get('write_host')).strip()
        self.validate_write_host()

    @if_validation_enabled
    def validate_write_db(self):
        client = get_influx_client(self.source.config['write_host'], self.source.config.get('write_username'),
                                   self.source.config.get('write_password'))
        if not any([db['name'] == self.source.config['write_db'] for db in client.get_list_database()]):
            raise click.UsageError(
                f"Database {self.source.config['write_db']} not found. Please check your credentials again")

    @infinite_retry
    def prompt_write_db(self, default_config):
        self.source.config['write_username'] = click.prompt('Username', type=click.STRING,
                                                            default=default_config.get('write_username', '')).strip()
        self.source.config['write_password'] = click.prompt('Password', type=click.STRING,
                                                            default=default_config.get('write_password', ''))
        self.source.config['write_db'] = click.prompt('Write database', type=click.STRING,
                                                      default=default_config.get('write_db', '')).strip()
        self.validate_write_db()
        self.validate_write_access()

    @if_validation_enabled
    def validate_write_access(self):
        client = get_influx_client(self.source.config['write_host'], self.source.config.get('write_username'),
                                   self.source.config.get('write_password'),
                                   self.source.config['write_db'])
        if not has_write_access(client):
            raise click.UsageError(
                f"""User {self.source.config.get('write_username')} does not have write permissions for db
             {self.source.config['write_db']} at {self.source.config['write_host']}""")

        click.secho('Access authorized')

    def validate_offset(self):
        if not self.source.config.get('offset'):
            return

        if self.source.config['offset'].isdigit():
            try:
                int(self.source.config['offset'])
            except ValueError:
                raise click.UsageError(self.source.config['offset'] + ' is not a valid integer')
        else:
            try:
                datetime.strptime(self.source.config['offset'], '%d/%m/%Y %H:%M').timestamp()
            except ValueError as e:
                raise click.UsageError(str(e))

    @infinite_retry
    def prompt_offset(self, default_config):
        self.source.config['offset'] = click.prompt(
            'Initial offset (amount of days ago or specific date in format "dd/MM/yyyy HH:mm")',
            type=click.STRING,
            default=default_config.get('offset', '')).strip()
        self.validate_offset()

    @if_validation_enabled
    def print_sample_data(self):
        records = self.get_sample_records()
        if not records or 'series' not in records[0]['results'][0]:
            print('No preview data available')
            return
        series = records[0]['results'][0]['series'][0]
        print_dicts(map_keys(series['values'], series['columns']))
