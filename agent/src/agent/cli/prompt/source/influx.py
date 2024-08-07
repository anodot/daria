import click

from .base import Prompter
from agent.modules.tools import infinite_retry
from agent import source


class InfluxPrompter(Prompter):
    def prompt(self, default_config, advanced=False):
        self.prompt_connection(default_config)
        self.prompt_db(default_config)
        self.prompt_offset(default_config)
        self.source.set_config(self.source.config)
        return self.source

    @infinite_retry
    def prompt_connection(self, default_config):
        self.source.config['host'] = click.prompt(
            'InfluxDB API url', type=click.STRING, default=default_config.get('host')
        ).strip()
        try:
            self.validator.validate_connection()
        except source.validator.ValidationException as e:
            raise click.UsageError(str(e))
        print('Successfully connected to the source')

    @infinite_retry
    def prompt_db(self, default_config):
        self._prompt_db(default_config)
        try:
            self.validator.validate_db()
        except source.validator.ValidationException as e:
            raise click.UsageError(str(e))
        click.secho('Access authorized')

    def _prompt_db(self, default_config: dict):
        self.source.config['username'] = click.prompt(
            'Username', type=click.STRING, default=default_config.get('username', '')
        ).strip()
        self.source.config['password'] = click.prompt(
            'Password', type=click.STRING, default=default_config.get('password', '')
        )
        self.source.config['db'] = click.prompt('Database', type=click.STRING, default=default_config.get('db')).strip()

    @infinite_retry
    def prompt_offset(self, default_config):
        self.source.config['offset'] = click.prompt(
            'Initial offset (amount of days ago or specific date in format "dd/MM/yyyy HH:mm")',
            type=click.STRING,
            default=default_config.get('offset', '')).strip()
        try:
            self.validator.validate_offset()
        except source.validator.ValidationException as e:
            raise click.UsageError(str(e))


class Influx2Prompter(InfluxPrompter):
    def prompt(self, default_config, advanced=False):
        self.prompt_connection(default_config)
        self.prompt_db(default_config)
        self.prompt_org(default_config)
        self.prompt_offset(default_config)
        self.source.set_config(self.source.config)
        return self.source

    def _prompt_db(self, default_config: dict):
        self.source.config['token'] = click.prompt('Token', type=click.STRING, default=default_config.get('token', ''))
        self.source.config['bucket'] = click.prompt(
            'Bucket', type=click.STRING, default=default_config.get('bucket')
        ).strip()

    def prompt_org(self, default_config: dict):
        self.source.config['org'] = \
            click.prompt('Organization', type=click.STRING, default=default_config.get('org'))
