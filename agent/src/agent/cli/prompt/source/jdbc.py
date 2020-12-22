import click

from .abstract_builder import Builder
from agent.modules.tools import infinite_retry
from agent import source


class JDBCSourceBuilder(Builder):
    def prompt(self, default_config, advanced=False):
        self.prompt_connection(default_config)
        return self.source

    @infinite_retry
    def prompt_connection_string(self, default_config):
        self.source.config[source.JDBCSource.CONFIG_CONNECTION_STRING] = \
            click.prompt('Connection string',
                         type=click.STRING,
                         default=default_config.get(source.JDBCSource.CONFIG_CONNECTION_STRING)).strip()
        try:
            self.validator.validate_connection_string()
        except source.validator.ValidationException as e:
            raise click.UsageError(e)

    @infinite_retry
    def prompt_connection(self, default_config):
        self.prompt_connection_string(default_config)
        self.source.config[source.JDBCSource.CONFIG_USERNAME] = \
            click.prompt('Username', type=click.STRING,
                         default=default_config.get(source.JDBCSource.CONFIG_USERNAME, '')).strip()
        self.source.config[source.JDBCSource.CONFIG_PASSWORD] = \
            click.prompt('Password', type=click.STRING,
                         default=default_config.get(source.JDBCSource.CONFIG_PASSWORD, ''))
        self.validator.validate_connection()
        print('Successfully connected to the source')
