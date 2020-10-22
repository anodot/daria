import click

from agent.modules.tools import infinite_retry
from .base import PromptConfig


class PromptConfigJDBC(PromptConfig):
    timestamp_types = ['datetime', 'unix', 'unix_ms']

    def prompt_config(self):
        self.set_query()
        self.prompt_interval()
        self.prompt_days_to_backfill()
        self.prompt_delay()
        self.set_timestamp()
        self.data_preview()
        self.set_values()
        self.set_dimensions()
        self.set_static_properties()
        self.set_tags()

    @infinite_retry
    def prompt_values(self):
        self.config['values'] = self.prompt_object(
            'Value columns with target types. Example - column:counter column2:gauge',
            self.get_default_object_value('values')
        )
        if not set(self.config['values'].values()).issubset(('counter', 'gauge')):
            raise click.UsageError('Target type should be counter or gauge')
        self.validate_properties_names(self.config['values'].keys(), self.pipeline.source.sample_data)

    def set_query(self):
        self.config['query'] = click.prompt('Query', type=click.STRING, default=self.default_config.get('query'))

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
