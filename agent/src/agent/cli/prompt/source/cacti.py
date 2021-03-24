import click

from .base import Prompter
from agent.modules.tools import infinite_retry
from agent import source
from agent.modules import validator


class CactiPrompter(Prompter):
    def prompt(self, default_config, advanced=False):
        self.prompt_mysql_connection(default_config)
        self.prompt_rrd_dir(default_config)
        self.source.set_config(self.source.config)
        return self.source

    @infinite_retry
    def prompt_mysql_connection(self, default_config):
        self.source.config[source.CactiSource.MYSQL_CONNECTION_STRING] = click.prompt(
            'Mysql connection string in format `mysql://username:pass@host:port/database`',
            type=click.STRING,
            default=default_config.get(source.CactiSource.MYSQL_CONNECTION_STRING)
        ).strip()

        self.validator.validate_connection()

    @infinite_retry
    def prompt_rrd_dir(self, default_config):
        directory = click.prompt(
            'Path to the directory containing rrd files',
            type=click.STRING,
            default=default_config.get(source.CactiSource.RRD_DIR)
        ).strip()
        validator.validate_dir(directory)
        self.source.config[source.CactiSource.RRD_DIR] = directory
