import click

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
        self.prompt_timestamp()
        self.set_values()
        self.set_dimensions()
        self.prompt_static_dimensions()
        self.prompt_tags()
        self.set_uses_schema()

    @infinite_retry
    def set_query(self):
        self.config['query'] = click.prompt('Query', type=click.STRING, default=self.default_config.get('query'))
        errors = jdbc_query.get_errors(self.config['query'])
        if errors:
            raise click.ClickException(errors)

    @infinite_retry
    def set_values(self):
        self.config['count_records'] = click.confirm('Count records?',
                                                     default=self.default_config.get('count_records', False))
        if self.config['count_records']:
            self.config['count_records_measurement_name'] = click.prompt('Measurement name', type=click.STRING,
                                                                         default=self.default_config.get(
                                                                             'count_records_measurement_name'))
        self.prompt_values()

        if not self.config['count_records'] and not self.config['values']:
            raise click.UsageError('Set value columns or count records flag')

    def set_dimensions(self):
        self.config['dimensions'] = self.prompt_dimensions('Dimensions', self.default_config.get('dimensions', []))
