import click

from .abstract_source import Source
from agent.tools import infinite_retry, is_url, print_dicts, if_validation_enabled
from sqlalchemy import create_engine
from urllib.parse import urlparse, urlunparse


class JDBCSource(Source):
    VALIDATION_SCHEMA_FILE_NAME = 'jdbc.json'
    TEST_PIPELINE_NAME = 'test_jdbc_pdsf4587'

    def get_connection_url(self):
        conn_info = urlparse(self.config['connection_string'])
        if self.config.get('hikariConfigBean.useCredentials'):
            userpass = self.config['hikariConfigBean.username'] + ':' + self.config['hikariConfigBean.password']
            netloc = userpass + '@' + conn_info.netloc
        else:
            netloc = conn_info.netloc

        scheme = conn_info.scheme + '+mysqlconnector' if self.type == 'mysql' else conn_info.scheme

        return urlunparse((scheme, netloc, conn_info.path, '', '', ''))

    def validate_connection_string(self):
        if not is_url(self.config['connection_string']):
            raise click.UsageError('Wrong url format. Correct format is `scheme://host:port`')

        result = urlparse(self.config['connection_string'])
        if self.type == 'mysql' and result.scheme != 'mysql':
            raise click.UsageError('Wrong url scheme. Use `mysql`')
        if self.type == 'postgres' and result.scheme != 'postgresql':
            raise click.UsageError('Wrong url scheme. Use `postgresql`')

    @infinite_retry
    def prompt_connection_string(self, default_config):
        self.config['connection_string'] = click.prompt('Connection string',
                                                        type=click.STRING,
                                                        default=default_config.get('connection_string')).strip()
        self.validate_connection_string()

    @if_validation_enabled
    def validate_connection(self):
        eng = create_engine(self.get_connection_url())
        eng.connect()
        click.secho('Connection successful')

    @infinite_retry
    def prompt_connection(self, default_config):
        self.prompt_connection_string(default_config)
        self.config['hikariConfigBean.username'] = click.prompt('Username',
                                                                type=click.STRING,
                                                                default=default_config.get('hikariConfigBean.username',
                                                                                           '')).strip()
        self.config['hikariConfigBean.password'] = click.prompt('Password',
                                                                type=click.STRING,
                                                                default=default_config.get('hikariConfigBean.password',
                                                                                           ''))
        if self.config['hikariConfigBean.password'] != '':
            self.config['hikariConfigBean.useCredentials'] = True

        self.validate_connection()

    def prompt(self, default_config, advanced=False):
        self.config = dict()
        self.prompt_connection(default_config)
        self.config['query_interval'] = click.prompt('Query interval (seconds)', type=click.IntRange(1),
                                                     default=default_config.get('query_interval', 10))

        return self.config

    def validate(self):
        super().validate()
        self.validate_connection_string()
        self.validate_connection()

    def set_config(self, config):
        super().set_config(config)
        self.config['hikariConfigBean.connectionString'] = 'jdbc:' + self.config['connection_string']
        self.config['queryInterval'] = '${' + str(self.config.get('query_interval', '10')) + ' * SECONDS}'

    @if_validation_enabled
    def print_sample_data(self):
        records = self.get_sample_records()
        if not records:
            return

        print_dicts(records)
