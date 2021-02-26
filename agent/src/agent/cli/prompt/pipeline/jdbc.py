import click

from agent import pipeline
from agent.modules.tools import infinite_retry
from agent.pipeline.validators import jdbc_query
from .base import Prompter


class JDBCPrompter(Prompter):
    timestamp_types = ['datetime', 'unix', 'unix_ms']

    def prompt_config(self):
        self.set_query()
        self.data_preview()
        self.prompt_interval()
        self.prompt_days_to_backfill()
        self.prompt_delay()
        self.set_timestamp()
        self.set_values()
        self.set_dimensions()
        self.set_static_dimensions()
        self.set_tags()
        self.set_uses_schema()

    @infinite_retry
    def prompt_values(self):
        self.config['values'] = self.prompt_object(
            'Value columns with target types. Example - column:counter column2:gauge',
            self.get_default_object_value('values')
        )
        if not set(self.config['values'].values()).issubset(('counter', 'gauge')):
            raise click.UsageError('Target type should be counter or gauge')
        self.validate_properties_names(self.config['values'].keys(), self.pipeline.source.sample_data)

    @infinite_retry
    def set_query(self):
        self.config['query'] = click.prompt('Query', type=click.STRING, default=self.default_config.get('query'))
        errors = jdbc_query.get_errors(self.config['query'])
        if errors:
            raise click.ClickException(errors)

    @infinite_retry
    def set_values(self):
        self.config['count_records'] = int(click.confirm('Count records?',
                                                         default=self.default_config.get('count_records', False)))
        if self.config['count_records']:
            self.config['count_records_measurement_name'] = click.prompt('Measurement name', type=click.STRING,
                                                                         default=self.default_config.get(
                                                                             'count_records_measurement_name'))
        self.prompt_values()

        if not self.config['count_records'] and not self.config['values']:
            raise click.UsageError('Set value columns or count records flag')

    def set_dimensions(self):
        self.config['dimensions'] = self.prompt_dimensions('Dimensions', self.default_config.get('dimensions', []))
