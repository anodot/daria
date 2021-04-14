import click

from .base import Prompter
from agent.modules.tools import infinite_retry
from agent import source
from agent.modules import validator


class CactiPrompter(Prompter):
    def prompt(self, default_config, advanced=False):
        self.prompt_mysql_connection(default_config)
        self.prompt_rrd_location(default_config)
        self.prompt_source_cache_ttl(default_config)
        self.source.set_config(self.source.config)
        return self.source

    @infinite_retry
    def prompt_mysql_connection(self, default_config: dict):
        self.source.config[source.CactiSource.MYSQL_CONNECTION_STRING] = click.prompt(
            'Mysql connection string in format `mysql://username:pass@host:port/database`',
            type=click.STRING,
            default=default_config.get(source.CactiSource.MYSQL_CONNECTION_STRING)
        ).strip()

        self.validator.validate_connection()

    def prompt_rrd_location(self, default_config: dict):
        if click.confirm('Are rrd files archived?'):
            self._prompt_rrd_archive(default_config)
        else:
            self._prompt_rrd_dir(default_config)

    @infinite_retry
    def _prompt_rrd_archive(self, default_config: dict):
        file_path = click.prompt(
            'Path to the archive with rrd files',
            type=click.STRING,
            default=default_config.get(source.CactiSource.RRD_ARCHIVE_PATH)
        ).strip()
        validator.file_exists(file_path)
        self.source.config[source.CactiSource.RRD_ARCHIVE_PATH] = file_path

    @infinite_retry
    def _prompt_rrd_dir(self, default_config: dict):
        dir_path = click.prompt(
            'Path to the directory with rrd files',
            type=click.STRING,
            default=default_config.get(source.CactiSource.RRD_DIR_PATH)
        ).strip()
        validator.dir_exists(dir_path)
        self.source.config[source.CactiSource.RRD_DIR_PATH] = dir_path

    def prompt_source_cache_ttl(self, default_config: dict):
        self.source.config['cache_ttl'] = click.prompt(
            'Cacti source cache TTL in seconds',
            type=click.INT,
            default=default_config.get('cache_ttl', 3600)
        )
