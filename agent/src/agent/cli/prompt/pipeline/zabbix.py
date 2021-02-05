import json
import click

from agent.cli.prompt.pipeline.schemaless import PromptConfigSchemaless
from agent.modules.tools import infinite_retry


class PromptConfigZabbix(PromptConfigSchemaless):
    def prompt_config(self):
        self.prompt_query_file()
        self.prompt_days_to_backfill()
        self.prompt_interval()
        self.data_preview()
        self.set_values()
        self.set_measurement_names()
        self.set_dimensions()
        self.prompt_delay()
        self.set_transform()
        self.set_static_properties()
        self.set_tags()
        # todo code duplicate
        self.config['timestamp'] = {}
        self.config['timestamp']['type'] = 'unix'
        self.config['timestamp']['name'] = 'clock'

    @infinite_retry
    def set_values(self):
        self.config['static_what'] = False
        self.config['count_records'] = \
            int(click.confirm('Count records?', default=self.default_config.get('count_records', False)))
        if self.config['count_records']:
            self.config['count_records_measurement_name'] = click.prompt(
                'Measurement name',
                type=click.STRING,
                default=self.default_config.get('count_records_measurement_name')
            )
        self.prompt_values()
        if not self.config['count_records'] and not self.config['values']:
            raise click.UsageError('Set value properties or count records flag')

    @infinite_retry
    def prompt_query_file(self):
        self.config['query_file'] = click.prompt('File with query params', type=click.STRING, default=self.default_config.get('query_file'))
        with open(self.config['query_file']) as fp:
            self.config['query'] = json.load(fp)

    def set_dimensions(self):
        self.config['dimensions'] = self.prompt_dimensions('Dimensions', self.default_config.get('dimensions', []))
