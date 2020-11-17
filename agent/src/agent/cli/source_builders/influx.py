import click

from .abstract_builder import Builder
from agent.modules.tools import infinite_retry, print_dicts, map_keys, if_validation_enabled
from agent import source, pipeline


class InfluxSourceBuilder(Builder):
    def prompt(self, default_config, advanced=False):
        self.prompt_connection(default_config)
        self.prompt_db(default_config)
        self.prompt_offset(default_config)
        self.source.set_config(self.source.config)
        return self.source

    @infinite_retry
    def prompt_connection(self, default_config):
        self.source.config['host'] = click.prompt('InfluxDB API url', type=click.STRING,
                                                  default=default_config.get('host')).strip()
        try:
            self.validator.validate_connection()
        except source.validator.ValidationException as e:
            raise click.UsageError(e)
        print('Successfully connected to the source')

    @infinite_retry
    def prompt_db(self, default_config):
        self.source.config['username'] = click.prompt('Username', type=click.STRING,
                                                      default=default_config.get('username', '')).strip()
        self.source.config['password'] = click.prompt('Password', type=click.STRING,
                                                      default=default_config.get('password', ''))
        self.source.config['db'] = click.prompt('Database', type=click.STRING, default=default_config.get('db')).strip()
        try:
            self.validator.validate_db()
        except source.validator.ValidationException as e:
            raise click.UsageError(e)
        click.secho('Access authorized')

    @infinite_retry
    def prompt_offset(self, default_config):
        self.source.config['offset'] = click.prompt(
            'Initial offset (amount of days ago or specific date in format "dd/MM/yyyy HH:mm")',
            type=click.STRING,
            default=default_config.get('offset', '')).strip()
        try:
            self.validator.validate_offset()
        except source.validator.ValidationException as e:
            raise click.UsageError(e)

    @if_validation_enabled
    def print_sample_data(self, pipeline_: pipeline.Pipeline):
        records, errors = self._get_sample_records(pipeline_)
        if records and 'series' in records[0]['results'][0]:
            series = records[0]['results'][0]['series'][0]
            print_dicts(map_keys(series['values'], series['columns']))
        else:
            print('No preview data available')
        print(*errors, sep='\n')
