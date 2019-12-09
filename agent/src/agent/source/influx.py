import click
import time

from .abstract_source import Source
from agent.tools import infinite_retry, is_url, print_dicts, map_keys, if_validation_enabled
from datetime import datetime
from urllib.parse import urlparse
from influxdb import InfluxDBClient
from influxdb.exceptions import InfluxDBClientError


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


class InfluxSource(Source):
    VALIDATION_SCHEMA_FILE_NAME = 'influx.json'
    TEST_PIPELINE_NAME = 'test_influx_qwe093'

    @if_validation_enabled
    def validate_connection(self):
        if not is_url(self.config['host']):
            raise click.UsageError(f"{self.config['host']} - wrong url format. Correct format is `scheme://host:port`")
        client = get_influx_client(self.config['host'])
        client.ping()

    @infinite_retry
    def prompt_connection(self, default_config):
        self.config['host'] = click.prompt('InfluxDB API url', type=click.STRING, default=default_config.get('host')).strip()
        self.validate_connection()
        click.secho('Connection successful')

    @if_validation_enabled
    def validate_db(self):
        client = get_influx_client(self.config['host'], self.config.get('username'), self.config.get('password'))
        if not any([db['name'] == self.config['db'] for db in client.get_list_database()]):
            raise click.UsageError(f"Database {self.config['db']} not found. Please check your credentials again")

    @infinite_retry
    def prompt_db(self, default_config):
        self.config['username'] = click.prompt('Username', type=click.STRING,
                                               default=default_config.get('username', '')).strip()
        self.config['password'] = click.prompt('Password', type=click.STRING,
                                               default=default_config.get('password', ''))
        self.config['db'] = click.prompt('Database', type=click.STRING, default=default_config.get('db')).strip()
        self.validate_db()
        click.secho('Access authorized')

    @if_validation_enabled
    def validate_write_host(self):
        if not is_url(self.config['write_host']):
            raise click.UsageError(f"{self.config['write_host']} - wrong url format. Correct format is `scheme://host:port`")
        client = get_influx_client(self.config['write_host'])
        client.ping()

    @infinite_retry
    def prompt_write_host(self, default_config):
        self.config['write_host'] = click.prompt('InfluxDB API url for writing data', type=click.STRING,
                                                 default=default_config.get('write_host')).strip()
        self.validate_write_host()
        click.secho('Connection successful')

    @if_validation_enabled
    def validate_write_db(self):
        client = get_influx_client(self.config['write_host'], self.config.get('write_username'),
                                   self.config.get('write_password'))
        if not any([db['name'] == self.config['write_db'] for db in client.get_list_database()]):
            raise click.UsageError(f"Database {self.config['write_db']} not found. Please check your credentials again")

    @infinite_retry
    def prompt_write_db(self, default_config):
        self.config['write_username'] = click.prompt('Username', type=click.STRING,
                                                     default=default_config.get('write_username', '')).strip()
        self.config['write_password'] = click.prompt('Password', type=click.STRING,
                                                     default=default_config.get('write_password', ''))
        self.config['write_db'] = click.prompt('Write database', type=click.STRING,
                                               default=default_config.get('write_db', '')).strip()
        self.validate_write_db()
        self.validate_write_access()
        click.secho('Access authorized')

    @if_validation_enabled
    def validate_write_access(self):
        client = get_influx_client(self.config['write_host'], self.config.get('write_username'),
                                   self.config.get('write_password'),
                                   self.config['write_db'])
        if not has_write_access(client):
            raise click.UsageError(f"""User {self.config.get('write_username')} does not have write permissions for db
             {self.config['write_db']} at {self.config['write_host']}""")

    def validate_offset(self):
        if not self.config.get('offset'):
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

    @infinite_retry
    def prompt_offset(self, default_config):
        self.config['offset'] = click.prompt(
            'Initial offset (amount of days ago or specific date in format "dd/MM/yyyy HH:mm")',
            type=click.STRING,
            default=default_config.get('offset', '')).strip()
        self.validate_offset()

    def prompt(self, default_config, advanced=False):
        self.config = dict()
        self.prompt_connection(default_config)
        self.prompt_db(default_config)

        client = get_influx_client(self.config['host'], self.config['username'], self.config['password'],
                                   self.config['db'])
        if self.config['username'] != '' and not has_write_access(client):
            self.prompt_write_host(default_config)
            self.prompt_write_db(default_config)

        self.prompt_offset(default_config)

        return self.config

    def validate(self):
        super().validate()
        self.validate_connection()
        self.validate_db()
        if 'write_host' in self.config:
            self.validate_write_host()
            self.validate_write_db()
            self.validate_write_access()
        self.validate_offset()

    @if_validation_enabled
    def print_sample_data(self):
        records = self.get_sample_records()
        if not records or 'series' not in records[0]['results'][0]:
            print('No preview data available')
            return
        series = records[0]['results'][0]['series'][0]
        print_dicts(map_keys([item for key, item in series['values'].items()], series['columns']))
